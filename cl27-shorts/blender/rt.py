# Runtime for the Blender shorts: world/light presets, shot timing, camera keys, visibility, rain, crowd colours.
import math, os, json
import numpy as np
from mathutils import Vector
import blib as B, bchar as BC, bprops as BP
from blib import D, rad


def ss(x): x = max(0.0, min(1.0, x)); return x * x * x * (x * (x * 6 - 15) + 10)
def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u
def lerp3(a, b, u): return tuple(lerp(x, y, u) for x, y in zip(a, b))
def keyed(arr, t, d=None):
    r = d
    for k, v in arr or []:
        if t >= k: r = v
    return r


def C(t, pos, target, lens=30, roll=0.0): return dict(t=t, pos=pos, target=target, lens=lens, roll=roll)


def cam_at(keys, t, seed=0.0):
    i = 0
    while i < len(keys) - 1 and t > keys[i + 1]['t']: i += 1
    a = keys[i]; b = keys[min(i + 1, len(keys) - 1)]; u = 0 if a is b else ss((t - a['t']) / max(0.01, b['t'] - a['t']))
    pos = list(lerp3(a['pos'], b['pos'], u)); tgt = lerp3(a['target'], b['target'], u)
    pos[0] += math.sin(t * 0.7 + seed) * 0.03; pos[2] += math.sin(t * 0.9 + seed * 2) * 0.02
    return pos, tgt, lerp(a['lens'], b['lens'], u), lerp(a.get('roll', 0), b.get('roll', 0), u)


class World:
    def __init__(self, sc):
        self.sc = sc; self.cam = B.camera(sc, 30); self.beans = {}; self.props = {}; self.flags = []; self.focus = {}
        self.lights = {}; self.crowd = None; self.crowd_tree = None; self.conf = None; self.trails = []
        sc.eevee.bokeh_max_size = 40
        self.bg = sc.world.node_tree.nodes['Background']
        self._rain = None

    # ---- lights
    def add_sun(self, name, energy, color, rot, shadow=True):
        ld = D.lights.new(name, 'SUN'); ld.energy = energy; ld.color = color; ld.angle = rad(3); ld.use_shadow = shadow
        o = D.objects.new(name, ld); B.link(o); o.rotation_euler = rot; self.lights[name] = [o]; return o

    def preset(self, name):
        if getattr(self, '_preset', None) == name: return
        self._preset = name
        on = {'night': {'flood', 'moon'}, 'booth': {'flood', 'moon'}, 'day': {'sun'}, 'golden': {'golden'}, 'vintage': {'vintage'}}[name]
        for k, objs in self.lights.items():
            for o in objs: o.hide_render = o.hide_viewport = k not in on
        sky = {'night': (0.006, 0.010, 0.030), 'booth': (0.006, 0.010, 0.030), 'day': (0.42, 0.62, 0.95), 'golden': (0.95, 0.55, 0.32), 'vintage': (0.75, 0.66, 0.5)}[name]
        self.bg.inputs['Color'].default_value = sky + (1,)

    # ---- visibility
    def show(self, beans=(), props=()):
        for k, b in self.beans.items(): b.set_visible(k in beans)
        for k, p in self.props.items(): p.show(k in props)

    def bean(self, key, **kw):
        b = BC.Bean(key, self.coll, **kw); self.beans[key] = b; return b

    def prop(self, key, p): self.props[key] = p; p.show(False); return p

    # ---- crowd colours
    def crowd_colors(self, cols, jump=None):
        if self.crowd is None: return
        key = tuple(cols)
        if getattr(self, '_ccols', None) != key:
            self._ccols = key; me = self.crowd.data; n = len(me.vertices); rng = np.random.default_rng(7)
            arr = np.array([B._hex(cols[i % len(cols)]) for i in rng.integers(0, 10 ** 6, n)], np.float32); arr[:, :3] *= rng.uniform(0.78, 1.08, (n, 1)).astype(np.float32)
            me.attributes['col'].data.foreach_set('color', arr.ravel()); me.update()
        if jump is not None: self.crowd_tree.nodes['jump'].outputs[0].default_value = jump

    # ---- rain streaks attached to the camera
    def rain_rig(self):
        Hs, Ws = 512, 256; a = np.zeros((Hs, Ws, 4), np.float32); rng = np.random.default_rng(11)
        for _ in range(150):
            x = rng.integers(0, Ws); y = rng.integers(0, Hs); L = rng.integers(18, 50); al = rng.uniform(0.25, 0.7)
            for k in range(L): a[(y + k) % Hs, x, :] = (0.85, 0.9, 1.0, al * (1 - k / L) ** 0.5)
        img = D.images.new('rainimg', Ws, Hs, alpha=True); img.pixels.foreach_set(a[::-1].ravel()); img.pack()
        m = D.materials.new('rain'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.name = 'rainmap'; L.new(tc.outputs['UV'], mp.inputs[0])
        ti = N.new('ShaderNodeTexImage'); ti.image = img; L.new(mp.outputs[0], ti.inputs[0])
        em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0.42; L.new(ti.outputs['Color'], em.inputs['Color'])
        tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader'); L.new(ti.outputs['Alpha'], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
        o = N.new('ShaderNodeOutputMaterial'); L.new(mx.outputs[0], o.inputs[0]); m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
        self._rain = []
        for k, (d, sc_) in enumerate([(3.0, (1.6, 3.2)), (8.0, (4.4, 8.6))]):
            pl = B.mesh_obj('rain%d' % k, [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [(0, 1, 2, 3)], m)
            uv = pl.data.uv_layers.new(); [setattr(uv.data[i], 'uv', v) for i, v in enumerate([(0, 0), (1 * (k + 1), 0), (1 * (k + 1), 2 * (k + 1)), (0, 2 * (k + 1))])]
            pl.parent = self.cam; pl.location = (0, 0, -d); pl.scale = (sc_[0], sc_[1], 1); pl.visible_shadow = False; self._rain.append(pl)
        self.rain(False, 0)

    def rain(self, on, t):
        if not self._rain: return
        for p in self._rain: p.hide_render = p.hide_viewport = not on
        if on: D.materials['rain'].node_tree.nodes['rainmap'].inputs['Location'].default_value = (t * 0.07, t * 1.9, 0)

    # ---- camera
    def camera(self, keys, lt, seed, dof=None):
        pos, tgt, lens, roll = cam_at(keys, lt, seed); B.look_at(self.cam, pos, tgt, roll); self.cam.data.lens = lens
        d = self.cam.data.dof
        if dof:
            fp, fstop = dof; d.use_dof = True; d.focus_distance = (Vector(pos) - Vector(fp)).length; d.aperture_fstop = fstop
        else: d.use_dof = False
        return pos, tgt


def shot_starts(shots, tim):
    st = []
    for i, s in enumerate(shots):
        if i == 0: st.append(0.0); continue
        L = tim['lines'][s['from']]
        st.append(L['t0'] + (L['t1'] - L['t0']) * s['half'] if 'half' in s else (s['at'] if 'at' in s else L['t0'] - 0.12))
    return st


# ---------------- set builders ----------------
def build_stadium(W, crowd_cols):
    C = W.coll
    st, spots = B.stadium(C); W.focus['stadium'] = B.turf(C, puddles=0.6); B.goals(C); B.net(C, -1); B.net(C, 1)
    # keep the commentary booth area (main stand, centre) free of fans
    keep = ~((np.abs(spots[:, 0]) < 4.0) & (spots[:, 1] < -40) & (spots[:, 1] > -50) & (spots[:, 2] > 3) & (spots[:, 2] < 12))
    W.crowd, W.crowd_tree = B.crowd(C, spots[keep], crowd_cols, n=60000, card=os.path.join(B.ASSET, 'fan.png'))
    ls = B.night_lights(C); W.lights['flood'] = ls[:-1]; W.lights['moon'] = [ls[-1]]
    W.add_sun('sun', 3.0, (1.0, 0.97, 0.9), (rad(48), rad(10), rad(-30)))
    W.add_sun('golden', 2.6, (1.0, 0.72, 0.46), (rad(72), rad(0), rad(-55)))
    W.add_sun('vintage', 2.8, (1.0, 0.9, 0.72), (rad(50), rad(8), rad(-20)))
    lite_compositor(W.sc)
    W.conf = BP.Confetti(C)


def vintage(W, v): W.sc.node_tree.nodes['vintage'].inputs[0].default_value = v


def clouds(W, center, n=10, r=260, z=70, seed=1):
    rng = np.random.default_rng(seed); m = B.toon('cloud', '#ffffff', spec=0.0, shadow=(0.8, 0.82, 0.9))
    for i in range(n):
        a = rng.uniform(0, 6.28); x, y = center[0] + math.cos(a) * r * rng.uniform(0.6, 1), center[1] + math.sin(a) * r * rng.uniform(0.6, 1)
        for k in range(4): B.prim('ico', 'cloud', m, (x + k * 9 - 13, y, z + rng.uniform(-4, 6)), r=rng.uniform(8, 14), sub=2, ink=0.6, c=W.coll)


def build_alps(W, cx, cy):
    C = W.coll; W.focus['alps'] = B.turf(C, puddles=0, center=(cx, cy), half=(45, 45), base_half=(420, 420), tag='_alps')
    rock = B.toon('rock', '#7d8fae', spec=0.0); snow = B.toon('snow', '#f4f6fb', spec=0.0, shadow=(0.7, 0.75, 0.9))
    for i, (dx, dy, s) in enumerate([(-120, 150, 1.0), (-40, 190, 1.3), (60, 170, 1.15), (150, 160, 0.95), (-200, 120, 0.9), (230, 130, 1.0)]):
        B.prim('cone', 'mtn', rock, (cx + dx, cy + dy, 40 * s - 6), r=70 * s, h=90 * s, seg=7, smooth=False, ink=0.5, c=C)
        B.prim('cone', 'snow', snow, (cx + dx, cy + dy, 40 * s - 6 + 28 * s), r=30 * s, h=34 * s, seg=7, smooth=False, ink=0.3, c=C)
    pine = B.toon('pine', '#2f7a3e', spec=0.0); trunk = B.toon('bark', '#6a5038')
    rng = np.random.default_rng(4)
    for k in range(26):
        x = cx + rng.uniform(-45, 45); y = cy + rng.uniform(22, 60)
        B.prim('cyl', 'trunk', trunk, (x, y, 0.8), r=0.25, h=1.6, seg=8, ink=0.03, c=C); B.prim('cone', 'pine', pine, (x, y, 3.6), r=1.6, h=4.6, seg=9, smooth=False, ink=0.04, c=C)
    for k, (x, y, yaw) in enumerate([(-16, 26, 0.3), (14, 30, -0.4), (-30, 16, 0.8)]):
        P = BP.Prop('chalet%d' % k, C, (cx + x, cy + y, 0), (0, 0, yaw)); P.box('body', B.toon('chaletwood', '#8a5a34', stripes=('#6a4428', 2.0, 'Z')), (0, 0, 2.0), (7, 6, 4), ink=0.04)
        rv = [(-4, -3.8, 4), (4, -3.8, 4), (4, 0, 6.6), (-4, 0, 6.6), (-4, 3.8, 4), (4, 3.8, 4)]; r = B.mesh_obj('croof', rv, [(0, 1, 2, 3), (3, 2, 5, 4)], B.toon('chaletroof', '#5a3a2a'), C); r.parent = P.root
        sol = r.modifiers.new('t', 'SOLIDIFY'); sol.thickness = 0.3; B.outline(r, 0.04)
        for sx in (-1, 1): P.box('win', B.toon('dglass', '#2a3448', spec=0.6), (sx * 1.8, -3.02, 2.4), (1.0, 0.08, 1.0), ink=0.015)
    clouds(W, (cx, cy), seed=2)


def build_dutch(W, cx, cy):
    C = W.coll; W.focus['dutch'] = B.turf(C, puddles=0, center=(cx, cy), half=(45, 45), base_half=(420, 420), tag='_nl')
    for k, (dx, dy, s, yaw) in enumerate([(-26, 40, 1.3, 0.2), (22, 52, 1.5, -0.3), (60, 80, 1.6, 0.1), (-70, 70, 1.4, 0.5)]):
        W.props['mill%d' % k] = BP.windmill(C, 'mill%d' % k, (cx + dx, cy + dy, 0), yaw, s)
    for k in range(7):
        BP.dutch_house(C, 'nlh%d' % k, (cx - 60 + k * 5.0, cy + 24, 0), w=4.6, h=8 + (k % 3) * 1.2, col=['#8a3a2a', '#5a4a3a', '#7a4a32', '#4a5a5a', '#9a5a3a', '#6a3a2a', '#e0d0b0'][k])
    # tulip rows (instanced like the crowd): stem + flower head with a colour attribute
    pts = [(cx + x, cy + y, 0) for y in np.arange(-13, -4, 0.9) for x in np.arange(-26, 26, 0.45)]
    me = D.meshes.new('tulippts'); me.vertices.add(len(pts)); me.vertices.foreach_set('co', np.array(pts, np.float32).ravel())
    rng = np.random.default_rng(9); pal = ['#e8283a', '#ffd23d', '#ff6aa8', '#ff8a2a', '#f4f4f4']
    rows = ((np.array(pts)[:, 1] - cy + 13) / 0.9).astype(int); cols = np.array([B._hex(pal[r % len(pal)]) for r in rows], np.float32)
    me.attributes.new('col', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', cols.ravel()); me.attributes.new('rz', 'FLOAT', 'POINT').data.foreach_set('value', rng.uniform(0, 6.28, len(pts)).astype(np.float32))
    me.attributes.new('ph', 'FLOAT', 'POINT').data.foreach_set('value', rng.uniform(0, 6.28, len(pts)).astype(np.float32))
    host = D.objects.new('tulips', me); B.link(host, C)
    head = B.prim('sphere', 'tulip', B.toon('tulipcol', '#ffffff', attr='col', spec=0.2), (0, 0, 0.42), size=(0.09, 0.09, 0.12), seg=10, ink=0.012, c=C)
    stem = B.prim('cyl', 'stem', B.toon('stem', '#3f8a3a'), (0, 0, 0.0), r=0.018, h=0.4, seg=6, ink=0, c=C, parent=head); stem.location = (0, 0, -0.21)
    t = D.node_groups.new('tulipGN', 'GeometryNodeTree'); t.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); t.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = t.nodes, t.links; gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput'); col = N.new('GeometryNodeCollectionInfo')
    tc = D.collections.new('tulipinst'); tc.objects.link(head); tc.objects.link(stem); col.inputs['Collection'].default_value = tc; col.inputs['Separate Children'].default_value = False
    iop = N.new('GeometryNodeInstanceOnPoints'); L.new(gi.outputs[0], iop.inputs['Points']); L.new(col.outputs[0], iop.inputs['Instance']); L.new(iop.outputs[0], go.inputs[0])
    host.modifiers.new('gn', 'NODES').node_group = t; host.visible_shadow = False
    for o in (head, stem):
        for cc in list(o.users_collection):
            if cc != tc: cc.objects.unlink(o)
    # canal in front of the houses (mirror water)
    wm = BP.glassmat('canal', '#3a5a7a', 0.0); B.mesh_obj('canal', [(cx - 80, cy + 17, 0.05), (cx + 80, cy + 17, 0.05), (cx + 80, cy + 20.5, 0.05), (cx - 80, cy + 20.5, 0.05)], [(0, 1, 2, 3)], B.toon('canalw', '#3a6a9a', wet=0.9, spec=0.0), C)
    clouds(W, (cx, cy), seed=3)


def build_masia(W, cx, cy):
    C = W.coll; W.focus['masia'] = B.turf(C, puddles=0, center=(cx, cy), half=(45, 45), base_half=(420, 420), tag='_masia')
    BP.masia(C, 'masia', (cx, cy + 18, 0), 0.0)
    for k, (x, y, s) in enumerate([(-12, 12, 1.2), (12, 14, 1.0), (-18, 4, 0.9), (17, 3, 1.1), (-6, 30, 1.3), (9, 32, 1.0)]): BP.olive_tree(C, 'olive%d' % k, (cx + x, cy + y, 0), s)
    BP.mini_goal(C, 'mg1', (cx, cy - 9, 0), 0.0); BP.mini_goal(C, 'mg2', (cx, cy + 9, 0), math.pi)
    hills = B.toon('hill', '#8aa85a', spec=0.0)
    for k in range(10):
        a = k / 10 * 6.28; B.prim('sphere', 'hill', hills, (cx + math.cos(a) * 240, cy + math.sin(a) * 240, -30), r=70 + (k % 3) * 20, seg=16, ink=0.5, c=C)
    clouds(W, (cx, cy), seed=4)


def flash(W, v): W.sc.node_tree.nodes['flash'].inputs[0].default_value = v


# ---------------- the Night Cup game's boards, ribbons, screens and banners (exported from the running game) ----------------
GX = os.path.join(B.ROOT, 'gx', 'export')


def _img(path):
    im = D.images.load(path, check_existing=True); return im


def _board_mat(name, info, texdir):
    """MeshBasic -> flat emissive picture (LEDs, screens); MeshStandard -> cel material; additive -> glow over transparent"""
    if name in B._mat: return B._mat[name]
    m = D.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial'); col = info.get('color', [1, 1, 1]); k = max(col) if col else 1.0
    if info.get('map'):
        ti = N.new('ShaderNodeTexImage'); ti.name = 'img'; ti.image = _img(os.path.join(texdir, info['map'] + '.png'))
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (info.get('offset', [0, 0])[0], info.get('offset', [0, 0])[1], 0)
        mp.inputs['Scale'].default_value = (info.get('repeat', [1, 1])[0], info.get('repeat', [1, 1])[1], 1); L.new(tc.outputs['UV'], mp.inputs[0]); L.new(mp.outputs[0], ti.inputs[0])
        csrc = ti.outputs['Color']; asrc = ti.outputs['Alpha']
    else:
        rgb = N.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (col[0] / k if k > 1 else col[0], col[1] / k if k > 1 else col[1], col[2] / k if k > 1 else col[2], 1); csrc = rgb.outputs[0]; asrc = None
    tint = N.new('ShaderNodeMixRGB'); tint.blend_type = 'MULTIPLY'; tint.inputs[0].default_value = 1; L.new(csrc, tint.inputs[1])
    tint.inputs[2].default_value = (min(1, col[0] / k), min(1, col[1] / k), min(1, col[2] / k), 1) if info.get('map') else (1, 1, 1, 1)
    if info['type'] == 'MeshStandardMaterial' and not info.get('additive'):
        diff = N.new('ShaderNodeBsdfDiffuse'); s2 = N.new('ShaderNodeShaderToRGB'); L.new(diff.outputs[0], s2.inputs[0]); bw = N.new('ShaderNodeRGBToBW'); L.new(s2.outputs['Color'], bw.inputs[0])
        rp = N.new('ShaderNodeValToRGB'); cr = rp.color_ramp; cr.interpolation = 'CONSTANT'; cr.elements[0].color = (0.45, 0.43, 0.58, 1); cr.elements[1].position = 0.12; cr.elements[1].color = (1, 1, 1, 1); L.new(bw.outputs[0], rp.inputs[0])
        mu = N.new('ShaderNodeMixRGB'); mu.blend_type = 'MULTIPLY'; mu.inputs[0].default_value = 1; L.new(tint.outputs[0], mu.inputs[1]); L.new(rp.outputs[0], mu.inputs[2])
        em = N.new('ShaderNodeEmission'); L.new(mu.outputs[0], em.inputs['Color'])
    else:
        em = N.new('ShaderNodeEmission'); em.name = 'em'; L.new(tint.outputs[0], em.inputs['Color']); em.inputs['Strength'].default_value = (k if k > 1 else 1.0) * info.get('gain', 1.0)
    sh = em.outputs[0]
    if info.get('additive'):
        tr = N.new('ShaderNodeBsdfTransparent'); ad = N.new('ShaderNodeAddShader'); L.new(tr.outputs[0], ad.inputs[0])
        if asrc is not None:
            mx = N.new('ShaderNodeMixShader'); tr2 = N.new('ShaderNodeBsdfTransparent'); tr2.inputs[0].default_value = (0, 0, 0, 1); L.new(asrc, mx.inputs[0]); L.new(tr2.outputs[0], mx.inputs[1]); L.new(sh, mx.inputs[2]); sh = mx.outputs[0]
        L.new(sh, ad.inputs[1]); sh = ad.outputs[0]; m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
    elif info.get('transparent') and asrc is not None:
        tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader'); L.new(asrc, mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(sh, mx.inputs[2]); sh = mx.outputs[0]
        m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
    m.use_backface_culling = info.get('side', 0) == 0 and not info.get('additive'); L.new(sh, out.inputs['Surface'])
    B._mat[name] = m; return m


def build_gameboards(W, pair, screen='score'):
    d = os.path.join(GX, pair)
    if not os.path.exists(os.path.join(d, 'meshes.json')): print('NO GAMEBOARDS', d); W.boards = None; return
    meshes = json.load(open(os.path.join(d, 'meshes.json'))); mats = json.load(open(os.path.join(d, 'materials.json'))); texdir = os.path.join(d, 'tex')
    c = W.coll; W.boards = {'led': [], 'dir': d}
    for k, me_ in enumerate(meshes):
        P = np.array(me_['pos'], np.float32).reshape(-1, 3); I = np.array(me_['idx'], np.int32); nt = len(I) // 3
        if nt == 0: continue
        me = D.meshes.new('gb%d' % k); me.vertices.add(len(P)); me.vertices.foreach_set('co', P.ravel())
        me.loops.add(len(I)); me.loops.foreach_set('vertex_index', I); me.polygons.add(nt)
        me.polygons.foreach_set('loop_start', np.arange(0, len(I), 3, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(nt, 3, np.int32))
        if me_.get('uv'):
            UV = np.array(me_['uv'], np.float32).reshape(-1, 2); uvl = me.uv_layers.new(); uvl.data.foreach_set('uv', UV[I].ravel())
        mi = np.zeros(nt, np.int32)
        for gi, (st, cnt, mat) in enumerate(me_['groups']): mi[st // 3:(st + cnt) // 3] = gi
        for gi, (st, cnt, mat) in enumerate(me_['groups']):
            info = mats[str(mat)]; me.materials.append(_board_mat('gbm_%s_%s' % (pair, mat), info, texdir))
            if info.get('role') == 'led': W.boards['led'].append(me.materials[-1])
            if info.get('role') == 'ledEnd': W.boards.setdefault('end', []).append(me.materials[-1])
            if info.get('role') == 'screen' and screen != 'score': me.materials[-1].node_tree.nodes['img'].image = _img(os.path.join(texdir, screen + '.png'))
        me.polygons.foreach_set('material_index', mi); me.update(calc_edges=True)
        ob = D.objects.new('gb_' + me_.get('name', str(k)), me); B.link(ob, c); ob.visible_shadow = False
    W.boards['pages'] = sorted(f for f in os.listdir(texdir) if f.startswith('ledpage'))
    print('GAMEBOARDS', len(meshes), 'meshes,', len(W.boards['led']), 'LED materials')


def gameboards_page(W, idx):
    b = getattr(W, 'boards', None)
    if not b or not b['led'] or not b['pages']: return
    name = b['pages'][idx % len(b['pages'])]
    if b.get('cur') == name: return
    b['cur'] = name; img = _img(os.path.join(b['dir'], 'tex', name)); img2 = _img(os.path.join(b['dir'], 'tex', b['pages'][(idx + 2) % len(b['pages'])]))
    for m in b['led']: m.node_tree.nodes['img'].image = img
    for m in b.get('end', []): m.node_tree.nodes['img'].image = img2


def lite_compositor(sc):
    """cheap in-Blender grade only (glare, flares and vignette are done in post.py with OpenCV)"""
    sc.use_nodes = True; nt = sc.node_tree; N, L = nt.nodes, nt.links; N.clear()
    rl = N.new('CompositorNodeRLayers'); comp = N.new('CompositorNodeComposite')
    cb = N.new('CompositorNodeColorBalance'); cb.correction_method = 'LIFT_GAMMA_GAIN'; cb.lift = (1.0, 0.99, 1.03); cb.gain = (1.04, 1.02, 0.98)
    hs = N.new('CompositorNodeHueSat'); hs.inputs['Saturation'].default_value = 1.12
    L.new(rl.outputs['Image'], cb.inputs['Image']); L.new(cb.outputs['Image'], hs.inputs['Image'])
    sep = N.new('CompositorNodeHueSat'); sep.inputs['Saturation'].default_value = 0.35; L.new(hs.outputs['Image'], sep.inputs['Image'])
    c2 = N.new('CompositorNodeColorBalance'); c2.correction_method = 'LIFT_GAMMA_GAIN'; c2.gain = (1.12, 1.0, 0.8); c2.lift = (1.04, 1.0, 0.94); L.new(sep.outputs['Image'], c2.inputs['Image'])
    mx = N.new('CompositorNodeMixRGB'); mx.name = 'vintage'; mx.inputs[0].default_value = 0.0; L.new(hs.outputs['Image'], mx.inputs[1]); L.new(c2.outputs['Image'], mx.inputs[2])
    fl = N.new('CompositorNodeMixRGB'); fl.name = 'flash'; fl.inputs[0].default_value = 0.0; fl.inputs[2].default_value = (1, 1, 1, 1)
    L.new(mx.outputs['Image'], fl.inputs[1]); L.new(fl.outputs['Image'], comp.inputs['Image'])
