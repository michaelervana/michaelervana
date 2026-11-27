# Per-line timing: Gemini audio model estimates when each script line starts; each estimate is then snapped to the
# middle of the nearest detected pause (if one is close), so cuts land in silence. The voice itself is never edited.
import sys, json, re, subprocess, base64, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vid'))
from gem import text
def pauses(path):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-38dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', o)]; en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', o)]
    return list(zip(st, en))
def dur(path): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)
out = json.load(open('timing.json')) if os.path.exists('timing.json') else {}
for v in json.load(open('scripts.json')):
    if len(sys.argv) > 1 and v['id'] not in sys.argv[1:]: continue
    path = f"vo/{v['id']}.wav"; D = dur(path)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-b:a', '48k', '/tmp/_t.mp3'])
    lines = '\n'.join(f'{i + 1}. {l}' for i, l in enumerate(v['lines']))
    prompt = (f"This audio is an Indonesian narration of the {len(v['lines'])} numbered lines below, read in order. Some lines contain two sentences; "
              f"treat each numbered line as one unit. For each numbered line give the time in seconds (3 decimals) when the FIRST word of that line starts. "
              f"Answer only JSON: a list of exactly {len(v['lines'])} objects like {{\"line\": 1, \"first_words\": \"...\", \"start\": 0.0}}.\n\n" + lines)
    raw = text(os.environ.get('M', 'gemini-flash-latest'), [{"text": prompt}, {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(open('/tmp/_t.mp3', 'rb').read()).decode()}}])
    print('RAW', raw[:600]); est = [float(o['start']) for o in json.loads(raw[raw.find('['):raw.rfind(']') + 1])]
    assert len(est) == len(v['lines']), raw
    P = pauses(path); starts = [0.0]
    import numpy as np
    pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768; hop = 160; env = np.sqrt(np.convolve(x * x, np.ones(1920) / 1920, 'same'))[::hop]  # 10 ms steps, 120 ms window
    for e in est[1:]:
        a, b = int(max(0, e - 0.8) * 100), int(min(D, e + 0.5) * 100); k = a + int(np.argmin(env[a:b])); q = k / 100
        # move to the end of that quiet dip (the onset of the next word)
        while k + 1 < len(env) and env[k + 1] < env[k] * 1.8 + 0.004 and (k + 1) / 100 < e + 0.6: k += 1
        starts.append(round(k / 100 - 0.04, 3))
    ends = []
    for i, s in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else D
        ends.append(round(max([p[0] for p in P if s < p[0] <= nxt + 0.01] or [nxt]), 3))
    out[v['id']] = {'dur': round(D, 3), 'lines': [{'t0': a, 't1': b, 'text': t} for a, b, t in zip(starts, ends, v['lines'])]}
    print(v['id'], round(D, 2), 'gemini', [round(x, 2) for x in est]); print('   snapped', starts)
json.dump(out, open('timing.json', 'w'), ensure_ascii=False, indent=1)
