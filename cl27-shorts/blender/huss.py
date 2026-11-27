# HUSS gag clip (2.2 s, 30 fps) rendered with a transparent background: blender -b -y --python huss.py -- <kit> <outdir>
import sys, os, math
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import blib as B, bchar as BC, bprops as BP, rt
from blib import rad
kit, out = sys.argv[sys.argv.index('--') + 1:][:2]
sc = B.reset(scale=100, samples=8); sc.render.resolution_x, sc.render.resolution_y = 560, 900
sc.render.film_transparent = True; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
sc.eevee.use_ssr = False; sc.eevee.use_bloom = False
c = B.coll('h'); W = rt.World(sc); W.coll = c
sun = W.add_sun('sun', 3.2, (1, 0.97, 0.92), (rad(50), rad(15), rad(-30)))
b = W.bean('h', kit=kit, skin='#f2c49b', hair='#3a2416'); b.set_visible(True)
ballo = BP.ball(c, 'hb', 0.2)
words = []
for k in range(3):
    P = BP.Prop('w%d' % k, c); P.text('t', 'HUSS!', B.toon('popyellow', '#ffd23d', spec=0.4, emit=0.35), (0, 0, 0), rot=(rad(90), 0, 0), size=0.56, extrude=0.08, ink=0.026); words.append(P)
cam = W.cam; cam.data.lens = 46; B.look_at(cam, (0.0, -6.4, 1.5), (0.12, 0, 1.3))
for f in range(66):
    t = f / 30.0
    pop = rt.ease_out(t / 0.25) * (1 - rt.ease_out((t - 1.9) / 0.3))
    beat = (t * 1.35) % 1; bounce = abs(math.sin(t * math.pi * 2.6))
    b.root.scale = (max(0.001, pop),) * 3
    b.place(-0.25, 0, rad(12), 0, bounce * 0.12, t, 0, False); b.pose('hold' if beat < 0.5 else 'cheer', t, legs='kick' if beat < 0.2 else None)
    b.face('laugh' if beat < 0.5 else 'smug'); b.look(0.3, -0.2, False)
    ballo.location = (0.45 * pop, -0.25, (0.2 + (1 - bounce) * 0.75) * pop); ballo.scale = (max(0.001, pop),) * 3; ballo.rotation_euler = (t * 9, t * 4, 0)
    for k, (d, P) in enumerate(zip((0.05, 0.75, 1.45), words)):
        a = t - d; s = rt.back(a / 0.18) * (1 - rt.ease_out((a - 0.42) / 0.18)) if 0 <= a <= 0.6 else 0.0
        P.root.location = (0.32 - k * 0.1, -0.6, 2.0 + k * 0.12); P.root.rotation_euler = (0, rad(-8 + k * 6), 0); P.root.scale = (max(0.001, s),) * 3
    sc.render.filepath = os.path.join(out, 'h%03d.png' % f); B.bpy.ops.render.render(write_still=True)
print('HUSS DONE', kit)
