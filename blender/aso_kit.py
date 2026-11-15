"""All Systems Operational: shared grey-box kit for the four Session 503 rooms (M3).

Builds on the vendored kits without changing them: blender/ep/gb.py (flat materials, boxes, planes, cameras,
seeded generators) and blender/ep/figlib.py (poses); blender/lib/sr_kit.py (the probes) is imported by sets.py.
Adds what the rooms need: the figure library linked as collection instances, Remotion textures on planes (lit,
glowing or flat-2D with alpha), the rain-on-glass window shader, distance fog for the park, render settings.

People: assets/figures/figures.blend (Ever Present's library v6) is LINKED, not appended, so its textures resolve
relative to assets/figures/ into assets/mpfb/ and nothing from it is copied into a saved file. Collections are
"fig_<person>_<pose>"; the library faces -Y, so person() turns each instance by pi (facing +Y at rot_z = 0, the
sanctuary.py convention). New poses come from blender/poses.py (posed copies of a linked person's rig).

Colours and light levels: config/aso_look.json (the four rooms); config/look.json stays the probe kit's.
Seeds: config/seeds.json main, via gb.rng(name) named streams.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "ep"))
import gb  # noqa: E402  (blender/ep/gb.py, vendored)

ROOT = gb.ROOT
LOOK = json.loads((ROOT / "config" / "aso_look.json").read_text())
PAL = LOOK["palette"]
TEX = ROOT / "assets" / "gen" / "tex"
FIGS = ROOT / "assets" / "figures" / "figures.blend"
LIB = {}                    # pose -> [linked collection, ...] sorted by person
M = {}                      # per-build material cache by role


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    gb._MATS.clear()
    M.clear()
    LIB.clear()
    gb.into(None)


def mat(role, rough=None, emit=0.0, metal=0.0, alpha=1.0):
    """A flat material in a palette colour (config/aso_look.json), cached by role."""
    key = f"{role}:{emit}:{alpha}"
    if key not in M:
        hexcol = PAL.get(role, role)
        M[key] = gb.mat(f"m_{role}_{len(M)}", hexcol, 0.8 if rough is None else rough, emit, metal, alpha)
    return M[key]


# ---------------------------------------------------------------- textures (Remotion stills in assets/gen/tex)

def tex_path(name):
    p = TEX / f"{name}.png"
    if not p.exists():
        raise FileNotFoundError(f"{p}: render the Remotion textures first (see blender/board.py docstring)")
    return p


def image_mat(name, tex, mode="lit", strength=1.0, rough=0.7):
    """A material showing a Remotion still. mode:
    lit   - printed surface (table tent, Polaroid, whiteboard, station sign, drum head): diffuse plus a little glow
            (strength) so its words still read in a backlit room;
    glow  - a lit sign or screen (ON AIR lit, phone): emission only;
    flat  - Little Switch: emission at 1.0 (shows the PNG's own colours, unshaded, 2D) with the PNG's alpha.
    Images with alpha (kick head, Switch) cut out by their alpha in every mode."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(tex_path(tex)), check_existing=True)
    img.interpolation = "Cubic"
    if mode == "lit":
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        b.inputs["Roughness"].default_value = rough
        b.inputs["Specular IOR Level"].default_value = 0.2
        nt.links.new(img.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(img.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = strength
        shader = b.outputs[0]
    else:
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Strength"].default_value = strength
        nt.links.new(img.outputs["Color"], e.inputs["Color"])
        shader = e.outputs[0]
    if img.image.depth == 32 or img.image.alpha_mode != "NONE":
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(img.outputs["Alpha"], mix.inputs[0])
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(shader, mix.inputs[2])
        shader = mix.outputs[0]
        m.surface_render_method = "DITHERED"
    nt.links.new(shader, out.inputs["Surface"])
    return m


def image_size(tex):
    im = bpy.data.images.load(str(tex_path(tex)), check_existing=True)
    return im.size[0], im.size[1]


def tex_plane(name, tex, center, height, facing="-Y", mode="lit", strength=0.4, width=None):
    """A plane showing a texture at its own aspect, `height` metres tall (or `width` wide)."""
    w, h = image_size(tex)
    size = (width, width * h / w) if width else (height * w / h, height)
    o = gb.plane(name, center, size, image_mat(f"tex_{name}", tex, mode, strength), facing=facing)
    if mode == "flat":
        o.visible_shadow = False
    return o


# ---------------------------------------------------------------- shaders

def window_mat(name, top="#d9dde0", bottom="#b9bfc4", strength=3.0, rain=1.0, steam=0.0, seed=0.0, see=0.0):
    """Rain on glass, as one emissive shader on the pane (the grey sky seen through it): a soft vertical gradient,
    long running streaks (noise stretched 1:14 along Z) and small droplets (Voronoi), both darkening and catching the
    light a little. steam (0..1) frosts it: flatter and paler, with a few clear drip trails. Opaque: nothing outside
    is modelled, so no plaza, street or water can show through."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    out, em = N("ShaderNodeOutputMaterial"), N("ShaderNodeEmission")
    tc = N("ShaderNodeTexCoord")
    # gradient over the object's generated Z
    sep = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Generated"], sep.inputs[0])
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = gb.lin(bottom)
    ramp.color_ramp.elements[1].color = gb.lin(top)
    L(sep.outputs["Z"], ramp.inputs["Fac"])
    # streaks: object coords scaled so features run down the glass
    mp = N("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (28.0, 28.0, 2.0)
    mp.inputs["Location"].default_value = (seed, seed * 0.7, 0)
    L(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 2.0
    L(mp.outputs[0], nz.inputs["Vector"])
    streak = N("ShaderNodeMapRange")
    streak.inputs["From Min"].default_value, streak.inputs["From Max"].default_value = 0.56, 0.66
    L(nz.outputs["Fac"], streak.inputs["Value"])
    # droplets
    vo = N("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 70.0
    L(tc.outputs["Object"], vo.inputs["Vector"])
    drop = N("ShaderNodeMapRange")
    drop.inputs["From Min"].default_value, drop.inputs["From Max"].default_value = 0.16, 0.05
    L(vo.outputs["Distance"], drop.inputs["Value"])
    wet = N("ShaderNodeMath")
    wet.operation = "MAXIMUM"
    L(streak.outputs[0], wet.inputs[0])
    L(drop.outputs[0], wet.inputs[1])
    amt = N("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    amt.inputs[1].default_value = 0.32 * rain * (1.0 - 0.6 * steam)
    L(wet.outputs[0], amt.inputs[0])
    dark = N("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.blend_type = "MULTIPLY"
    dark.inputs["B"].default_value = gb.lin("#8a9096")
    L(amt.outputs[0], dark.inputs["Factor"])
    L(ramp.outputs["Color"], dark.inputs["A"])
    col = dark.outputs["Result"]
    if steam:
        fog = N("ShaderNodeMix")
        fog.data_type = "RGBA"
        fog.inputs["B"].default_value = gb.lin("#e8e6e0")
        fog.inputs["Factor"].default_value = 0.55 * steam
        L(col, fog.inputs["A"])
        col = fog.outputs["Result"]
    L(col, em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    shader = em.outputs[0]
    if see:   # see-through glass (the treehouse: trees outside): mostly clear, the wet streaks and drops stay visible
        op = N("ShaderNodeMath"); op.operation = "MULTIPLY_ADD"
        op.inputs[1].default_value = 2.5
        op.inputs[2].default_value = 1.0 - see
        op.use_clamp = True
        L(amt.outputs[0], op.inputs[0])
        tr = N("ShaderNodeBsdfTransparent")
        mix = N("ShaderNodeMixShader")
        L(op.outputs[0], mix.inputs[0])
        L(tr.outputs[0], mix.inputs[1])
        L(shader, mix.inputs[2])
        shader = mix.outputs[0]
        m.surface_render_method = "DITHERED"
    L(shader, out.inputs["Surface"])
    m["window"] = True
    return m


def fog_mat(name, hexcol, fog="#c4c9cc", dist=60.0, rough=0.9, emit_fog=1.0):
    """A diffuse surface fading into fog with distance from the camera (1 - exp(-d / dist)): a cheap aerial
    perspective for the park's trees and the skyline, deterministic and noise-free at any sample count. The fog
    colour is emitted, so far things go to the flat bright grey of the sky, not to black."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    b = N("ShaderNodeBsdfDiffuse")
    b.inputs["Color"].default_value = gb.lin(hexcol)
    b.inputs["Roughness"].default_value = rough
    cam = N("ShaderNodeCameraData")
    f = N("ShaderNodeMath"); f.operation = "DIVIDE"; f.inputs[1].default_value = -dist
    L(cam.outputs["View Distance"], f.inputs[0])
    ex = N("ShaderNodeMath"); ex.operation = "EXPONENT"
    L(f.outputs[0], ex.inputs[0])
    inv = N("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    L(ex.outputs[0], inv.inputs[1])
    e = N("ShaderNodeEmission")
    e.inputs["Color"].default_value = gb.lin(fog)
    e.inputs["Strength"].default_value = emit_fog
    mix = N("ShaderNodeMixShader")
    L(inv.outputs[0], mix.inputs[0])
    L(b.outputs[0], mix.inputs[1])
    L(e.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs["Surface"])
    return m


def bulb_mat(name="string_bulb", hexcol="#ffc27a", strength=18.0, off="#2a2219"):
    """One shared material for every string-light bulb: emission scaled by the bulb object's own "on" property
    (0..1, Attribute node, object type), so a script or keyframes can put out any single bulb (O16's cascade)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    at = N("ShaderNodeAttribute")
    at.attribute_type, at.attribute_name = "OBJECT", '["on"]'
    b = N("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = gb.lin(off)
    b.inputs["Roughness"].default_value = 0.3
    b.inputs["Emission Color"].default_value = gb.lin(hexcol)
    mul = N("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = strength
    L(at.outputs["Fac"], mul.inputs[0])
    L(mul.outputs[0], b.inputs["Emission Strength"])
    L(b.outputs[0], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- people

def load_people(poses=None):
    """Link every fig_ collection (or only these poses) from the library."""
    with bpy.data.libraries.load(str(FIGS), link=True) as (src, dst):
        dst.collections = [c for c in src.collections if c.startswith("fig_")
                           and (poses is None or "_".join(c.split("_")[2:]) in poses)]
    for c in dst.collections:
        LIB.setdefault("_".join(c.name.split("_")[2:]), []).append(c)
    for v in LIB.values():
        v.sort(key=lambda c: c.name)


def person_index(c):
    return int(c.name.split("_")[1])


def pick(pose, u=None, who=None):
    pool = LIB[pose]
    if who is not None:
        return next(c for c in pool if person_index(c) == who)
    return pool[int(u * len(pool)) % len(pool)]


def person(name, pose, loc, rot_z=0.0, u=0.0, who=None, coll=None):
    """An instance of a library person in a pose at loc, facing +Y rotated by rot_z (radians, CCW from above).
    rot_z = pi faces -Y (toward a camera at -Y... only ever with the light behind them)."""
    c = coll or pick(pose, u, who)
    e = bpy.data.objects.new(name, None)
    e.instance_type, e.instance_collection = "COLLECTION", c
    e.location, e.rotation_euler = loc, (0, 0, rot_z + math.pi)
    e["pose"], e["person"] = pose, person_index(c) if c.name.startswith("fig_") else -1
    gb.link(e)
    return e


def facing(src, dst):
    """rot_z for person() so a figure at src faces dst."""
    d = Vector(dst) - Vector(src)
    return math.atan2(d.y, d.x) - math.pi / 2


def local_to_world(e, p):
    """A point in figure space (the library's frame, facing -Y) to world space for instance e."""
    bpy.context.view_layer.update()        # matrix_world is stale until the depsgraph updates (Ever Present log 9)
    return e.matrix_world @ Vector(p)


# ---------------------------------------------------------------- lights

def area(name, loc, target, energy, size, color="#ffffff", size_y=None, shadow=True, spec=1.0):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE" if size_y else "SQUARE"
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.energy, ld.color = energy, gb.lin(color)[:3]
    ld.use_shadow = shadow
    ld.specular_factor = spec
    o = gb.link(bpy.data.objects.new(name, ld))
    o.location = loc
    o.rotation_euler = gb.look_rot(loc, target)
    return o


def point(name, loc, energy, color="#ffcf9a", radius=0.05, shadow=True):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = energy, gb.lin(color)[:3], radius
    ld.use_shadow = shadow
    o = gb.link(bpy.data.objects.new(name, ld))
    o.location = loc
    return o


def sun(name, rot, energy, color="#ffffff", angle=10.0):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy, ld.color, ld.angle = energy, gb.lin(color)[:3], math.radians(angle)
    o = gb.link(bpy.data.objects.new(name, ld))
    o.rotation_euler = rot
    return o


def world(hexcol, strength, light=None):
    """World colour. light (optional): the strength every non-camera ray sees, so an open sky or a window onto it
    can read bright to the camera while lighting the room only dimly (people stay silhouettes)."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = gb.lin(hexcol)
    bg.inputs["Strength"].default_value = strength
    if light is not None:
        lp = nt.nodes.new("ShaderNodeLightPath")
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"
        mx.inputs[1].default_value = strength - light
        mx.inputs[2].default_value = light
        nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
        nt.links.new(mx.outputs[0], bg.inputs["Strength"])
    return w


def bloom(threshold=1.5, size=0.25, strength=0.35):
    """Compositor bloom (Eevee has none of its own) so bulbs and lit signs glow; Blender 5 node-group compositor,
    as blender/lib/sr_kit.bloom."""
    sc = bpy.context.scene
    nt = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = nt
    rl = nt.nodes.new("CompositorNodeRLayers")
    g = nt.nodes.new("CompositorNodeGlare")
    g.inputs["Type"].default_value = "Bloom"
    g.inputs["Threshold"].default_value = threshold
    g.inputs["Size"].default_value = size
    g.inputs["Strength"].default_value = strength
    nt.links.new(rl.outputs["Image"], g.inputs["Image"])
    nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    out = nt.nodes.new("NodeGroupOutput")
    nt.links.new(g.outputs["Image"], out.inputs[0])


def render_settings(size=(1280, 720), samples=32, exposure=0.0):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_shadows = True
    ee.shadow_pool_size = "1024"          # the default overflows with many lights (Ever Present log 9)
    ee.use_raytracing = True
    ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    ee.use_volumetric_shadows = True
    ee.volumetric_tile_size = "4"
    ee.volumetric_end = 120.0
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = LOOK["agx_look"]
    sc.view_settings.exposure = LOOK["exposure"] + exposure
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
