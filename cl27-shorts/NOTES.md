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

The PDF is a prompt template: `/motion-kartun` + "Buatkan video penjelasan dengan bahasa Indonesia" + the skill's style
line (flat 2D bean-head characters, colourful 3D world, black ink outlines, painted textures, depth of field, gliding
cameras, 1080x1920 30 fps, as long as the voiceover, voice unchanged, music and SFX at 50 % of the voice), then two
blanks for the user to fill: **Tema Video** and **Script**. So the next video is an Indonesian explainer cartoon.

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

## Real Madrid / Barcelona 3D cartoon shorts (`kartun-spain/`)

- Female Gemini TTS voice (Zephyr), scripts in `kartun-spain/scripts.json`; videos 54 s and 52 s, HUSS gag at 9/18/27/36/45 s.
- Native 1080x1920 three.js render (`render.js`, headless Chromium + SwiftShader, ~2.8 s/frame alone, ~7 s/frame with 3 workers).
- Crests: the user's own crests from `golazo-night-cup/index.html` (`LOGO.rma`, `LOGO.bar`), extracted to `web/img/logo_*.png`
  (not committed). `web/badges.js` holds their outlines (OpenCV contour) for the extruded, bevelled 3D badges.
- New look: wet ground with mirror reflections + rain ripples (`WORLD.wet`, mirror pass in `engine.js`), rain streaks,
  bloom and lens flares in the post shader, volume shading on the bean cards, 3D leather ball kick-ups, 3D crown/trophies.
- Real archive photos: Commons API is rate-limited from the cloud and thumbnail downloads were refused, so photo
  pop-ups (`photos` keys in `stories.js`) are skipped unless files are placed in `web/img/<key>.jpg`.

## Full-Blender shorts (`blender/`): Parkir Bus / Catenaccio and Tiki-Taka

- User preference (Nov 2026): from now on the videos are made **fully in Blender**, with the **Night Cup stadium**,
  a **cute female voice** (Gemini TTS "Leda"), light-Jaksel Indonesian, and the "huss huss huss" gag about every 10 s
  placed right after a sentence ends, plus once more after the punchline.
- Blender 4.0 (apt) runs headless with Eevee on llvmpipe: `xvfb-run -a blender -b -y --python film.py -- <story> <a-b> <out> 66 3`.
  About 3.2 s/frame at 66% scale and 3 samples. `post.py` upscales to 1080x1920 and adds bloom/star/anamorphic/ghost flares
  and the HUSS overlay. Blender renders at -0.5 EV so only light sources clip (and bloom); post restores the exposure.
- `decode.py` turns `golazo-night-cup/stadium.js` (GSTD blob) and `pitch.js` (goal GLB, grass, ball, grass tufts) into
  Blender assets. Turf = wet base with screen-space puddle reflections (no Shader-to-RGB there, it disables SSR), 8 grass shells
  from the game's height map, and the game's real tuft tile instanced around the action.
- The game's LED boards, UCL ribbons, giant screens and flags are exported from the running game (`gx/exp.js`): the page is served
  with a small hook that exposes the closure's scene, three.js comes from npm three@0.147.0, fonts from @fontsource, and
  `WebGLRenderer.render` is stubbed so the headless page loads in a few minutes.
- Stadium model licence: CC BY-NC-SA 4.0 (credit Ninh Pham, non-commercial). The boards show real sponsor and club marks.
