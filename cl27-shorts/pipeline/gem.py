import json, base64, subprocess, sys, time, os
K = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.key')).read().strip()
def call(model, body, tries=6):
    for a in range(tries):
        r = subprocess.run(['curl', '-sS', '-m', '600', '-H', 'x-goog-api-key: ' + K, '-H', 'Content-Type: application/json', '-d', '@-', f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'], input=json.dumps(body), capture_output=True, text=True)
        try: d = json.loads(r.stdout)
        except Exception: d = {'error': {'code': 0, 'message': r.stdout[:200] + r.stderr[:200]}}
        if 'error' in d and d['error'].get('code') in (500, 503, 0): print('  retry', model, d['error'].get('code'), file=sys.stderr); time.sleep(10 + a * 15); continue
        return d
    return d
def text(model, parts):
    d = call(model, {"contents": [{"parts": parts}]})
    if 'error' in d: return 'ERR ' + json.dumps(d['error'])[:300]
    return ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
if __name__ == '__main__':
    audio = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'gemini-flash-latest'
    print(text(model, [{"text": "This is the narration of a YouTube video 'Top 10 Facts - Football'. Transcribe it, grouped into short paragraphs, each prefixed with its start timestamp [mm:ss]. Mark where each of the 10 facts begins with '### FACT n:' and a short title."}, {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(open(audio, 'rb').read()).decode()}}]))
