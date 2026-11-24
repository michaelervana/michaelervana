# CL27 Shorts pipeline

Ten standalone TikTok videos (1080x1920, under 59 s each) of football facts, in Indonesian, made with Remotion.

- `scripts.json`: the ten scripts (one line per scene).
- `tts.py`: Gemini TTS voiceover, one request per video, cut into one clip per line at the pauses. Needs a Google AI Studio key in `pipeline/.key` (never committed).
- `gem.py`, `hear.py`: Gemini text helpers (transcribe, check the voiceover).
- `capture.js`: records vertical gameplay footage from the Champions League 27 game (served locally), one frame per 50 ms game step.

Material used per video: the reference "Top 10 Facts - Football" video (not in this repo), game footage, and Wikimedia Commons photos.
