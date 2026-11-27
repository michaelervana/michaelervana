# Decode the Night Cup stadium (GSTD blob) and pitch assets into files Blender can use.
import re, base64, json, struct, numpy as np, sys
G = '/home/user/michaelervana/golazo-night-cup/'
s = open(G + 'stadium.js').read(); b = base64.b64decode(re.search(r'__STADIUM_B64="([^"]+)"', s).group(1))
assert b[:4] == b'GSTD'; hl = struct.unpack('<I', b[4:8])[0]; head = json.loads(b[8:8 + hl]); o = 8 + hl
qv = np.frombuffer(b, np.uint16, head['nv'] * 3, o).reshape(-1, 3).astype(np.float64); o += head['nv'] * 6; o += (4 - o % 4) % 4
idx = np.frombuffer(b, np.uint32, head['ni'], o); o += head['ni'] * 4
qc = np.frombuffer(b, np.uint16, head['nc'] * 3, o).reshape(-1, 3).astype(np.float64)
lo, sc = np.array(head['lo']), np.array(head['sc'])
P = lo + qv * sc; S = lo + qc * sc
# three.js (y up, -z forward) -> Blender (z up): (x, y, z) -> (x, -z, y)
toB = lambda a: np.stack([a[:, 0], -a[:, 2], a[:, 1]], 1).astype(np.float32)
np.savez_compressed('assets/stadium.npz', P=toB(P), I=idx.astype(np.int32), S=toB(S))
json.dump({k: v for k, v in head.items() if k not in ('lo', 'sc')}, open('assets/stadium_head.json', 'w'), indent=1)
print('verts', len(P), 'tris', len(idx) // 3, 'spots', len(S), 'groups', len(head['groups']))
print('bbox three', P.min(0).round(1), P.max(0).round(1)); print('spots bbox', S.min(0).round(1), S.max(0).round(1))
for g in head['groups'][:60]: print(' ', g['name'], [round(c, 3) for c in g['color']], g['opacity'], g['ni'] // 3)
p = open(G + 'pitch.js').read()
for name in re.findall(r'window\.(__[A-Z_]+)\s*=', p):
    m = re.search(name + r'\s*=\s*["\']([^"\']+)["\']', p)
    if not m: print(name, 'non-string'); continue
    v = m.group(1)
    if v.startswith('data:'):
        mime, data = v[5:].split(';base64,'); ext = mime.split('/')[1]; raw = base64.b64decode(data)
    else: raw = base64.b64decode(v); ext = 'glb' if raw[:4] == b'glTF' else 'bin'
    open(f'assets/{name.strip("_").lower()}.{ext}', 'wb').write(raw); print(name, ext, len(raw))
