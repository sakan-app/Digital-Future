# DIGITAL-FUTURE.AI — Security review notes

## What was inspected
The repository's `main` root has a static `index.html`. No `package.json`, Vercel Function/API routes, Supabase client setup, database schema, or server-side controllers were found in the inspected root. This means server-side SQL injection, CSRF/session enforcement, and IDOR cannot be safely fixed in this static repository alone.

## Vercel headers
The security branch adds `vercel.json` with `X-Frame-Options: DENY`, a restrictive CSP, `nosniff`, HSTS, Referrer-Policy, Permissions-Policy, COOP and CORP. CSP currently allows the Tailwind CDN and Google Fonts used by the existing page, HTTPS images, and Supabase HTTPS/WebSocket endpoints as a compatibility baseline. Inline scripts/styles are allowed to preserve the existing page. Prefer self-hosted assets and nonce/hash-based CSP before removing `'unsafe-inline'`.

## XSS
Prefer safe text APIs (`textContent`, form control `value`) and framework auto-escaping. Do not interpolate untrusted values into HTML strings or assign them to `innerHTML`. If rich HTML is a real requirement, sanitize at the render boundary with DOMPurify. Input validation is not a replacement for context-aware output encoding.

## Supabase and IDOR
- Keep the Supabase `service_role` key only in server-side Vercel environment variables; never put it in browser code or any `NEXT_PUBLIC_*` variable.
- The browser may use a publishable/anon key, but access must be constrained by Row Level Security (RLS).
- Enable RLS for every exposed table and write schema-specific policies using `auth.uid()` and verified ownership/role columns.
- Never trust a user ID supplied by the browser. For private records, enforce ownership and role checks in server handlers and RLS.
- The inspected static page did not reveal Supabase schema or server-side handlers, so no generic policies were invented.

## SQL injection and CSRF
- Use parameterized SQL for direct SQL (`$1`, `$2`, etc.) or a safe Supabase query builder; never concatenate user input into SQL.
- For cookie-authenticated state-changing endpoints, verify a session-bound CSRF token and Origin. Use `Secure`, `HttpOnly`, and `SameSite=Strict` cookies where compatible with the authentication flow.
- Validate Stripe/webhook signatures against the raw body if webhook handlers exist.

## Validation
This is a baseline header/documentation change, not a full security certification. Preview deployment and functional tests are required. Audit all JavaScript sinks and actual Supabase tables/functions before claiming all five categories are remediated.
