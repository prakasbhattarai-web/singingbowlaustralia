# Bowl recordings

The player on the home page loads `audio/bowl-1.mp3`. The current file is a 2-minute AI-generated singing bowl track (ElevenLabs Music v2.5 via Higgsfield). Replace it with Prakash's own recording when ready. If the file is ever removed, the page shows a "recording coming soon" sign-up instead.

How to record (phone is fine):
- Quiet room, no fan, fridge or traffic. Phone 30–50 cm from the bowl, on something soft.
- Strike or rim the bowl, then let it ring all the way out. Strike again every 10–15 seconds.
- Record at least 60 seconds. Longer (2–3 minutes) loops more naturally.

Then run `scripts/prepare-bowl.sh your-recording.m4a` and commit `audio/bowl-1.mp3`.
The player crossfades the end of the clip into the start, so it loops smoothly for 5–30 minutes.
