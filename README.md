# Singing Bowl Australia

Website for **singingbowlaustralia.com**: a free looping singing bowl sound, sound bath bookings, "How much?" interest capture for bowls, and a path into Prakash Bhattarai's Meditation for Beginners community.

Static HTML with one Cloudflare Pages Function (`functions/api/subscribe.js`) that adds form sign-ups to GetResponse.

## Files
- `index.html` is the whole site.
- `functions/api/subscribe.js` handles `POST /api/subscribe`. All three forms (bowl price, session request, recording waitlist) post here.
- `audio/bowl-1.mp3` is the bowl recording (not committed yet). Until it exists, the page shows a "coming soon" waitlist instead of the player. See `audio/README.md`.
- `scripts/prepare-bowl.sh` cleans a phone recording into `audio/bowl-1.mp3`.
- `404.html`, `robots.txt`, `sitemap.xml`, `favicon.svg`.

## GetResponse
Every sign-up goes to one list and gets tags, so you can filter who wants what:

| Tag | Meaning |
|---|---|
| `sba_bowl_quote` | Clicked "How much?" and wants prices |
| `sba_bowl_small` / `_medium` / `_large` / `_help_choose` | Which bowl they asked about |
| `sba_session` + `sba_session_online` / `_inperson` / `_group` | Asked to book a session |
| `sba_sound_waitlist` | Wants the bowl recording when it's ready |
| `sba_updates_optin` | Ticked "also send me occasional emails" (marketing consent) |

The contact's **note** field holds the bowl, suburb and message. Only mail general marketing to contacts tagged `sba_updates_optin`. Everyone else asked for one specific thing: prices, a session reply or the recording.

## Deploy to Cloudflare Pages
1. Cloudflare Dashboard → Workers & Pages → Create → Pages → connect this GitHub repo.
2. Framework preset: None. Build command: empty. Output directory: `/`.
3. Settings → Variables and secrets (Production):
   - `GR_API_KEY`: GetResponse API key (as a **secret**)
   - `GR_CAMPAIGN_ID`: id of the Singing Bowl Australia list
4. Deploy, then add the custom domains `singingbowlaustralia.com` and `www.singingbowlaustralia.com`.

Until the two variables are set, the forms show "Sign-up is not set up yet" rather than losing leads silently.

## Local preview
`python3 -m http.server` in this folder, then open http://localhost:8000. The forms need Cloudflare (`npx wrangler pages dev .`) to actually submit.
