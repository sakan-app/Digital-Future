// Accuracy test for /api/letter: sends the 10 fictional letters and checks the deadline and sender.
// Usage: node tests/letters/run.mjs [api-url]   (default http://localhost:8788/api/letter)
// Each letter is one real Claude call (a few cents). Passing: at least 9 of 10.
import { readFile } from "node:fs/promises";

const here = new URL(".", import.meta.url);
const url = process.argv[2] || "http://localhost:8788/api/letter";
const origin = new URL(url).origin.startsWith("http://") ? "http://localhost" : "https://digital-future.ai";
const cases = JSON.parse(await readFile(new URL("cases.json", here), "utf8"));

let passed = 0;
for (const testCase of cases) {
  const data = (await readFile(new URL(`${testCase.id}.png`, here))).toString("base64");
  const started = Date.now();
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: origin },
    body: JSON.stringify({ language: testCase.language, files: [{ media_type: "image/png", data }] }),
  });
  const body = await response.json().catch(() => ({}));
  const seconds = ((Date.now() - started) / 1000).toFixed(1);
  if (!response.ok) {
    console.log(`FAIL ${testCase.id}: HTTP ${response.status} ${body.error || ""} (${seconds}s)`);
    if (response.status === 503 || response.status === 429) break; // switched off or limited: later cases would fail the same way
    continue;
  }
  const result = body.result || {};
  const deadline = (result.deadline && result.deadline.date) || null;
  const sender = String(result.sender || "").toLowerCase();
  const deadlineOk = deadline === testCase.expected.deadline;
  const senderOk = testCase.expected.sender_contains.some((part) => sender.includes(part.toLowerCase()));
  if (deadlineOk && senderOk) passed++;
  console.log(`${deadlineOk && senderOk ? "PASS" : "FAIL"} ${testCase.id}: deadline ${deadline} (expected ${testCase.expected.deadline}), sender "${result.sender}" ${senderOk ? "ok" : "unexpected"} (${seconds}s)`);
}

console.log(`\n${passed}/${cases.length} passed`);
process.exit(passed >= cases.length - 1 ? 0 : 1);
