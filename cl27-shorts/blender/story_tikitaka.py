# Tiki-taka: shots timed to the voice lines in timing.json (line index `from`).
import math
import blib as B, bchar as BC, bprops as BP, rt
from rt import C, ss, ease_out, back, lerp, keyed
from blib import rad

TAIL = 2.1
NX, NY = 4000.0, 0.0     # Dutch village
MX, MY = 6000.0, 0.0     # La Masia
SK = ['#f2c49b', '#e0a87e', '#c98d62', '#8d5a3c', '#f6cfa8']
HR = ['#3a2416', '#1d140f', '#5a3a22', '#2a1a10', '#7a5a3a']
BARCA = ['#a50044', '#004d98', '#f6c21c', '#a50044']
SPAIN = ['#c8102e', '#f1bf00', '#c8102e', '#ffffff']
ORANGE = ['#ff7a00', '#ffffff', '#ff7a00', '#21468b']
BOOTH = (0.0, -43.6, 4.6)


def build(W):
    rt.build_stadium(W, BARCA); rt.build_dutch(W, NX, NY); rt.build_masia(W, MX, MY)
    rt.build_gameboards(W, 'bar_mun', screen='promo')
    c = W.coll
    for i in range(8): W.bean('p%d' % i, kit='barca', skin=SK[i % 5], hair=HR[i % 5])
    for i in range(7): W.bean('k%d' % i, kit='kid', skin=SK[(i + 2) % 5], hair=HR[(i + 1) % 5], scale=0.7)
    W.bean('n14', kit='orange', skin='#f2c49b', hair='#6a4a2a', number='14')
    W.bean('cruyff', outfit='suit', coat=True, skin='#f2c49b', hair='#6a4a2a')
    W.bean('montes', outfit='suit', hat='headset', skin='#d9a07a', hair='#2a1a10', glasses=True)
    W.bean('coach', outfit='cardigan', skin='#e8b48e', hair='#3a3a3a')
    W.prop('booth', BP.booth(c, 'booth', BOOTH))
    kinds = ['cup', 'bigears', 'tall', 'globe', 'plate', 'shield']
    pod = BP.Prop('podium', c, (0, 8, 0)); pod.box('pod', B.toon('podium', '#f4f1e8', spec=0.3), (0, 0, 0.35), (7.4, 1.4, 0.7), bevel=0.06, ink=0.03)
    pod.box('podstripe', B.toon('podgold', '#f2c230', spec=0.6), (0, -0.71, 0.35), (7.4, 0.04, 0.16), ink=0); W.prop('podium', pod)
    for i, k in enumerate(kinds): W.prop('tb%d' % i, BP.trophy(c, 'tb%d' % i, k, (-3.0 + i * 1.2, 8, 0.7)))
    for i, k in enumerate(['tall', 'globe', 'tall']): W.prop('ts%d' % i, BP.trophy(c, 'ts%d' % i, k, (-1.4 + i * 1.4, 8, 0.7)))
    for word in ('TIKI!', 'TAKA!'):
        P = BP.Prop(word, c); P.text('w', word, B.toon('popyellow', '#ffd23d', spec=0.4, emit=0.35), (0, 0, 0), rot=(rad(90), 0, 0), size=1.25, extrude=0.14, ink=0.05); W.prop(word, P)
    bb = W.prop('baby', BP.baby_ball(c))
    W.prop('flagEs', BP.flag(c, 'flagEs', 'spain', (-6.5, 9.5, 0), rad(180))); W.prop('flagCat', BP.flag(c, 'flagCat', 'catalonia', (6.5, 9.5, 0), rad(180)))
    W.prop('flagNl', BP.flag(c, 'flagNl', 'netherlands', (NX + 7.5, NY + 9, 0), rad(180)))
    W.balls = [BP.ball(c, 'ball%d' % i) for i in range(2)]
    W.trail = BP.Trail(c, 'trail', '#aaf4ff')
    W.rain_rig()


def bean(W, k, x, y, yaw=None, pose='hang', face='smile', t=0.0, walk=0.0, run=False, hop=0.0, z=0.0, kit=None, look=(0, 0), lean=0.0, legs=None, cam=None, hat=None, seed=0.0):
    b = W.beans[k]
    if kit: b.set_kit(kit)
    if yaw is None: yaw = BC.yaw_to(x, y, cam[0], cam[1]) if cam else 0.0
    b.place(x, y, yaw, z, hop, t + seed, walk, run, lean); b.pose(pose, t + seed, walk, run, legs=legs); b.face(face); b.hat(hat if hat else b.state.get('fixedhat'))
    b.look(look[0], look[1], blink=((t + seed * 1.7) % 3.3) < 0.11)
    return b


def ball_at(W, i, p):
    bl = W.balls[i]
    if p is None: bl.hide_render = bl.hide_viewport = True; return
    bl.hide_render = bl.hide_viewport = False; bl.location = p; bl.rotation_euler = (p[0] * 4, p[1] * 4, 0)


def pass_path(pts, times, t, height=0.25):
    """ball position along a chain of passes: pts[i] -> pts[i+1] between times[i] and times[i+1]"""
    if t <= times[0]: return (pts[0][0], pts[0][1], 0.22), None
    for i in range(len(times) - 1):
        if t < times[i + 1]:
            u = (t - times[i]) / (times[i + 1] - times[i]); a, b = pts[i], pts[i + 1]
            p = (lerp(a[0], b[0], u), lerp(a[1], b[1], u), 0.22 + math.sin(u * math.pi) * height); return p, (a, p)
    return (pts[-1][0], pts[-1][1], 0.22), None


def ring(n, r, cx=0.0, cy=0.0, a0=0.0): return [(cx + math.cos(a0 + 2 * math.pi * k / n) * r, cy + math.sin(a0 + 2 * math.pi * k / n) * r) for k in range(n)]


# ---------------- shot bodies ----------------
def s0(W, lt, u, t, cam):   # hook: fast one-touch passing, the opponents get dizzy
    R = ring(6, 3.4, 0, 0, lt * 0.15)
    for i, (x, y) in enumerate(R): bean(W, 'p%d' % i, x, y, yaw=BC.yaw_to(x, y, 0, 0), pose='hang', face='laugh' if i % 2 else 'smug', t=lt, kit='barca', seed=i)
    for i, (x, y) in enumerate([(-0.6, 0.2), (0.7, -0.3)]):
        bean(W, 'p%d' % (6 + i), x, y, yaw=lt * (7 + i * 2), pose='shrug', face='shock', t=lt, kit='white' if False else 'grey', hop=abs(math.sin(lt * 5 + i)) * 0.12, lean=8, seed=i)
    order = [0, 3, 1, 4, 2, 5, 0, 2, 4, 1, 3, 5]; times = [0.3 + k * 0.38 for k in range(len(order))]
    p, seg = pass_path([(R[o][0] * 0.85, R[o][1] * 0.85) for o in order], times, lt, 0.15)
    ball_at(W, 0, p); ball_at(W, 1, None)
    if seg: W.trail.set((seg[0][0], seg[0][1], 0.25), p, 0.05)
    else: W.trail.show(False)
    W.crowd_colors(BARCA, jump=0.22)


def s1(W, lt, u, t, cam):   # total football: everybody plays everywhere (a rotating carousel)
    for i, (x, y) in enumerate(ring(6, 3.2, NX, NY + 4, lt * 0.9)):
        bean(W, 'p%d' % i, x, y, pose='run', face='laugh', t=lt, walk=1.0, run=True, cam=cam, kit='orange', yaw=BC.yaw_to(x, y, NX, NY + 4) + rad(90), seed=i)
    for k in range(4):
        P = W.props.get('mill%d' % k)
        if P: P.parts['hub'].rotation_euler = (0, lt * 0.9 + k, 0)
    ball_at(W, 0, (NX + math.cos(lt * 0.9) * 1.2, NY + 4 + math.sin(lt * 0.9) * 1.2, 0.22)); ball_at(W, 1, None); W.trail.show(False)


def s2(W, lt, u, t, cam):   # the star becomes Barcelona's coach
    swap = lt > 2.25
    if not swap:
        k = min(1.0, lt / 2.0); bean(W, 'n14', lerp(-9.0, -1.0, ease_out(k)), lerp(-4.0, -0.5, ease_out(k)), pose='run' if k < 1 else 'wave', face='laugh', t=lt, walk=1.0 if k < 1 else 0, run=True, cam=cam if k >= 1 else None, yaw=None if k >= 1 else BC.yaw_to(-9, -4, -1, -0.5), kit='orange')
        W.beans['cruyff'].set_visible(False)
    else:
        W.beans['n14'].set_visible(False); W.beans['cruyff'].set_visible(True)
        bean(W, 'cruyff', -1.0, -0.5, pose=keyed([(0, 'present'), (3.0, 'point')], lt - 2.25), face='smug', t=lt, cam=cam)
    for i, (x, y) in enumerate([(1.6, 1.0), (2.8, -0.4), (0.4, 2.2), (-2.6, 1.6)]):
        bean(W, 'p%d' % i, x, y, pose='cheer' if swap else 'clap', face='laugh', t=lt, cam=cam, kit='barca', hop=abs(math.sin(lt * 7 + i)) * (0.3 if swap else 0.05), seed=i)
    if swap and lt < 3.6: W.conf.show(True); W.conf.update(lt - 2.25, (-1.0, -0.5, 0.0), (5, 5), 5.0)
    else: W.conf.show(False)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(BARCA, jump=0.3 if swap else 0.1)


def s3(W, lt, u, t, cam):   # La Masia rondo: keep the ball, pass, move, pass again
    R = ring(6, 2.3, MX, MY - 1.0, 0.3)
    for i, (x, y) in enumerate(R): bean(W, 'k%d' % i, x, y, yaw=BC.yaw_to(x, y, MX, MY - 1.0), pose='hang', face='laugh', t=lt, kit='kid', hop=abs(math.sin(lt * 4 + i)) * 0.05, seed=i)
    bean(W, 'k6', MX + math.sin(lt * 1.5) * 0.6, MY - 1.0 + math.cos(lt * 1.3) * 0.5, yaw=lt * 1.4, pose='run', face='shock', t=lt, walk=0.6, kit='grey', seed=3)
    beats = [20.2, 21.15, 21.6, 22.1, 22.55]; T0 = 16.78; order = [0, 2, 4, 1, 3, 5]
    times = [b - T0 for b in beats] + [beats[-1] - T0 + 0.45]
    p, seg = pass_path([(R[o][0] * 1.0 + (MX - R[o][0]) * 0.12, R[o][1] + (MY - 1.0 - R[o][1]) * 0.12) for o in order], times, lt, 0.1)
    ball_at(W, 0, p); ball_at(W, 1, None)
    if seg: W.trail.set((seg[0][0], seg[0][1], 0.25), p, 0.04)
    else: W.trail.show(False)


def s4(W, lt, u, t, cam):   # the commentator in his booth
    bx, by, bz = BOOTH
    bean(W, 'montes', bx, by + 0.35, yaw=rad(180), z=bz, pose=keyed([(0, 'mic'), (2.6, 'cheer')], lt), face=keyed([(0, 'laugh'), (2.6, 'shock'), (3.4, 'laugh')], lt), t=lt, hat='headset', hop=abs(math.sin(lt * 9)) * 0.08 if lt > 2.6 else 0)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(SPAIN, jump=0.15)


def s4b(W, lt, u, t, cam):  # "tiki, taka!": a pass each way, the words pop out
    A, Bp = (-1.45, 0.0), (1.45, 0.0); T0 = 27.9
    bean(W, 'p0', A[0], A[1], yaw=BC.yaw_to(A[0], A[1], cam[0], cam[1]) * 0.5 + rad(-90) * 0.5, pose='hang', face='laugh', t=lt, kit='barca', legs='kick' if abs(lt - (30.0 - T0 - 0.2)) < 0.3 else None)
    bean(W, 'p1', Bp[0], Bp[1], yaw=BC.yaw_to(Bp[0], Bp[1], cam[0], cam[1]) * 0.5 + rad(90) * 0.5, pose='hang', face='laugh', t=lt, kit='barca', seed=1, legs='kick' if abs(lt - (30.48 - T0 - 0.2)) < 0.3 else None)
    times = [30.0 - T0 - 0.15, 30.48 - T0 - 0.1, 30.48 - T0 + 0.35]
    p, seg = pass_path([(A[0] + 0.5, 0), (Bp[0] - 0.5, 0), (A[0] + 0.5, 0)], times, lt, 0.12); ball_at(W, 0, p); ball_at(W, 1, None)
    if seg: W.trail.set((seg[0][0], seg[0][1], 0.25), p, 0.05)
    else: W.trail.show(False)
    for word, tw, x in (('TIKI!', 30.0 - T0, -0.95), ('TAKA!', 30.48 - T0, 0.95)):
        P = W.props[word]; k = lt - tw; s = back(k / 0.22) if k > 0 else 0.0
        P.root.location = (x, -0.8, 2.45 + (0.35 if x > 0 else 0) + max(0, k) * 0.3); P.root.rotation_euler = (0, rad(-8 if x < 0 else 8), 0); P.root.scale = (max(0.001, s) * 0.62,) * 3
    W.crowd_colors(BARCA, jump=0.3 if lt > 2.0 else 0.12)


def trophies(W, keys, t0, step, lt):
    for i, k in enumerate(keys):
        d = t0 + i * step; s = back((lt - d) / 0.32) if lt > d else 0.0; P = W.props[k]; P.root.scale = (max(0.001, s),) * 3; P.root.rotation_euler = (0, 0, math.sin(lt * 2 + i) * 0.3)


def s5(W, lt, u, t, cam):   # six trophies in one year
    trophies(W, ['tb%d' % i for i in range(6)], 0.55, 0.48, lt)
    for i, x in enumerate([-3.4, -1.7, 0.0, 1.7, 3.4]): bean(W, 'p%d' % i, x, 9.6, pose='cheer', face='laugh', t=lt, cam=cam, kit='barca', hop=abs(math.sin(lt * 7 + i)) * 0.35, seed=i)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(BARCA, jump=0.35)


def s5b(W, lt, u, t, cam):  # Spain: three big tournaments in a row
    trophies(W, ['ts0', 'ts1', 'ts2'], 0.35, 0.6, lt)
    for i, x in enumerate([-3.0, -1.5, 0.0, 1.5, 3.0]): bean(W, 'p%d' % i, x, 9.6, pose='cheer', face='laugh', t=lt, cam=cam, kit='spain', hop=abs(math.sin(lt * 7 + i)) * 0.35, seed=i)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(SPAIN, jump=0.35)


def hold_baby(W, b, mood):
    P = W.props['baby']; P.root.parent = b.body; P.root.location = (0, -0.42, 0.98) if mood != 'away' else (0.05, -0.92, 0.72); P.root.rotation_euler = (rad(-15), 0, rad(8))
    P.parts['smile'].hide_render = P.parts['smile'].hide_viewport = mood == 'sad'
    P.parts['sad'].hide_render = P.parts['sad'].hide_viewport = mood != 'sad'


def s6(W, lt, u, t, cam):   # the proud "father" of tiki-taka
    b = bean(W, 'coach', 0.0, 0.0, pose='baby', face='love', t=lt, cam=cam, look=(0.0, -0.6)); hold_baby(W, b, 'happy')
    for i, (x, y) in enumerate([(-1.6, 1.4), (1.7, 1.2)]): bean(W, 'p%d' % i, x, y, pose='clap', face='laugh', t=lt, cam=cam, kit='barca', seed=i)
    W.conf.show(True); W.conf.recolor(('#ff8fb0', '#ffffff', '#ffd23d')); W.conf.update(lt, (0, 0.6, 0.0), (5, 4), 5.5)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(BARCA, jump=0.12)


def s7(W, lt, u, t, cam):   # plot twist: he hates it
    angry = lt > 0.6
    b = bean(W, 'coach', 0.0, 0.0, pose='baby' if not angry else 'baby', face='angry' if angry else 'smile', t=lt, cam=cam, hop=abs(math.sin(lt * 10)) * 0.05 if angry else 0, look=(0.0, -0.4))
    hold_baby(W, b, 'sad' if angry else 'happy')
    W.beans['coach'].head.rotation_euler = (0, 0, math.sin(lt * 14) * 0.12 if angry else 0)
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.conf.show(False); W.crowd_colors(BARCA, jump=0.05)


def s7b(W, lt, u, t, cam):  # "passing without a purpose is useless": sideways ping-pong, nobody goes forward
    A, Bp = (-2.0, 7.0), (2.0, 7.0)
    bean(W, 'p0', A[0], A[1], yaw=rad(-90), pose='hang', face='flat', t=lt, kit='barca'); bean(W, 'p1', Bp[0], Bp[1], yaw=rad(90), pose='hang', face='flat', t=lt, kit='barca', seed=1)
    k = (lt * 0.8) % 2.0; x = lerp(A[0] + 0.5, Bp[0] - 0.5, k if k < 1 else 2 - k); ball_at(W, 0, (x, 7.0, 0.22)); ball_at(W, 1, None); W.trail.show(False)
    b = bean(W, 'coach', 0.6, 0.6, pose='facepalm', face='sad', t=lt, cam=cam); W.props['baby'].show(False)
    W.crowd_colors(BARCA, jump=0.0)


def s8(W, lt, u, t, cam):   # punchline: holding his "child" at arm's length
    b = bean(W, 'coach', 0.0, 0.0, pose='away', face=keyed([(0, 'flat'), (2.4, 'smug')], lt), t=lt, cam=cam, look=(0.0, -0.3), lean=-6)
    hold_baby(W, b, 'away'); W.props['baby'].show(True); W.props['baby'].parts['sad'].hide_render = False; W.props['baby'].parts['smile'].hide_render = True
    ball_at(W, 0, None); ball_at(W, 1, None); W.trail.show(False); W.crowd_colors(BARCA, jump=0.08)


SHOTS = [
    dict(from_=0, set='stadium', light='night', fx=('rain',), beans=tuple('p%d' % i for i in range(8)), props=(), run=s0, board=0,
         cam=[C(0, (2.5, -9.5, 9.5), (0, 0, 0.3), 24), C(5.6, (-2.0, -11.0, 4.4), (0, 0, 0.7), 24)]),
    dict(from_=1, set='dutch', light='day', beans=tuple('p%d' % i for i in range(6)), props=('flagNl', 'mill0', 'mill1', 'mill2', 'mill3'), run=s1,
         cam=[C(0, (NX + 2.0, NY - 15.0, 0.9), (NX, NY + 4, 1.6), 26), C(6.0, (NX - 1.5, NY - 12.5, 4.6), (NX, NY + 4, 1.0), 26)]),
    dict(from_=2, set='stadium', light='night', beans=('n14', 'cruyff', 'p0', 'p1', 'p2', 'p3'), props=('flagEs', 'flagCat'), run=s2, board=1,
         cam=[C(0, (-6.5, -9.5, 1.7), (-3.5, -1.5, 1.4), 28), C(4.9, (-2.2, -6.4, 1.6), (-0.6, -0.4, 1.4), 30)], dof=((-1.0, -0.5, 1.3), 3.5)),
    dict(from_=3, set='masia', light='golden', beans=tuple('k%d' % i for i in range(7)), props=(), run=s3,
         cam=[C(0, (MX + 0.5, MY - 8.4, 3.8), (MX, MY + 1.0, 0.6), 26), C(6.2, (MX - 2.6, MY - 6.8, 3.0), (MX, MY - 0.4, 0.5), 26)]),
    dict(from_=4, set='stadium', light='booth', beans=('montes',), props=('booth',), run=s4, board=1,
         cam=[C(0, (BOOTH[0] + 1.4, BOOTH[1] + 4.6, BOOTH[2] + 1.9), (BOOTH[0], BOOTH[1] + 0.3, BOOTH[2] + 1.2), 30), C(4.8, (BOOTH[0] + 0.6, BOOTH[1] + 3.2, BOOTH[2] + 1.6), (BOOTH[0], BOOTH[1] + 0.3, BOOTH[2] + 1.25), 34)],
         dof=((BOOTH[0], BOOTH[1] + 0.35, BOOTH[2] + 1.3), 2.8)),
    dict(from_=4, at=27.9, set='stadium', light='night', beans=('p0', 'p1'), props=('TIKI!', 'TAKA!'), run=s4b, board=0,
         cam=[C(0, (0.0, -6.9, 1.35), (0, 0, 1.7), 24), C(3.4, (0.0, -6.2, 1.25), (0, 0, 1.85), 24)]),
    dict(from_=5, set='stadium', light='night', beans=tuple('p%d' % i for i in range(5)), props=('podium',) + tuple('tb%d' % i for i in range(6)) + ('flagCat',), run=s5, conf=('#a50044', '#004d98', '#f6c21c'), board=2,
         cam=[C(0, (0.0, -2.8, 2.3), (0, 8, 1.3), 26), C(3.6, (0.5, -0.2, 1.9), (0, 8, 1.3), 28)]),
    dict(from_=5, at=34.95, set='stadium', light='night', beans=tuple('p%d' % i for i in range(5)), props=('podium', 'ts0', 'ts1', 'ts2', 'flagEs'), run=s5b, conf=('#c8102e', '#f1bf00', '#ffffff'), board=1,
         cam=[C(0, (-0.8, 0.4, 2.0), (0, 8, 1.3), 28), C(2.6, (0.4, 1.8, 1.8), (0, 8, 1.3), 30)]),
    dict(from_=6, set='stadium', light='night', beans=('coach', 'p0', 'p1'), props=('baby',), run=s6, board=3,
         cam=[C(0, (0.2, -5.2, 1.8), (0, 0, 1.5), 30), C(4.3, (0.1, -3.6, 1.7), (0, 0, 1.45), 34)], dof=((0, 0, 1.4), 3.0)),
    dict(from_=7, set='stadium', light='night', fx=('rain',), beans=('coach',), props=('baby',), run=s7, flash=True, board=3,
         cam=[C(0, (0.0, -3.4, 1.65), (0, 0, 1.5), 34), C(4.3, (0.0, -2.7, 1.6), (0, 0, 1.55), 38)], dof=((0, 0, 1.5), 2.8)),
    dict(from_=7, at=46.4, set='stadium', light='night', beans=('coach', 'p0', 'p1'), props=(), run=s7b, board=0,
         cam=[C(0, (1.6, -3.6, 1.5), (0.2, 3.0, 1.3), 26), C(3.1, (1.2, -3.0, 1.5), (0.2, 3.0, 1.3), 28)], dof=((0.6, 0.6, 1.4), 3.5)),
    dict(from_=8, set='stadium', light='night', beans=('coach',), props=('baby',), run=s8, board=3,
         cam=[C(0, (1.4, -4.4, 1.9), (0, -0.3, 1.35), 30), C(6.2, (0.9, -3.4, 1.8), (0, -0.3, 1.4), 34)], dof=((0, -0.6, 1.4), 3.0)),
]
for s in SHOTS: s['from'] = s.pop('from_')


def apply(W, shot, lt, u, t, si):
    W.preset(shot['light']); rt.vintage(W, 0.0)
    W.show(beans=shot.get('beans', ()), props=shot.get('props', ()))
    pos, tgt = W.camera(shot['cam'], lt, si * 1.7, shot.get('dof'))
    f = W.focus[shot['set']]; f.location = (tgt[0] * 0.65 + pos[0] * 0.35, tgt[1] * 0.65 + pos[1] * 0.35, 0)
    W.rain('rain' in shot.get('fx', ()), t)
    if 'conf' in shot:
        W.conf.recolor(shot['conf']); W.conf.show(True); W.conf.update(lt, (tgt[0], tgt[1], 0.0), (10, 6), 7.0)
    else: W.conf.show(False)
    rt.gameboards_page(W, shot.get('board', 0))
    for k in ('flagEs', 'flagCat', 'flagNl'):
        if k in shot.get('props', ()): BP.wave_flag(W.props[k], t)
    shot['run'](W, lt, u, t, pos)
    B.turf_time(t)
    rt.flash(W, max(0.0, 1 - lt / 0.25) if shot.get('flash') else 0.0)
