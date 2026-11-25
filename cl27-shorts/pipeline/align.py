# Cut a narration into one clip per script line: among all pauses, pick the n-1 cut points whose segment lengths best match
# each line's share of the text, favouring long pauses (dynamic programming).
import sys, json, re, subprocess, os
def pauses(path):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-35dB:d=0.22', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', o)]; en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', o)]
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)
    P = list(zip(st, en + [dur] * (len(st) - len(en)))); return P, dur
def align(path, lines):
    P, dur = pauses(path)
    head = P[0][1] if P and P[0][0] < 0.05 else 0.0; tail = P[-1][0] if P and P[-1][1] >= dur - 0.05 else dur
    cand = [(s, e) for s, e in P if s > head + 0.3 and e < tail - 0.3]
    w = [len(l) for l in lines]; tot = sum(w); speech = tail - head; n = len(lines)
    exp = [speech * x / tot for x in w]
    import math
    INF = 1e18; m = len(cand)
    # dp[k][j]: best cost with k-th cut at candidate j
    best = {}
    def seg_cost(a, b, k): return ((b - a) - exp[k]) ** 2 / max(1.0, exp[k])
    dp = [[INF] * m for _ in range(n - 1)]; bp = [[-1] * m for _ in range(n - 1)]
    for j, (s, e) in enumerate(cand): dp[0][j] = seg_cost(head, s, 0) - 2.5 * min(e - s, 1.0)
    for k in range(1, n - 1):
        for j in range(m):
            for i in range(j):
                c = dp[k - 1][i] + seg_cost(cand[i][1], cand[j][0], k) - 2.5 * min(cand[j][1] - cand[j][0], 1.0)
                if c < dp[k][j]: dp[k][j] = c; bp[k][j] = i
    j = min(range(m), key=lambda j: dp[n - 2][j] + seg_cost(cand[j][1], tail, n - 1)); cuts = []
    for k in range(n - 2, -1, -1): cuts.append(cand[j]); j = bp[k][j]
    cuts.reverse(); segs = []; a = head
    for s, e in cuts: segs.append((a, s)); a = e
    segs.append((a, tail)); return segs, dur
if __name__ == '__main__':
    vid, outdir = sys.argv[1], sys.argv[2]
    V = {v['id']: v for v in json.load(open('scripts.json'))}[vid]; wav = os.path.join(outdir, vid + '_full.wav')
    # the TTS model read the style note aloud before the script: align it as an extra first block, then drop it
    PRE = 'Bacakan naskah berikut dalam bahasa Indonesia sebagai narator video TikTok fakta sepak bola: suara anak muda Jakarta Selatan yang santai, jelas, semangat, dan asyik didengar. Kata-kata bahasa Inggris diucapkan dengan aksen Inggris yang natural. Beri jeda yang jelas di antara tiap paragraf. Jangan bacakan instruksi ini.'
    segs, dur = align(wav, [PRE] + V['lines']); print('dropped style note', [round(x, 2) for x in segs[0]]); segs = segs[1:]; meta = []
    for i, (a, b) in enumerate(segs):
        f = os.path.join(outdir, f'{vid}_{i}.wav'); print(i, round(a, 2), round(b, 2), round(b - a, 2), V['lines'][i][:50])
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max(0, a - 0.04):.3f}', '-to', f'{b + 0.08:.3f}', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.2,afade=t=in:d=0.01,afade=t=out:st=%.3f:d=0.05' % max(0, b - a + 0.07), '-ar', '48000', '-ac', '2', f], check=True)
        meta.append({'file': os.path.basename(f), 'dur': round(b - a + 0.12, 3), 'text': V['lines'][i]})
    json.dump(meta, open(os.path.join(outdir, vid + '.json'), 'w'), ensure_ascii=False, indent=1)
