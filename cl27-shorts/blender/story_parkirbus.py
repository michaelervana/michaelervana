# Parkir Bus / Catenaccio: shots timed to the voice lines in timing.json (line index `from`).
import math
import blib as B, bchar as BC, bprops as BP, rt
from rt import C, ss, ease_out, back, lerp, keyed
from blib import rad

TAIL = 2.1                      # the closing "huss huss huss" plays after the last line
AX, AY = 2000.0, 0.0            # Swiss Alps set
SK = ['#f2c49b', '#e0a87e', '#c98d62', '#8d5a3c', '#f6cfa8']
HR = ['#3a2416', '#1d140f', '#5a3a22', '#2a1a10', '#7a5a3a']
NEUTRAL = ['#d81e2a', '#ffffff', '#1d5fd8', '#f4f4f2']
CHE_TOT = ['#0a47c2', '#ffffff', '#1b2350', '#0a47c2']
ITALY = ['#1d5fd8', '#ffffff', '#009246', '#ce2b37']
INTER = ['#0a3a9e', '#151518', '#ffffff', '#f2c230']
BARCA = ['#a50044', '#004d98', '#f6c21c', '#a50044']


def build(W):
    rt.build_stadium(W, NEUTRAL); rt.build_alps(W, AX, AY)
    rt.build_gameboards(W, 'che_tot')
    c = W.coll
    for i in range(9): W.bean('p%d' % i, kit='white', skin=SK[i % 5], hair=HR[i % 5])
    W.bean('rappan', outfit='oldcoach', coat=True, moustache=True, hat='flatcap', skin='#f6cfa8', hair='#5a3a22')
    W.bean('coach', outfit='coach', coat=True, hat='driver', skin='#e8b48e', hair='#4a3a30')
    W.prop('busred', BP.bus(c, 'busred', '#d81e2a', '#f4f1e8', 'PARKIR BUS', (49.2, 0, 0), rad(90)))
    W.prop('buswhite', BP.bus(c, 'buswhite', '#f2f2ee', '#1b2350', 'PARKIR BUS', (49.2, -30, 0), rad(90)))
    W.prop('businter', BP.bus(c, 'businter', '#0a3a9e', '#151518', 'PARKIR BUS', (49.2, 0, 0), rad(90)))
    W.prop('padlock', BP.padlock(c, 'padlock', (AX, AY + 10.2, 30)))
    W.props['padlock'].root.scale = (1.9, 1.9, 1.9)
    W.prop('door', BP.bolt_door(c, 'door', (52.45, 0, 0), rad(-90)))
    br = W.prop('broom', BP.broom(c)); hand = W.beans['p4'].arm[1][2]; br.root.parent = hand; br.root.location = (0, 0.05, -0.35); br.root.rotation_euler = (rad(25), 0, 0)
    pod = BP.Prop('podium', c, (30, 0, 0)); pod.box('pod', B.toon('podium', '#f4f1e8', spec=0.3), (0, 0, 0.35), (3.2, 1.4, 0.7), bevel=0.06, ink=0.03)
    pod.box('podstripe', B.toon('podgold', '#f2c230', spec=0.6), (0, -0.71, 0.35), (3.2, 0.04, 0.16), ink=0); W.prop('podium', pod)
    W.prop('t1', BP.trophy(c, 't1', 'bigears', (29.2, 0, 0.7))); W.prop('t2', BP.trophy(c, 't2', 'bigears', (30.8, 0, 0.7)))
    W.prop('psign', BP.parking_sign(c, 'psign', (44.2, 7.4, 0), rad(-20)))
    W.prop('screen', BP.big_screen(c, 'screen', '0 - 0', (63.5, 0, 9.0), rad(-90)))
    W.prop('board', BP.chalkboard(c, 'board', (AX - 3.3, AY + 2.6, 0), rad(18)))
    og = BP.mini_goal(c, 'oldgoal', (AX, AY + 10.2, 0), 0.0); og.root.scale = (2.4, 2.4, 2.4); W.prop('oldgoal', og)
    W.prop('flagIt1', BP.flag(c, 'flagIt1', 'italy', (47.5, -7.5, 0), rad(-90))); W.prop('flagIt2', BP.flag(c, 'flagIt2', 'italy', (47.5, 7.5, 0), rad(-90)))
    W.prop('flagCh', BP.flag(c, 'flagCh', 'swiss', (AX + 6.5, AY + 8.0, 0), rad(180)))
    W.prop('flagInter', BP.flag(c, 'flagInter', 'inter', (27.2, 1.6, 0), rad(180)))
    W.balls = [BP.ball(c, 'ball%d' % i) for i in range(3)]
    W.rain_rig()


def bean(W, k, x, y, yaw=None, pose='hang', face='smile', t=0.0, walk=0.0, run=False, hop=0.0, z=0.0, kit=None, look=(0, 0), lean=0.0, legs=None, cam=None, hat=None, seed=0.0):
    b = W.beans[k]
    if kit: b.set_kit(kit)
    if yaw is None: yaw = BC.yaw_to(x, y, cam[0], cam[1]) if cam else 0.0
    b.place(x, y, yaw, z, hop, t + seed, walk, run, lean); b.pose(pose, t + seed, walk, run, legs=legs); b.face(face); b.hat(hat)
    b.look(look[0], look[1], blink=((t + seed * 1.7) % 3.3) < 0.11)
    return b


def balls(W, pos):
    for i, bl in enumerate(W.balls):
        if i < len(pos) and pos[i] is not None: bl.hide_render = bl.hide_viewport = False; bl.location = pos[i]; bl.rotation_euler = (pos[i][0] * 3, pos[i][1] * 3, 0)
        else: bl.hide_render = bl.hide_viewport = True


# ---------------- shot bodies ----------------
def s0(W, lt, u, t, cam):   # hook: a bus parked across the goal, attackers bounce off it
    for i, (y0, dl) in enumerate([(-3.2, 0.0), (0.4, 0.35), (3.4, 0.7)]):
        k = (lt - dl) % 2.2; run = k < 1.1; x = 41.5 + (ease_out(k / 1.1) * 4.6 if run else 4.6 - ease_out((k - 1.1) / 1.1) * 3.0)
        bean(W, 'p%d' % i, x, y0, yaw=rad(-90) if run else rad(-90), pose='run' if run else 'shrug', face='shock' if not run else 'angry', t=lt, walk=1.0 if run else 0.0, run=run,
             hop=0.0 if run else abs(math.sin((k - 1.1) * 4)) * 0.35, lean=-12 if not run else 8, kit='white', seed=i)
    W.crowd_colors(NEUTRAL, jump=0.25)


def s1(W, lt, u, t, cam):   # 1930s Switzerland: Rappan and his verrou
    W.props['padlock'].root.location = (AX, AY + 10.25, 30.0)
    bean(W, 'rappan', AX - 1.9, AY + 2.2, pose=keyed([(0, 'hang'), (1.0, 'point'), (3.0, 'think')], lt), face=keyed([(0, 'smile'), (3.0, 'smug')], lt), t=lt, cam=cam, hat='flatcap')
    for i in range(4):
        x = AX - 3.0 + i * 2.0; bean(W, 'p%d' % i, x, AY + 7.2, pose='cross' if lt > 2.0 + i * 0.2 else 'hang', face='smug' if lt > 2.2 else 'smile', t=lt, cam=cam, kit='swiss', seed=i * 0.7)


def s1b(W, lt, u, t, cam):  # "artinya gembok": a giant padlock slams onto the goal
    k = (lt - 0.9) / 0.65; z = 14.0 - 12.1 * min(1.0, max(0.0, k)) ** 2 if k < 1 else 1.9 + abs(math.sin((lt - 1.55) * 9)) * 0.25 * max(0.0, 1 - (lt - 1.55) * 2.5)
    W.props['padlock'].root.location = (AX, AY + 10.25, z); W.props['padlock'].root.rotation_euler = (0, rad(math.sin(lt * 3) * 4), 0)
    landed = lt > 1.55
    for i in range(4):
        x = AX - 3.0 + i * 2.0; bean(W, 'p%d' % i, x, AY + 7.2, pose='cheer' if landed else 'hang', face='laugh' if landed else 'shock', t=lt, cam=cam, kit='swiss', hop=abs(math.sin(lt * 8 + i)) * 0.3 if landed else 0, seed=i)
    bean(W, 'rappan', AX - 4.8, AY + 4.0, pose='pointup' if not landed else 'cheer', face='laugh', t=lt, cam=cam, hat='flatcap')


def s2(W, lt, u, t, cam):   # Italy: catenaccio = the door bolt
    slide = ease_out((lt - 4.3) / 0.35); W.props['door'].parts['bolt'].location.x = 1.1 * (1 - slide)
    bean(W, 'p0', 51.75, -1.75, pose='hold' if lt < 4.6 else 'cheer', face='smug' if lt < 4.6 else 'laugh', t=lt, cam=cam, kit='italy', hop=0.25 * abs(math.sin(lt * 8)) if lt > 4.7 else 0)
    W.crowd_colors(ITALY, jump=0.12 + 0.2 * slide)


def s3(W, lt, u, t, cam):   # the libero sweeps every loose ball away
    W.props['door'].parts['bolt'].location.x = 1.1
    for i, y in enumerate([-4.5, -1.5, 1.5, 4.5]): bean(W, 'p%d' % i, 44.0, y, yaw=rad(-90), pose='cross', face='smug', t=lt, kit='italy', seed=i)
    sweep = lt > 3.3
    bean(W, 'p4', 48.2, 0.2 + math.sin(lt * 2) * 0.4, yaw=rad(-90) + (math.sin(lt * 6) * 0.35 if sweep else 0), pose='sweep', face='laugh' if sweep else 'smile', t=lt, kit='italy')
    for i, y in enumerate([-3.0, 0.5, 3.5]):
        bean(W, 'p%d' % (5 + i), 35.5 + min(lt, 1.0) * 1.2, y, yaw=rad(-90), pose='run' if lt < 1.0 else ('facepalm' if sweep else 'shrug'), face='angry' if not sweep else 'shock', t=lt, walk=1.0 if lt < 1.0 else 0, run=True, legs='kick' if 0.6 < lt < 1.2 else None, kit='red', seed=i * 0.5)
    pos = []
    for i, y in enumerate([-2.2, 0.6, 2.6]):
        k0 = 0.9 + i * 0.35; k = lt - k0
        if k < 0: pos.append((37.4, y, 0.22)); continue
        if lt < 3.3 + i * 0.25: pos.append((37.4 + min(k / 2.2, 1.0) * 10.0, y + min(k / 2.2, 1.0) * (0.2 - y) * 0.6, 0.22)); continue
        kk = lt - (3.3 + i * 0.25); pos.append((47.4 - kk * 9.0, y * 0.4 + (y * 0.6) * min(1, kk) + kk * (i - 1) * 2.0, 0.22 + max(0.0, math.sin(min(kk, 1.2) * math.pi / 1.2)) * 3.0))
    balls(W, pos)
    W.crowd_colors(ITALY, jump=0.15)


def s4(W, lt, u, t, cam):   # Inter, two European Cups in a row
    for k, (tk, dl) in enumerate([('t1', 3.6), ('t2', 4.35)]):
        s = back((lt - dl) / 0.35) if lt > dl else 0.0; W.props[tk].root.scale = (max(0.001, s),) * 3; W.props[tk].root.rotation_euler = (0, 0, lt * 0.8 + k)
    for i, (x, y) in enumerate([(28.0, -1.6), (29.4, -2.1), (30.6, -2.1), (32.0, -1.6), (30.0, 1.6)]):
        bean(W, 'p%d' % i, x, y, pose='cheer' if lt > 3.7 else 'clap', face='laugh', t=lt, cam=cam, kit='inter', hop=abs(math.sin(lt * 7 + i)) * (0.35 if lt > 3.7 else 0.1), seed=i)
    W.crowd_colors(INTER, jump=0.3 if lt > 3.7 else 0.15)


def s5(W, lt, u, t, cam):   # 2004, 0-0: the coach fumes on the touchline
    bean(W, 'coach', 24.0, -33.6, pose=keyed([(0, 'cross'), (1.2, 'shout'), (2.6, 'point')], lt), face=keyed([(0, 'flat'), (1.2, 'angry')], lt), t=lt, cam=cam, hat=None)
    for i, (x, y) in enumerate([(30.0, -27.5), (31.6, -26.5)]): bean(W, 'p%d' % i, x, y, pose='facepalm', face='sad', t=lt, cam=cam, kit='blue', seed=i)
    for i, y in enumerate([-4.5, -1.5, 1.5, 4.5]): bean(W, 'p%d' % (2 + i), 50.6, y, yaw=rad(-90), pose='cross', face='smug', t=lt, kit='white', seed=i * 0.3)
    W.crowd_colors(CHE_TOT, jump=0.08)


def s5b(W, lt, u, t, cam):  # "...parkir bus di depan gawang!": the bus drives in and parks
    k = ss((lt - 0.2) / 1.9); bus = W.props['buswhite']; bus.root.location = (49.2, lerp(-34.0, 0.0, k), 0); bus.root.rotation_euler = (0, 0, rad(90))
    bus.root.location.z = abs(math.sin(lt * 9)) * 0.03 * (1 - k)
    bean(W, 'coach', 38.5, -5.5, pose='facepalm' if lt > 2.2 else 'point', face='angry' if lt < 2.2 else 'shock', t=lt, cam=cam)
    for i, y in enumerate([-6.8, 6.4]): bean(W, 'p%d' % (2 + i), 47.0, y, pose='cheer' if lt > 2.2 else 'hang', face='laugh', t=lt, cam=cam, kit='white', hop=abs(math.sin(lt * 8 + i)) * 0.3 if lt > 2.2 else 0)
    W.crowd_colors(CHE_TOT, jump=0.25 if lt > 2.2 else 0.1)


def s6(W, lt, u, t, cam):   # a parking sign pops up next to the bus
    W.props['buswhite'].root.location = (49.2, 0.0, 0.0); W.props['buswhite'].root.rotation_euler = (0, 0, rad(90))
    s = back((lt - 2.9) / 0.4) if lt > 2.9 else 0.0; P = W.props['psign']; P.root.scale = (1, 1, max(0.001, s)); P.root.rotation_euler = (0, 0, rad(-20) + math.sin(max(0, lt - 2.9) * 10) * 0.12 * max(0, 1 - (lt - 2.9)))
    for i, y in enumerate([-6.8, 6.4]): bean(W, 'p%d' % (2 + i), 47.0, y, pose='cheer' if lt > 3.0 else 'hip', face='laugh' if lt > 3.0 else 'smug', t=lt, cam=cam, kit='white', hop=abs(math.sin(lt * 8 + i)) * 0.25 if lt > 3.0 else 0)
    W.crowd_colors(CHE_TOT, jump=0.3 if lt > 3.0 else 0.1)


def s7(W, lt, u, t, cam):   # 2010, Camp Nou: Inter park the bus, the coach on its roof
    for i, y in enumerate([-6.0, -3.6, -1.2, 1.2, 3.6, 6.0]): bean(W, 'p%d' % i, 45.6, y, yaw=rad(-90), pose='cross', face='smug', t=lt, kit='inter', seed=i * 0.4)
    for i, y in enumerate([-2.4, 0.3, 2.8]):
        k = (lt - i * 0.45) % 2.0; run = k < 1.0; x = 38.0 + (ease_out(k) * 6.2 if run else 6.2 - ease_out(k - 1.0) * 4.0)
        bean(W, 'p%d' % (6 + i), x, y, yaw=rad(-90), pose='run' if run else 'shrug', face='angry' if run else 'shock', t=lt, walk=1.0 if run else 0, run=run, kit='barca', hop=0 if run else abs(math.sin((k - 1) * 5)) * 0.3, seed=i)
    bean(W, 'coach', 49.2, 0.0, yaw=rad(-90), z=4.36, pose='cross', face='smug', t=lt, hat=None)
    W.crowd_colors(BARCA, jump=0.06)


def s8(W, lt, u, t, cam):   # punchline: he is the bus driver
    honk = 2.3 < lt < 2.75 or 3.0 < lt < 3.4
    bus = W.props['businter']
    for key in ('hl-1', 'hl1'): bus.parts[key].scale = (1.6, 1.6, 1.6) if honk else (1, 1, 1)
    bean(W, 'coach', 49.75, 3.85, yaw=rad(180), z=0.42, pose='drive', face='laugh' if honk else 'smug', t=lt, legs='sit', hat='driver', look=(0.0, 0.2))
    W.crowd_colors(BARCA, jump=0.1)


SHOTS = [
    dict(from_=0, set='stadium', light='night', fx=('rain',), beans=('p0', 'p1', 'p2'), props=('busred',), run=s0, board=0,
         cam=[C(0, (24, -30, 26), (47, 0, 2), 24), C(4.5, (40.6, -6.4, 0.75), (48.6, 0.6, 2.3), 26)], dof=((49, 0, 1.5), 4.0)),
    dict(from_=1, set='alps', light='vintage', vintage=0.42, beans=('rappan', 'p0', 'p1', 'p2', 'p3'), props=('board', 'oldgoal', 'flagCh'), run=s1,
         cam=[C(0, (AX + 1.2, AY - 8.5, 2.6), (AX - 0.6, AY + 5, 1.7), 28), C(5.2, (AX - 1.2, AY - 3.2, 1.9), (AX - 2.2, AY + 2.4, 1.6), 33)], dof=((AX - 1.9, AY + 2.2, 1.5), 2.8)),
    dict(from_=1, at=9.75, set='alps', light='vintage', vintage=0.42, beans=('rappan', 'p0', 'p1', 'p2', 'p3'), props=('padlock', 'oldgoal', 'flagCh'), run=s1b,
         cam=[C(0, (AX + 2.0, AY - 3.5, 0.9), (AX, AY + 10, 3.0), 24), C(2.3, (AX + 0.8, AY - 2.2, 1.0), (AX, AY + 10, 2.7), 26)]),
    dict(from_=2, set='stadium', light='night', beans=('p0',), props=('door', 'flagIt1', 'flagIt2'), run=s2, board=3,
         cam=[C(0, (42.5, -7.5, 1.6), (52.3, 0, 1.4), 26), C(5.8, (47.3, -3.2, 1.55), (52.2, 0.2, 1.3), 30)], dof=((51.8, -1.7, 1.2), 3.5)),
    dict(from_=3, set='stadium', light='night', fx=('rain',), beans=('p0', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7'), props=('broom',), run=s3, board=0,
         cam=[C(0, (57.5, -6.5, 7.0), (43.0, 0, 0.6), 26), C(3.1, (54.5, -5.5, 3.2), (46.0, 0, 0.8), 28), C(5.4, (51.8, -3.2, 1.6), (48.2, 0.2, 1.0), 30)]),
    dict(from_=4, set='stadium', light='night', beans=('p0', 'p1', 'p2', 'p3', 'p4'), props=('podium', 't1', 't2', 'flagInter'), run=s4, conf=('#0a3a9e', '#151518', '#f2c230'), board=1,
         cam=[C(0, (23.5, -6.5, 0.9), (30, 0, 1.6), 24), C(5.9, (25.6, -3.6, 1.25), (30, 0, 1.5), 28)], dof=((30, -1.5, 1.2), 4.0)),
    dict(from_=5, set='stadium', light='night', beans=('coach', 'p0', 'p1', 'p2', 'p3', 'p4', 'p5'), props=(), run=s5, board=2,
         cam=[C(0, (20.6, -30.0, 1.7), (24.0, -33.0, 1.5), 30), C(3.9, (12.0, -24.0, 2.0), (52.0, -2.0, 18.0), 24)]),
    dict(from_=5, at=33.6, set='stadium', light='night', beans=('coach', 'p2', 'p3'), props=('buswhite',), run=s5b, board=2,
         cam=[C(0, (33.0, -12.5, 1.6), (48.0, -3.0, 2.4), 22), C(2.9, (35.2, -9.6, 1.5), (48.5, -0.5, 2.3), 24)]),
    dict(from_=6, set='stadium', light='night', fx=('rain',), beans=('p2', 'p3'), props=('buswhite', 'psign'), run=s6, board=0,
         cam=[C(0, (38.6, -4.2, 2.0), (47.5, 1.8, 2.6), 26), C(4.0, (40.4, 0.6, 2.4), (45.0, 6.4, 3.0), 30)], dof=((44.2, 7.4, 3.0), 4.5)),
    dict(from_=7, set='stadium', light='night', fx=('rain',), beans=('coach', 'p0', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'), props=('businter',), run=s7, flash=True, board=1,
         cam=[C(0, (18, -26, 15), (48, 0, 2.0), 24), C(4.5, (34.5, -11.5, 2.6), (48.5, 0, 3.0), 26), C(7.1, (39.0, -6.8, 2.2), (49.0, 0, 3.6), 28)]),
    dict(from_=8, set='stadium', light='night', fx=('rain',), beans=('coach',), props=('businter',), run=s8,
         cam=[C(0, (49.8, 9.0, 2.15), (49.75, 3.9, 1.7), 30), C(5.6, (49.78, 6.8, 2.0), (49.75, 3.9, 1.65), 36)], dof=((49.75, 3.85, 1.6), 3.2)),
]
for s in SHOTS: s['from'] = s.pop('from_')


def apply(W, shot, lt, u, t, si):
    W.preset(shot['light']); rt.vintage(W, shot.get('vintage', 0.0))
    W.show(beans=shot.get('beans', ()), props=shot.get('props', ()))
    pos, tgt = W.camera(shot['cam'], lt, si * 1.7, shot.get('dof'))
    f = W.focus[shot['set']]; f.location = (tgt[0] * 0.65 + pos[0] * 0.35, tgt[1] * 0.65 + pos[1] * 0.35, 0)
    W.rain('rain' in shot.get('fx', ()), t)
    if 'conf' in shot:
        W.conf.recolor(shot['conf']); W.conf.show(True); W.conf.update(lt, (tgt[0], tgt[1], 0.0), (10, 8), 7.0)
    else: W.conf.show(False)
    rt.gameboards_page(W, shot.get('board', 0))
    for k in ('flagIt1', 'flagIt2', 'flagCh', 'flagInter'):
        if k in shot.get('props', ()): BP.wave_flag(W.props[k], t)
    balls(W, [])
    shot['run'](W, lt, u, t, pos)
    B.turf_time(t)
    rt.flash(W, max(0.0, 1 - lt / 0.25) if shot.get('flash') else 0.0)
