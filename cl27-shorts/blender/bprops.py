# Props and set pieces for the 3D cartoon shorts (cel shading + ink outlines), all built from primitives in Blender.
import math, os
import numpy as np
from mathutils import Vector, Euler, Matrix
import blib as B
from blib import prim, empty, toon, glow, rad, D, outline, mesh_obj, text3d, _hex

FONT = os.path.join(B.ASSET, 'bc900.ttf')


class Prop:
    def __init__(self, name, c, loc=(0, 0, 0), rot=(0, 0, 0)):
        self.c = c; self.root = empty(name, loc, c=c, rot=rot); self.objs = []; self.vis = True; self.parts = {}
    def add(self, ob, key=None):
        if ob.parent is None: ob.parent = self.root
        self.objs.append(ob)
        if key: self.parts[key] = ob
        return ob
    def show(self, v):
        if v == self.vis: return
        self.vis = v
        for o in self.objs: o.hide_render = o.hide_viewport = not v
    def box(self, name, mat, loc, size, bevel=0.0, ink=0.02, rot=(0, 0, 0), parent=None, key=None):
        ob = prim('box', name, mat, loc, rot, size=size, ink=0, c=self.c, parent=parent or self.root, smooth=False)
        if bevel:
            bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 3; bv.limit_method = 'ANGLE'
            for p in ob.data.polygons: p.use_smooth = True
            ob.data.use_auto_smooth = True; ob.data.auto_smooth_angle = rad(35)
        if ink: outline(ob, ink)
        return self.add(ob, key)
    def p(self, kind, name, mat, loc=(0, 0, 0), rot=(0, 0, 0), ink=0.02, parent=None, key=None, **kw):
        return self.add(prim(kind, name, mat, loc, rot, ink=ink, c=self.c, parent=parent or self.root, **kw), key)
    def text(self, name, body, mat, loc, rot=(rad(90), 0, 0), size=1.0, extrude=0.06, ink=0.03, parent=None, key=None):
        t = text3d(name, body, mat, size=size, extrude=extrude, bevel=0.01, c=self.c, font=FONT, ink=ink)
        t.location = loc; t.rotation_euler = rot; t.parent = parent or self.root
        return self.add(t, key)


def glassmat(name, col='#a8c8f0', alpha=0.16):
    if name in B._mat: return B._mat[name]
    m = D.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    gl = N.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.05; gl.inputs['Color'].default_value = _hex(col)
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader'); mx.inputs[0].default_value = alpha
    L.new(tr.outputs[0], mx.inputs[1]); L.new(gl.outputs[0], mx.inputs[2]); o = N.new('ShaderNodeOutputMaterial'); L.new(mx.outputs[0], o.inputs[0])
    m.blend_method = 'BLEND'; m.shadow_method = 'NONE'; m.use_backface_culling = False; m.show_transparent_back = False; B._mat[name] = m; return m


# ---------------- textures painted with numpy (no external files needed at render time) ----------------
def np_image(name, arr):
    h, w = arr.shape[:2]; img = D.images.new(name, w, h, alpha=True); px = np.ones((h, w, 4), np.float32)
    px[..., :arr.shape[2]] = arr; img.pixels.foreach_set(px[::-1].ravel()); img.pack(); return img


def tex_mat(name, img, spec=0.1, emit=0.0):
    """toon material whose base colour is an image (UV mapped)"""
    if name in B._mat: return B._mat[name]
    m = toon(name, '#ffffff', spec=spec, emit=emit); N = m.node_tree.nodes; L = m.node_tree.links
    rgb = [n for n in N if n.type == 'RGB'][0]; ti = N.new('ShaderNodeTexImage'); ti.image = img
    for l in list(rgb.outputs[0].links): L.new(ti.outputs['Color'], l.to_socket)
    return m


def uv_quad(ob):
    uv = ob.data.uv_layers.new()
    for i, v in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = v


# ---------------- the bus ----------------
def bus(c, name, paint='#d81e2a', stripe='#f4f1e8', sign='PARKIR BUS', loc=(0, 0, 0), yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); pm = toon('bus_' + name, paint, spec=0.35); sm = toon('busband_' + name, stripe, spec=0.2)
    dark = toon('busdark', '#1e2433', spec=0.6); tyre = toon('tyre', '#16161a', spec=0.2); hub = toon('hub', '#b8bcc8', spec=0.7)
    P.box('lower', pm, (-0.9, 0, 1.35), (8.6, 2.5, 2.1), bevel=0.16)
    for sy in (-1, 1): P.box('cabwall', pm, (4.3, sy * 1.22, 1.35), (1.8, 0.06, 2.1), bevel=0.02, ink=0.015)
    P.box('cabfloor', dark, (4.3, 0, 0.42), (1.8, 2.44, 0.14), ink=0)
    P.box('dash', pm, (5.02, 0, 0.75), (0.36, 2.44, 0.8), bevel=0.06)
    P.box('upper', pm, (0, 0, 3.38), (10.3, 2.46, 1.96), bevel=0.24)
    P.box('band', sm, (0, 0, 2.42), (10.46, 2.54, 0.22), bevel=0.05)
    for z, h, x, L in [(1.95, 0.95, -0.9, 8.0), (3.45, 0.95, 0, 9.3)]: P.box('win', dark, (x, 0, z), (L, 2.53, h), bevel=0.06, ink=0.012)
    P.box('upfront', dark, (5.12, 0, 3.45), (0.07, 2.1, 0.92), bevel=0.03, ink=0.012)
    P.add(prim('box', 'windshield', glassmat('busglass'), (5.2, 0, 1.85), size=(0.05, 2.36, 1.0), ink=0, c=c, parent=P.root, smooth=False))
    P.box('sign', toon('signbg', '#141418'), (5.15, 0, 4.12), (0.06, 1.9, 0.38), ink=0.012)
    P.text('signtxt', sign, glow('signled', '#ffb020', 3.0), (5.2, 0, 4.12), rot=(rad(90), 0, rad(90)), size=0.3, extrude=0.01, ink=0)
    for x in (-3.3, 3.4):
        for sy in (-1, 1):
            P.p('cyl', 'tyre', tyre, (x, sy * 1.12, 0.56), (rad(90), 0, 0), r=0.56, h=0.36, seg=20, ink=0.02)
            P.p('cyl', 'hub', hub, (x, sy * 1.31, 0.56), (rad(90), 0, 0), r=0.3, h=0.04, seg=16, ink=0.01)
    for sy in (-1, 1):
        P.p('sphere', 'headl', glow('headlight', '#fff6d8', 1.25), (5.2, sy * 0.85, 0.78), size=(0.06, 0.2, 0.14), seg=12, ink=0.01, key='hl%d' % sy)
        P.p('sphere', 'taill', glow('taillight', '#ff2a2a', 4.0), (-5.22, sy * 0.95, 0.85), size=(0.05, 0.14, 0.12), seg=10, ink=0.01)
    P.box('grille', dark, (5.21, 0, 0.42), (0.05, 1.3, 0.3), ink=0.01)
    P.box('seat', toon('seat', '#3a2a22'), (3.85, -0.55, 0.85), (0.55, 0.6, 0.12), ink=0.01)
    P.box('seatback', toon('seat', '#3a2a22'), (3.55, -0.55, 1.25), (0.12, 0.6, 0.8), ink=0.01)
    P.p('torus', 'wheel', toon('steer', '#1a1a20', spec=0.5), (4.62, -0.55, 1.42), (0, rad(-62), 0), R=0.24, r=0.03, seg=20, ink=0.008, key='steer')
    P.box('door', dark, (3.6, 1.26, 1.25), (0.9, 0.04, 1.7), ink=0.01)
    return P


def padlock(c, name='padlock', loc=(0, 0, 0)):
    P = Prop(name, c, loc); gold = toon('lockgold', '#f2c230', spec=0.8); silver = toon('locksilver', '#c9d0dc', spec=0.9)
    P.box('lockbody', gold, (0, 0, 0.62), (1.6, 0.7, 1.25), bevel=0.22, ink=0.035)
    P.p('torus', 'shackle', silver, (0, 0, 1.25), (rad(90), 0, 0), R=0.52, r=0.13, a0=0, a1=math.pi, seg=20, ink=0.03)
    for sx in (-1, 1): P.p('cyl', 'leg', silver, (sx * 0.52, 0, 1.2), r=0.13, h=0.2, seg=12, ink=0)
    P.p('cyl', 'keyhole', toon('keyhole', '#1a1414'), (0, -0.36, 0.72), (rad(90), 0, 0), r=0.12, h=0.04, seg=14, ink=0)
    P.box('keyslot', toon('keyhole', '#1a1414'), (0, -0.37, 0.52), (0.08, 0.03, 0.28), ink=0)
    return P


def bolt_door(c, name='door', loc=(0, 0, 0), yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); wood = toon('doorwood', '#9a6a3c', stripes=('#7d522c', 1.6, 'X'), spec=0.1)
    iron = toon('iron', '#3a3d46', spec=0.7)
    P.box('door', wood, (0, 0, 1.24), (7.3, 0.22, 2.44), bevel=0.05, ink=0.03)
    for z in (0.5, 1.95): P.box('strap', iron, (0, -0.13, z), (7.2, 0.04, 0.16), ink=0.015)
    for x in (-0.4, 0.35, 1.1): P.box('bracket', iron, (x, -0.2, 1.25), (0.16, 0.14, 0.3), bevel=0.02, ink=0.015)
    bolt = empty(name + '_bolt', (0, 0, 0), P.root, c); P.objs.append(bolt); P.parts['bolt'] = bolt
    P.p('cyl', 'boltbar', iron, (0.3, -0.24, 1.25), (0, rad(90), 0), r=0.075, h=1.8, seg=14, ink=0.015, parent=bolt)
    P.p('cyl', 'knob', iron, (0.2, -0.36, 1.25), (rad(90), 0, 0), r=0.05, h=0.2, seg=10, ink=0.01, parent=bolt)
    return P


def broom(c, name='broom'):
    P = Prop(name, c); stick = toon('broomstick', '#a8743c', spec=0.2); straw = toon('straw', '#e8c25a', spec=0.1)
    P.p('cyl', 'stick', stick, (0, 0, 0.1), r=0.032, h=1.5, seg=10, ink=0.012)
    P.p('cone', 'bristle', straw, (0, 0, -0.78), r=0.3, r2=0.08, h=0.45, seg=14, ink=0.02)
    P.p('cyl', 'band', toon('bandred', '#c8302e'), (0, 0, -0.55), r=0.09, h=0.08, seg=12, ink=0.01)
    return P


TROPHIES = {
    'bigears': ([(0.0, 0), (0.24, 0), (0.24, 0.1), (0.13, 0.16), (0.07, 0.3), (0.07, 0.5), (0.15, 0.62), (0.3, 0.85), (0.36, 1.05), (0.34, 1.08)], 'silver', True),
    'cup': ([(0.0, 0), (0.2, 0), (0.2, 0.12), (0.09, 0.2), (0.06, 0.4), (0.18, 0.55), (0.25, 0.8), (0.24, 0.84)], 'gold', False),
    'tall': ([(0.0, 0), (0.18, 0), (0.18, 0.15), (0.07, 0.25), (0.07, 0.7), (0.16, 0.85), (0.2, 1.15), (0.19, 1.18)], 'silver', False),
    'globe': ([(0.0, 0), (0.2, 0), (0.2, 0.15), (0.08, 0.25), (0.12, 0.45), (0.22, 0.65), (0.2, 0.85), (0.08, 0.95), (0.0, 0.98)], 'gold', False),
    'plate': ([(0.0, 0), (0.16, 0), (0.16, 0.1), (0.05, 0.2), (0.05, 0.45)], 'silver', False),
    'shield': ([(0.0, 0), (0.22, 0), (0.22, 0.18), (0.1, 0.28), (0.1, 0.36)], 'gold', False),
}


def trophy(c, name, kind='bigears', loc=(0, 0, 0)):
    prof, metal, ears = TROPHIES[kind]; P = Prop(name, c, loc)
    m = toon('t' + metal, '#e4e8f0' if metal == 'silver' else '#f2c230', spec=0.9)
    P.p('lathe', 'body', m, (0, 0, 0), prof=prof, seg=24, ink=0.02)
    P.p('cyl', 'base', toon('tbase', '#4a3426'), (0, 0, -0.08), r=prof[1][0] * 1.15, h=0.16, seg=20, ink=0.02)
    if ears:
        for sx in (-1, 1): P.p('torus', 'ear', m, (sx * 0.42, 0, 0.72), (rad(90), 0, 0), R=0.2, r=0.035, seg=18, ink=0.012)
    elif kind in ('cup', 'tall'):
        for sx in (-1, 1): P.p('torus', 'ear', m, (sx * 0.24, 0, 0.66 if kind == 'cup' else 0.95), (rad(90), 0, 0), R=0.08, r=0.025, seg=12, ink=0.01)
    if kind == 'plate': P.p('cyl', 'disc', m, (0, 0, 0.75), (rad(90), 0, 0), r=0.32, h=0.05, seg=28, ink=0.015)
    if kind == 'shield': P.p('sphere', 'shield', m, (0, 0, 0.75), size=(0.3, 0.06, 0.38), seg=20, ink=0.015)
    return P


def parking_sign(c, name='psign', loc=(0, 0, 0), yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); blue = toon('pblue', '#1f5fd8', spec=0.4); white = toon('pwhite', '#ffffff', spec=0.2, emit=0.2)
    P.p('cyl', 'pole', toon('pole', '#a8aeb8', spec=0.6), (0, 0.05, 1.5), r=0.06, h=3.0, seg=10, ink=0.015)
    P.box('panel', blue, (0, 0, 3.25), (1.5, 0.08, 1.5), bevel=0.12, ink=0.03)
    P.box('rim', white, (0, 0.01, 3.25), (1.36, 0.085, 1.36), bevel=0.1, ink=0)
    P.box('inner', blue, (0, 0, 3.25), (1.24, 0.1, 1.24), bevel=0.08, ink=0)
    P.text('P', 'P', white, (0, -0.07, 3.22), size=1.15, extrude=0.03, ink=0.02)
    return P


def big_screen(c, name, text, loc, yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); P.box('frame', toon('screenframe', '#16181f', spec=0.4), (0, 0.15, 0), (12.5, 0.3, 6.6), bevel=0.1, ink=0.04)
    P.box('screen', glow('screenbg', '#0b1a46', 1.2), (0, 0, 0), (11.8, 0.05, 6.0), ink=0)
    P.text('score', text, glow('scoretxt', '#ffffff', 5.0), (0, -0.06, -0.2), size=3.6, extrude=0.02, ink=0, key='txt')
    return P


def chalkboard(c, name='board', loc=(0, 0, 0), yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); wood = toon('easelwood', '#8a5a34')
    for sx in (-1, 1): P.p('cyl', 'leg', wood, (sx * 0.75, 0.0, 1.1), (rad(-8), rad(sx * 10), 0), r=0.04, h=2.3, seg=8, ink=0.012)
    P.p('cyl', 'back', wood, (0, 0.45, 1.0), (rad(25), 0, 0), r=0.035, h=2.2, seg=8, ink=0.012)
    W2, H2 = 512, 340; a = np.zeros((H2, W2, 3), np.float32); a[:] = (0.07, 0.2, 0.13)
    yy, xx = np.mgrid[0:H2, 0:W2]
    def ring(cx, cy, r): return np.abs(np.hypot(xx - cx, yy - cy) - r) < 4
    def cross(cx, cy, r): return ((np.abs((xx - cx) - (yy - cy)) < 5) | (np.abs((xx - cx) + (yy - cy)) < 5)) & (np.abs(xx - cx) < r) & (np.abs(yy - cy) < r)
    chalk = np.zeros((H2, W2), bool)
    for cx, cy in [(120, 230), (200, 240), (280, 240), (360, 230), (240, 300)]: chalk |= ring(cx, cy, 18)
    for cx, cy in [(150, 110), (250, 90), (350, 110)]: chalk |= cross(cx, cy, 18)
    chalk |= (np.abs(yy - 170) < 3) & (xx > 90) & (xx < 420)
    chalk |= (np.abs(xx - 240) < 3) & (yy > 255) & (yy < 300)
    a[chalk] = (0.92, 0.92, 0.88); a[:6] = a[-6:] = (0.45, 0.3, 0.18); a[:, :6] = a[:, -6:] = (0.45, 0.3, 0.18)
    img = np_image('chalk', a)
    bd = P.add(mesh_obj('boardface', [(-0.9, 0, 0.75), (0.9, 0, 0.75), (0.9, 0, 1.95), (-0.9, 0, 1.95)], [(0, 1, 2, 3)], tex_mat('chalkmat', img, spec=0.0), c))
    uv_quad(bd); bd.parent = P.root; bd.location.y = -0.03
    P.box('boardback', wood, (0, 0.02, 1.35), (1.9, 0.05, 1.3), ink=0.02)
    return P


def windmill(c, name, loc, yaw=0.0, s=1.0, body='#5a4a3a'):
    P = Prop(name, c, loc, (0, 0, yaw)); P.root.scale = (s, s, s)
    bm = toon('mill_' + body, body, spec=0.1); white = toon('millwhite', '#f2efe6'); cap = toon('millcap', '#3a3d46')
    P.p('lathe', 'tower', bm, (0, 0, 0), prof=[(2.6, 0), (2.4, 2.5), (1.9, 6.5), (1.6, 8.6), (0.0, 8.6)], seg=8, smooth=False, ink=0.05)
    P.p('torus', 'gallery', white, (0, 0, 3.2), R=2.55, r=0.12, seg=24, ink=0.02)
    P.p('lathe', 'cap', cap, (0, 0, 8.6), prof=[(1.8, 0), (1.6, 0.8), (1.0, 1.5), (0.0, 1.8)], seg=12, ink=0.04)
    for z in (1.0, 4.2, 6.8): P.box('window', toon('millwin', '#2a2a30'), (0, -2.3 + 0.12 * (z / 3), z), (0.6, 0.1, 0.8), ink=0.015)
    hubE = empty(name + '_hub', (0, -1.9, 9.3), P.root, c); P.objs.append(hubE); P.parts['hub'] = hubE
    P.p('cyl', 'axle', cap, (0, 0.3, 0), (rad(90), 0, 0), r=0.25, h=1.2, seg=12, ink=0.02, parent=hubE)
    sail = toon('sail', '#efe6d0', stripes=('#8a6a4a', 2.2, 'Z'), spec=0.0)
    for k in range(4):
        arm = empty(name + '_arm', (0, 0, 0), hubE, c, rot=(0, rad(90 * k + 20), 0)); P.objs.append(arm)
        P.box('spar', toon('spar', '#6a4a32'), (0, -0.1, 4.0), (0.16, 0.12, 8.0), ink=0.015, parent=arm)
        P.box('sail', sail, (0.55, -0.05, 4.4), (0.95, 0.05, 6.2), ink=0.015, parent=arm)
    return P


def dutch_house(c, name, loc, w=4.6, h=9.0, col='#8a3a2a', yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); bm = toon('brick_' + col, col, spec=0.05); white = toon('frame', '#f4f1e8'); glassd = toon('dglass', '#2a3448', spec=0.6)
    P.box('body', bm, (0, 0, h / 2), (w, 6, h), ink=0.03)
    for k, (sw, sh) in enumerate([(w * 0.78, 1.0), (w * 0.52, 1.0), (w * 0.28, 1.0)]): P.box('step', bm, (0, -2.6, h + 0.5 + k), (sw, 0.8, sh), ink=0.025)
    P.box('top', white, (0, -2.6, h + 3.05), (w * 0.3, 0.84, 0.12), ink=0.01)
    for fz in range(3):
        for fx in (-1, 1):
            z = 2.6 + fz * 2.4; x = fx * w * 0.22
            P.box('wf', white, (x, -3.02, z), (1.1, 0.08, 1.6), ink=0.012); P.box('wg', glassd, (x, -3.05, z), (0.85, 0.06, 1.35), ink=0)
    P.box('door', toon('ddoor', '#2a4a3a'), (0, -3.02, 1.0), (1.0, 0.08, 2.0), ink=0.012)
    return P


def masia(c, name, loc, yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw))
    rng = np.random.default_rng(2); Hs, Ws = 256, 256; a = np.zeros((Hs, Ws, 3), np.float32); a[:] = (0.55, 0.47, 0.38)
    for r in range(10):
        y0 = r * 26; off = rng.integers(0, 40)
        for k in range(-1, 6):
            x0 = k * 50 + off; col = np.array([0.82, 0.72, 0.58]) * rng.uniform(0.8, 1.1)
            a[y0 + 3:y0 + 24, max(0, x0 + 3):max(0, min(Ws, x0 + 47))] = col
    stone = tex_mat('stone', np_image('stoneimg', a), spec=0.05)
    wall = P.box('walls', stone, (0, 0, 3.0), (11, 9, 6), ink=0.035)
    uvl = wall.data.uv_layers.new()
    for poly in wall.data.polygons:
        for li in poly.loop_indices:
            v = wall.data.vertices[wall.data.loops[li].vertex_index].co; n = poly.normal
            u = (v.y if abs(n.x) > 0.5 else v.x) * 0.35; vv = (v.y if abs(n.z) > 0.5 else v.z) * 0.35; uvl.data[li].uv = (u, vv)
    roof = toon('terracotta', '#c8643a', stripes=('#a84e2e', 3.0, 'X'), spec=0.1)
    rv = [(-6.2, -5.2, 6), (6.2, -5.2, 6), (6.2, 0, 8.6), (-6.2, 0, 8.6), (-6.2, 5.2, 6), (6.2, 5.2, 6)]
    r = P.add(mesh_obj('roof', rv, [(0, 1, 2, 3), (3, 2, 5, 4)], roof, c)); r.parent = P.root
    sol = r.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = 0.25; outline(r, 0.035)
    gv = [(-5.5, -4.5, 6), (-5.5, 4.5, 6), (-5.5, 0, 8.3)]; g1 = P.add(mesh_obj('gable', gv, [(0, 1, 2)], stone, c)); g1.parent = P.root
    g2 = P.add(mesh_obj('gable2', [(5.5, -4.5, 6), (5.5, 4.5, 6), (5.5, 0, 8.3)], [(0, 2, 1)], stone, c)); g2.parent = P.root
    P.box('door', toon('masiadoor', '#5a3a22'), (0, -4.52, 1.3), (1.8, 0.1, 2.6), ink=0.02)
    P.p('cyl', 'arch', toon('masiadoor', '#5a3a22'), (0, -4.52, 2.6), (rad(90), 0, 0), r=0.9, h=0.1, seg=20, ink=0.02)
    for x in (-3.6, 3.6):
        for z in (1.8, 4.4):
            P.box('mwin', toon('dglass', '#2a3448', spec=0.6), (x, -4.52, z), (1.1, 0.08, 1.2), ink=0.012)
            for sx in (-1, 1): P.box('shutter', toon('shutter', '#3a7a4a'), (x + sx * 0.85, -4.55, z), (0.55, 0.06, 1.25), ink=0.012)
    P.box('chimney', stone, (3.5, 2.0, 8.6), (0.9, 0.9, 2.2), ink=0.025)
    return P


def olive_tree(c, name, loc, s=1.0):
    P = Prop(name, c, loc); P.root.scale = (s, s, s)
    P.p('cyl', 'trunk', toon('bark', '#6a5038'), (0, 0, 1.0), (rad(6), 0, 0), r=0.22, r2=0.14, h=2.0, seg=8, ink=0.02)
    for k, (x, y, z, r) in enumerate([(0, 0, 2.6, 1.2), (0.9, 0.2, 2.3, 0.9), (-0.8, -0.2, 2.4, 0.9), (0.2, 0.6, 3.1, 0.8)]):
        P.p('ico', 'leaf', toon('olive', '#6a8a4a', spec=0.05), (x, y, z), r=r, sub=1, smooth=False, ink=0.025)
    return P


def mini_goal(c, name, loc, yaw=0.0):
    P = Prop(name, c, loc, (0, 0, yaw)); w = toon('goalwhite', '#f4f6fb', spec=0.3)
    for sx in (-1, 1): P.p('cyl', 'post', w, (sx * 1.5, 0, 0.6), r=0.05, h=1.2, seg=10, ink=0.015)
    P.p('cyl', 'bar', w, (0, 0, 1.2), (0, rad(90), 0), r=0.05, h=3.1, seg=10, ink=0.015)
    return P


def booth(c, name, loc):
    """commentary booth on the main stand, open towards the pitch (+y)"""
    P = Prop(name, c, loc); wall = toon('boothwall', '#2a3550', spec=0.1); desk = toon('desk', '#6a4a32', spec=0.2)
    P.box('floor', toon('boothfloor', '#3a3a44'), (0, 0, -0.05), (4.6, 3.2, 0.1), ink=0)
    P.box('back', wall, (0, -1.6, 1.4), (4.6, 0.1, 2.9), ink=0.02)
    for sx in (-1, 1): P.box('side', wall, (sx * 2.3, 0, 1.4), (0.1, 3.2, 2.9), ink=0.02)
    P.box('roof', wall, (0, 0, 2.9), (4.7, 3.3, 0.14), ink=0.02)
    P.box('sill', toon('sill', '#1a1f2e'), (0, 1.55, 0.5), (4.6, 0.12, 1.0), ink=0.02)
    P.box('desk', desk, (0, 0.95, 0.95), (3.6, 0.9, 0.08), bevel=0.02, ink=0.015)
    for x in (-1.1, 1.2):
        P.box('mon', toon('monframe', '#16181f'), (x, 1.1, 1.3), (0.8, 0.06, 0.52), ink=0.012)
        P.box('monscr', glow('monscr', '#3aa860', 1.4), (x, 1.07, 1.3), (0.72, 0.02, 0.44), ink=0)
    P.p('cyl', 'micstand', toon('micstand', '#22242c', spec=0.5), (0.15, 0.75, 1.15), (rad(-30), 0, 0), r=0.015, h=0.45, seg=8, ink=0.006)
    P.p('sphere', 'micfoam', toon('micfoam2', '#3a3d48'), (0.15, 0.62, 1.37), size=(0.07, 0.07, 0.09), seg=12, ink=0.01, key='mic')
    for x in (-1.6, 0.6, 1.8): P.box('poster', toon('poster%d' % int(x * 10), ['#d81e2a', '#ffd23d', '#1f5fd8'][int(x + 2) % 3]), (x, -1.53, 1.9), (0.7, 0.03, 0.9), ink=0.01)
    lt = D.lights.new(name + '_lamp', 'POINT'); lt.energy = 180; lt.color = (1.0, 0.85, 0.65); lt.shadow_soft_size = 0.4; lt.use_custom_distance = True; lt.cutoff_distance = 8
    lo = D.objects.new(name + '_lamp', lt); B.link(lo, c); lo.parent = P.root; lo.location = (0, 0.4, 2.5); P.objs.append(lo)
    return P


def ball(c, name='ball', r=0.22):
    m = B.toon('matchball', '#ffffff', tex=os.path.join(B.ASSET, 'ball_tex.jpeg'), spec=0.5, emit=0.35)
    return prim('sphere', name, m, (0, 0, r), r=r, seg=24, ink=0.012, c=c)


def baby_ball(c, name='baby'):
    """the 'child' tiki-taka: a football with a cute face, swaddled in a blaugrana blanket with a name tag"""
    P = Prop(name, c); blanket = toon('blanket', '#a50044', stripes=('#004d98', 5.0, 'X'), spec=0.1)
    P.p('sphere', 'wrap', blanket, (0, 0, 0), size=(0.26, 0.22, 0.4), seg=20, ink=0.015)
    P.p('torus', 'hood', toon('hood', '#f2e6d8'), (0, 0, 0.3), (rad(70), 0, 0), R=0.19, r=0.06, seg=18, ink=0.012)
    m = B.toon('matchball', '#ffffff', tex=os.path.join(B.ASSET, 'ball_tex.jpeg'), spec=0.5)
    P.p('sphere', 'head', m, (0, -0.02, 0.36), size=(0.17, 0.17, 0.17), seg=20, ink=0.012, key='head')
    for sx in (-1, 1):
        P.p('sphere', 'beye', toon('pupil', '#1a1020', spec=0.6), (sx * 0.06, -0.17, 0.4), size=(0.028, 0.012, 0.036), seg=10, ink=0)
        P.p('sphere', 'bglint', glow('glint', '#ffffff', 1.3), (sx * 0.055, -0.183, 0.412), size=(0.009, 0.004, 0.01), seg=6, ink=0)
        P.p('sphere', 'bblush', toon('blush', '#ff8f98', spec=0.0), (sx * 0.1, -0.15, 0.33), size=(0.03, 0.01, 0.018), seg=8, ink=0)
    P.p('torus', 'bsmile', toon('mouthline', '#2a1020'), (0, -0.172, 0.335), (rad(90), 0, 0), R=0.035, r=0.008, a0=rad(200), a1=rad(340), seg=10, ink=0, key='smile')
    P.p('torus', 'bsad', toon('mouthline', '#2a1020'), (0, -0.172, 0.31), (rad(90), 0, 0), R=0.03, r=0.008, a0=rad(30), a1=rad(150), seg=10, ink=0, key='sad')
    P.box('tag', toon('tag', '#fff6e0', emit=0.1), (0, -0.23, -0.05), (0.34, 0.02, 0.12), ink=0.008)
    P.text('tagtxt', 'TIKI-TAKA', toon('tagtxt', '#a50044'), (0, -0.245, -0.07), size=0.075, extrude=0.004, ink=0)
    return P


# ---------------- flags (cloth waved per frame) ----------------
FLAGS = {'italy': ('v', ['#009246', '#ffffff', '#ce2b37']), 'netherlands': ('h', ['#ae1c28', '#ffffff', '#21468b']), 'spain': ('h', ['#aa151b', '#f1bf00', '#f1bf00', '#aa151b']),
         'catalonia': ('h', ['#fcdd09', '#da121a'] * 4 + ['#fcdd09']), 'inter': ('v', ['#0a3a9e', '#151518'] * 3), 'barca': ('v', ['#a50044', '#004d98'] * 3), 'swiss': ('swiss', [])}


def flag(c, name, kind, loc, yaw=0.0, w=1.8, h=1.2, pole=3.2):
    P = Prop(name, c, loc, (0, 0, yaw)); P.p('cyl', 'pole', toon('pole', '#a8aeb8', spec=0.6), (0, 0, pole / 2), r=0.04, h=pole, seg=8, ink=0.012)
    P.p('sphere', 'finial', toon('lockgold', '#f2c230', spec=0.8), (0, 0, pole + 0.05), size=(0.08, 0.08, 0.08), seg=10, ink=0.01)
    typ, cols = FLAGS[kind]; Hs, Ws = 64, 96; a = np.zeros((Hs, Ws, 3), np.float32)
    lin = lambda h_: np.array([int(h_[i:i + 2], 16) / 255 for i in (1, 3, 5)])   # byte images take display (sRGB) values
    if typ == 'v':
        for i, cc in enumerate(cols): a[:, i * Ws // len(cols):(i + 1) * Ws // len(cols)] = lin(cc)
    elif typ == 'h':
        for i, cc in enumerate(cols): a[i * Hs // len(cols):(i + 1) * Hs // len(cols)] = lin(cc)
    else:
        a[:] = lin('#d52b1e'); a[24:40, 34:62] = 1; a[14:50, 42:54] = 1
    img = np_image('flag_' + kind, a); mat = tex_mat('flagmat_' + kind, img, spec=0.05)
    nu, nv = 16, 8; vs = [(w * i / nu, 0, pole - h + h * j / nv) for j in range(nv + 1) for i in range(nu + 1)]
    fs = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i) for j in range(nv) for i in range(nu)]
    cl = mesh_obj(name + '_cloth', vs, fs, mat, c, smooth=True); cl.parent = P.root
    uv = cl.data.uv_layers.new()
    for poly in cl.data.polygons:
        for li in poly.loop_indices:
            v = cl.data.vertices[cl.data.loops[li].vertex_index].co; uv.data[li].uv = (v.x / w, (v.z - (pole - h)) / h)
    m2 = cl.data.materials; outline(cl, 0.012); P.add(cl, 'cloth')
    P.base = np.array([v.co[:] for v in cl.data.vertices], np.float32); P.w = w
    return P


def wave_flag(P, t):
    cl = P.parts['cloth']; b = P.base.copy(); k = b[:, 0] / P.w
    b[:, 1] = np.sin(b[:, 0] * 3.0 - t * 7 + b[:, 2] * 0.8) * 0.16 * k; b[:, 2] -= k * k * 0.1
    cl.data.vertices.foreach_set('co', b.ravel()); cl.data.update()


# ---------------- confetti (one mesh, moved per frame) ----------------
class Confetti:
    def __init__(self, c, name='confetti', n=220, cols=('#ffd23d', '#ffffff', '#d81e2a')):
        rng = np.random.default_rng(5); self.n = n; self.r = rng.random((n, 8)).astype(np.float32)
        vs, fs = [], []
        for i in range(n): k = len(vs); vs += [(-0.06, 0, -0.04), (0.06, 0, -0.04), (0.06, 0, 0.04), (-0.06, 0, 0.04)]; fs.append((k, k + 1, k + 2, k + 3))
        self.ob = mesh_obj(name, vs, fs, None, c)
        self.mats = []
        for j, cc in enumerate(cols): m = glow('conf_%s' % cc, cc, 1.4); self.ob.data.materials.append(m)
        for i, p in enumerate(self.ob.data.polygons): p.material_index = i % len(cols)
        self.ob.visible_shadow = False; self.on = True; self.show(False)
    def recolor(self, cols):
        for j, cc in enumerate(cols[:len(self.ob.data.materials)]):
            m = glow('conf_%s' % cc, cc, 1.4); self.ob.data.materials[j] = m
    def show(self, v):
        if v != self.on: self.on = v; self.ob.hide_render = self.ob.hide_viewport = not v
    def update(self, t, center, spread=(9, 9), height=7.0):
        r = self.r; ph = (t * 0.32 + r[:, 0]) % 1.0
        x = center[0] + (r[:, 1] - 0.5) * spread[0] + np.sin(t * 2 + r[:, 2] * 9) * 0.4; y = center[1] + (r[:, 3] - 0.5) * spread[1]; z = center[2] + height * (1 - ph)
        a = t * 5 * (0.5 + r[:, 4]) + r[:, 5] * 6; ca, sa = np.cos(a), np.sin(a)
        quad = np.array([(-0.06, -0.04), (0.06, -0.04), (0.06, 0.04), (-0.06, 0.04)], np.float32); out = np.zeros((self.n, 4, 3), np.float32)
        for k, (qx, qz) in enumerate(quad):
            out[:, k, 0] = x + qx * ca; out[:, k, 1] = y + qx * sa * 0.6 + qz * np.sin(a * 0.7); out[:, k, 2] = z + qz * np.cos(a * 0.7)
        self.ob.data.vertices.foreach_set('co', out.ravel()); self.ob.data.update()


class Trail:
    """glowing streak behind a passed ball"""
    def __init__(self, c, name='trail', col='#9ff0ff'):
        self.ob = prim('cyl', name, glow(name + 'm', col, 3.0), (0, 0, 0), r=1, h=1, seg=10, ink=0, c=c, shift=(0, 0, 0.5)); self.ob.visible_shadow = False; self.show(False)
    def show(self, v): self.ob.hide_render = self.ob.hide_viewport = not v
    def set(self, a, b, width=0.05):
        a, b = Vector(a), Vector(b); d = b - a
        if d.length < 1e-4: self.show(False); return
        self.show(True); self.ob.location = a; self.ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); self.ob.scale = (width, width, d.length)
