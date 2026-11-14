# Singing Bowl Australia

Official website for **singingbowlaustralia.com** — sound healing, free singing bowl sounds, and meditation coaching.

## Live Site
Deployed via Cloudflare Pages.

## Features
- Free singing bowl sound players
- Information about sound healing
- Lead capture form for meditation coaching and healing sessions
- Mobile-responsive, calm spiritual design

## Deploy to Cloudflare Pages
1. Go to Cloudflare Dashboard → Workers & Pages → Create application → Pages
2. Connect to GitHub and select this repository (`singingbowlaustralia`)
3. Build settings:
   - Framework preset: None
   - Build command: (leave empty)
   - Build output directory: `/`
4. Deploy
5. Add your custom domain `singingbowlaustralia.com` in the Pages project settings (Cloudflare will handle DNS since the domain is already there)

## Customize
- Replace placeholder audio files in `index.html` with your own recordings (upload to the repo or use a CDN)
- Update the Formspree form ID in the contact form (or switch to Cloudflare Forms / Netlify Forms)
- Add more pages or sections as needed

## Local Preview
Open `index.html` in a browser.
