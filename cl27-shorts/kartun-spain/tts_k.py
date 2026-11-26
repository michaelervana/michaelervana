# One Gemini TTS request per video: script only (no style note, which this model reads aloud), saved as WAV.
import sys, json, base64, subprocess, os, time
K = open(sys.argv[3]).read().strip(); vid = sys.argv[1]; model = sys.argv[2]
V = {v['id']: v for v in json.load(open('scripts.json'))}[vid]
body = {"contents": [{"parts": [{"text": '\n\n'.join(V['lines'])}]}], "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": os.environ.get("VOICE","Zephyr")}}}}}
for a in range(6):
    r = subprocess.run(['curl', '-sS', '-m', '300', '-H', 'x-goog-api-key: ' + K, '-H', 'Content-Type: application/json', '-d', '@-', f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'], input=json.dumps(body), capture_output=True, text=True)
    try: d = json.loads(r.stdout)
    except Exception: d = {'error': {'code': 0}}
    if 'error' in d:
        c = d['error'].get('code'); print(vid, model, c, d['error'].get('message', '')[:100], flush=True)
        if c in (500, 503, 0): time.sleep(15 + a * 20); continue
        sys.exit(1)
    raw = base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data']); out = f'vo/{vid}.wav'
    if raw[:4] == b'RIFF': open(out, 'wb').write(raw)
    else: open(out + '.pcm', 'wb').write(raw); subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', out + '.pcm', out]); os.remove(out + '.pcm')
    print(vid, 'ok', flush=True); sys.exit(0)
sys.exit(1)
