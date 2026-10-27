# Push to Browser — write a large payload through a logged-in page

For an agent driving a Chrome tab (browser MCP running javascript_exec in the page)
that must write big content (full HTML, large JSON) into an app the tab is ALREADY
logged into.

Why: one giant eval freezes / gets rejected, and you must never type credentials.
Fix: ride the page's own authenticated fetch; assemble the payload across small evals.

## Steps
1. base64-encode the UTF-8 payload; record the exact base64 length.
2. Split the base64 into ~3500-char chunks.
3. Chunk 0:      window.__X = '<b64>'; window.__X.length;
4. Chunks 1..n:  window.__X = (window.__X||'') + '<b64>'; window.__X.length;
   (length should grow by the chunk size each call — watch it)
5. VERIFY before using:  window.__X.length === <expectedLength>   // must be true
   short = a chunk was skipped; long = a chunk was doubled. Do NOT post if it fails.
6. Decode (plain atob alone mangles UTF-8):
   const b = Uint8Array.from(atob(window.__X), c => c.charCodeAt(0));
   window.__D = new TextDecoder('utf-8').decode(b);
7. Sanity-check __D: starts / ends / length ~= source.
8. POST via the app's own auth (WordPress):
   await wp.apiFetch({ path:'/wp/v2/pages/<ID>', method:'POST', data:{ content: window.__D } });
9. Verify live: refetch the public URL with ?cb=<Date.now()> and check markers.

## Fixes
- Skipped chunk: window.__X = window.__X.slice(0, <lastGoodLen>); then re-send the missing chunk(s).
- Doubled chunk: same — the length check catches both.
- Always gate the POST on the exact-length check.

## Variations
- Images: don't base64. One eval: <canvas> resize -> toBlob -> FormData ->
  wp.apiFetch({ path:'/wp/v2/media', method:'POST', body: fd }). Resize to display size;
  verify the returned URL loads (new Image()) — a named thumbnail size may not exist yet.
- Small edits: GET ?context=edit, string-replace, POST back (no full re-inject).
- Other apps: swap wp.apiFetch for whatever authenticated client the page exposes.
