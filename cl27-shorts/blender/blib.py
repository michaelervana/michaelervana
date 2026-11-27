# Shared Blender helpers for the 3D cartoon shorts: toon materials, ink outlines, the Night Cup stadium, crowd,
# lights, render + compositor setup. Run inside Blender 4.0 (Eevee), e.g. xvfb-run blender -b -y --python story.py
import bpy, bmesh, math, os, json, random
import numpy as np
from mathutils import Vector, Euler, Matrix, Quaternion
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(ROOT, 'assets')
D = bpy.data
rad = math.radians
W, H = 1080, 1920


def reset(scale=75, samples=4):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, scale
    sc.render.fps = 30
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 93
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    sc.view_settings.exposure = -0.5; sc.view_settings.gamma = 1   # post.py restores +0.5 EV; only light sources clip, so only they bloom
    e = sc.eevee
    e.taa_render_samples = samples; e.use_bloom = True; e.bloom_threshold = 1.0; e.bloom_intensity = 0.06; e.bloom_radius = 5.5
    e.use_ssr = True; e.use_ssr_halfres = True; e.ssr_quality = 0.4; e.ssr_max_roughness = 0.35; e.ssr_thickness = 0.4
    e.use_gtao = False; e.use_soft_shadows = True; e.shadow_cube_size = '512'; e.shadow_cascade_size = '2048'
    e.use_shadow_high_bitdepth = True; e.use_motion_blur = False; e.use_volumetric_lights = False
    e.light_threshold = 0.01
    w = D.worlds.new('world'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.006, 0.010, 0.030, 1); bg.inputs['Strength'].default_value = 1
    return sc


def coll(name, parent=None):
    c = D.collections.get(name)
    if not c:
        c = D.collections.new(name); (parent or bpy.context.scene.collection).children.link(c)
    return c


# ---------------- materials ----------------
_mat = {}
def ink_mat():
    if 'ink' in _mat: return _mat['ink']
    m = D.materials.new('ink'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (0.018, 0.008, 0.02, 1)
    o = N.new('ShaderNodeOutputMaterial'); L.new(e.outputs[0], o.inputs[0])
    m.use_backface_culling = True; m.shadow_method = 'NONE'; _mat['ink'] = m; return m


def _hex(c):
    if isinstance(c, str):
        c = c.lstrip('#'); r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
        f = lambda x: x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
        return (f(r), f(g), f(b), 1)
    return tuple(c) + ((1,) if len(c) == 3 else ())


def toon(name, col='#ffffff', emit=0.0, tex=None, tex_scale=(1, 1, 1), tex_coord='UV', spec=0.22, wet=0.0, stripes=None,
         shadow=(0.42, 0.40, 0.56), attr=None, alpha_tex=None, puddles=0.0):
    """Cel-shaded material: diffuse light -> 3-step ramp -> x base colour, plus a hard specular dot; emission output.
    wet adds a glossy reflection (screen-space) masked by puddles; stripes = (colB, freq, axis)."""
    if name in _mat: return _mat[name]
    m = D.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial')
    base = N.new('ShaderNodeRGB'); base.outputs[0].default_value = _hex(col); bcol = base.outputs[0]
    if stripes:
        colB, freq, axis = stripes
        tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
        mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = freq; L.new(sep.outputs['XYZ'.index(axis)], mu.inputs[0])
        fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(mu.outputs[0], fr.inputs[0])
        gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.5; L.new(fr.outputs[0], gt.inputs[0])
        mx = N.new('ShaderNodeMixRGB'); L.new(gt.outputs[0], mx.inputs[0]); mx.inputs[1].default_value = _hex(col); mx.inputs[2].default_value = _hex(colB); bcol = mx.outputs[0]
    if attr:  # per-instance colour from geometry nodes
        at = N.new('ShaderNodeAttribute'); at.attribute_type = 'INSTANCER'; at.attribute_name = attr; bcol = at.outputs['Color']
    if tex:
        img = D.images.load(tex, check_existing=True)
        ti = N.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Linear'
        if tex_coord != 'UV' or tex_scale != (1, 1, 1):
            tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = tex_scale
            L.new(tc.outputs[tex_coord], mp.inputs[0]); L.new(mp.outputs[0], ti.inputs[0])
        mm = N.new('ShaderNodeMixRGB'); mm.blend_type = 'MULTIPLY'; mm.inputs[0].default_value = 1
        L.new(bcol, mm.inputs[1]); L.new(ti.outputs['Color'], mm.inputs[2]); bcol = mm.outputs[0]
    diff = N.new('ShaderNodeBsdfDiffuse'); diff.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N.new('ShaderNodeShaderToRGB'); L.new(diff.outputs[0], s2r.inputs[0])
    bw = N.new('ShaderNodeRGBToBW'); L.new(s2r.outputs['Color'], bw.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp; cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0.0; cr.elements[0].color = shadow + (1,)
    cr.elements[1].position = 0.09; cr.elements[1].color = (0.74, 0.72, 0.80, 1)
    e3 = cr.elements.new(0.34); e3.color = (1, 1, 1, 1)
    e4 = cr.elements.new(0.85); e4.color = (1.12, 1.1, 1.06, 1)
    L.new(bw.outputs[0], ramp.inputs[0])
    mul = N.new('ShaderNodeMixRGB'); mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
    L.new(bcol, mul.inputs[1]); L.new(ramp.outputs[0], mul.inputs[2]); colr = mul.outputs[0]
    if spec > 0:
        gl = N.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.32
        s2 = N.new('ShaderNodeShaderToRGB'); L.new(gl.outputs[0], s2.inputs[0]); b2 = N.new('ShaderNodeRGBToBW'); L.new(s2.outputs['Color'], b2.inputs[0])
        r2 = N.new('ShaderNodeValToRGB'); c2 = r2.color_ramp; c2.interpolation = 'CONSTANT'; c2.elements[0].color = (0, 0, 0, 1)
        c2.elements[1].position = 0.55; c2.elements[1].color = (spec, spec, spec, 1); L.new(b2.outputs[0], r2.inputs[0])
        ad = N.new('ShaderNodeMixRGB'); ad.blend_type = 'ADD'; ad.inputs[0].default_value = 1; L.new(colr, ad.inputs[1]); L.new(r2.outputs[0], ad.inputs[2]); colr = ad.outputs[0]
    em = N.new('ShaderNodeEmission'); L.new(colr, em.inputs['Color']); em.inputs['Strength'].default_value = 1 + emit
    sh = em.outputs[0]
    if wet > 0:
        g2 = N.new('ShaderNodeBsdfGlossy'); g2.inputs['Roughness'].default_value = 0.04; g2.inputs['Color'].default_value = (wet, wet, wet, 1)
        fac = None
        if puddles > 0:
            tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.09; nz.inputs['Detail'].default_value = 3
            L.new(tc.outputs['Object'], nz.inputs['Vector'])
            pr = N.new('ShaderNodeValToRGB'); pr.color_ramp.elements[0].position = 0.5; pr.color_ramp.elements[1].position = 0.56; L.new(nz.outputs['Fac'], pr.inputs[0])
            mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'; mx.inputs[1].default_value = 1 - puddles; L.new(pr.outputs[0], mx.inputs[0]); fac = mx.outputs[0]
        ms = N.new('ShaderNodeAddShader')
        if fac is not None:
            mz = N.new('ShaderNodeMixShader'); tr = N.new('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (0, 0, 0, 1)
            L.new(fac, mz.inputs[0]); L.new(tr.outputs[0], mz.inputs[1]); L.new(g2.outputs[0], mz.inputs[2]); L.new(sh, ms.inputs[0]); L.new(mz.outputs[0], ms.inputs[1])
        else:
            L.new(sh, ms.inputs[0]); L.new(g2.outputs[0], ms.inputs[1])
        sh = ms.outputs[0]
    if alpha_tex:
        img = D.images.load(alpha_tex, check_existing=True); ti = N.new('ShaderNodeTexImage'); ti.image = img
        tr = N.new('ShaderNodeBsdfTransparent'); mz = N.new('ShaderNodeMixShader'); L.new(ti.outputs['Alpha'], mz.inputs[0]); L.new(tr.outputs[0], mz.inputs[1]); L.new(sh, mz.inputs[2]); sh = mz.outputs[0]
        m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'; m.alpha_threshold = 0.5
    L.new(sh, out.inputs['Surface'])
    _mat[name] = m; return m


def glow(name, col, strength=4.0):
    if name in _mat: return _mat[name]
    m = D.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = _hex(col); e.inputs['Strength'].default_value = strength
    o = N.new('ShaderNodeOutputMaterial'); L.new(e.outputs[0], o.inputs[0]); m.shadow_method = 'NONE'; _mat[name] = m; return m


def outline(ob, width=0.018):
    """Inverted-hull ink line: solidify outward, flipped normals, ink material with backface culling."""
    if ob.type != 'MESH' and ob.type not in ('CURVE', 'FONT'): return
    mats = ob.data.materials
    if ink_mat().name not in [m.name for m in mats if m]: mats.append(ink_mat())
    idx = [m.name if m else '' for m in mats].index('ink')
    s = ob.modifiers.new('ink', 'SOLIDIFY'); s.thickness = width; s.offset = 1; s.use_flip_normals = True; s.use_rim = False
    s.material_offset = idx; s.use_quality_normals = False
    return s


def link(ob, c=None):
    (c or bpy.context.scene.collection).objects.link(ob); return ob


def mesh_obj(name, verts, faces, mat=None, c=None, smooth=False):
    me = D.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    ob = D.objects.new(name, me); link(ob, c)
    if mat: me.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob


def prim(kind, name, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), c=None, ink=0.018, parent=None, seg=24, smooth=True, size=None, shift=None, **kw):
    """Primitive mesh built with bmesh (no operators, so it is fast and works in background)."""
    me = D.meshes.new(name); bm = bmesh.new()
    if kind == 'sphere': bm.loops.layers.uv.new('UVMap'); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=kw.get('r', 1), calc_uvs=True)
    elif kind == 'ico': bmesh.ops.create_icosphere(bm, subdivisions=kw.get('sub', 2), radius=kw.get('r', 1))
    elif kind == 'cyl': bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=kw.get('r', 1), radius2=kw.get('r2', kw.get('r', 1)), depth=kw.get('h', 1))
    elif kind == 'cone': bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=kw.get('r', 1), radius2=kw.get('r2', 0), depth=kw.get('h', 1))
    elif kind == 'box': bmesh.ops.create_cube(bm, size=1)
    elif kind == 'torus':
        R, r, a0, a1 = kw.get('R', 1), kw.get('r', 0.2), kw.get('a0', 0), kw.get('a1', 2 * math.pi); n, m = seg, 10; vs = []
        full = abs(a1 - a0 - 2 * math.pi) < 1e-6; cnt = n if full else n + 1
        for i in range(cnt):
            a = a0 + (a1 - a0) * i / n
            for j in range(m):
                b = 2 * math.pi * j / m; vs.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        for i in range(n):
            for j in range(m):
                i2 = (i + 1) % cnt; a, b2, c2, d = vs[i * m + j], vs[i * m + (j + 1) % m], vs[i2 * m + (j + 1) % m], vs[i2 * m + j]; bm.faces.new((a, b2, c2, d))
        if not full:
            for i in (0, n): bm.faces.new([vs[i * m + j] for j in range(m)][::(1 if i else -1)])
    elif kind == 'lathe':
        prof = kw['prof']; n = seg; rings = []
        for i in range(n):
            a = 2 * math.pi * i / n; rings.append([bm.verts.new((x * math.cos(a), x * math.sin(a), z)) for x, z in prof])
        for i in range(n):
            r0, r1 = rings[i], rings[(i + 1) % n]
            for k in range(len(prof) - 1): bm.faces.new((r0[k], r1[k], r1[k + 1], r0[k + 1]))
    if size: bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if shift: bmesh.ops.translate(bm, vec=Vector(shift), verts=bm.verts)
    bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    ob = D.objects.new(name, me); link(ob, c)
    if mat: me.materials.append(mat)
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    if parent: ob.parent = parent
    if ink: outline(ob, ink)
    return ob


def empty(name, loc=(0, 0, 0), parent=None, c=None, rot=(0, 0, 0)):
    e = D.objects.new(name, None); link(e, c); e.location = loc; e.rotation_euler = rot
    if parent: e.parent = parent
    return e


def text3d(name, body, mat, size=1.0, extrude=0.08, bevel=0.015, c=None, font=None, align='CENTER', ink=0.03):
    cu = D.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 2
    cu.align_x = align; cu.align_y = 'CENTER'
    if font: cu.font = D.fonts.load(font, check_existing=True)
    ob = D.objects.new(name, cu); link(ob, c); cu.materials.append(mat)
    if ink: outline(ob, ink)
    return ob


# ---------------- Night Cup stadium ----------------
RECOLOR = {'Material.009': '#0b1a55', 'Material.053': '#0b1a55', 'Material.058': '#0b1a55', 'Material.007': '#1e44b8', 'Material.054': '#1e44b8',
           'Material.055': '#142a78', 'Material.001': '#2a2b36', 'Material.060': '#30323e', 'Material.047': '#2a2b36', 'Material.013': '#c9ced8',
           'Material.043': '#dfe3ea', 'Material.015': '#dfe3ea', 'Material.014': '#8a90a0', 'Material.003': '#8a90a0', 'CC-06.008': '#6a7080',
           'Material.044': '#1440c0', 'Material.056': '#fff6e8', 'Material.057': '#d05a6a'}


def stadium(c):
    z = np.load(os.path.join(ASSET, 'stadium.npz')); head = json.load(open(os.path.join(ASSET, 'stadium_head.json')))
    P, I = z['P'], z['I']; nt = len(I) // 3
    me = D.meshes.new('stadium'); me.vertices.add(len(P)); me.vertices.foreach_set('co', P.ravel())
    me.loops.add(len(I)); me.loops.foreach_set('vertex_index', I)
    me.polygons.add(nt); me.polygons.foreach_set('loop_start', np.arange(0, len(I), 3, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(nt, 3, np.int32))
    mi = np.zeros(nt, np.int32)
    for k, g in enumerate(head['groups']):
        mi[g['i0'] // 3:(g['i0'] + g['ni']) // 3] = k
        col = RECOLOR.get(g['name']) or tuple(g['color'])
        m = toon('st_' + g['name'], col, spec=0.12 if g['metal'] > 0.4 else 0.05)
        if g['opacity'] < 0.99: pass
        me.materials.append(m)
    me.polygons.foreach_set('material_index', mi); me.update(calc_edges=True); me.validate()
    ob = D.objects.new('stadium', me); link(ob, c)
    ob.visible_shadow = False
    return ob, z['S']


def pitch_textures():
    """Pitch line texture (alpha) generated once with PIL outside Blender; returns path."""
    return os.path.join(ASSET, 'pitchlines.png')


def pitch(c, wet=0.0, puddles=0.0):
    # grass with mowing stripes (two materials alternate), line markings from a transparent texture on top
    g1 = toon('grassA', '#3f9a3c', tex=os.path.join(ASSET, 'grass_tex.jpeg'), tex_coord='Object', tex_scale=(0.25, 0.25, 0.25), spec=0.0, wet=wet, puddles=puddles)
    g2 = toon('grassB', '#57b84c', tex=os.path.join(ASSET, 'grass_tex.jpeg'), tex_coord='Object', tex_scale=(0.25, 0.25, 0.25), spec=0.0, wet=wet, puddles=puddles)
    verts, faces, mats = [], [], []
    X0, X1, Y0, Y1, n = -60, 60, -42, 42, 20
    for i in range(n):
        x0 = X0 + (X1 - X0) * i / n; x1 = X0 + (X1 - X0) * (i + 1) / n; k = len(verts)
        verts += [(x0, Y0, 0), (x1, Y0, 0), (x1, Y1, 0), (x0, Y1, 0)]; faces.append((k, k + 1, k + 2, k + 3)); mats.append(i % 2)
    ob = mesh_obj('pitch', verts, faces, None, c); ob.data.materials.append(g1); ob.data.materials.append(g2)
    for p, mi in zip(ob.data.polygons, mats): p.material_index = mi
    # lines: textured plane slightly above the grass
    lm = toon('lines', '#f4f6fb', alpha_tex=pitch_textures(), spec=0.0, emit=0.15)
    L = mesh_obj('pitchlines', [(-56, -38, 0.01), (56, -38, 0.01), (56, 38, 0.01), (-56, 38, 0.01)], [(0, 1, 2, 3)], lm, c)
    uv = L.data.uv_layers.new(); [setattr(uv.data[i], 'uv', v) for i, v in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)])]
    L.visible_shadow = False
    return ob


def goals(c):
    """The game's goal frame (glTF), one at each end, plus a white net box."""
    out = []
    for side in (-1, 1):
        before = set(D.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(ASSET, 'goal_glb.glb'))
        new = [o for o in D.objects if o not in before]
        root = empty('goal%d' % side, (side * 52.5, 0, 0), c=c, rot=(0, 0, 0 if side < 0 else math.pi))
        for o in new:
            for cc in list(o.users_collection): cc.objects.unlink(o)
            c.objects.link(o)
            if o.parent is None: o.parent = root
            if o.type == 'MESH':
                o.data.materials.clear(); o.data.materials.append(toon('goalwhite', '#f4f6fb', spec=0.3)); outline(o, 0.03)
        out.append((root, new))
    return out


def net(c, side):
    """Simple net box behind the goal line: thin wire grid (wireframe modifier)."""
    x = side * 52.5; d = side * 2.2; w, h = 3.66, 2.44
    vs, fs = [], []
    def quad(a, b, cc, dd, nu, nv):
        k = len(vs)
        for j in range(nv + 1):
            for i in range(nu + 1):
                u, v = i / nu, j / nv; p = [a[t] + (b[t] - a[t]) * u + (dd[t] - a[t]) * v + (cc[t] - b[t] - dd[t] + a[t]) * u * v for t in range(3)]; vs.append(p)
        for j in range(nv):
            for i in range(nu): q = k + j * (nu + 1) + i; fs.append((q, q + 1, q + nu + 2, q + nu + 1))
    quad((x + d, -w, 0), (x + d, w, 0), (x + d * 0.6, w, h), (x + d * 0.6, -w, h), 36, 12)
    quad((x, -w, h), (x, w, h), (x + d * 0.6, w, h), (x + d * 0.6, -w, h), 36, 4)
    quad((x, -w, 0), (x + d, -w, 0), (x + d * 0.6, -w, h), (x, -w, h), 8, 12)
    quad((x, w, 0), (x + d, w, 0), (x + d * 0.6, w, h), (x, w, h), 8, 12)
    ob = mesh_obj('net%d' % side, vs, fs, toon('netwhite', '#e8ecf4', spec=0.0), c)
    wm = ob.modifiers.new('wire', 'WIREFRAME'); wm.thickness = 0.025; wm.use_replace = True
    ob.visible_shadow = False
    return ob


def crowd(c, spots, colors, n=60000, seed=3, card=None):
    """Spectators as instanced alpha cards facing the pitch, each with a colour attribute; a 'jump' value bounces them."""
    rng = np.random.default_rng(seed); sel = rng.choice(len(spots), min(n, len(spots)), replace=False); pts = spots[sel].astype(np.float32)
    me = D.meshes.new('crowdpts'); me.vertices.add(len(pts)); me.vertices.foreach_set('co', pts.ravel())
    cols = np.array([_hex(colors[i % len(colors)]) for i in rng.integers(0, 10 ** 6, len(pts))], np.float32)
    cols[:, :3] *= rng.uniform(0.75, 1.1, (len(pts), 1)).astype(np.float32)
    a = me.attributes.new('col', 'FLOAT_COLOR', 'POINT'); a.data.foreach_set('color', cols.ravel())
    yaw = np.arctan2(-pts[:, 1], -pts[:, 0]) + math.pi / 2  # card faces the pitch centre
    r = me.attributes.new('rz', 'FLOAT', 'POINT'); r.data.foreach_set('value', yaw.astype(np.float32))
    ph = me.attributes.new('ph', 'FLOAT', 'POINT'); ph.data.foreach_set('value', rng.uniform(0, 6.28, len(pts)).astype(np.float32))
    ob = D.objects.new('crowd', me); link(ob, c)
    # the card: 0.55 x 0.95 m quad, bottom at the seat
    cm = mesh_obj('fan', [(-0.27, 0, 0), (0.27, 0, 0), (0.27, 0, 0.95), (-0.27, 0, 0.95)], [(0, 1, 2, 3)], fan_mat(card), c)
    uv = cm.data.uv_layers.new(); [setattr(uv.data[i], 'uv', v) for i, v in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)])]
    cm.hide_render = True; cm.hide_viewport = True
    t = D.node_groups.new('crowdGN', 'GeometryNodeTree')
    t.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); t.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = t.nodes, t.links
    gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')
    oi = N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = cm
    na = N.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = 'rz'
    cx = N.new('ShaderNodeCombineXYZ'); L.new(na.outputs['Attribute'], cx.inputs['Z'])
    iop = N.new('GeometryNodeInstanceOnPoints'); L.new(gi.outputs[0], iop.inputs['Points']); L.new(oi.outputs['Geometry'], iop.inputs['Instance']); L.new(cx.outputs[0], iop.inputs['Rotation'])
    st = N.new('GeometryNodeInputSceneTime'); p2 = N.new('GeometryNodeInputNamedAttribute'); p2.data_type = 'FLOAT'; p2.inputs['Name'].default_value = 'ph'
    m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 9.0; L.new(st.outputs['Seconds'], m1.inputs[0])
    m2 = N.new('ShaderNodeMath'); m2.operation = 'ADD'; L.new(m1.outputs[0], m2.inputs[0]); L.new(p2.outputs['Attribute'], m2.inputs[1])
    m3 = N.new('ShaderNodeMath'); m3.operation = 'SINE'; L.new(m2.outputs[0], m3.inputs[0])
    m4 = N.new('ShaderNodeMath'); m4.operation = 'MAXIMUM'; m4.inputs[1].default_value = 0; L.new(m3.outputs[0], m4.inputs[0])
    jump = N.new('ShaderNodeValue'); jump.name = 'jump'; jump.outputs[0].default_value = 0.25
    m5 = N.new('ShaderNodeMath'); m5.operation = 'MULTIPLY'; L.new(m4.outputs[0], m5.inputs[0]); L.new(jump.outputs[0], m5.inputs[1])
    c2 = N.new('ShaderNodeCombineXYZ'); L.new(m5.outputs[0], c2.inputs['Z'])
    tr = N.new('GeometryNodeTranslateInstances'); L.new(iop.outputs[0], tr.inputs['Instances']); L.new(c2.outputs[0], tr.inputs['Translation'])
    tr.inputs['Local Space'].default_value = False
    L.new(tr.outputs[0], go.inputs[0])
    md = ob.modifiers.new('gn', 'NODES'); md.node_group = t
    ob.visible_shadow = False
    return ob, t


def night_lights(c, power=1.0):
    """Floodlight key (sun-like spot from high above) + fill spots + roof light rows."""
    out = []
    for i, (x, y) in enumerate([(-75, -62), (75, -62), (-75, 62), (75, 62)]):
        ld = D.lights.new('flood%d' % i, 'SPOT'); ld.energy = 2.6e6 * power; ld.spot_size = rad(70); ld.spot_blend = 0.6; ld.shadow_soft_size = 3.0
        ld.use_shadow = i == 0; ld.color = (1.0, 0.96, 0.9); ld.specular_factor = 0.0
        o = D.objects.new('flood%d' % i, ld); link(o, c); o.location = (x, y, 55)
        d = Vector((0, 0, 0)) - Vector(o.location); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); out.append(o)
    sd = D.lights.new('moon', 'SUN'); sd.energy = 0.9 * power; sd.angle = rad(2); sd.color = (0.75, 0.82, 1.0); sd.use_shadow = True
    so = D.objects.new('moon', sd); link(so, c); so.rotation_euler = (rad(38), rad(-18), rad(-35)); out.append(so)
    gm = glow('floodlamp', '#fff6e0', 30.0); hm = toon('floodframe', '#3a3d48', spec=0.3)
    lamps = []
    for x in np.arange(-50, 50.1, 4.0):
        for y in (-36.5, 36.5): lamps.append((x, y, 41.5))
    for y in np.arange(-30, 30.1, 4.0):
        for x in (-55.5, 55.5): lamps.append((x, y, 41.5))
    for i, (x, y, z) in enumerate(lamps):
        d = Vector((-x * 0.15, -y * 0.15, -z)).normalized(); q = d.to_track_quat('-Z', 'Y')
        hd = prim('cyl', 'lamphead', hm, (x, y, z), r=0.75, h=0.5, seg=12, ink=0, c=c, smooth=False); hd.rotation_euler = q.to_euler(); hd.visible_shadow = False
        lf = prim('cyl', 'lampface', gm, (0, 0, -0.27), r=0.62, h=0.06, seg=12, ink=0, c=c, smooth=False, parent=hd); lf.visible_shadow = False
    return out


def compositor(sc, streaks=True):
    sc.use_nodes = True; nt = sc.node_tree; N, L = nt.nodes, nt.links; N.clear()
    rl = N.new('CompositorNodeRLayers'); comp = N.new('CompositorNodeComposite')
    g1 = N.new('CompositorNodeGlare'); g1.glare_type = 'FOG_GLOW'; g1.threshold = 1.0; g1.size = 7; g1.mix = -0.72; g1.quality = 'MEDIUM'
    L.new(rl.outputs['Image'], g1.inputs['Image']); last = g1.outputs['Image']
    if streaks:
        g2 = N.new('CompositorNodeGlare'); g2.glare_type = 'STREAKS'; g2.streaks = 6; g2.threshold = 1.6; g2.fade = 0.86; g2.mix = -0.78; g2.quality = 'MEDIUM'; g2.angle_offset = rad(15)
        L.new(last, g2.inputs['Image']); last = g2.outputs['Image']
        g3 = N.new('CompositorNodeGlare'); g3.glare_type = 'GHOSTS'; g3.threshold = 3.0; g3.mix = -0.9; g3.iterations = 3; g3.quality = 'LOW'
        L.new(last, g3.inputs['Image']); last = g3.outputs['Image']
    el = N.new('CompositorNodeEllipseMask'); el.width = 1.05; el.height = 1.0; el.mask_type = 'ADD'
    bl = N.new('CompositorNodeBlur'); bl.size_x = 220; bl.size_y = 220; bl.filter_type = 'GAUSS'; L.new(el.outputs[0], bl.inputs['Image'])
    mr = N.new('CompositorNodeMapRange'); mr.inputs['To Min'].default_value = 0.62; L.new(bl.outputs[0], mr.inputs['Value'])
    mx = N.new('CompositorNodeMixRGB'); mx.blend_type = 'MULTIPLY'; L.new(last, mx.inputs[1]); L.new(mr.outputs[0], mx.inputs[2])
    cb = N.new('CompositorNodeColorBalance'); cb.correction_method = 'LIFT_GAMMA_GAIN'; cb.lift = (1.0, 0.99, 1.03); cb.gain = (1.04, 1.02, 0.98)
    hs = N.new('CompositorNodeHueSat'); hs.inputs['Saturation'].default_value = 1.12
    L.new(mx.outputs[0], cb.inputs['Image']); L.new(cb.outputs['Image'], hs.inputs['Image']); L.new(hs.outputs['Image'], comp.inputs['Image'])
    return nt


def camera(sc, lens=32):
    cd = D.cameras.new('cam'); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_start = 0.1; cd.clip_end = 1500
    cd.dof.use_dof = False
    co = D.objects.new('cam', cd); link(co); sc.camera = co
    return co


def look_at(ob, pos, target, roll=0.0):
    ob.location = pos
    d = Vector(target) - Vector(pos); q = d.to_track_quat('-Z', 'Y'); e = q.to_euler()
    if roll: e = (q @ Quaternion((0, 0, 1), roll)).to_euler()
    ob.rotation_euler = e


def fan_mat(card, bright=0.6):
    """Cheap crowd card shader: texture, shirt (pure white pixels) tinted by the per-instance colour, emission only."""
    if 'fanmat' in _mat: return _mat['fanmat']
    m = D.materials.new('fanmat'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    ti = N.new('ShaderNodeTexImage'); ti.image = D.images.load(card, check_existing=True)
    at = N.new('ShaderNodeAttribute'); at.attribute_type = 'INSTANCER'; at.attribute_name = 'col'
    sp = N.new('ShaderNodeSeparateColor'); L.new(ti.outputs['Color'], sp.inputs[0])
    m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; L.new(sp.outputs[0], m1.inputs[0]); L.new(sp.outputs[2], m1.inputs[1])
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.85; L.new(m1.outputs[0], gt.inputs[0])
    mu = N.new('ShaderNodeMixRGB'); mu.blend_type = 'MULTIPLY'; mu.inputs[0].default_value = 1; L.new(ti.outputs['Color'], mu.inputs[1]); L.new(at.outputs['Color'], mu.inputs[2])
    mx = N.new('ShaderNodeMixRGB'); L.new(gt.outputs[0], mx.inputs[0]); L.new(ti.outputs['Color'], mx.inputs[1]); L.new(mu.outputs[0], mx.inputs[2])
    em = N.new('ShaderNodeEmission'); em.name = 'fanem'; em.inputs['Strength'].default_value = bright; L.new(mx.outputs[0], em.inputs['Color'])
    tr = N.new('ShaderNodeBsdfTransparent'); ms = N.new('ShaderNodeMixShader'); L.new(ti.outputs['Alpha'], ms.inputs[0]); L.new(tr.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
    o = N.new('ShaderNodeOutputMaterial'); L.new(ms.outputs[0], o.inputs[0])
    m.blend_method = 'CLIP'; m.shadow_method = 'NONE'; m.alpha_threshold = 0.5; _mat['fanmat'] = m; return m


# ---------------- 3D turf: wet base with puddle reflections + grass shells + real tufts near the action ----------------
GA, GB, TUFT_H = '#3f9a3c', '#58ba4c', 0.075
def _n(N, t, **kw):
    n = N.new(t)
    for k, v in kw.items():
        if k == 'op': n.operation = v
        elif k == 'blend': n.blend_type = v
        else: setattr(n, k, v)
    return n


def _turf_color(N, L, pos, lay=None):
    """stripe colour x grass detail x layer shade, with the line markings; returns colour socket"""
    sep = _n(N, 'ShaderNodeSeparateXYZ'); L.new(pos, sep.inputs[0])
    m1 = _n(N, 'ShaderNodeMath', op='MULTIPLY'); m1.inputs[1].default_value = 1 / 10.5; L.new(sep.outputs[0], m1.inputs[0])
    fr = _n(N, 'ShaderNodeMath', op='FRACT'); L.new(m1.outputs[0], fr.inputs[0])
    gt = _n(N, 'ShaderNodeMath', op='GREATER_THAN'); gt.inputs[1].default_value = 0.5; L.new(fr.outputs[0], gt.inputs[0])
    mx = _n(N, 'ShaderNodeMixRGB'); L.new(gt.outputs[0], mx.inputs[0]); mx.inputs[1].default_value = _hex(GA); mx.inputs[2].default_value = _hex(GB)
    mp = _n(N, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.3, 0.3, 0.3); L.new(pos, mp.inputs[0])
    gi = _n(N, 'ShaderNodeTexImage'); gi.image = D.images.load(os.path.join(ASSET, 'grass_tex.jpeg'), check_existing=True); L.new(mp.outputs[0], gi.inputs[0])
    gm = _n(N, 'ShaderNodeMixRGB', blend='MULTIPLY'); gm.inputs[0].default_value = 0.85; L.new(mx.outputs[0], gm.inputs[1]); L.new(gi.outputs['Color'], gm.inputs[2])
    col = gm.outputs[0]
    if lay is not None:
        sh = _n(N, 'ShaderNodeMapRange'); sh.inputs['To Min'].default_value = 0.5; sh.inputs['To Max'].default_value = 1.28; L.new(lay, sh.inputs['Value'])
        ml = _n(N, 'ShaderNodeMixRGB', blend='MULTIPLY'); ml.inputs[0].default_value = 1; L.new(col, ml.inputs[1])
        cv = _n(N, 'ShaderNodeCombineColor'); L.new(sh.outputs[0], cv.inputs[0]); L.new(sh.outputs[0], cv.inputs[1]); L.new(sh.outputs[0], cv.inputs[2]); L.new(cv.outputs[0], ml.inputs[2]); col = ml.outputs[0]
    # line markings (texture covers x -56..56, y -38..38)
    lm = _n(N, 'ShaderNodeMapping'); lm.inputs['Location'].default_value = (0.5, 0.5, 0); lm.inputs['Scale'].default_value = (1 / 112, 1 / 76, 1); L.new(pos, lm.inputs[0])
    li = _n(N, 'ShaderNodeTexImage'); li.image = D.images.load(os.path.join(ASSET, 'pitchlines.png'), check_existing=True); li.extension = 'CLIP'; L.new(lm.outputs[0], li.inputs[0])
    lw = _n(N, 'ShaderNodeMixRGB'); L.new(li.outputs['Alpha'], lw.inputs[0]); L.new(col, lw.inputs[1]); lw.inputs[2].default_value = (0.86, 0.9, 0.86, 1)
    return lw.outputs[0], li.outputs['Alpha']


def _toon_light(N, L, col, shadow=(0.42, 0.40, 0.56)):
    diff = _n(N, 'ShaderNodeBsdfDiffuse'); s2r = _n(N, 'ShaderNodeShaderToRGB'); L.new(diff.outputs[0], s2r.inputs[0])
    bw = _n(N, 'ShaderNodeRGBToBW'); L.new(s2r.outputs['Color'], bw.inputs[0])
    rp = _n(N, 'ShaderNodeValToRGB'); cr = rp.color_ramp; cr.interpolation = 'CONSTANT'; cr.elements[0].color = shadow + (1,)
    cr.elements[1].position = 0.09; cr.elements[1].color = (0.74, 0.72, 0.8, 1); e3 = cr.elements.new(0.34); e3.color = (1, 1, 1, 1); L.new(bw.outputs[0], rp.inputs[0])
    mu = _n(N, 'ShaderNodeMixRGB', blend='MULTIPLY'); mu.inputs[0].default_value = 1; L.new(col, mu.inputs[1]); L.new(rp.outputs[0], mu.inputs[2])
    em = _n(N, 'ShaderNodeEmission'); L.new(mu.outputs[0], em.inputs['Color']); return em


def _puddle(N, L, pos, amount):
    mp = _n(N, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 0); L.new(pos, mp.inputs[0])
    nz = _n(N, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.11; nz.inputs['Detail'].default_value = 3.0; L.new(mp.outputs[0], nz.inputs['Vector'])
    mr = _n(N, 'ShaderNodeMapRange'); lo = 0.58 - 0.12 * amount if amount > 0 else 5.0; mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = lo + 0.04; L.new(nz.outputs['Fac'], mr.inputs['Value'])
    return mr.outputs[0]


def turf(c, puddles=0.6, shells=8, shell_h=0.058, center=(0, 0), half=(62, 44), base_half=(130, 110), tag=''):
    cx, cy = center
    # base ground: turf colour, lines, damp sheen and mirror-like puddles with animated rain ripples
    m = D.materials.new('turf' + tag); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    geo = _n(N, 'ShaderNodeNewGeometry'); pos = geo.outputs['Position']
    col, lines = _turf_color(N, L, pos, None)
    dk = _n(N, 'ShaderNodeMixRGB', blend='MULTIPLY'); dk.inputs[0].default_value = 1; L.new(col, dk.inputs[1]); dk.inputs[2].default_value = (0.55, 0.58, 0.55, 1)
    em = _n(N, 'ShaderNodeEmission'); L.new(dk.outputs[0], em.inputs['Color'])   # no Shader-to-RGB here: it would switch off screen-space reflections
    pud = _puddle(N, L, pos, puddles)
    rip = _n(N, 'ShaderNodeTexNoise'); rip.noise_dimensions = '4D'; rip.name = 'ripple'; rip.inputs['Scale'].default_value = 9.0; rip.inputs['Detail'].default_value = 1.0; L.new(pos, rip.inputs['Vector'])
    bump = _n(N, 'ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.12; bump.inputs['Distance'].default_value = 0.02; L.new(rip.outputs['Fac'], bump.inputs['Height'])
    gl = _n(N, 'ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.02; L.new(bump.outputs['Normal'], gl.inputs['Normal'])
    lw = _n(N, 'ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
    amt = _n(N, 'ShaderNodeMath', op='MULTIPLY_ADD'); L.new(pud, amt.inputs[0]); amt.inputs[1].default_value = 0.85; amt.inputs[2].default_value = 0.12
    fz = _n(N, 'ShaderNodeMath', op='MULTIPLY'); L.new(amt.outputs[0], fz.inputs[0]); fr = _n(N, 'ShaderNodeMath', op='MULTIPLY_ADD'); L.new(lw.outputs['Fresnel'], fr.inputs[0]); fr.inputs[1].default_value = 0.6; fr.inputs[2].default_value = 0.4; L.new(fr.outputs[0], fz.inputs[1])
    ms = _n(N, 'ShaderNodeMixShader'); L.new(fz.outputs[0], ms.inputs[0]); L.new(em.outputs[0], ms.inputs[1]); L.new(gl.outputs[0], ms.inputs[2])
    out = _n(N, 'ShaderNodeOutputMaterial'); L.new(ms.outputs[0], out.inputs[0])
    bx, by = base_half
    base = mesh_obj('turfbase' + tag, [(cx - bx, cy - by, 0), (cx + bx, cy - by, 0), (cx + bx, cy + by, 0), (cx - bx, cy + by, 0)], [(0, 1, 2, 3)], m, c); base.visible_shadow = False
    # shells: stacked alpha-clipped layers; blades from the game's height map, none inside puddles, thinning with distance
    sm = D.materials.new('shell' + tag); sm.use_nodes = True; nt = sm.node_tree; N, L = nt.nodes, nt.links; N.clear()
    geo = _n(N, 'ShaderNodeNewGeometry'); pos = geo.outputs['Position']
    at = _n(N, 'ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = 'lay'; lay = at.outputs['Fac']
    col, lines = _turf_color(N, L, pos, lay)
    hm = D.images.load(os.path.join(ASSET, 'grass_h.jpeg'), check_existing=True); hm.colorspace_settings.name = 'Non-Color'
    m1 = _n(N, 'ShaderNodeMapping'); m1.inputs['Scale'].default_value = (1 / 0.92, 1 / 0.92, 1); L.new(pos, m1.inputs[0])
    t1 = _n(N, 'ShaderNodeTexImage'); t1.image = hm; L.new(m1.outputs[0], t1.inputs[0])
    m2 = _n(N, 'ShaderNodeMapping'); m2.inputs['Rotation'].default_value = (0, 0, rad(90)); m2.inputs['Scale'].default_value = (1.37 / 0.92, 1.37 / 0.92, 1); m2.inputs['Location'].default_value = (0.31, 0.31, 0); L.new(pos, m2.inputs[0])
    t2 = _n(N, 'ShaderNodeTexImage'); t2.image = hm; L.new(m2.outputs[0], t2.inputs[0])
    s2 = _n(N, 'ShaderNodeMath', op='MULTIPLY'); s2.inputs[1].default_value = 0.92; L.new(t2.outputs['Color'], s2.inputs[0])
    bh = _n(N, 'ShaderNodeMath', op='MAXIMUM'); L.new(t1.outputs['Color'], bh.inputs[0]); L.new(s2.outputs[0], bh.inputs[1])
    th = _n(N, 'ShaderNodeMath', op='MULTIPLY_ADD'); L.new(lay, th.inputs[0]); th.inputs[1].default_value = 0.9; th.inputs[2].default_value = 0.06
    pud = _puddle(N, L, pos, puddles); p2 = _n(N, 'ShaderNodeMath', op='MULTIPLY_ADD'); L.new(pud, p2.inputs[0]); p2.inputs[1].default_value = 1.2; L.new(th.outputs[0], p2.inputs[2])
    cd = _n(N, 'ShaderNodeCameraData'); dr = _n(N, 'ShaderNodeMapRange'); dr.inputs['From Min'].default_value = 40; dr.inputs['From Max'].default_value = 85; dr.inputs['To Max'].default_value = 0.8
    L.new(cd.outputs['View Distance'], dr.inputs['Value']); p3 = _n(N, 'ShaderNodeMath', op='ADD'); L.new(p2.outputs[0], p3.inputs[0]); L.new(dr.outputs[0], p3.inputs[1])
    keep = _n(N, 'ShaderNodeMath', op='GREATER_THAN'); L.new(bh.outputs[0], keep.inputs[0]); L.new(p3.outputs[0], keep.inputs[1])
    em = _toon_light(N, L, col)
    tr = _n(N, 'ShaderNodeBsdfTransparent'); mx = _n(N, 'ShaderNodeMixShader'); L.new(keep.outputs[0], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
    out = _n(N, 'ShaderNodeOutputMaterial'); L.new(mx.outputs[0], out.inputs[0])
    sm.blend_method = 'CLIP'; sm.shadow_method = 'NONE'; sm.alpha_threshold = 0.5
    for i in range(shells):
        hx, hy = half; s = mesh_obj('shell%d%s' % (i, tag), [(cx - hx, cy - hy, 0), (cx + hx, cy - hy, 0), (cx + hx, cy + hy, 0), (cx - hx, cy + hy, 0)], [(0, 1, 2, 3)], sm, c)
        s.location.z = shell_h * (i + 1) / shells; s['lay'] = (i + 1) / shells; s.visible_shadow = False
    # real tufts (the game's grass model tile) instanced on a world grid around a focus point; none in puddles
    z = np.load(os.path.join(ASSET, 'tuft.npz')); P, I, T = z['P'], z['I'], z['T']
    me = D.meshes.new('tuft' + tag); me.vertices.add(len(P)); me.vertices.foreach_set('co', P.ravel()); nt3 = len(I) // 3
    me.loops.add(len(I)); me.loops.foreach_set('vertex_index', I); me.polygons.add(nt3)
    me.polygons.foreach_set('loop_start', np.arange(0, len(I), 3, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(nt3, 3, np.int32)); me.update(calc_edges=True)
    tip = me.attributes.new('tip', 'FLOAT', 'POINT'); tip.data.foreach_set('value', T)
    tm = D.materials.new('tuftmat' + tag); tm.use_nodes = True; nt = tm.node_tree; N, L = nt.nodes, nt.links; N.clear()
    geo = _n(N, 'ShaderNodeNewGeometry'); at = _n(N, 'ShaderNodeAttribute'); at.attribute_name = 'tip'
    col, _ = _turf_color(N, L, geo.outputs['Position'], at.outputs['Fac'])
    em = _toon_light(N, L, col); out = _n(N, 'ShaderNodeOutputMaterial'); L.new(em.outputs[0], out.inputs[0]); tm.use_backface_culling = False; tm.shadow_method = 'NONE'
    me.materials.append(tm); tile = D.objects.new('tufttile' + tag, me); link(tile, c); tile.hide_render = tile.hide_viewport = True
    ext = float(P[:, 0].max() - P[:, 0].min())
    focus = empty('grassfocus' + tag, (cx, cy, 0), c=c)
    host = mesh_obj('tufts' + tag, [(0, 0, 0)], [], None, c); host.visible_shadow = False
    t = D.node_groups.new('tuftGN' + tag, 'GeometryNodeTree'); t.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); t.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = t.nodes, t.links; gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')
    R = 9.0; n = int(2 * R / ext) + 1
    fo = N.new('GeometryNodeObjectInfo'); fo.inputs['Object'].default_value = focus; fo.transform_space = 'ORIGINAL'
    sn = N.new('ShaderNodeVectorMath'); sn.operation = 'SNAP'; sn.inputs[1].default_value = (ext, ext, 1e6); L.new(fo.outputs['Location'], sn.inputs[0])
    gr = N.new('GeometryNodeMeshGrid'); gr.inputs['Size X'].default_value = (n - 1) * ext; gr.inputs['Size Y'].default_value = (n - 1) * ext; gr.inputs['Vertices X'].default_value = n; gr.inputs['Vertices Y'].default_value = n
    tg = N.new('GeometryNodeTransform'); L.new(gr.outputs['Mesh'], tg.inputs['Geometry']); L.new(sn.outputs[0], tg.inputs['Translation'])
    m2p = N.new('GeometryNodeMeshToPoints'); L.new(tg.outputs[0], m2p.inputs['Mesh'])
    ps = N.new('GeometryNodeInputPosition'); dist = N.new('ShaderNodeVectorMath'); dist.operation = 'DISTANCE'; L.new(ps.outputs[0], dist.inputs[0]); L.new(fo.outputs['Location'], dist.inputs[1])
    far = N.new('ShaderNodeMath'); far.operation = 'GREATER_THAN'; far.inputs[1].default_value = R; L.new(dist.outputs['Value'], far.inputs[0])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.11; nz.inputs['Detail'].default_value = 3.0
    mp = N.new('ShaderNodeVectorMath'); mp.operation = 'MULTIPLY'; mp.inputs[1].default_value = (1, 1, 0); L.new(ps.outputs[0], mp.inputs[0]); L.new(mp.outputs[0], nz.inputs['Vector'])
    wet = N.new('ShaderNodeMath'); wet.operation = 'GREATER_THAN'; wet.inputs[1].default_value = (0.58 - 0.12 * puddles) if puddles > 0 else 5.0; L.new(nz.outputs['Fac'], wet.inputs[0])
    out_pitch = N.new('ShaderNodeMath'); out_pitch.operation = 'ADD'; L.new(far.outputs[0], out_pitch.inputs[0]); L.new(wet.outputs[0], out_pitch.inputs[1])
    dl = N.new('GeometryNodeDeleteGeometry'); dl.domain = 'POINT'; L.new(m2p.outputs[0], dl.inputs['Geometry']); L.new(out_pitch.outputs[0], dl.inputs['Selection'])
    ti = N.new('GeometryNodeObjectInfo'); ti.inputs['Object'].default_value = tile
    rv = N.new('FunctionNodeRandomValue'); rv.data_type = 'INT'; rv.inputs['Min'].default_value = 0; rv.inputs['Max'].default_value = 3
    ra = N.new('ShaderNodeMath'); ra.operation = 'MULTIPLY'; ra.inputs[1].default_value = math.pi / 2; L.new(rv.outputs[2], ra.inputs[0])
    rc = N.new('ShaderNodeCombineXYZ'); L.new(ra.outputs[0], rc.inputs['Z'])
    sc_ = N.new('ShaderNodeMapRange'); sc_.inputs['From Min'].default_value = R * 0.65; sc_.inputs['From Max'].default_value = R; sc_.inputs['To Min'].default_value = 1.0; sc_.inputs['To Max'].default_value = 0.25; L.new(dist.outputs['Value'], sc_.inputs['Value'])
    sv = N.new('ShaderNodeCombineXYZ'); sv.inputs['X'].default_value = 1; sv.inputs['Y'].default_value = 1; L.new(sc_.outputs[0], sv.inputs['Z'])
    iop = N.new('GeometryNodeInstanceOnPoints'); L.new(dl.outputs[0], iop.inputs['Points']); L.new(ti.outputs['Geometry'], iop.inputs['Instance']); L.new(rc.outputs[0], iop.inputs['Rotation']); L.new(sv.outputs[0], iop.inputs['Scale'])
    L.new(iop.outputs[0], go.inputs[0])
    md = host.modifiers.new('gn', 'NODES'); md.node_group = t
    return focus


def turf_time(t):
    for m in D.materials:
        if m.name.startswith('turf') and m.node_tree and 'ripple' in m.node_tree.nodes: m.node_tree.nodes['ripple'].inputs['W'].default_value = t * 1.6
