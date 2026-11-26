# CL27 Shorts: working notes

Notes for picking this work up again in a later session.

## Next request (waiting for the user's upload)

The user will upload material for the **next video: a breakdown of how the animation is made**, using
**Blender and Remotion** ("breakdown animasinya, cara buatnya"). Wait for the upload before starting, then plan
the breakdown around what they send.

**Use the user's own guides for it:** `next/Skill_Motion_Kartun.md` (the "motion-kartun" skill: idea → script →
voiceover → finished MP4, cartoon cards in a toon-shaded 3D world, music and SFX at 50 % of the voice) and
`next/Prompt_Claude_Motion_Kartun.pdf`. The skill expects a `kit/` folder (engine, tools, vendored three.js and
toon.ts); it was not uploaded, so ask for it or rebuild the parts needed.

## How the user wants videos

- TikTok format: 1080 x 1920, **under 59 s**.
- Several videos are **standalone**, never a numbered series ("jangan 1/10").
- Language: Indonesian, casual South Jakarta style ("agak Jaksel"): mostly Indonesian, a few English terms.
- Voiceover: **Google AI Studio (Gemini TTS)**, Indonesian. Voice used so far: `Puck`. The user supplies the key; keep it in
  `pipeline/.key` (gitignored) and delete it when done.
- Send finished audio and videos **straight into the chat** (no drag and drop for the user).
- The user's Mac is old and slow: do the work (capture, TTS, render) in the cloud session.
- Visual identity: the user's game **Champions League 27** (formerly "Golazo Night Cup", folder `golazo-night-cup/`):
  gameplay footage, Barlow / Barlow Condensed type, navy + gold, end card "CHAMPIONS LEAGUE 27".

## What exists

- `src/Short.tsx`, `src/plans.ts`: one composition per fact (card over blurred copy, full-screen gameplay, hook title,
  big numbers, word-by-word captions, game menu music under the voice, end card).
- `pipeline/`: scripts (`scripts.json`), Gemini TTS (`tts.py`), per-line alignment (`align.py`), gameplay capture
  (`capture.js`).
- Ten videos rendered on 2026-11-24 (cuju, kemari, larangan 1314, soccer, skor 149-0, Maracanazo, Perang Sepak Bola,
  bola tertua, kartu merah, ukuran gawang). Heavy media is not in git.

## Lessons from the first batch

- `gemini-3.8-flash-tts` **reads a style note in the prompt aloud**. Either send only the script, or keep the note and
  cut it off afterwards (`pipeline/align.py` drops it and splits the rest per script line). Always check one clip by
  transcription before using the audio.
- Free tier: about **10 TTS requests per day per model**; one request per video (all lines in one read) fits.
- Headless Chrome here does not trust the proxy's certificate: Google Fonts fail in Remotion renders. Use the local
  fonts in `public/fonts/` (never disable certificate checks).
- Wikimedia Commons API is rate-limited from the cloud container; scraping its HTML pages instead is not allowed.
- Gameplay capture: drive `requestAnimationFrame` by hand (`capture.js`), 20 fps, about 3 s per frame on CPU. Start
  camera moves outside the stands (the first kick-off frames were blocked by the near stand).
- Render: about 6 to 8 minutes per 40 s video with 4 CPU cores. Deliver with `deliver.sh` (about 6 Mbps, 20 to 30 MB).
