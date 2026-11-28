# Letter accuracy test

Ten invented German letters (job center, immigration office, tax office, landlord, health insurance,
family benefits office, broadcasting fee, library, employment agency, online shop reminder) with the
correct deadline for each. One letter has no deadline on purpose. All names and offices are made up.

Run it before turning the letter API on for the public, and after every change to the AI instructions
in `functions/api/letter.js`. Each letter is one Claude call, so a full run costs a few cents.

## Run locally (recommended)

1. Put the key in `.dev.vars` (never commit it):
   ```
   ANTHROPIC_API_KEY=...
   LETTER_API_ENABLED=true
   ```
2. Start the site with a local limit store and a higher per-visitor limit:
   ```
   npx wrangler pages dev . --port 8788 --kv LETTER_LIMITS --binding LETTER_LIMIT_PER_VISITOR=20
   ```
3. In another terminal: `node tests/letters/run.mjs`

Passing means at least 9 of 10 letters have the right deadline and sender.

## Change the letters

Edit `cases.json`, then run `python3 tests/letters/render_letters.py` to redraw the PNG files.
