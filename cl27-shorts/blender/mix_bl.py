# Audio for the Blender shorts: voice (unedited) + synthesized music bed + whooshes on cuts + twist sting + rain + HUSS.
import sys, json, re, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, lfilter
SR = 48000; sid = sys.argv[1]
T = json.load(open('timing.json'))[sid]; src = open(f'story_{sid}.py').read()
TAIL = float(re.search(r'TAIL = ([0-9.]+)', src).group(1))
HUSS = {'parkirbus': [11.95, 17.85, 29.45, 40.62, 51.45], 'tikitaka': [11.45, 22.9, 30.75, 37.55, 53.7]}[sid]
def load(p):
    sr, x = wavfile.read(p); x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = resample_poly(x, SR, sr).astype(np.float32)
    return x
v = load(f'vo/{sid}.wav'); N = int((T['dur'] + TAIL) * SR); v = np.pad(v, (0, max(0, N - len(v))))[:N]; t = np.arange(N) / SR
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2) + 1e-9); vr = rms(v); rng = np.random.default_rng(1)
# shot starts (for whooshes) and rain shots, parsed from the story file
shots = re.findall(r"dict\(from_=(\d+)(?:, at=([0-9.]+))?(.*?)run=", src, re.S); starts = []
for i, (fr, at, rest) in enumerate(shots):
    L = T['lines'][int(fr)]; starts.append(0.0 if i == 0 else (float(at) if at else L['t0'] - 0.12))
ends = starts[1:] + [N / SR]; rainy = [(a, b) for (fr, at, rest), a, b in zip(shots, starts, ends) if "'rain'" in rest]
twist = T['lines'][7]['t0']
def pluck(f, d, a=1.0, bright=1.0, decay=8.0):
    n = int(d * SR); tt = np.arange(n) / SR; w = np.sin(2 * np.pi * f * tt) + 0.35 * bright * np.sin(4 * np.pi * f * tt) + 0.15 * bright * np.sin(6 * np.pi * f * tt)
    return (a * w * np.exp(-tt * decay)).astype(np.float32)
mus = np.zeros(N, np.float32)
def put(sig, at):
    i = int(at * SR); e = min(N, i + len(sig))
    if 0 <= i < N: mus[i:e] += sig[:e - i]
if sid == 'parkirbus':   # tarantella: 6/8, A minor, mandolin tremolo-ish plucks + oom-pah bass
    bpm = 132; step = 60 / bpm / 2; mel = [0, 3, 7, 3, 0, 3, 8, 7, 5, 3, 2, -1, 0, 3, 7, 12, 10, 8, 7, 5, 3, 2, 3, 0]; bass = [0, 0, 5, 5, -2, -2, -5, -5]
    k = 0; b = 0.0
    while b < N / SR - 0.3:
        quiet = twist - 0.2 < b < twist + 1.6
        f = 220.0 * 2 ** (mel[k % len(mel)] / 12)
        if not quiet:
            put(pluck(f, step * 0.95, 0.45, 1.2, 14), b); put(pluck(f * 2, step * 0.5, 0.12, 1.0, 22), b)
            if k % 3 == 0: put(pluck(55.0 * 2 ** (bass[(k // 3) % len(bass)] / 12), step * 2.6, 0.9, 0.6, 5), b)
            if k % 3 == 2: n = int(0.04 * SR); put((rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 90) * 0.12).astype(np.float32), b)
        b += step; k += 1
else:                    # flamenco-ish: fast staccato guitar in A Phrygian dominant, "tiki-taka" rhythm
    bpm = 150; step = 60 / bpm / 2; mel = [7, 8, 7, 5, 4, 5, 4, 1, 0, 1, 4, 5, 7, 5, 4, 1]; chords = [[0, 4, 7], [-2, 2, 5], [-4, 0, 3], [-5, -1, 2]]
    k = 0; b = 0.0
    while b < N / SR - 0.3:
        quiet = twist - 0.2 < b < twist + 1.6
        if not quiet:
            f = 220.0 * 2 ** (mel[k % len(mel)] / 12); put(pluck(f, step * 0.9, 0.42, 1.4, 18), b)
            if k % 4 == 0:
                for j, s_ in enumerate(chords[(k // 8) % 4]): put(pluck(110.0 * 2 ** (s_ / 12), step * 3, 0.32, 1.2, 6), b + j * 0.012)
            if k % 2 == 1: n = int(0.03 * SR); put((rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 120) * 0.1).astype(np.float32), b)
        b += step; k += 1
m = t >= twist + 1.6; mus[m] *= 1.0
m2 = (t > twist - 0.2) & (t < twist + 1.6); mus[m2] += (0.22 * np.sin(2 * np.pi * 73.4 * t[m2]) * np.minimum(1, (t[m2] - twist + 0.2) / 0.3)).astype(np.float32)
mus *= vr / rms(mus) * 0.5
sfx = np.zeros(N, np.float32)
def whoosh(at, d=0.45):
    n = int(d * SR); w = lfilter([0.15], [1, -0.85], rng.standard_normal(n)); env = np.sin(np.pi * np.arange(n) / n) ** 2; i = int(at * SR); e = min(N, i + n)
    if 0 <= i < N: sfx[i:e] += (w * env)[:e - i].astype(np.float32)
for s0 in starts[1:]: whoosh(max(0, s0 - 0.28))
i = int(twist * SR); n = int(0.7 * SR); tt = np.arange(n) / SR; st = sum(np.sin(2 * np.pi * f * tt) for f in (523, 659, 784, 1046)) * np.exp(-tt * 4.5); e = min(N, i + n); sfx[i:e] += st[:e - i].astype(np.float32)
sfx *= vr * 0.5 / max(rms(sfx), 1e-6)
h = load('huss.wav'); h *= vr * 0.6 / rms(h)
for at in HUSS:
    i = int(at * SR); e = min(N, i + len(h)); sfx[i:e] += h[:e - i]
rn = lfilter([0.3], [1, -0.6], rng.standard_normal(N)).astype(np.float32); env = np.zeros(N, np.float32)
for a, b in rainy:
    i, j = int(a * SR), min(N, int(b * SR)); w = np.ones(j - i, np.float32); r = min(int(0.25 * SR), (j - i) // 2); w[:r] = np.linspace(0, 1, r); w[-r:] = np.linspace(1, 0, r); env[i:j] = w
rn *= env; rn *= (vr * 0.2 / max(rms(rn), 1e-6)) if env.any() else 0
out = v + mus + sfx + rn; out /= max(1, np.abs(out).max() / 0.95)
wavfile.write(f'mix_{sid}.wav', SR, (out * 32767).astype(np.int16)); print(sid, round(N / SR, 2), 'shots', len(starts), 'rainy', len(rainy), 'huss', HUSS)
