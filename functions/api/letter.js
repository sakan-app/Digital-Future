// Letter helper API (Cloudflare Pages Function): POST /api/letter
// Body: { language: "ar" | "en" | "de" | "tr", files: [{ media_type, data }] } where data is base64 without a data: prefix.
// Letters are sent to Claude and never stored or logged. Usage is capped per visitor and per day (KV binding LETTER_LIMITS).
import Anthropic from "@anthropic-ai/sdk";

const MODEL = "claude-opus-5-5";
const LANGUAGES = { ar: "Arabic", en: "English", de: "German", tr: "Turkish" };
const IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const MAX_FILES = 6;
const MAX_TOTAL_BASE64 = 20 * 1024 * 1024;
const ALLOWED_ORIGINS = [
  /^https:\/\/(www\.)?digital-future\.ai$/,
  /^https:\/\/([a-z0-9-]+\.)?digital-future\.pages\.dev$/,
  /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
];

const DEFAULT_LIMIT_PER_VISITOR = 3;
const DEFAULT_LIMIT_PER_DAY = 50;
const COUNTER_TTL = { expirationTtl: 2 * 24 * 60 * 60 };

// The visitor key is a hash of the IP salted with the day, so no IP is stored and days can't be linked.
async function visitorHash(ip, day) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`${day}:${ip}`));
  return [...new Uint8Array(digest)].slice(0, 16).map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

// Counts are approximate (KV is eventually consistent), which is enough for a cost cap.
async function takeQuota(env, request) {
  const day = new Date().toISOString().slice(0, 10);
  const perVisitor = Number(env.LETTER_LIMIT_PER_VISITOR) || DEFAULT_LIMIT_PER_VISITOR;
  const perDay = Number(env.LETTER_LIMIT_PER_DAY) || DEFAULT_LIMIT_PER_DAY;
  const visitorKey = `visitor:${day}:${await visitorHash(request.headers.get("CF-Connecting-IP") || "unknown", day)}`;
  const dayKey = `day:${day}`;
  const [visitorUsed, dayUsed] = (await Promise.all([env.LETTER_LIMITS.get(visitorKey), env.LETTER_LIMITS.get(dayKey)])).map((value) => Number(value) || 0);
  if (dayUsed >= perDay) return "daily_limit_reached";
  if (visitorUsed >= perVisitor) return "limit_reached";
  await Promise.all([
    env.LETTER_LIMITS.put(visitorKey, String(visitorUsed + 1), COUNTER_TTL),
    env.LETTER_LIMITS.put(dayKey, String(dayUsed + 1), COUNTER_TTL),
  ]);
  return null;
}

const RESULT_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["is_official_letter", "sender", "summary", "deadline", "steps", "reply", "unclear"],
  properties: {
    is_official_letter: { type: "boolean" },
    sender: { type: "string" },
    summary: { type: "string" },
    deadline: {
      type: "object",
      additionalProperties: false,
      required: ["date", "description"],
      properties: {
        date: { type: ["string", "null"], description: "YYYY-MM-DD, or null if the letter gives no deadline" },
        description: { type: "string" },
      },
    },
    steps: { type: "array", items: { type: "string" } },
    reply: { type: "string" },
    unclear: { type: "array", items: { type: "string" } },
  },
};

const SYSTEM_PROMPT = `You help people in Germany understand official letters (job center, immigration office, tax office, landlord, health insurance and similar).
Read every page you are given. Then fill the response fields:
- is_official_letter: false if the pages are not a letter; then keep the other fields short and explain that in summary.
- sender: the office or company that sent the letter.
- summary: what the letter says, in 2-4 short, plain sentences.
- deadline: the date by which the reader must act, exactly as written in the letter. Never guess or calculate a date that is not printed; if there is none, use null and say so in description.
- steps: what the reader must do, as short numbered actions in order.
- reply: a short, polite reply in the letter's own language that the reader can send, with placeholders like [your name] for personal details.
- unclear: anything you could not read or are unsure about. Leave it empty only when everything was clear.
Write sender, summary, deadline.description, steps and unclear in the reader's language given in the user message. Use simple words. You explain letters; you do not give legal advice.`;

function json(body, status, origin) {
  const headers = { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
  if (origin) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers["Vary"] = "Origin";
  }
  return new Response(JSON.stringify(body), { status, headers });
}

function allowedOrigin(request) {
  const origin = request.headers.get("Origin");
  return origin && ALLOWED_ORIGINS.some((pattern) => pattern.test(origin)) ? origin : null;
}

export async function onRequestOptions({ request }) {
  const origin = allowedOrigin(request);
  if (!origin) return new Response(null, { status: 403 });
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "600",
      "Vary": "Origin",
    },
  });
}

export async function onRequestPost({ request, env }) {
  const origin = allowedOrigin(request);
  if (!origin) return json({ error: "origin_not_allowed" }, 403);
  // Off until the owner sets LETTER_API_ENABLED=true and ANTHROPIC_API_KEY in Cloudflare.
  if (env.LETTER_API_ENABLED !== "true" || !env.ANTHROPIC_API_KEY) return json({ error: "not_enabled" }, 503, origin);
  // Fail closed: without the LETTER_LIMITS KV binding there is no cost cap, so the API stays off.
  if (!env.LETTER_LIMITS) return json({ error: "not_configured" }, 503, origin);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid_json" }, 400, origin);
  }
  const language = LANGUAGES[body && body.language] ? body.language : "en";
  const files = Array.isArray(body && body.files) ? body.files : [];
  if (files.length === 0 || files.length > MAX_FILES) return json({ error: "files_required", max: MAX_FILES }, 400, origin);

  let total = 0;
  const content = [];
  for (const file of files) {
    const mediaType = String(file && file.media_type || "");
    const data = String(file && file.data || "");
    total += data.length;
    if (!data || !/^[A-Za-z0-9+/=]+$/.test(data)) return json({ error: "invalid_file_data" }, 400, origin);
    if (IMAGE_TYPES.has(mediaType)) {
      content.push({ type: "image", source: { type: "base64", media_type: mediaType, data } });
    } else if (mediaType === "application/pdf") {
      content.push({ type: "document", source: { type: "base64", media_type: "application/pdf", data } });
    } else {
      return json({ error: "unsupported_file_type" }, 400, origin);
    }
  }
  if (total > MAX_TOTAL_BASE64) return json({ error: "files_too_large" }, 413, origin);
  content.push({ type: "text", text: `Reader's language: ${LANGUAGES[language]}. Explain this letter.` });

  const limited = await takeQuota(env, request);
  if (limited) return json({ error: limited }, 429, origin);

  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  try {
    const response = await client.beta.messages.create({
      model: MODEL,
      max_tokens: 16000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: { effort: "medium", format: { type: "json_schema", schema: RESULT_SCHEMA } },
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content }],
    });
    if (response.stop_reason === "refusal") return json({ error: "declined" }, 422, origin);
    if (response.stop_reason === "max_tokens") return json({ error: "too_long" }, 502, origin);
    const text = response.content.find((block) => block.type === "text");
    if (!text) return json({ error: "no_result" }, 502, origin);
    return json({ language, result: JSON.parse(text.text) }, 200, origin);
  } catch (error) {
    // Log only the error type and status, never the letter.
    if (error instanceof Anthropic.RateLimitError) {
      console.error("letter api: rate limited");
      return json({ error: "busy" }, 429, origin);
    }
    if (error instanceof Anthropic.AuthenticationError) {
      console.error("letter api: authentication failed");
      return json({ error: "not_configured" }, 503, origin);
    }
    if (error instanceof Anthropic.APIError) {
      // Anthropic's error message describes the request (e.g. billing or a bad parameter), never the letter.
      const detail = error.error && error.error.error ? error.error.error : {};
      console.error("letter api: upstream error", error.status, detail.type, String(detail.message || "").slice(0, 300));
      return json({ error: "upstream_error" }, 502, origin);
    }
    console.error("letter api: unexpected error", error && error.name);
    return json({ error: "server_error" }, 500, origin);
  }
}
