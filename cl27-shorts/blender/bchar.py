# 3D bean-head characters: primitives with cel shading and ink outlines, cute faces, poses, walk cycle, kits and hats.
import math, os
from mathutils import Vector, Euler
import blib as B
from blib import prim, empty, toon, rad

KITS = {
    'swiss': dict(shirt='#d52b1e', shorts='#ffffff', socks='#d52b1e'),
    'italy': dict(shirt='#1d5fd8', shorts='#ffffff', socks='#1d5fd8'),
    'inter': dict(shirt='#0a3a9e', stripe='#151518', shorts='#151518', socks='#151518'),
    'barca': dict(shirt='#a50044', stripe='#004d98', shorts='#004d98', socks='#a50044'),
    'blue': dict(shirt='#0a47c2', shorts='#0a47c2', socks='#ffffff'),
    'white': dict(shirt='#f4f4f2', shorts='#1b2350', socks='#f4f4f2'),
    'red': dict(shirt='#d81e2a', shorts='#ffffff', socks='#d81e2a'),
    'orange': dict(shirt='#ff7a00', shorts='#ffffff', socks='#ff7a00'),
    'spain': dict(shirt='#c8102e', shorts='#13246b', socks='#13246b'),
    'kid': dict(shirt='#a50044', stripe='#004d98', shorts='#004d98', socks='#a50044'),
    'grey': dict(shirt='#8a8f9c', shorts='#3a3f4c', socks='#3a3f4c'),
}
OUTFITS = {  # non-kit clothes: top colour, trousers, coat
    'coach': dict(shirt='#2a2c36', shorts='#2a2c36', socks='#2a2c36', coat='#1d1f28', scarf='#5a5f70'),
    'oldcoach': dict(shirt='#6a5236', shorts='#4a3b2c', socks='#4a3b2c', coat='#7a5a3a'),
    'cardigan': dict(shirt='#5d6470', shorts='#2a2c36', socks='#2a2c36'),
    'suit': dict(shirt='#2f3446', shorts='#2f3446', socks='#2f3446'),
    'driver': dict(shirt='#2a4a8a', shorts='#1d2a4a', socks='#1d2a4a'),
}
ARM = {  # per arm: (forward raise, outward raise, elbow bend, elbow twist) in degrees
    'hang': ((4, 8, 10, 0), (4, 8, 10, 0)), 'cheer': ((15, 150, 8, 0), (15, 150, 8, 0)), 'wave': ((4, 8, 10, 0), (8, 145, 35, 0)),
    'point': ((4, 8, 10, 0), (88, 18, 0, 0)), 'hold': ((50, 14, 75, 0), (50, 14, 75, 0)), 'cross': ((42, 18, 112, 70), (42, 18, 112, 70)),
    'hip': ((6, 38, 95, 80), (6, 38, 95, 80)), 'shrug': ((14, 60, 105, -60), (14, 60, 105, -60)), 'facepalm': ((4, 8, 10, 0), (118, 14, 132, 0)),
    'think': ((40, 12, 100, 70), (70, 8, 135, 0)), 'drive': ((62, 14, 38, 0), (62, 14, 38, 0)), 'sweep': ((48, 6, 22, 0), (58, 2, 34, 0)),
    'clap': ((60, 4, 70, 40), (60, 4, 70, 40)), 'pointup': ((4, 8, 10, 0), (165, 10, 0, 0)), 'present': ((40, 40, 30, 0), (40, 40, 30, 0)),
    'shout': ((40, 30, 100, -40), (40, 30, 100, -40)), 'baby': ((55, 10, 85, 55), (50, 12, 80, 55)), 'away': ((85, 12, 5, 0), (85, 12, 5, 0)),
    'run': ((0, 10, 70, 0), (0, 10, 70, 0)), 'mic': ((4, 8, 10, 0), (55, 8, 110, 20)),
}
FACES = ('smile', 'laugh', 'shock', 'flat', 'sad', 'angry', 'smug', 'love')


def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


class Bean:
    def __init__(self, name, c, kit='blue', outfit=None, skin='#f2c49b', hair='#3a2416', hat=None, moustache=False, glasses=False,
                 coat=False, scale=1.0, hairstyle='cap', ink=0.017, number=None):
        self.name = name; self.c = c; self.parts = []
        self.root = empty(name, c=c)
        self.body = empty(name + '_body', (0, 0, 0), self.root, c)
        k = OUTFITS.get(outfit) or KITS[kit]; self.kitname = outfit or kit
        mshirt = toon('shirt_' + self.kitname, k['shirt'], stripes=(k['stripe'], 3.2, 'X') if k.get('stripe') else None, spec=0.15)
        mshorts = toon('shorts_' + self.kitname, k['shorts'], spec=0.12); msocks = toon('socks_' + self.kitname, k['socks'], spec=0.1)
        mskin = toon('skin_' + skin, skin, spec=0.28); mshoe = toon('shoe', '#1b1b22', spec=0.4); mhair = toon('hair_' + hair, hair, spec=0.3)
        self.mskin = mskin
        P = lambda *a, **kw: self._p(prim(*a, c=c, ink=kw.pop('ink', ink), **kw))
        # legs (pivots at the hips)
        self.leg = []
        for sx in (-1, 1):
            hp = empty(name + '_hip', (sx * 0.12, 0, 0.56), self.body, c)
            P('cyl', 'thigh', mshorts if (outfit or coat) else mskin, (0, 0, -0.12), r=0.078, h=0.24, seg=12, parent=hp)
            P('cyl', 'shin', msocks, (0, 0, -0.34), r=0.074, h=0.24, seg=12, parent=hp)
            P('sphere', 'shoe', mshoe, (0, -0.05, -0.47), size=(0.095, 0.155, 0.065), seg=14, parent=hp)
            self.leg.append(hp)
        # hips / shorts, torso
        P('sphere', 'shorts', mshorts, (0, 0, 0.6), size=(0.27, 0.21, 0.16), seg=18, parent=self.body)
        self.torso = P('sphere', 'torso', mshirt, (0, 0, 0.88), size=(0.29, 0.22, 0.33), seg=20, parent=self.body)
        if coat:
            mcoat = toon('coat_' + self.kitname, k.get('coat', '#1d1f28'), spec=0.12)
            P('cone', 'coat', mcoat, (0, 0, 0.72), r=0.36, r2=0.27, h=0.78, seg=18, parent=self.body)
            if k.get('scarf'): P('torus', 'scarf', toon('scarf', k['scarf']), (0, 0, 1.12), R=0.15, r=0.06, seg=16, parent=self.body)
        # arms (pivots at the shoulders, elbows)
        self.arm = []
        msleeve = toon('coat_' + self.kitname, k.get('coat', k['shirt'])) if coat else mshirt
        for sx in (-1, 1):
            sh = empty(name + '_sh', (sx * 0.27, 0, 1.06), self.body, c)
            P('cyl', 'upper', msleeve, (0, 0, -0.13), r=0.064, h=0.27, seg=12, parent=sh)
            el = empty(name + '_el', (0, 0, -0.27), sh, c)
            P('cyl', 'fore', mskin if not (outfit or coat) else msleeve, (0, 0, -0.12), r=0.058, h=0.24, seg=12, parent=el)
            hand = P('sphere', 'hand', mskin, (0, 0, -0.27), size=(0.078, 0.078, 0.078), seg=14, parent=el)
            self.arm.append((sh, el, hand))
        # head (pivot at the neck) and face
        self.head = empty(name + '_head', (0, 0, 1.2), self.body, c)
        P('sphere', 'head', mskin, (0, 0, 0.36), size=(0.34, 0.31, 0.43), seg=28, parent=self.head)
        if hairstyle == 'cap': P('sphere', 'hair', mhair, (0, 0.035, 0.6), size=(0.335, 0.31, 0.26), seg=22, parent=self.head)
        elif hairstyle == 'bald': P('sphere', 'hair', mhair, (0, 0.06, 0.42), size=(0.345, 0.3, 0.2), seg=20, parent=self.head)
        elif hairstyle == 'long': P('sphere', 'hair', mhair, (0, 0.06, 0.5), size=(0.355, 0.33, 0.36), seg=22, parent=self.head)
        white = toon('eyewhite', '#ffffff', spec=0.0, shadow=(0.85, 0.85, 0.9)); black = toon('pupil', '#1a1020', spec=0.6)
        self.eyes, self.pupils = [], []
        for sx in (-1, 1):
            e = P('sphere', 'eye', white, (sx * 0.118, -0.272, 0.4), size=(0.078, 0.04, 0.098), seg=16, parent=self.head, ink=0.009)
            p = P('sphere', 'pupil', black, (sx * 0.118, -0.305, 0.385), size=(0.046, 0.02, 0.058), seg=12, parent=self.head, ink=0)
            P('sphere', 'glint', B.glow('glint', '#ffffff', 1.3), (sx * 0.104, -0.322, 0.408), size=(0.014, 0.008, 0.016), seg=8, parent=self.head, ink=0)
            self.eyes.append(e); self.pupils.append(p)
        self.brows = [P('box', 'brow', toon('brow', '#2a1a14'), (sx * 0.12, -0.285, 0.53), size=(0.085, 0.02, 0.022), parent=self.head, ink=0, smooth=False) for sx in (-1, 1)]
        for sx in (-1, 1): P('sphere', 'blush', toon('blush', '#ff8f98', spec=0.0, shadow=(0.8, 0.7, 0.75)), (sx * 0.2, -0.255, 0.27), size=(0.06, 0.02, 0.032), seg=10, parent=self.head, ink=0)
        # mouths: one shown at a time
        mm = toon('mouth', '#6a1a2a', spec=0.0); mi = toon('mouthline', '#2a1020', spec=0.0)
        self.mouths = {}
        self.mouths['smile'] = P('torus', 'm_smile', mi, (0, -0.29, 0.25), rot=(rad(90), 0, 0), R=0.085, r=0.013, a0=rad(200), a1=rad(340), seg=14, parent=self.head, ink=0)
        self.mouths['smug'] = P('torus', 'm_smug', mi, (0.03, -0.29, 0.24), rot=(rad(90), 0, rad(-12)), R=0.07, r=0.013, a0=rad(220), a1=rad(330), seg=12, parent=self.head, ink=0)
        self.mouths['laugh'] = P('sphere', 'm_laugh', mm, (0, -0.282, 0.215), size=(0.085, 0.03, 0.065), seg=14, parent=self.head, ink=0.008)
        self.mouths['shock'] = P('sphere', 'm_shock', mm, (0, -0.285, 0.2), size=(0.045, 0.028, 0.065), seg=12, parent=self.head, ink=0.008)
        self.mouths['flat'] = P('box', 'm_flat', mi, (0, -0.292, 0.235), size=(0.09, 0.015, 0.016), parent=self.head, ink=0, smooth=False)
        self.mouths['sad'] = P('torus', 'm_sad', mi, (0, -0.29, 0.17), rot=(rad(90), 0, 0), R=0.075, r=0.013, a0=rad(30), a1=rad(150), seg=12, parent=self.head, ink=0)
        self.mouths['angry'] = P('box', 'm_angry', mm, (0, -0.288, 0.215), size=(0.1, 0.02, 0.035), parent=self.head, ink=0.006, smooth=False)
        self.mouths['love'] = self.mouths['laugh']
        if moustache:
            for sx in (-1, 1): P('sphere', 'mous', mhair, (sx * 0.045, -0.3, 0.3), rot=(0, rad(sx * 14), 0), size=(0.058, 0.03, 0.022), seg=10, parent=self.head, ink=0.006)
        if glasses:
            for sx in (-1, 1): P('torus', 'glass', toon('glasses', '#1a1a22'), (sx * 0.118, -0.31, 0.4), rot=(rad(90), 0, 0), R=0.085, r=0.011, seg=16, parent=self.head, ink=0)
        self.hats = {}
        if hat: self.add_hat(hat)
        if number:
            nt = B.text3d(name + '_num', number, toon('numwhite', '#ffffff', spec=0.1), size=0.24, extrude=0.008, bevel=0.002, c=c, font=os.path.join(B.ASSET, 'bc900.ttf'), ink=0.006)
            nt.parent = self.body; nt.location = (0, -0.232, 0.86); nt.rotation_euler = (rad(84), 0, 0); self._p(nt)
        self.root.scale = (scale,) * 3
        self.roles = {}
        for o in self.parts:
            if o.type == 'MESH' and o.data.materials and o.data.materials[0]:
                n = o.data.materials[0].name
                for r in ('shirt_', 'shorts_', 'socks_'):
                    if n.startswith(r): self.roles.setdefault(r, []).append(o)
        self.state = {}; self.visible = True; self.set_visible(False)

    def _p(self, ob): self.parts.append(ob); return ob

    def set_kit(self, kit):
        if self.kitname == kit: return
        k = KITS[kit]; self.kitname = kit
        mats = {'shirt_': toon('shirt_' + kit, k['shirt'], stripes=(k['stripe'], 3.2, 'X') if k.get('stripe') else None, spec=0.15),
                'shorts_': toon('shorts_' + kit, k['shorts'], spec=0.12), 'socks_': toon('socks_' + kit, k['socks'], spec=0.1)}
        for r, objs in self.roles.items():
            for o in objs: o.data.materials[0] = mats[r]

    def add_hat(self, hat):
        P = lambda *a, **kw: self._p(prim(*a, c=self.c, ink=kw.pop('ink', 0.016), **kw))
        g = empty(self.name + '_hat_' + hat, (0, 0, 0), self.head, self.c); objs = []
        if hat == 'flatcap':
            m = toon('flatcap', '#5a4a3a', spec=0.1)
            objs += [P('sphere', 'cap', m, (0, 0.02, 0.66), size=(0.35, 0.33, 0.16), seg=18, parent=g), P('sphere', 'brim', m, (0, -0.2, 0.62), size=(0.24, 0.16, 0.04), seg=14, parent=g)]
        elif hat == 'driver':
            m = toon('drivercap', '#1d2a5a', spec=0.25)
            objs += [P('cyl', 'cap', m, (0, 0.0, 0.7), r=0.3, r2=0.34, h=0.16, seg=20, parent=g),
                     P('box', 'visor', toon('visor', '#101014', spec=0.6), (0, -0.25, 0.62), rot=(rad(14), 0, 0), size=(0.42, 0.18, 0.025), parent=g, smooth=False),
                     P('sphere', 'badge', toon('gold', '#f2c230', spec=0.6), (0, -0.33, 0.72), size=(0.05, 0.015, 0.045), seg=10, parent=g, ink=0.006)]
        elif hat == 'headset':
            m = toon('headset', '#22242c', spec=0.4)
            objs += [P('torus', 'band', m, (0, 0, 0.36), rot=(0, rad(90), 0), R=0.38, r=0.022, a0=rad(-10), a1=rad(190), seg=18, parent=g)]
            for sx in (-1, 1): objs.append(P('cyl', 'cup', m, (sx * 0.355, 0, 0.36), rot=(0, rad(90), 0), r=0.09, h=0.07, seg=14, parent=g))
            objs.append(P('cyl', 'boom', m, (-0.25, -0.2, 0.22), rot=(rad(70), 0, rad(-40)), r=0.012, h=0.3, seg=6, parent=g, ink=0))
            objs.append(P('sphere', 'micball', toon('micfoam', '#3a3d48'), (-0.12, -0.32, 0.2), size=(0.04, 0.04, 0.04), seg=10, parent=g))
        elif hat == 'crown':
            m = toon('gold', '#f2c230', spec=0.6)
            objs.append(P('cyl', 'crown', m, (0, 0, 0.78), r=0.2, r2=0.24, h=0.16, seg=16, parent=g))
        self.hats[hat] = (g, objs)

    def set_visible(self, v):
        if v == self.visible: return
        self.visible = v
        for o in self.parts: o.hide_render = not v; o.hide_viewport = not v
        if v: self._sync_hats(); self.face(self.state.get('face', 'smile'), force=True)

    def _sync_hats(self):
        h = self.state.get('hat')
        for k, (g, objs) in self.hats.items():
            for o in objs: o.hide_render = o.hide_viewport = (k != h) or not self.visible

    def face(self, f, force=False):
        if not force and self.state.get('face') == f: return
        self.state['face'] = f
        show = {'love': 'laugh'}.get(f, f)
        for k, o in self.mouths.items():
            if k == 'love': continue
            o.hide_render = o.hide_viewport = (k != show) or not self.visible
        br = {'angry': (-22, 0.0), 'sad': (20, 0.0), 'shock': (-6, 0.035), 'smug': (8, 0.0)}.get(f, (0, 0))
        for i, b in enumerate(self.brows):
            sx = -1 if i == 0 else 1; b.rotation_euler = (0, rad(br[0] * sx), 0); b.location.z = 0.53 + br[1]
        self.eye_sc = 1.25 if f == 'shock' else (0.6 if f in ('angry', 'smug') else 1.0)
        for e in self.eyes: e.scale = (1, 1, self.eye_sc)

    def hat(self, h):
        if self.state.get('hat') == h: return
        self.state['hat'] = h; self._sync_hats()

    def pose(self, name, t=0.0, walk=0.0, run=False, wave_speed=7.0, legs=None):
        A = ARM.get(name, ARM['hang'])
        for i, (sh, el, hand) in enumerate(self.arm):
            fwd, abd, eb, tw = A[i]; s = -1 if i == 1 else 1   # i==1 is the right arm (+x)
            if name == 'wave' and i == 1: eb += 22 * math.sin(t * wave_speed)
            if name == 'clap': eb += 18 * math.sin(t * 14); abd += 10 * math.sin(t * 14)
            if name == 'cheer': abd += 10 * math.sin(t * 9 + i * 3)
            if name == 'sweep': fwd += 18 * math.sin(t * 6)
            if walk:
                sw = math.sin(t * (11 if run else 7.5)) * (40 if run else 24) * walk * (1 if i == 0 else -1)
                if name in ('hang', 'run'): fwd += sw
            sh.rotation_euler = (rad(-fwd), rad(abd * s), 0); el.rotation_euler = (rad(-eb), 0, rad(tw * s))
        for i, hp in enumerate(self.leg):
            a = math.sin(t * (11 if run else 7.5)) * (38 if run else 26) * walk * (1 if i == 0 else -1)
            if legs == 'sit': a = -84
            elif legs == 'kick' and i == 1: a = -55 * max(0.0, math.sin(t * 6))
            elif legs == 'jump': a = 18 * (1 if i == 0 else -1)
            hp.rotation_euler = (rad(a), 0, 0)

    def place(self, x, y, yaw=0.0, z=0.0, hop=0.0, t=0.0, walk=0.0, run=False, lean=0.0, bob=1.0):
        self.root.location = (x, y, z); self.root.rotation_euler = (0, 0, yaw)
        b = abs(math.sin(t * (11 if run else 7.5))) * 0.05 * walk + (math.sin(t * 2.6) * 0.012 * bob)
        self.body.location = (0, 0, b + hop); self.body.rotation_euler = (rad(lean), 0, 0)

    def look(self, lx=0.0, lz=0.0, blink=False, head_tilt=0.0, head_turn=0.0):
        for p, sx in zip(self.pupils, (-1, 1)): p.location.x = sx * 0.118 + lx * 0.03; p.location.z = 0.385 + lz * 0.025
        for e in self.eyes: e.scale.z = 0.08 if blink else getattr(self, 'eye_sc', 1.0)
        self.head.rotation_euler = (0, rad(head_tilt), rad(head_turn))


def yaw_to(x, y, tx, ty):
    """yaw so that the character's front (-Y) looks from (x,y) toward (tx,ty)"""
    return math.atan2(tx - x, -(ty - y)) if (tx, ty) != (x, y) else 0.0
