# Render frames of one story: blender -b -y --python film.py -- <story> <a-b> <outdir> [scale] [samples]
import sys, os, time, json, importlib
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import blib as B, rt
argv = sys.argv[sys.argv.index('--') + 1:]
story, span, out = argv[0], argv[1], argv[2]; scale = int(argv[3]) if len(argv) > 3 else 75; samples = int(argv[4]) if len(argv) > 4 else 4
TIM = json.load(open(os.path.join(ROOT, 'timing.json')))[story]
mod = importlib.import_module('story_' + story)
sc = B.reset(scale=scale, samples=samples); W = rt.World(sc); W.coll = B.coll('main')
t0 = time.time(); mod.build(W); print('BUILD', round(time.time() - t0, 1), flush=True)
starts = rt.shot_starts(mod.SHOTS, TIM); DUR = TIM['dur'] + mod.TAIL; N = int(round(DUR * 30))
frames = []
for part in span.split(','):
    a, _, b = part.partition('-'); frames += list(range(int(a), (min(int(b), N - 1) if b else int(a)) + 1))
os.makedirs(out, exist_ok=True); tt = time.time()
for k, f in enumerate(frames):
    path = os.path.join(out, 'f%04d.jpg' % f)
    if os.environ.get('RESUME') and os.path.exists(path): continue
    t = f / 30.0; si = 0
    while si + 1 < len(starts) and t >= starts[si + 1]: si += 1
    shot = mod.SHOTS[si]; lt = t - starts[si]; ln = (starts[si + 1] if si + 1 < len(starts) else DUR) - starts[si]
    mod.apply(W, shot, lt, min(1.0, lt / ln), t, si)
    sc.frame_set(f); sc.render.filepath = path; B.bpy.ops.render.render(write_still=True)
    if k % 20 == 0: print('FRAME', story, f, '/', N, round((time.time() - tt) / (k + 1), 2), 's/frame', flush=True)
print('DONE', story, len(frames), flush=True)
