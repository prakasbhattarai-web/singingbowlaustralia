# Bowl recordings

The home-page player offers two sounds:

- `prakash-bowl.mp3` (default): Prakash playing his own bowl, taken from the first 41 s of the YouTube Short
  "Singing Bowl Healing Sounds" (youtube.com/shorts/m9YJPf9YVqg). Denoised, loudness-normalised, faded at the end.
- `bowl-1.mp3`: a 2-minute AI-generated singing bowl track (ElevenLabs Music v2.5 via Higgsfield).

The player crossfades the end of a clip into its start, so either one loops smoothly for 5–30 minutes.
If `prakash-bowl.mp3` is missing, the page shows a "recording coming soon" sign-up instead of the player.

To swap in a new recording: run `scripts/prepare-bowl.sh your-recording.m4a audio/prakash-bowl.mp3`.

The About-section video is `video/prakash-singing-bowl.mp4` (same Short, H.264 480p, faststart) with the poster `img/prakash-poster.webp`.
