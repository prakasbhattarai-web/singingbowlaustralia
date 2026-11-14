#!/usr/bin/env bash
# Turn a raw phone recording of a singing bowl into the web loop file.
# Usage: scripts/prepare-bowl.sh path/to/recording.(m4a|mov|mp4|wav) [output.mp3]
# Trims leading silence, removes low rumble, evens out loudness, and exports a 160 kbps stereo MP3.
set -euo pipefail
in="$1"; out="${2:-audio/bowl-1.mp3}"
ffmpeg -hide_banner -y -i "$in" -vn \
  -af "silenceremove=start_periods=1:start_threshold=-50dB,highpass=f=40,loudnorm=I=-20:TP=-2:LRA=11,aformat=channel_layouts=stereo" \
  -ar 44100 -b:a 160k "$out"
ffprobe -v error -show_entries format=duration -of default=nw=1 "$out"
