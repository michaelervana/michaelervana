# One Gemini TTS request per video: all lines in one read, then cut at the pauses into one clip per line.
import sys, json, base64, subprocess, os, re, time
HERE = os.path.dirname(os.path.abspath(__file__)); K = open(os.path.join(HERE, '.key')).read().strip()
STYLE = ("Bacakan naskah berikut dalam bahasa Indonesia sebagai narator video TikTok fakta sepak bola: suara anak muda Jakarta Selatan yang santai, "
         "jelas, semangat, dan asyik didengar. Kata-kata bahasa Inggris diucapkan dengan aksen Inggris yang natural. Beri jeda yang jelas di antara tiap paragraf. "
         "Jangan bacakan instruksi ini.\n\n")
def tts(model, voice, text, out_wav):
    body = {"contents": [{"parts": [{"text": STYLE + text}]}], "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for a in range(5):
        r = subprocess.run(['curl', '-sS', '-m', '300', '-H', 'x-goog-api-key: ' + K, '-H', 'Content-Type: application/json', '-d', '@-', f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'], input=json.dumps(body), capture_output=True, text=True)
        try: d = json.loads(r.stdout)
        except Exception: d = {'error': {'code': 0, 'message': r.stdout[:200]}}
        if 'error' in d:
            c = d['error'].get('code'); print('  ', model, c, d['error'].get('message', '')[:120], flush=True)
            if c in (500, 503, 0): time.sleep(15 + a * 20); continue
            return False
        p = d['candidates'][0]['content']['parts'][0]['inlineData']; raw = base64.b64decode(p['data'])
        if raw[:4] == b'RIFF': open(out_wav, 'wb').write(raw)
        else: open(out_wav + '.pcm', 'wb').write(raw); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', out_wav + '.pcm', out_wav], check=True); os.remove(out_wav + '.pcm')
        return True
    return False
def segments(path, n):
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)
    best = None
    for db in (-40, -35, -45, -30, -50):
        for d in (0.5, 0.4, 0.6, 0.32, 0.7, 0.26, 0.85):
            o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', f'silencedetect=noise={db}dB:d={d}', '-f', 'null', '-'], capture_output=True, text=True).stderr
            st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', o)]; en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', o)]
            cuts, t = [], 0.0
            for s, e in zip(st, en + [dur] * (len(st) - len(en))):
                if s > t + 0.15: cuts.append((t, s))
                t = e
            if dur > t + 0.15: cuts.append((t, dur))
            if len(cuts) == n: return cuts, dur
            if best is None or abs(len(cuts) - n) < abs(len(best) - n): best = cuts
    return best, dur
if __name__ == '__main__':
    vid, model, voice, outdir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    V = {v['id']: v for v in json.load(open(os.path.join(HERE, 'scripts.json')))}[vid] if vid != 'test' else {'id': 'test', 'lines': ["Kalau kamu pikir sepak bola itu ciptaan Inggris... plot twist, bukan.", "Cu artinya menendang, ju artinya bola. Literally, nendang bola."]}
    os.makedirs(outdir, exist_ok=True); wav = os.path.join(outdir, vid + '_full.wav')
    if not os.path.exists(wav) and not tts(model, voice, '\n\n'.join(V['lines']), wav): print('FAILED'); sys.exit(1)
    cuts, dur = segments(wav, len(V['lines'])); print(vid, 'dur', round(dur, 2), 'segments', len(cuts), '/', len(V['lines']))
    if len(cuts) != len(V['lines']): sys.exit(2)
    meta = []
    for i, (a, b) in enumerate(cuts):
        f = os.path.join(outdir, f'{vid}_{i}.wav')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max(0, a - 0.04):.3f}', '-to', f'{b + 0.08:.3f}', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.2,afade=t=in:d=0.01,afade=t=out:st=%.3f:d=0.05' % max(0, b - a + 0.07), '-ar', '48000', '-ac', '2', f], check=True)
        meta.append({'file': os.path.basename(f), 'dur': round(b - a + 0.12, 3), 'text': V['lines'][i]})
    json.dump(meta, open(os.path.join(outdir, vid + '.json'), 'w'), ensure_ascii=False, indent=1); print('ok', sum(m['dur'] for m in meta))
