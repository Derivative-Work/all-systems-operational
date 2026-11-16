"""M7c: the hilltop park rebuilt (human interventions 18, 19 and 22; production log 41's diagnosis; decisions 35+).

Called from blender/look.py's park() when the look is on (blender/coverage_m7.py), after blender/sets.py has built
M3's park (people, Switch, the umbrella, drizzle): this replaces the ground, the path, the trees, the skyline, the lamp
post and the fog, in the direction of the M7b concepts 1-2 (park_crest_b s41/s42): a lawn that runs to a real brow, the
ground falling away beyond it, roofs and bare trees below, the city 2-4 km off with its tops in the cloud base.

- Ground: a crest plateau (z = 0 where people stand, as M3's) inside an irregular rim; beyond the rim the lawn rolls
  over a convex brow and drops at about 32 degrees toward the view (+Y), 18 on the camera side (where O19b rises out of
  the trees), 26 at the sides, easing to about 12 degrees far down. ground_z() is the one height function: the mesh,
  the paths, the trees and the walker (sets.hill_z is patched to hill_z here, M7 only) all read it.
- Surface: wet lawn (patchy, trodden and muddy near the path, a wet sheen, darker in hollows; brush and bracken on the
  steep slope), a gravel path with stone kerbs from the back edge to a viewpoint on the brow (a short stone retaining
  wall there, a bench), puddles on the path and in a few hollows (no standing water body), grass blades along the brow
  and the path edges.
- Trees: firs as volumetric prototypes (whorls of branches carrying needle sprays at many angles, outward normals; no
  flat sprays), placed in irregular groups: big ones framing the crest, young firs on the back slope round O19b's rise,
  firs on the flanks of the drop, bare deciduous trees (recursive branches and twigs) below the brow in the view, more
  of both far down the slope, a few houses (roofs) in the valley fog. All seeded (gb.rng "m7c_*").
- Far: the generated plate (scripts/m7c_plate.py: far plate 1 extended, the ridges plates as the far tree lines) on a
  cylinder 2 km out, emissive, mapped by angle (px per degree, horizon row), through the inverse of the view transform
  so it reads as generated; its top fades into the sky (the world's camera colour matched to it), its bottom into the
  valley fog. The 3D's fog is layered: distance and valley (below the crest) fog on every surface, coloured from the
  plate's horizon and mist band, a near haze volume that drifts, terrain-following fog curtains over the drop and in
  front of the plate's lower edge, drifting on the clock.
- Lamp post: a generic cast-iron park lamp (plinth, fluted shaft, collars, a four-sided glazed lantern under a cap and
  finial) carrying the M3 weatherproof outlet box; the box and Switch's plane stay exactly where M7b had them.
Nothing of Ever Present's is used here. Guardrails: no water body (puddles only), no boats, no tower or landmark; the
plate was checked take by take (config/m7c_plate.json, log/prompts/m7c_park.md).
"""
import json
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

import aso_kit as K
import aso_props as PR
import gb
import sets as S

ROOT = gb.ROOT
CFG = json.loads((ROOT / "config" / "look_m7.json").read_text())
P = CFG["m7c"]
G = P["ground"]
TEX = ROOT / "assets" / "gen" / "tex" / "m7c"
STATE = {}


def _old_hill_z(x, y):
    """M3's dome (blender/sets.py hill_z), for where M7b had the lamp post and Switch."""
    return -32.0 * (1.0 - math.exp(-(x * x + y * y) / 3600.0))


# ---------------------------------------------------------------- the ground

def _profile_table():
    """z(s) per direction (front, back, side): s is the distance past the rim (m, negative inside). A convex roll from
    -roll to 0, then the slope eases to its steep value over 3 m, and eases again to the far slope further down."""
    s = np.arange(-15.0, 320.0, 0.05)
    out = {}
    for k in ("front", "back", "side"):
        d = G["profile"][k]
        g = np.zeros_like(s)
        p, w, h = 2.2, d["roll"], d["roll_drop"]
        m = (s > -w) & (s <= 0)
        g[m] = h * p / w * ((s[m] + w) / w) ** (p - 1)
        g0 = h * p / w
        u = np.clip(s / 3.0, 0, 1)
        u = u * u * (3 - 2 * u)
        v = np.clip((s - d["far_from"]) / d["far_width"], 0, 1)
        v = v * v * (3 - 2 * v)
        gs = g0 + (d["steep"] - g0) * u + (d["far"] - d["steep"]) * v
        g[s > 0] = gs[s > 0]
        out[k] = -np.cumsum(g) * 0.05
    return s, out


_S, _Z = _profile_table()


def rim(th):
    """Distance from the crest's centre to its rim (the brow) at angle th (radians, from +X toward +Y)."""
    c, s = np.cos(th), np.sin(th)
    rx = np.where(s > 0, G["r_front"], G["r_back"])
    r = 1.0 / np.sqrt((c / G["r_side"]) ** 2 + (s / rx) ** 2)
    for a, f, ph in G["wobble"]:
        r = r + a * np.sin(f * th + ph)
    return r


def rim_s(x, y):
    """(s, th): distance past the rim and the angle round the crest's centre."""
    cx, cy = G["centre"]
    dx, dy = np.asarray(x, float) - cx, np.asarray(y, float) - cy
    th = np.arctan2(dy, dx)
    return np.hypot(dx, dy) - rim(th), th


def _relief(x, y):
    a = 0.6 * np.sin(0.71 * x + 0.33 * y) * np.sin(0.52 * y - 0.21 * x + 1.0) + 0.4 * np.sin(1.9 * x + 1.3 * y + 0.5)
    return G["relief"] * a


def _seg_dist(px, py, pts):
    """Distance from points to a polyline [(x, y), ...]."""
    d = np.full(np.shape(px), 1e9)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        ux, uy = bx - ax, by - ay
        L2 = ux * ux + uy * uy
        t = np.clip(((px - ax) * ux + (py - ay) * uy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(px - (ax + t * ux), py - (ay + t * uy)))
    return d


def layout():
    """The path's centreline and the viewpoint (computed once from the walker's line, which the M5c3 walker follows:
    blender/perf_crowd.py walker, (1, -3) -> (3.2, 12))."""
    if "path" in STATE:
        return STATE
    p0, p1 = np.array([1.0, -3.0]), np.array([3.2, 12.0])
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    # the viewpoint's wall stands kerb_s inside the rim, on the walker's line
    t = np.linspace(0, 12, 2401)
    pts = p1[None] + t[:, None] * d[None]
    s, _ = rim_s(pts[:, 0], pts[:, 1])
    k = int(np.argmax(s >= P["viewpoint"]["kerb_s"]))
    wall = pts[k]
    rp = P["viewpoint"]["radius"]
    centre = wall - d * rp
    path = [tuple(v) for v in P["path"]["back"]] + [tuple(p0), tuple(centre - d * (rp - 0.4))]
    STATE.update(path=path, centre=tuple(centre), dir=tuple(d), rp=rp)
    return STATE


def flat_mask(x, y):
    """1 on the path's bed and the viewpoint terrace (they stay level where the lawn rolls toward the brow)."""
    L = layout()
    hw = P["path"]["width"] / 2
    dp = _seg_dist(x, y, L["path"])
    m = 1 - np.clip((dp - hw - 0.35) / 1.2, 0, 1)
    m = m * m * (3 - 2 * m)
    O = M7D.get("o19b", {}) if M7D.get("on") else {}
    if O.get("back_follow"):
        # M7d (the coordinator's point 7): on the back slope the bed follows the lawn's roll over the crest's back edge
        # instead of staying level, which left it standing proud as a flat-topped block seen from O19b's start; level
        # from y0 on (the walker's line, the crowd, the terrace: unchanged)
        y0, y1 = O["back_follow"]
        w = np.clip((np.asarray(y, float) - y0) / (y1 - y0), 0, 1)
        m = m * (w * w * (3 - 2 * w))
    cx, cy = L["centre"]
    dc = np.hypot(np.asarray(x) - cx, np.asarray(y) - cy)
    mt = (dc < L["rp"] + 0.12).astype(float)
    return np.maximum(m, mt)


def people_mask(x, y):
    (x0, x1), (y0, y1) = G["flat_zone"]
    fx = np.clip(np.minimum(np.asarray(x) - x0, x1 - np.asarray(x)) / 1.5, 0, 1)
    fy = np.clip(np.minimum(np.asarray(y) - y0, y1 - np.asarray(y)) / 1.5, 0, 1)
    return np.minimum(fx, fy)


def ground_z(x, y):
    """The park's height at (x, y) (vectorised)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    s, th = rim_s(x, y)
    sn, c = np.sin(th), np.cos(th)
    wf, wb, ws = np.clip(sn, 0, 1) ** 2, np.clip(-sn, 0, 1) ** 2, c * c
    z = wf * np.interp(s, _S, _Z["front"]) + wb * np.interp(s, _S, _Z["back"]) + ws * np.interp(s, _S, _Z["side"])
    fm = flat_mask(x, y)
    inside = s < P["viewpoint"]["kerb_s"] + 0.05
    z = np.where(inside, z * (1 - fm), z)
    rel = _relief(x, y) * (1 - people_mask(x, y)) * (1 - fm) * np.clip(1 - s / 2.0, 0, 1)
    return z + rel


def hill_z(x, y):
    """sets.hill_z's M7c replacement (scalar): the ground, plus 2 cm on the path's bed and the terrace, as the M5c3
    walker stood on M3's plank (blender/perf_crowd.py keys 0.02 m before y 8.3 and hill_z after)."""
    return float(ground_z(x, y) + 0.02 * (flat_mask(x, y) > 0.99))


# ---------------------------------------------------------------- materials (node helpers from look.py)

def _look():
    import look
    return look


def fog_colours():
    """(level, valley, sky) scene-linear: from the plate (assets/gen/tex/m7c/park_backdrop.json), so the 3D's fog
    meets the plate's horizon haze and mist band; config fallbacks before the plate exists."""
    f = TEX / "park_backdrop.json"
    if f.exists():
        j = json.loads(f.read_text())
        return j.get("level_lin", j["fog_lin"]), j["fog_lin"], j["sky_lin"]
    lin = lambda h: list(gb.lin(h)[:3])  # noqa: E731
    return lin(P["fog"]["level"]), lin(P["fog"]["valley"]), lin(P["fog"]["sky"])


def park_fog(nb, shader, dist=None, emit=1.0):
    """Layered fog on a surface: distance from the camera and depth below the crest (the valley fills with fog), its
    colour from the plate's horizon haze at the crest's level to its mist band below."""
    F = P["fog"]
    level, valley, _ = fog_colours()
    cam = nb.n("ShaderNodeCameraData")
    ex = nb.math("EXPONENT", nb.math("DIVIDE", cam.outputs["View Distance"], -(dist or F["dist"])))
    Pw, _ = nb.world_pos()
    _, _, z = nb.sep(Pw)
    below = nb.math("MAXIMUM", nb.math("SUBTRACT", F["valley_top"], z), 0.0)
    ev = nb.math("EXPONENT", nb.math("DIVIDE", below, -F["valley_scale"]))
    f = nb.math("SUBTRACT", 1.0, nb.mul(ex, ev))
    w = nb.maprange(z, F["valley_top"], F["valley_top"] - F["valley_blend"], 0.0, 1.0, smooth=True)
    col = nb.mix(w, tuple(level) + (1.0,), tuple(valley) + (1.0,))
    e = nb.n("ShaderNodeEmission")
    nb.put(e.inputs["Color"], col)
    e.inputs["Strength"].default_value = emit
    mx = nb.n("ShaderNodeMixShader")
    nb.put(mx.inputs[0], f)
    nb.nt.links.new(shader, mx.inputs[1])
    nb.nt.links.new(e.outputs[0], mx.inputs[2])
    return mx.outputs[0]


def _mat(name):
    m = bpy.data.materials.new(name)
    m["m7"] = True
    return m


def lawn_mat():
    """Wet park grass: patchy olive and dark green with tussocks, trodden and muddy toward the path, a wet sheen
    (lower roughness in the hollows), fine blades in the bump; brush and bracken where the ground is steep."""
    L = _look()
    m = _mat("m7c_lawn")
    nb = L.NB(m)
    Pw, N = nb.world_pos()
    _, _, nz = nb.sep(N)
    n1, _ = nb.noise(Pw, 0.35, 4.0, 0.6)
    n2, _ = nb.noise(Pw, 2.2, 3.0, 0.6)
    n3, _ = nb.noise(Pw, 26.0, 2.0, 0.65)
    n4, _ = nb.noise(Pw, 140.0, 1.0, 0.7)
    n5, _ = nb.noise(Pw, 0.08, 2.0, 0.5)
    t = nb.madd(n1, 0.45, nb.madd(n2, 0.35, nb.mul(n5, 0.2)))
    grass = nb.ramp(t, [(0.3, "#1f2e16"), (0.42, "#33461f"), (0.55, "#47602b"), (0.66, "#5a6a34"), (0.78, "#6b6a3e"), (0.9, "#5a5034")])
    # trodden: bare, muddy grass near the path (attribute 'trod' on the mesh: 1 at the path's edge)
    at = nb.n("ShaderNodeAttribute", attribute_name="trod")
    mud = nb.ramp(n2, [(0.3, "#2a241b"), (0.7, "#3e3626")])
    trod = nb.mul(at.outputs["Fac"], nb.maprange(n3, 0.3, 0.7, 0.55, 1.0))
    col = nb.mix(trod, grass, mud)
    # steep ground: brush and dead bracken
    steep = nb.maprange(nz, 0.93, 0.8, 0.0, 1.0, smooth=True)
    brush = nb.ramp(n2, [(0.25, "#2a2116"), (0.5, "#4a3420"), (0.7, "#5a4024"), (0.85, "#2e3320")])
    col = nb.mix(nb.mul(steep, nb.maprange(n3, 0.25, 0.6, 0.6, 1.0)), col, brush)
    v = nb.madd(n4, 0.3, 0.8)
    col = nb.mix(1.0, col, nb.comb(v, v, v), "MULTIPLY")
    wet = nb.maprange(n5, 0.35, 0.65, 0.42, 0.78)
    b = nb.principled(col, wet, spec=0.3, normal=nb.bump(nb.madd(n4, 0.6, nb.mul(n3, 0.4)), 0.35, 0.01))
    b.inputs["Coat Weight"].default_value = 0.08
    b.inputs["Coat Roughness"].default_value = 0.3
    nb.out(park_fog(nb, b.outputs[0]))
    return m


def gravel_mat():
    L = _look()
    m = _mat("m7c_gravel")
    nb = L.NB(m)
    Pw, _ = nb.world_pos()
    d, c, _ = nb.voronoi(Pw, 70.0)
    d2, c2, _ = nb.voronoi(Pw, 26.0)
    s1, _, _ = nb.sep(c)
    s2, _, _ = nb.sep(c2)
    n1, _ = nb.noise(Pw, 1.6, 3.0, 0.6)
    t = nb.madd(s1, 0.3, nb.madd(s2, 0.25, nb.madd(n1, 0.35, 0.28)))
    col = nb.ramp(t, [(0.25, "#38342e"), (0.55, "#5a554b"), (0.8, "#79726a")])
    wetn, _ = nb.noise(Pw, 0.8, 2.0, 0.5)
    wet = nb.maprange(wetn, 0.4, 0.62, 0.0, 1.0, smooth=True)
    col = nb.mix(nb.mul(wet, 0.45), col, nb.mix(1.0, col, (0.55, 0.55, 0.55, 1.0), "MULTIPLY"))
    h = nb.add(nb.maprange(d, 0.0, 0.5, 1.0, 0.0, smooth=True), nb.mul(nb.maprange(d2, 0.0, 0.5, 1.0, 0.0, smooth=True), 0.6))
    b = nb.principled(col, nb.maprange(wet, 0.0, 1.0, 0.6, 0.25), spec=0.45, normal=nb.bump(h, 0.55, 0.008))
    nb.out(park_fog(nb, b.outputs[0]))
    return m


def stone_mat():
    """Granite kerbs and the viewpoint's wall: grey, speckled, wet-darkened, a little moss in the joints."""
    L = _look()
    m = _mat("m7c_stone")
    nb = L.NB(m)
    Pw, N = nb.world_pos()
    _, _, nz = nb.sep(N)
    n1, _ = nb.noise(Pw, 4.0, 4.0, 0.6)
    n2, _ = nb.noise(Pw, 60.0, 2.0, 0.7)
    t = nb.madd(n1, 0.6, nb.mul(n2, 0.4))
    col = nb.ramp(t, [(0.3, "#4a4a46"), (0.6, "#6c6a64"), (0.85, "#8a8780")])
    mossy = nb.mul(nb.maprange(n1, 0.55, 0.75, 0.0, 1.0), nb.maprange(nz, 0.2, 0.9, 1.0, 0.3))
    col = nb.mix(nb.mul(mossy, 0.5), col, "#3e4a26")
    b = nb.principled(col, nb.madd(n2, 0.3, 0.4), spec=0.45, normal=nb.bump(n2, 0.3, 0.004))
    nb.out(park_fog(nb, b.outputs[0]))
    return m


def water_mat():
    """Puddles: a dark, still film that mirrors the sky, ripples from the drizzle (rings on the clock), its rim soft
    (UV v: 0 at the edge, 1 inside)."""
    L = _look()
    m = _mat("m7c_puddle")
    nb = L.NB(m)
    Pw, _ = nb.world_pos()
    clk = L.clock_node(nb)
    uv = nb.n("ShaderNodeUVMap", uv_map="UVMap")
    _, v, _ = nb.sep(uv.outputs[0])
    vec = nb.comb(*[nb.mul(c, 9.0) for c in nb.sep(Pw)[:2]], nb.mul(clk, 0.9))
    vor = nb.n("ShaderNodeTexVoronoi", voronoi_dimensions="3D")
    nb.put(vor.inputs["Vector"], vec)
    vor.inputs["Scale"].default_value = 1.0
    ring = nb.math("SINE", nb.mul(vor.outputs["Distance"], 40.0))
    fade = nb.maprange(vor.outputs["Distance"], 0.05, 0.35, 1.0, 0.0)
    h = nb.mul(ring, fade)
    b = nb.principled("#1d1e1d", 0.05, spec=0.6, normal=nb.bump(h, 0.08, 0.002))
    sh = park_fog(nb, b.outputs[0])
    tp = nb.n("ShaderNodeBsdfTransparent")
    mx = nb.n("ShaderNodeMixShader")
    nb.put(mx.inputs[0], nb.maprange(v, 0.0, 0.35, 0.0, 1.0, smooth=True))
    nb.nt.links.new(tp.outputs[0], mx.inputs[1])
    nb.nt.links.new(sh, mx.inputs[2])
    nb.out(mx.outputs[0])
    return m


def needles_mat(name, base, fog_fn, sky=None, sky_dir=None):
    """Fir needles on the M7c prototypes' sprays (UV: u from the spray's base 0 to its tip 1, v across, 0.5 on the
    twig): needles as a ragged comb along the twig, tapering to the tip, gaps between them; darker toward the inside,
    lighter tips; a little translucency for the backlight; per-tree tint. fog_fn(nb, shader) -> shader.
    M7d (FIRS_M7D on): a fringe of needles at each spray's edge, the colour from the mesh's ambient occlusion and its
    per-branch value, translucency strongest at the crown's skin, and 'sky' (a strength, None for the config's park
    value): the overcast's light from above on the needles that face it (an emission term on the shading normal, the
    occlusion and the albedo, under the fog), for forests whose world is kept dark so the people stay silhouettes."""
    if FIRS_M7D.get("on"):
        return _needles_m7d(name, base, fog_fn, FIRS_M7D["sky_park"] if sky is None else sky, sky_dir)
    L = _look()
    m = _mat(name)
    nb = L.NB(m)
    oi = nb.n("ShaderNodeObjectInfo")
    uv = nb.n("ShaderNodeUVMap", uv_map="UVMap")
    u, v, _ = nb.sep(uv.outputs[0])
    col_at = nb.n("ShaderNodeAttribute", attribute_name="shade")             # 0 inside the crown, 1 at its skin
    dv = nb.mul(nb.math("ABSOLUTE", nb.math("SUBTRACT", v, 0.5)), 2.0)
    du = nb.mul(nb.math("SUBTRACT", u, 0.55), 2.2)
    ell = nb.math("SUBTRACT", 1.0, nb.add(nb.mul(dv, dv), nb.mul(du, du)))          # 1 at the centre, 0 at the rim
    seed = nb.mul(oi.outputs["Random"], 17.0)
    clump, _ = nb.noise(nb.comb(nb.mul(u, 3.5), nb.mul(v, 3.0), seed), 1.0, 3.0, 0.6)
    fine, _ = nb.noise(nb.comb(nb.mul(u, 64.0), nb.mul(v, 46.0), seed), 1.0, 2.0, 0.7)
    dens = nb.add(nb.mul(ell, 0.9), nb.madd(clump, 0.7, nb.madd(fine, 0.5, -0.69)))
    keep = nb.math("GREATER_THAN", dens, 0.0)
    keep = nb.math("MAXIMUM", keep, nb.mul(nb.math("LESS_THAN", dv, 0.06), nb.math("LESS_THAN", nb.math("ABSOLUTE", du), 0.9)))
    tone = nb.madd(oi.outputs["Random"], 0.25, nb.madd(col_at.outputs["Fac"], 0.45, nb.madd(u, 0.18, 0.2)))
    col = nb.ramp(tone, [(0.15, L.tint(base, 0.5)), (0.5, base), (0.9, L.tint(base, 1.4))])
    b = nb.principled(col, 0.7, spec=0.35)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.put(tr.inputs["Color"], "#4e6a3a")
    mx = nb.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.35
    nb.nt.links.new(b.outputs[0], mx.inputs[1])
    nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    sh = fog_fn(nb, mx.outputs[0])
    tp = nb.n("ShaderNodeBsdfTransparent")
    mk = nb.n("ShaderNodeMixShader")
    nb.put(mk.inputs[0], keep)
    nb.nt.links.new(tp.outputs[0], mk.inputs[1])
    nb.nt.links.new(sh, mk.inputs[2])
    nb.out(mk.outputs[0])
    m.surface_render_method = "DITHERED"
    return m


def _needles_m7d(name, base, fog_fn, sky, sky_dir=None):
    F7 = FIRS_M7D
    L = _look()
    m = _mat(name)
    nb = L.NB(m)
    oi = nb.n("ShaderNodeObjectInfo")
    uv = nb.n("ShaderNodeUVMap", uv_map="UVMap")
    u, v, _ = nb.sep(uv.outputs[0])
    ao = nb.n("ShaderNodeAttribute", attribute_name="shade").outputs["Fac"]     # occlusion: 0 deep inside, 1 at the tips
    cl = nb.n("ShaderNodeAttribute", attribute_name="clump").outputs["Fac"]     # the branch's own value
    dv = nb.mul(nb.math("ABSOLUTE", nb.math("SUBTRACT", v, 0.5)), 2.0)
    du = nb.mul(nb.math("SUBTRACT", u, 0.55), 2.2)
    ell = nb.math("SUBTRACT", 1.0, nb.add(nb.mul(dv, dv), nb.mul(du, du)))
    seed = nb.mul(oi.outputs["Random"], 17.0)
    clump, _ = nb.noise(nb.comb(nb.mul(u, 3.5), nb.mul(v, 3.0), seed), 1.0, 3.0, 0.6)
    fine, _ = nb.noise(nb.comb(nb.mul(u, 64.0), nb.mul(v, 46.0), seed), 1.0, 2.0, 0.7)
    dens = nb.add(nb.mul(ell, 0.9), nb.madd(clump, 0.7, nb.madd(fine, 0.5, -0.69)))
    # the edge of each spray is a fringe of needles (slanted toward the tip, a little irregular), the core solid
    fr = F7["fringe"]
    inner = nb.math("GREATER_THAN", dens, fr["band"])
    phase = nb.add(nb.mul(u, fr["n"]), nb.add(nb.mul(dv, fr["slant"]), nb.mul(fine, fr["jitter"])))
    nid, _ = nb.white(nb.comb(nb.math("FLOOR", phase), seed, nb.math("GREATER_THAN", v, 0.5)))   # each needle its own length
    needle = nb.math("LESS_THAN", nb.math("FRACT", phase), fr["duty"])
    outer = nb.mul(nb.math("GREATER_THAN", dens, nb.mul(nb.madd(nid, 1.0 - fr["vary"], fr["vary"]), -fr["reach"])), needle)
    keep = nb.math("MAXIMUM", inner, outer)
    keep = nb.math("MAXIMUM", keep, nb.mul(nb.math("LESS_THAN", dv, 0.06), nb.math("LESS_THAN", nb.math("ABSOLUTE", du), 0.9)))
    T = F7["tone"]
    tone = nb.madd(oi.outputs["Random"], T["tree"], nb.madd(ao, T["ao"], nb.madd(cl, T["clump"], nb.madd(u, T["tip"], T["base"]))))
    col = nb.ramp(tone, [(0.05, L.tint(base, T["dark"])), (0.45, base), (0.95, L.tint(base, T["light"]))])
    b = nb.principled(col, 0.7, spec=0.35)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.put(tr.inputs["Color"], nb.mix(ao, F7["trans_inner"], F7["trans_outer"]))
    mx = nb.n("ShaderNodeMixShader")
    nb.put(mx.inputs[0], nb.mul(ao, F7["trans"]))
    nb.nt.links.new(b.outputs[0], mx.inputs[1])
    nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    lit = mx.outputs[0]
    if sky > 0:
        # the overcast is brightest overhead and toward the far view: a soft wrap from that direction on the crown
        # proxy's normal (world space), so each crown is lit as one volume (the side and top turned to the sky
        # lighter, the camera-facing middle and the skirt darker), times the occlusion (dark deep inside and under the
        # tiers), in a lit grey-green needle tone
        at = nb.n("ShaderNodeAttribute", attribute_name="pn")
        vt = nb.n("ShaderNodeVectorTransform", vector_type="NORMAL", convert_from="OBJECT", convert_to="WORLD")
        nb.nt.links.new(at.outputs["Vector"], vt.inputs[0])
        nm_ = nb.n("ShaderNodeVectorMath", operation="NORMALIZE")
        nb.nt.links.new(vt.outputs[0], nm_.inputs[0])
        dp = nb.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
        nb.nt.links.new(nm_.outputs[0], dp.inputs[0])
        sd = sky_dir or F7["sky_dir_park"]
        ln = math.sqrt(sum(c * c for c in sd))
        dp.inputs[1].default_value = tuple(c / ln for c in sd)
        f = nb.math("POWER", nb.math("MAXIMUM", nb.madd(dp.outputs["Value"], 0.5, 0.5), 0.0), F7["sky_pow"])
        e = nb.n("ShaderNodeEmission")
        tone_l = nb.ramp(nb.madd(cl, 0.5, nb.madd(oi.outputs["Random"], 0.3, 0.1)),
                         [(0.0, L.tint(F7["sky_tone"], 0.8)), (1.0, L.tint(F7["sky_tone"], 1.15))])
        nb.put(e.inputs["Color"], tone_l)
        nb.put(e.inputs["Strength"], nb.mul(nb.mul(f, nb.math("POWER", ao, F7["sky_ao_pow"])), sky))
        ad = nb.n("ShaderNodeAddShader")
        nb.nt.links.new(lit, ad.inputs[0])
        nb.nt.links.new(e.outputs[0], ad.inputs[1])
        lit = ad.outputs[0]
    sh = fog_fn(nb, lit)
    tp = nb.n("ShaderNodeBsdfTransparent")
    mk = nb.n("ShaderNodeMixShader")
    nb.put(mk.inputs[0], keep)
    nb.nt.links.new(tp.outputs[0], mk.inputs[1])
    nb.nt.links.new(sh, mk.inputs[2])
    nb.out(mk.outputs[0])
    m.surface_render_method = "DITHERED"
    return m


def bark_mat(name, base, fog_fn, spec=0.3, rough=0.85):
    L = _look()
    m = _mat(name)
    nb = L.NB(m)
    tc = nb.n("ShaderNodeTexCoord")
    x, y, z = nb.sep(tc.outputs["Object"])
    n1, _ = nb.noise(nb.comb(nb.mul(x, 40.0), nb.mul(y, 40.0), nb.mul(z, 4.0)), 1.0, 5.0, 0.6)
    col = nb.ramp(n1, [(0.3, L.tint(base, 0.55)), (0.7, L.tint(base, 1.15))])
    b = nb.principled(col, rough, spec=spec, normal=nb.bump(n1, 0.4, 0.01))
    nb.out(fog_fn(nb, b.outputs[0]))
    return m


def painted_mat(name, base, rough=0.6, metal=0.0):
    L = _look()
    m = _mat(name)
    nb = L.NB(m)
    Pw, _ = nb.world_pos()
    n1, _ = nb.noise(Pw, 9.0, 3.0, 0.6)
    col = nb.mix(1.0, base, nb.comb(*(nb.madd(n1, 0.14, 0.93),) * 3), "MULTIPLY")
    b = nb.principled(col, nb.madd(n1, 0.15, rough), metal=metal, spec=0.45)
    nb.out(park_fog(nb, b.outputs[0]))
    return m


# ---------------------------------------------------------------- geometry helpers

def _mesh(name, verts, faces, mats, mat_idx=None, uvs=None, attrs=None, smooth=False, normals=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    for mt in mats:
        me.materials.append(mt)
    if mat_idx is not None:
        me.polygons.foreach_set("material_index", np.asarray(mat_idx, np.int32))
    if smooth:
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    if uvs is not None:                      # per loop
        uv = me.uv_layers.new(name="UVMap")
        uv.data.foreach_set("uv", np.asarray(uvs, np.float32).ravel())
    for k, vals in (attrs or {}).items():
        arr = np.asarray(vals, np.float32)
        if arr.ndim == 2:
            a = me.attributes.new(k, "FLOAT_VECTOR", "POINT")
            a.data.foreach_set("vector", arr.ravel())
        else:
            a = me.attributes.new(k, "FLOAT", "POINT")
            a.data.foreach_set("value", arr)
    me.update()
    if normals is not None:
        try:
            me.normals_split_custom_set_from_vertices([tuple(n) for n in normals])
        except (AttributeError, RuntimeError):
            pass
    return me


def _obj(name, me, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, me)
    gb.link(o)
    o.location = loc
    return o


def grid_nodes(lo, hi, core, step, grow=1.18, maxstep=8.0):
    a, b = core
    mid = np.arange(a, b + 1e-6, step)
    left, x, st = [], a, step
    while x > lo:
        st = min(st * grow, maxstep)
        x -= st
        left.append(max(x, lo))
    right, x, st = [], b, step
    while x < hi:
        st = min(st * grow, maxstep)
        x += st
        right.append(min(x, hi))
    return np.concatenate([np.array(left[::-1]), mid, np.array(right)])


def build_ground(mat):
    E = G["extent"]
    xs = grid_nodes(E["x"][0], E["x"][1], E["core_x"], E["step"])
    ys = grid_nodes(E["y"][0], E["y"][1], E["core_y"], E["step"])
    X, Y = np.meshgrid(xs, ys)
    Z = ground_z(X, Y)
    nx, ny = len(xs), len(ys)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    faces = np.stack([a, b, c, d], 1)
    # trodden ground toward the path (the lawn shader's 'trod')
    dp = _seg_dist(X.ravel(), Y.ravel(), layout()["path"]) - P["path"]["width"] / 2
    trod = np.clip(1.0 - dp / 1.3, 0, 1) ** 1.5
    me = _mesh("m7c_ground", verts, faces, [mat], attrs={"trod": trod}, smooth=True)
    o = _obj("m7c_ground", me)
    return o, len(verts)


def _path_frame(pts, step):
    """Resample a polyline every step m: points, unit tangents, left normals."""
    pts = np.asarray(pts, float)
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0], np.cumsum(L)])
    t = np.arange(0, cum[-1] + 1e-6, step)
    px = np.interp(t, cum, pts[:, 0])
    py = np.interp(t, cum, pts[:, 1])
    # smooth the corners a little
    k = np.ones(9) / 9
    if len(px) > 12:
        px = np.concatenate([px[:4], np.convolve(px, k, "same")[4:-4], px[-4:]])
        py = np.concatenate([py[:4], np.convolve(py, k, "same")[4:-4], py[-4:]])
    tx, ty = np.gradient(px), np.gradient(py)
    n = np.hypot(tx, ty)
    tx, ty = tx / n, ty / n
    return np.stack([px, py], 1), np.stack([tx, ty], 1), np.stack([-ty, tx], 1)


def build_path(gravel, stone, rng):
    """The gravel path (a slightly crowned strip 1.5 cm over the ground) with granite kerbs along both edges, and the
    viewpoint terrace at its end: a gravel disc, a kerb round its camera side, a short retaining wall of stone
    blocks along its brow side (the ground falls away beyond it), a bench."""
    L = layout()
    hw = P["path"]["width"] / 2
    c, tg, nm = _path_frame(L["path"], 0.25)
    acr = np.linspace(-1, 1, 7)
    verts, faces, uvs = [], [], []
    for i in range(len(c)):
        for j, a in enumerate(acr):
            x, y = c[i] + nm[i] * a * hw
            verts.append((x, y, float(ground_z(x, y)) + 0.015 + 0.008 * (1 - a * a)))
    n = len(acr)
    for i in range(len(c) - 1):
        for j in range(n - 1):
            faces.append((i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j))
    # the terrace: a disc
    cx, cy = L["centre"]
    rp = L["rp"]
    base = len(verts)
    rings, segs = 6, 48
    verts.append((cx, cy, 0.025))
    for r in range(1, rings + 1):
        for k in range(segs):
            a = 2 * math.pi * k / segs
            rr = rp * r / rings
            verts.append((cx + rr * math.cos(a), cy + rr * math.sin(a), 0.025 - 0.006 * (r / rings) ** 2))
    for k in range(segs):
        faces.append((base, base + 1 + k, base + 1 + (k + 1) % segs))
    for r in range(1, rings):
        o0, o1 = base + 1 + (r - 1) * segs, base + 1 + r * segs
        for k in range(segs):
            faces.append((o0 + k, o1 + k, o1 + (k + 1) % segs, o0 + (k + 1) % segs))
    me = _mesh("m7c_path", verts, faces, [gravel], smooth=True)
    _obj("m7c_path", me)
    # kerbs: granite slabs along both edges of the path (not across the terrace), some missing, a little askew
    b = gb.Builder([stone])
    kerbs = 0
    tlen = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
    for side in (-1, 1):
        s = 0.2
        while s < tlen[-1] - 0.5:
            ln = rng.uniform(0.45, 0.8)
            mid = s + ln / 2
            i = int(np.searchsorted(tlen, mid))
            i = min(i, len(c) - 1)
            p = c[i] + nm[i] * side * (hw + 0.06)
            ang = math.atan2(tg[i][1], tg[i][0]) + rng.uniform(-0.03, 0.03)
            if rng.random() > 0.05:
                z = float(ground_z(*p)) + 0.02 + rng.uniform(-0.01, 0.008)
                ta = p - tg[i] * ln / 2
                tb = p + tg[i] * ln / 2
                pitch = math.atan2(float(ground_z(*tb) - ground_z(*ta)), ln)
                import bmesh
                cube = bmesh.ops.create_cube(b.bm, size=1.0)
                Mk = (Matrix.Translation((p[0], p[1], z - 0.04)) @ Matrix.Rotation(ang, 4, "Z")
                      @ Matrix.Rotation(-pitch + rng.uniform(-0.03, 0.03), 4, "Y")
                      @ Matrix.Rotation(rng.uniform(-0.02, 0.02), 4, "X") @ Matrix.Diagonal((ln - 0.02, 0.13, 0.14, 1.0)))
                b._tag(cube["verts"], 0, Mk)
                kerbs += 1
            s += ln + rng.uniform(0.005, 0.03)
    # the terrace's rim: kerb toward the camera, a retaining wall toward the brow
    dx, dy = L["dir"]
    a_dir = math.atan2(dy, dx)
    wall = 0
    k = 0
    a = 0.0
    while a < 2 * math.pi:
        ln = rng.uniform(0.42, 0.6)
        da = ln / (rp + 0.12)
        aa = a + da / 2
        rel = math.atan2(math.sin(aa - a_dir), math.cos(aa - a_dir))
        px, py = cx + (rp + 0.12) * math.cos(aa), cy + (rp + 0.12) * math.sin(aa)
        if abs(rel) < math.radians(P["viewpoint"]["wall_deg"]):
            zb = float(ground_z(px + 0.3 * math.cos(aa), py + 0.3 * math.sin(aa)))
            top = 0.38 + rng.uniform(-0.02, 0.02)
            h = top - (zb - 0.3)
            b.box((px, py, top - h / 2), (ln - 0.015, 0.3, h), rot=(0, rng.uniform(-0.015, 0.015), aa + math.pi / 2))
            wall += 1
        elif rng.random() > 0.04 and not _on_brow_path(px, py):
            b.box((px, py, 0.0), (ln - 0.02, 0.13, 0.12), rot=(0, 0, aa + math.pi / 2))
        k += 1
        a += da + 0.008
    o = gb.mesh_obj("m7c_kerbs", b.to_mesh("m7c_kerbs"))
    _bevel(o, 0.012)
    bench(cx, cy, a_dir, rp)
    return kerbs, wall


def _bevel(o, w):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=w, segments=1, affect="EDGES", clamp_overlap=True)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False


def bench(cx, cy, a_dir, rp):
    """A park bench on the terrace's left side, facing the view: two dark cast ends, five wooden slats."""
    L = _look()
    wood = L.wood(_mat("m7c_bench_wood"), "#5a4632", 0.09, 1.8, rough=0.55, coat=0.15)
    wood["m7"] = True
    iron = painted_mat("m7c_bench_iron", "#1e2220", 0.5, 0.4)
    b = PR.B([wood, iron])
    side = np.array([-math.sin(a_dir), math.cos(a_dir)])     # left of the walker's line
    fwd = np.array([math.cos(a_dir), math.sin(a_dir)])
    p = np.array([cx, cy]) + side * (rp * 0.55) - fwd * 0.2
    rot = a_dir - math.pi / 2                                  # the bench's +Y faces the view
    for sx in (-0.75, 0.75):
        b.bx((sx, 0.0, 0.22), (0.06, 0.5, 0.44), 1)
        b.bx((sx, 0.22, 0.62), (0.05, 0.06, 0.5), 1, rot=(0.25, 0, 0))
    for k in range(3):
        b.bx((0, -0.18 + 0.15 * k, 0.45), (1.62, 0.12, 0.035), 0)
    for k in range(2):
        b.bx((0, 0.26 + 0.03 * k, 0.6 + 0.15 * k), (1.62, 0.035, 0.11), 0, rot=(0.25, 0, 0))
    o = b.obj("m7c_bench", None, (p[0], p[1], 0.025), rot)
    return o


def puddles(mat, rng):
    """Small puddles on the path and the terrace and in a few hollows of the lawn beside the path: noisy outlines,
    0.3-1.1 m, 3 mm over the surface, a soft rim (UV v 0 at the edge)."""
    L = layout()
    c, tg, nm = _path_frame(L["path"], 0.25)
    spots = []
    for f, off, sz in P["puddles"]["path"]:
        i = int(f * (len(c) - 1))
        spots.append((c[i] + nm[i] * off, sz, 0.018))
    cx, cy = L["centre"]
    spots.append((np.array([cx - 0.5, cy - 0.6]), 0.5, 0.03))
    for f, off, sz in P["puddles"]["lawn"]:
        i = int(f * (len(c) - 1))
        spots.append((c[i] + nm[i] * off, sz, 0.004))
    verts, faces, uvs = [], [], []
    for (px, py), sz, lift in spots:
        z = float(ground_z(px, py)) + lift
        n, base = 28, len(verts)
        ph = rng.uniform(0, 6.28, 3)
        verts.append((px, py, z))
        for k in range(n):
            a = 2 * math.pi * k / n
            r = sz * 0.5 * (1 + 0.22 * math.sin(2 * a + ph[0]) + 0.12 * math.sin(3 * a + ph[1]) + 0.07 * math.sin(5 * a + ph[2]))
            verts.append((px + r * math.cos(a) * 1.3, py + r * math.sin(a) * 0.8, z))
        for k in range(n):
            faces.append((base, base + 1 + k, base + 1 + (k + 1) % n))
            uvs += [(0.5, 1.0), (0.5, 0.0), (0.5, 0.0)]
    me = _mesh("m7c_puddles", verts, faces, [mat], uvs=uvs)
    o = _obj("m7c_puddles", me)
    o.visible_shadow = False
    return len(spots)


def grass_fringe(mat, rng):
    """Blades along the brow (silhouetted against the fog) and along the path's edges (the closes at foot level)."""
    verts, faces = [], []

    def blade(x, y, z, h, lean, yaw, w=0.006):
        b0 = len(verts)
        dx, dy = math.cos(yaw), math.sin(yaw)
        tip = (x + lean * h * math.cos(yaw + 1.2), y + lean * h * math.sin(yaw + 1.2), z + h)
        verts.extend([(x - w * dx, y - w * dy, z - 0.01), (x + w * dx, y + w * dy, z - 0.01),
                      ((x + tip[0]) / 2 + 0.3 * w * dx, (y + tip[1]) / 2 + 0.3 * w * dy, z + 0.55 * h), tip])
        faces.extend([(b0, b0 + 1, b0 + 2), (b0, b0 + 2, b0 + 3)])
    F = P["fringe"]
    th = np.linspace(math.radians(F["brow_deg"][0]), math.radians(F["brow_deg"][1]), F["brow_n"])
    L = layout()
    cx0, cy0 = G["centre"]
    for t in th:
        for _ in range(F["per_point"]):
            r = float(rim(t)) + rng.uniform(*F["brow_s"])
            x, y = cx0 + r * math.cos(t), cy0 + r * math.sin(t)
            if np.hypot(x - L["centre"][0], y - L["centre"][1]) < L["rp"] + 0.5:
                continue
            blade(x, y, float(ground_z(x, y)), rng.uniform(0.05, 0.16), rng.uniform(0.1, 0.5), rng.uniform(0, 6.28))
    c, tg, nm = _path_frame(L["path"], 0.05)
    hw = P["path"]["width"] / 2
    for i in range(len(c)):
        if c[i][1] < F["path_y"][0] or c[i][1] > F["path_y"][1]:
            continue
        for side in (-1, 1):
            for _ in range(F["path_per"]):
                p = c[i] + nm[i] * side * (hw + 0.16 + rng.uniform(0, 0.25)) + tg[i] * rng.uniform(-0.03, 0.03)
                blade(p[0], p[1], float(ground_z(*p)), rng.uniform(0.04, 0.11), rng.uniform(0.1, 0.6), rng.uniform(0, 6.28))
    me = _mesh("m7c_fringe", verts, faces, [mat], smooth=True)
    o = _obj("m7c_fringe", me)
    o.visible_shadow = False
    return len(faces) // 2


def fringe_mat():
    L = _look()
    m = _mat("m7c_blades")
    nb = L.NB(m)
    Pw, _ = nb.world_pos()
    n1, _ = nb.noise(Pw, 3.0, 2.0, 0.6)
    col = nb.ramp(n1, [(0.3, "#1e2a16"), (0.6, "#34442a"), (0.85, "#5a5634")])
    b = nb.principled(col, 0.55, spec=0.35)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.put(tr.inputs["Color"], "#4a5a30")
    mx = nb.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.3
    nb.nt.links.new(b.outputs[0], mx.inputs[1])
    nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    nb.out(park_fog(nb, mx.outputs[0]))
    return m


# ---------------------------------------------------------------- firs and bare trees

FIR_PROTOS = {}
BARE_PROTOS = {}
# M7d (config/look_m7.json m7d; human interventions 23): the weak points' fixes, on whenever m7d.on is
M7D = CFG.get("m7d", {})
FIRS_M7D = M7D.get("firs", {}) if M7D.get("on") else {}


def fir_mesh(k, mats, name="fir"):
    """One fir prototype, 1 m tall, crown radius about CR (0.14) at its foot: a tapered trunk; whorls of branches
    (each a drooping rachis) carrying needle sprays at many angles round the branch (level, side shoots, hanging
    curtains on the cedar-like ones), so the crown has depth from every side; normals point out of the crown, and a
    'shade' attribute runs 0 deep inside to 1 at the skin. k < 6: Douglas-fir-like (open, irregular, tips upturned);
    k >= 6: cedar- and hemlock-like (denser, drooping)."""
    r = gb.rng(f"m7c_fir_{k}")
    douglas = k < 6
    verts, faces, uvs, mi, norms, shade = [], [], [], [], [], []
    # M7d (human interventions 23, weak point 1; decisions 42): the same crowns (M7c's seeded draws untouched; M7d's own
    # values come from a second stream, gb.rng m7d_fir_k), shaded as volumes: per-vertex normals blended from an
    # ellipsoid proxy of the whole crown and the branch tier (the tops of the sprays face the sky, the hanging curtains
    # face down and out), a 'shade' that is ambient occlusion (dark deep in the crown and under the tiers, light at the
    # tips), a 'clump' value per branch (value variation between clusters), and the branches themselves as thin tubes
    F7 = FIRS_M7D if FIRS_M7D.get("on") else None
    rd = gb.rng(f"m7d_fir_{k}")
    clump, pnv = [], []

    def quad(a, b_, c, d, uv4, mat, nrm, sh, cl=0.5, pn=None):
        i = len(verts)
        verts.extend([a, b_, c, d])
        faces.append((i, i + 1, i + 2, i + 3))
        uvs.extend(uv4)
        mi.append(mat)
        norms.extend(nrm if isinstance(nrm, list) else [nrm] * 4)
        shade.extend(sh if isinstance(sh, list) else [sh] * 4)
        clump.extend([cl] * 4)
        pn = nrm if pn is None else pn
        pnv.extend(pn if isinstance(pn, list) else [pn] * 4)
    # trunk
    nseg, ns = 10, 7
    lean = Vector((r.uniform(-0.02, 0.02), r.uniform(-0.02, 0.02), 0))
    rings = []
    for j in range(nseg + 1):
        t = j / nseg
        c = Vector((0, 0, -0.03 + 1.03 * t)) + lean * t * t + Vector((0.004 * math.sin(9 * t + k), 0.004 * math.cos(7 * t), 0))
        rad = 0.016 * (1 - t) ** 1.1 + 0.0015
        rings.append([c + Vector((rad * math.cos(2 * math.pi * q / ns), rad * math.sin(2 * math.pi * q / ns), 0)) for q in range(ns)])
    for j in range(nseg):
        for q in range(ns):
            a, b_ = rings[j][q], rings[j][(q + 1) % ns]
            c, d = rings[j + 1][(q + 1) % ns], rings[j + 1][q]
            nrm = ((a + b_) / 2 - Vector((0, 0, a.z))).normalized()
            quad(a, b_, c, d, [(0, 0), (1, 0), (1, 1), (0, 1)], 1, tuple(nrm), 0.0)
    z0 = r.uniform(0.07, 0.16) if douglas else r.uniform(0.04, 0.09)
    whorls = int(r.uniform(32, 42))
    levels = []
    for wi in range(whorls):
        t = min(1.0, max(0.0, (wi + r.uniform(-0.3, 0.3)) / (whorls - 1)))
        levels.append((t, False))
        if t < 0.9:
            levels.append((min(1.0, t + 0.5 / (whorls - 1)), True))      # short branches between the whorls
    for t, inter in levels:
        z = z0 + (0.985 - z0) * t
        crown = (1.0 - t) ** (0.85 if douglas else 0.95) * (0.92 + 0.16 * math.sin(6.1 * t + 1.7 * k))
        nb = (int(r.uniform(2, 4)) if inter else int(r.uniform(5, 8))) if t < 0.85 else 4
        a0 = r.uniform(0, 2 * math.pi)
        for bi in range(nb):
            if r.random() < (0.16 if douglas else 0.08) and t < 0.92:
                continue
            a = a0 + 2 * math.pi * bi / nb + r.uniform(-0.3, 0.3)
            L = max(0.006, 0.14 * crown * r.uniform(0.5, 1.2) * (r.uniform(0.45, 0.75) if inter else 1.0))
            d = Vector((math.cos(a), math.sin(a), 0))
            side = Vector((-d.y, d.x, 0))
            e0 = math.radians((r.uniform(-2, 16) if douglas else r.uniform(-14, 4)) + 8 * t)
            droop = r.uniform(0.2, 0.55) * (1.25 - t) * (0.9 if douglas else 1.35)
            upt = r.uniform(0.05, 0.22) if douglas else 0.0
            base = Vector((lean.x * z * z, lean.y * z * z, z))

            def rach(u):
                return base + d * (u * L) + Vector((0, 0, L * (u * math.tan(e0) - droop * u * u + upt * u ** 3)))
            cl = rd.random() if F7 else 0.5                              # M7d: this branch's value
            if F7 and F7.get("branches") and L > F7["branch_min"]:
                _branch_tube(quad, rach, L, F7)
            M = 6 + int(L / 0.14 * 9)
            for s in range(M):
                u = (s + r.uniform(0.25, 0.75)) / M
                p = rach(u)
                tang = (rach(min(1, u + 0.05)) - rach(max(0, u - 0.05))).normalized()
                ls = L / M * r.uniform(1.5, 2.1) * (1.15 - 0.35 * u)
                ws = ls * r.uniform(0.7, 1.0)
                out = (p - Vector((0, 0, p.z))).normalized() if p.xy.length > 1e-5 else d
                sh = min(1.0, 0.35 + 0.75 * u)
                # a fuzzy cluster: sprays fanned round the branch at many angles (level, sideways, up, hanging)
                specs = [(r.uniform(-0.5, 0.5), r.uniform(0, math.pi)) for _ in range(3)]
                specs.append((r.uniform(0.6, 1.1) * (1 if r.random() < 0.5 else -1), r.uniform(0, math.pi)))
                if not douglas or r.random() < 0.7:
                    specs.append(("hang", r.uniform(0, math.pi)))
                for yaw, roll in specs:
                    if yaw == "hang":
                        dirv = (tang * (0.8 if douglas else 0.45) + Vector((0, 0, -1.0)) + out * 0.3).normalized()
                        lsh = ls * (0.8 if douglas else 1.25)
                    else:
                        dirv = (Matrix.Rotation(yaw, 3, "Z") @ tang).normalized()
                        dirv.z += r.uniform(-0.08, 0.12) + (0.12 if douglas and u > 0.6 else 0)
                        dirv.normalize()
                        lsh = ls
                    wv = dirv.cross(Vector((0, 0, 1)))
                    if wv.length < 1e-4:
                        wv = side.copy()
                    wv.normalize()
                    wv = Matrix.Rotation(roll, 3, dirv) @ wv
                    q0 = p - dirv * lsh * 0.08
                    q1 = p + dirv * lsh
                    hw = ws * 0.5
                    nrm = (out * 0.75 + Vector((0, 0, 0.45)) + dirv.cross(wv).normalized() * 0.2).normalized()
                    q4 = [q0 - wv * hw, q0 + wv * hw, q1 + wv * hw * 0.6, q1 - wv * hw * 0.6]
                    if F7:
                        nrm, sh4, pn4 = _spray_shading(q4, out, dirv, wv, yaw == "hang", t, crown, z0, F7)
                        quad(*q4, [(0, 0), (0, 1), (1, 1), (1, 0)], 0, nrm, sh4, cl, pn4)
                        continue
                    quad(*q4, [(0, 0), (0, 1), (1, 1), (1, 0)], 0, tuple(nrm), sh)
    attrs = {"shade": shade}
    if F7:
        attrs["clump"] = clump
        attrs["pn"] = [tuple(v) for v in pnv]                     # the crown proxy's normal (object space)
    me = _mesh(f"{name}_proto_{k}", verts, faces, mats, mat_idx=mi,
               uvs=[uv for uv in uvs], attrs=attrs, smooth=True, normals=norms)
    return me


def _spray_shading(q4, out, dirv, wv, hang, t, crown, z0, F7):
    """M7d: per-vertex normals and ambient occlusion for one spray. The normal blends an ellipsoid proxy of the crown
    (its top faces the sky, its skirt faces down), the branch tier (a spray's top faces up and out, a hanging curtain
    down and out) and a little of the spray's own facet (turned outward); the occlusion is the vertex's radial depth in
    the crown at its height (deep inside dark, the tips light) times a tier factor (hanging curtains sit under their
    branch)."""
    N = F7["normal"]
    up = Vector((0, 0, 1))
    zc = z0 + N["centre"] * (1 - z0)
    a2, b2 = N["a"] ** 2, (N["b"] * (1 - z0)) ** 2
    tier = (out * N["tier_out"] + up * (-N["hang_down"] if hang else N["top_up"])).normalized()
    fac = dirv.cross(wv).normalized()
    if fac.dot(out) < 0:
        fac = -fac
    rmax = max(0.012, 0.14 * 1.3 * crown)
    ao0, ao_hang = F7["ao"], F7["ao_hang"]
    nrms, shs, prs = [], [], []
    for v in q4:
        pr = Vector((v.x / a2, v.y / a2, (v.z - zc) / b2)).normalized()
        prs.append(tuple(pr))
        n = (pr * N["proxy"] + tier * N["tier"] + fac * N["facet"]).normalized()
        nrms.append(tuple(n))
        rv = min(1.0, v.xy.length / rmax)
        sh = (ao0 + (1 - ao0) * rv ** F7["ao_pow"]) * (ao_hang if hang else 1.0) * (F7["ao_low"] + (1 - F7["ao_low"]) * t)
        shs.append(max(0.0, min(1.0, sh)))
    return nrms, shs, prs


def _branch_tube(quad, rach, L, F7):
    """M7d: a branch's rachis as a thin tapering four-sided tube (bark), so the nearest firs show wood through the
    gaps between the sprays."""
    n_seg, sides = 5, 4
    r0 = F7["branch_r0"] + F7["branch_rk"] * L
    rings = []
    for j in range(n_seg + 1):
        u = j / n_seg
        c = rach(u)
        tg = (rach(min(1.0, u + 0.05)) - rach(max(0.0, u - 0.05))).normalized()
        a = tg.cross(Vector((0, 0, 1)))
        if a.length < 1e-5:
            a = Vector((1, 0, 0))
        a.normalize()
        b = tg.cross(a).normalized()
        rr = r0 * (1 - 0.8 * u)
        rings.append([(c + (a * math.cos(2 * math.pi * q / sides) + b * math.sin(2 * math.pi * q / sides)) * rr, c)
                      for q in range(sides)])
    for j in range(n_seg):
        for q in range(sides):
            p0, c0 = rings[j][q]
            p1, _ = rings[j][(q + 1) % sides]
            p2, c1 = rings[j + 1][(q + 1) % sides]
            p3, _ = rings[j + 1][q]
            nr = [tuple((p - c).normalized()) for p, c in ((p0, c0), (p1, c0), (p2, c1), (p3, c1))]
            quad(p0, p1, p2, p3, [(0, 0), (1, 0), (1, 1), (0, 1)], 1, nr, 0.3)


def fir_proto(k, mats, tag):
    key = (tag, k)
    me = FIR_PROTOS.get(key)
    try:
        ok = me is not None and bpy.data.meshes.get(me.name) == me
    except ReferenceError:
        ok = False
    if not ok:
        me = FIR_PROTOS[key] = fir_mesh(k, mats, f"m7c_{tag}")
    return me


def bare_mesh(k, mat):
    """A bare deciduous tree (maple- or alder-like, November), 1 m tall: a trunk forking into limbs, four more levels
    of branches (upward, spreading, the last drooping a little) and twigs, as thin 5-sided tubes.
    M7d (human interventions 23, weak point 3; config m7d.bare): thinner, with fewer of the finest branches and twigs,
    so the fog reads through them: the same seeded draws (the limbs keep their shapes); a second stream (gb.rng
    m7d_bare_k) decides which fine branches and twigs are kept, and the branches from the second level on are slimmer."""
    r = gb.rng(f"m7c_bare_{k}")
    B7 = M7D.get("bare", {}) if M7D.get("on") else {}
    rd = gb.rng(f"m7d_bare_{k}")
    verts, faces = [], []
    zmax = [0.0]

    def tube(a, b_, ra, rb, n=5, show=True):
        zmax[0] = max(zmax[0], a.z, b_.z)
        d = (b_ - a)
        if d.length < 1e-6 or not show:
            return
        q = d.normalized()
        u = q.cross(Vector((0, 0, 1)) if abs(q.z) < 0.95 else Vector((1, 0, 0))).normalized()
        v = q.cross(u)
        i0 = len(verts)
        for (c, rr) in ((a, ra), (b_, rb)):
            for j in range(n):
                ang = 2 * math.pi * j / n
                verts.append(tuple(c + (u * math.cos(ang) + v * math.sin(ang)) * rr))
        for j in range(n):
            faces.append((i0 + j, i0 + (j + 1) % n, i0 + n + (j + 1) % n, i0 + n + j))

    def branch(p, d, L, rad, lvl, show=True):
        if lvl > 5:
            return
        n_seg = 3
        pts = [p]
        dd = d.copy()
        for s in range(n_seg):
            dd = (dd + Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 0.12 - 0.07 * lvl))).normalized()
            pts.append(pts[-1] + dd * (L / n_seg))
        rs = B7.get("slim", 1.0) if B7 and lvl >= 2 else 1.0
        for s in range(n_seg):
            tube(pts[s], pts[s + 1], rs * rad * (1 - 0.25 * s / n_seg), rs * rad * (1 - 0.25 * (s + 1) / n_seg), show=show)
        if lvl == 5:
            for _ in range(int(r.uniform(2, 5))):
                a = pts[int(r.uniform(1, n_seg + 1))]
                tw = (dd + Vector((r.uniform(-0.8, 0.8), r.uniform(-0.8, 0.8), r.uniform(-0.2, 0.6)))).normalized()
                keep = show and (not B7 or rd.random() < B7["twig_keep"])
                tube(a, a + tw * L * r.uniform(0.25, 0.5), 0.0011 * (B7.get("twig_slim", 1.0) if B7 else 1.0), 0.0005, n=3,
                     show=keep)
            return
        nc = int(r.uniform(2, 4)) if lvl > 0 else int(r.uniform(2, 4))
        for c in range(nc):
            f = r.uniform(0.45, 1.0) if lvl > 0 else 1.0
            at = pts[min(n_seg, int(round(f * n_seg)))]
            ang = math.radians(r.uniform(22, 48))
            axis = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0)).normalized()
            nd = (Matrix.Rotation(ang, 3, axis.cross(dd).normalized() if axis.cross(dd).length > 1e-4 else Vector((1, 0, 0))) @ dd)
            nd = (Matrix.Rotation(2 * math.pi * c / nc + r.uniform(-0.4, 0.4), 3, dd) @ nd).normalized()
            ch = show
            if B7 and lvl + 1 >= B7["thin_from"]:
                ch = show and rd.random() < B7["keep"][str(lvl + 1)]
            branch(at, nd, L * r.uniform(0.6, 0.76), rad * r.uniform(0.55, 0.68), lvl + 1, ch)
    h_fork = r.uniform(0.25, 0.4)
    tube(Vector((0, 0, -0.03)), Vector((r.uniform(-0.02, 0.02), r.uniform(-0.02, 0.02), h_fork)), 0.026, 0.02, n=7)
    top = Vector((0, 0, h_fork))
    for c in range(int(r.uniform(2, 4))):
        a = 2 * math.pi * c / 3 + r.uniform(-0.5, 0.5)
        d = Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1.0)).normalized()
        branch(top, d, r.uniform(0.28, 0.38), 0.016, 1)
    me = _mesh(f"m7c_bare_proto_{k}", verts, faces, [mat], smooth=True)
    # normalise to 1 m tall (M7d: by the tree's full height, so thinning doesn't rescale it)
    zm = zmax[0] if B7 else max(v[2] for v in verts)
    me.transform(Matrix.Scale(1.0 / zm, 4))
    return me


def place(me, name, x, y, h, rad_scale=1.0, rot=None, rng=None, z=None):
    o = bpy.data.objects.new(name, me)
    gb.link(o)
    o.location = (x, y, float(ground_z(x, y)) - 0.15 if z is None else z)
    o.rotation_euler.z = rot if rot is not None else rng.uniform(0, 6.28)
    o.scale = (h * rad_scale, h * rad_scale, h)
    o.visible_shadow = False
    return o


def trees(fog_fn):
    """Every tree, by group (config m7c.trees): hand-placed firs framing the crest, then seeded scatters. Returns
    the placed list [(kind, x, y, h, radius)] for the clearance checks."""
    T = P["trees"]
    fir_m = [needles_mat("m7c_needles", T["needle_colour"], fog_fn), bark_mat("m7c_fir_bark", "#3a2c22", fog_fn)]
    if M7D.get("on") and M7D.get("bare"):
        # M7d (weak point 3): the bare trees paler and in more aerial perspective (a shorter fog distance), so the
        # fog reads through them from O20e
        B7 = M7D["bare"]
        bare_m = bark_mat("m7c_bare_bark", B7["colour"], lambda nb, sh: park_fog(nb, sh, dist=B7["fog_dist"]),
                          spec=B7["spec"], rough=B7["rough"])
    else:
        bare_m = bark_mat("m7c_bare_bark", "#4a463f", fog_fn)
    protos = [fir_proto(k, fir_m, "park") for k in range(10)]
    bares = [bare_mesh(k, bare_m) for k in range(T["bare_protos"])]
    rng = gb.rng("m7c_trees")
    placed = []
    L = layout()
    cam = np.array(P["cameras"]["wide"]["loc"])

    def brow_sightline(x, y):
        """z of the line from the wide's camera over the brow, at (x, y) (the corridor's trees stay near it)."""
        th = math.atan2(y - cam[1], x - cam[0])
        # the rim point on the camera's ray
        for dd in np.arange(5, 60, 0.25):
            px, py = cam[0] + dd * math.cos(th), cam[1] + dd * math.sin(th)
            if rim_s(px, py)[0] > 0.0:
                break
        zb = float(ground_z(px, py))
        D = math.hypot(x - cam[0], y - cam[1])
        return cam[2] + (zb - cam[2]) * D / dd

    def ok(x, y, rad, minsep):
        if any(math.hypot(x - q[1], y - q[2]) < minsep * (rad + q[4]) for q in placed):
            return False
        for (ex, ey, er) in T["keep_clear"]:
            if math.hypot(x - ex, y - ey) < er + rad:
                return False
        if _seg_dist(np.array([x]), np.array([y]), L["path"])[0] < P["path"]["width"] / 2 + 0.8 + rad * 0.5:
            return False
        return True

    def add(kind, x, y, h, k=None, z=None):
        if kind == "fir":
            me = protos[k if k is not None else int(rng.integers(0, 10))]
            rs = rng.uniform(0.9, 1.1)
            o = place(me, f"m7c_fir_{len(placed)}", x, y, h, rs, rng=rng, z=z)
            placed.append(("fir", x, y, h, 0.14 * h * rs))
        else:
            me = bares[int(rng.integers(0, len(bares)))]
            rs = rng.uniform(0.75, 1.0)
            o = place(me, f"m7c_bare_{len(placed)}", x, y, h, rs, rng=rng, z=z)
            placed.append(("bare", x, y, h, 0.35 * h * rs))
        return o
    for x, y, h, k in T["frame"]:
        add("fir", x, y, h, k)
    for g in T["groups"]:
        n, tries = 0, 0
        while n < g["n"] and tries < g["n"] * 60:
            tries += 1
            x, y = rng.uniform(*g["x"]), rng.uniform(*g["y"])
            s, th = rim_s(x, y)
            if not (g["s"][0] <= s <= g["s"][1]):
                continue
            if "dens" in g:
                dn = 0.5 + 0.5 * math.sin(0.09 * x + 1.3) * math.sin(0.07 * y + 0.4)
                if rng.random() > g["dens"] + (1 - g["dens"]) * dn:
                    continue
            h = rng.uniform(*g["h"])
            kind = g["kind"] if g["kind"] != "mix" else ("fir" if rng.random() < g.get("fir_share", 0.6) else "bare")
            if g.get("corridor") and abs(x - g["corridor"][0]) < g["corridor"][1]:
                if kind == "fir" and not g.get("firs_in_corridor"):
                    continue
                zg = float(ground_z(x, y))
                top = brow_sightline(x, y) + rng.uniform(*g["poke"])
                h = min(h, top - zg)
                if h < g["h"][0] * 0.6:
                    continue
            rad = (0.14 if kind == "fir" else 0.3) * h
            if not ok(x, y, rad, g.get("sep", 0.7)):
                continue
            add(kind, x, y, h)
            n += 1
    return placed, len(protos), len(bares)


def houses(rng, wall_mats, roof_mat):
    """A few houses far down the slope (roofs in the valley fog): boxes with gabled roofs, turned to the contour."""
    H = P["houses"]
    b = PR.B(wall_mats + [roof_mat])
    nroof = len(wall_mats)
    n, tries = 0, 0
    pts = []
    while n < H["n"] and tries < 2000:
        tries += 1
        x, y = rng.uniform(*H["x"]), rng.uniform(*H["y"])
        s, th = rim_s(x, y)
        if not (H["s"][0] <= s <= H["s"][1]) or any(math.hypot(x - a, y - c) < 22 for a, c in pts):
            continue
        z = float(ground_z(x, y))
        gx = float(ground_z(x + 1, y) - ground_z(x - 1, y))
        gy = float(ground_z(x, y + 1) - ground_z(x, y - 1))
        rot = math.atan2(gy, gx) + math.pi / 2 + rng.uniform(-0.2, 0.2)
        w, d, hh = rng.uniform(7, 10), rng.uniform(8, 12), rng.uniform(5, 7)
        pitch = math.radians(rng.uniform(28, 40))
        rh = w / 2 * math.tan(pitch)
        mw = int(rng.integers(0, nroof))
        M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z")
        verts = [(-w / 2, -d / 2, -2), (w / 2, -d / 2, -2), (w / 2, d / 2, -2), (-w / 2, d / 2, -2),
                 (-w / 2, -d / 2, hh), (w / 2, -d / 2, hh), (w / 2, d / 2, hh), (-w / 2, d / 2, hh),
                 (0, -d / 2 - 0.4, hh + rh), (0, d / 2 + 0.4, hh + rh)]
        import bmesh
        bm = b.bm
        vs = [bm.verts.new(M @ Vector(v)) for v in verts]
        for f, mi in (((0, 1, 5, 4), mw), ((1, 2, 6, 5), mw), ((2, 3, 7, 6), mw), ((3, 0, 4, 7), mw),
                      ((4, 5, 8), mw), ((6, 7, 9), mw)):
            bm.faces.new([vs[i] for i in f]).material_index = mi
        e0 = [bm.verts.new(M @ Vector(v)) for v in ((-w / 2 - 0.5, -d / 2 - 0.4, hh - 0.3), (0, -d / 2 - 0.4, hh + rh),
                                                     (0, d / 2 + 0.4, hh + rh), (-w / 2 - 0.5, d / 2 + 0.4, hh - 0.3))]
        e1 = [bm.verts.new(M @ Vector(v)) for v in ((0, -d / 2 - 0.4, hh + rh), (w / 2 + 0.5, -d / 2 - 0.4, hh - 0.3),
                                                     (w / 2 + 0.5, d / 2 + 0.4, hh - 0.3), (0, d / 2 + 0.4, hh + rh))]
        bm.faces.new(e0).material_index = nroof
        bm.faces.new(e1).material_index = nroof
        pts.append((x, y))
        n += 1
    o = b.obj("m7c_houses")
    o.visible_shadow = False
    return n


# ---------------------------------------------------------------- M7d: the drop made legible from eye level

def _brow_cfg():
    return M7D.get("brow", {}) if M7D.get("on") and M7D.get("brow", {}).get("on") else {}


def _on_brow_path(x, y):
    B = _brow_cfg()
    if not B.get("path"):
        return False
    return float(_seg_dist(np.array([x]), np.array([y]), B["path"]["pts"])[0]) < B["path"]["width"] / 2 + 0.15


def _sightline(cam, x, y):
    """z of the line from a camera over the brow, at (x, y)."""
    th = math.atan2(y - cam[1], x - cam[0])
    for dd in np.arange(5, 60, 0.25):
        px, py = cam[0] + dd * math.cos(th), cam[1] + dd * math.sin(th)
        if rim_s(px, py)[0] > 0.0:
            break
    zb = float(ground_z(px, py))
    D = math.hypot(x - cam[0], y - cam[1])
    return cam[2] + (zb - cam[2]) * D / dd


def brow_cues(placed, protos, gravel, stone):
    """M7d (human interventions 23, weak point 5; config m7d.brow): cues that make the drop legible in the eye-level
    wides without moving a camera. Fir crowns rising from below the brow on either side of the view (their tops a few
    metres over the brow's sight line from the wide, their trunks hidden by the crest); a path that leaves the
    viewpoint terrace and goes over the brow down the front slope (gravel and kerbs following the ground); a railing
    along the terrace's retaining wall, as a viewpoint over a drop has. Trees standing on the new path are hidden."""
    B = _brow_cfg()
    notes = []
    if not B:
        return notes
    rng = gb.rng("m7d_brow")
    cam = np.array(P["cameras"]["wide"]["loc"])
    n = 0
    for x, y, poke, k in B.get("crowns", []):
        zg = float(ground_z(x, y))
        h = _sightline(cam, x, y) + poke - zg
        rad = 0.14 * h
        if any(q[0] == "fir" and math.hypot(x - q[1], y - q[2]) < B["crown_sep"] * (rad + q[4]) for q in placed):
            notes.append(f"brow crown at ({x}, {y}) skipped: too near a tree")
            continue
        place(protos[k], f"m7d_crown_{len(placed)}", x, y, h, rng.uniform(0.92, 1.08), rng=rng)
        placed.append(("fir", x, y, h, rad))
        n += 1
    notes.append(f"M7d brow: {n} fir crowns below the brow")
    if B.get("path"):
        bp = B["path"]
        hw = bp["width"] / 2
        c, tg, nm = _path_frame(bp["pts"], 0.25)
        acr = np.linspace(-1, 1, 7)
        verts, faces = [], []
        for i in range(len(c)):
            for a in acr:
                x, y = c[i] + nm[i] * a * hw
                verts.append((x, y, float(ground_z(x, y)) + 0.015 + 0.008 * (1 - a * a)))
        m_ = len(acr)
        for i in range(len(c) - 1):
            for j in range(m_ - 1):
                faces.append((i * m_ + j, i * m_ + j + 1, (i + 1) * m_ + j + 1, (i + 1) * m_ + j))
        _obj("m7d_brow_path", _mesh("m7d_brow_path", verts, faces, [gravel], smooth=True))
        b = gb.Builder([stone])
        kerbs = 0
        tlen = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
        import bmesh
        for side in (-1, 1):
            s_ = 0.3
            while s_ < tlen[-1] - 0.5:
                ln = rng.uniform(0.45, 0.8)
                i = min(int(np.searchsorted(tlen, s_ + ln / 2)), len(c) - 1)
                p_ = c[i] + nm[i] * side * (hw + 0.06)
                ta, tb = p_ - tg[i] * ln / 2, p_ + tg[i] * ln / 2
                pitch = math.atan2(float(ground_z(*tb) - ground_z(*ta)), ln)
                z = float(ground_z(*p_)) + 0.02
                cube = bmesh.ops.create_cube(b.bm, size=1.0)
                Mk = (Matrix.Translation((p_[0], p_[1], z - 0.04)) @ Matrix.Rotation(math.atan2(tg[i][1], tg[i][0]), 4, "Z")
                      @ Matrix.Rotation(-pitch, 4, "Y") @ Matrix.Diagonal((ln - 0.02, 0.13, 0.14, 1.0)))
                b._tag(cube["verts"], 0, Mk)
                kerbs += 1
                s_ += ln + rng.uniform(0.005, 0.03)
        ko = gb.mesh_obj("m7d_brow_kerbs", b.to_mesh("m7d_brow_kerbs"))
        _bevel(ko, 0.012)
        hid = 0
        for i, q in enumerate(placed):
            if float(_seg_dist(np.array([q[1]]), np.array([q[2]]), bp["pts"])[0]) < hw + bp["clear"]:
                for nm_ in (f"m7c_{q[0]}_{i}", f"m7d_crown_{i}"):
                    o = bpy.data.objects.get(nm_)
                    if o is not None:
                        o.hide_render = o.hide_viewport = True
                        hid += 1
        notes.append(f"M7d brow path: {tlen[-1]:.1f} m over the brow, {kerbs} kerbs, {hid} trees on its line hidden")
    if B.get("rail"):
        R_ = B["rail"]
        L = layout()
        cx, cy = L["centre"]
        rp = L["rp"]
        dx, dy = L["dir"]
        a_dir = math.atan2(dy, dx)
        iron = bpy.data.materials.get("m7c_bench_iron") or painted_mat("m7c_bench_iron", "#1e2220", 0.5, 0.4)
        b = PR.B([iron])
        half = math.radians(P["viewpoint"]["wall_deg"] - R_["inset_deg"])
        rr = rp + 0.12
        npost = max(2, int(2 * half * rr / R_["spacing"]) + 1)
        z0 = 0.38
        prev = None
        for i in range(npost):
            a = a_dir - half + 2 * half * i / (npost - 1)
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            b.bx((x, y, z0 + R_["height"] / 2), (0.04, 0.04, R_["height"]), 0, rot=(0, 0, a))
            if prev is not None:
                for zz in (z0 + R_["height"], z0 + R_["height"] * 0.55):
                    b.rod((prev[0], prev[1], zz), (x, y, zz), 0.018, 0, segs=8)
            prev = (x, y)
        b.obj("m7d_rail")
        notes.append(f"M7d rail: {npost} posts along the terrace wall")
    return notes


# ---------------------------------------------------------------- the far plate, fog and sky

def backdrop():
    """The generated plate on a cylinder section round the crest (radius 2 km): azimuth maps to the panorama's columns
    and elevation to its rows (px per degree), its horizon row at the crest's eye height. Emission (the texture is
    scene-linear / scale, Non-Color), alpha in the texture (the top fades into the sky); beyond the image the edge
    pixels hold (EXTEND: the valley-fog colour below, the outer columns' profile at the sides)."""
    B = P["backdrop"]
    img_path = TEX / "park_backdrop.png"
    meta = json.loads((TEX / "park_backdrop.json").read_text())
    pw, ph = meta["size"]
    R, zh, ppd = B["radius"], B["eye_z"], B["ppd"]
    cx_px = B["centre_px"]                     # the panorama column at azimuth 0 (+Y)
    hz_px = B["horizon_px"]
    az = np.arange(B["az"][0], B["az"][1] + 1e-6, 1.0)
    e_top = hz_px / ppd + 0.2
    el = np.concatenate([np.arange(B["el_bottom"], e_top, 0.5), [e_top]])
    verts, uvs_v = [], []
    for e in el:
        for a in az:
            ar, er = math.radians(a), math.radians(e)
            verts.append((R * math.sin(ar), R * math.cos(ar), zh + R * math.tan(er)))
            uvs_v.append(((cx_px + a * ppd) / pw, 1.0 - (hz_px - e * ppd) / ph))
    na = len(az)
    faces, uvs = [], []
    for i in range(len(el) - 1):
        for j in range(na - 1):
            f = (i * na + j, (i + 1) * na + j, (i + 1) * na + j + 1, i * na + j + 1)
            faces.append(f)
            uvs.extend(uvs_v[q] for q in f)
    m = _mat("m7c_backdrop")
    L = _look()
    nb = L.NB(m)
    tex = nb.n("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path), check_existing=True)
    tex.image.colorspace_settings.name = "Non-Color"
    tex.image.alpha_mode = "STRAIGHT"
    tex.extension = "EXTEND"
    tex.interpolation = "Linear"
    uvn = nb.n("ShaderNodeUVMap", uv_map="UVMap")
    nb.put(tex.inputs["Vector"], uvn.outputs[0])
    e = nb.n("ShaderNodeEmission")
    nb.put(e.inputs["Color"], tex.outputs["Color"])
    e.inputs["Strength"].default_value = meta["scale"] * B.get("gain", 1.0)
    tp = nb.n("ShaderNodeBsdfTransparent")
    mx = nb.n("ShaderNodeMixShader")
    nb.put(mx.inputs[0], tex.outputs["Alpha"])
    nb.nt.links.new(tp.outputs[0], mx.inputs[1])
    nb.nt.links.new(e.outputs[0], mx.inputs[2])
    nb.out(mx.outputs[0])
    m.surface_render_method = "BLENDED"
    me = _mesh("m7c_backdrop", verts, faces, [m], uvs=uvs)
    o = _obj("m7c_backdrop", me)
    o.visible_shadow = False
    for k in ("hide_probe_volume", "hide_probe_sphere", "hide_probe_plane"):
        if hasattr(o, k):
            setattr(o, k, True)
    return o


def world(R):
    """look.park_world with the camera rays' colour matched to the plate's top (so its fade into the sky is seamless);
    the light the people and the set get is unchanged (bright behind the band, dim behind the camera)."""
    L = _look()
    L.park_world(R)
    _, _, sky = fog_colours()
    w = bpy.context.scene.world
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    lp = next(n for n in nt.nodes if n.type == "LIGHT_PATH")
    # Background colour = lit colour for light rays, the plate's sky for camera rays; strength for camera rays 1
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    nt.links.new(lp.outputs["Is Camera Ray"], mixc.inputs[0])
    mixc.inputs[6].default_value = bg.inputs["Color"].default_value[:]
    mixc.inputs[7].default_value = tuple(sky) + (1.0,)
    nt.links.new(mixc.outputs[2], bg.inputs["Color"])
    st = bg.inputs["Strength"].links[0].from_node
    # the strength node is ADD(light part, camera part * sky_cam): replace sky_cam's multiplier by 1
    for n in nt.nodes:
        if n.type == "MATH" and n.operation == "MULTIPLY" and any(l.from_node == lp for l in n.inputs[0].links) \
                and abs(n.inputs[1].default_value - R["sky_cam"]) < 1e-6:
            n.inputs[1].default_value = 1.0
    return st


def fog_volume():
    """The near haze over the crest and the first of the drop (drizzle air), drifting on the clock; lit by the sky and
    the soft sun from behind the band."""
    F = P["fog"]
    L = _look()
    m = _mat("m7c_haze")
    nb = L.NB(m)
    v = nb.n("ShaderNodeVolumePrincipled")
    Pw, _ = nb.world_pos()
    clk = L.clock_node(nb)
    q = nb.n("ShaderNodeVectorMath", operation="SUBTRACT")
    nb.put(q.inputs[0], Pw)
    nb.put(q.inputs[1], nb.comb(nb.mul(clk, F["drift"]), 0.0, 0.0))
    n1, _ = nb.noise(q.outputs[0], 0.06, 2.0, 0.55)
    _, _, z = nb.sep(Pw)
    lowz = nb.maprange(z, 4.0, -12.0, 1.0, 1.3)
    nb.put(v.inputs["Density"], nb.mul(nb.mul(nb.maprange(n1, 0.3, 0.7, 0.55, 1.45), lowz), F["near_density"]))
    v.inputs["Color"].default_value = (0.9, 0.92, 0.93, 1)
    v.inputs["Anisotropy"].default_value = 0.35
    nb.out(None, v.outputs[0])
    (x0, x1), (y0, y1), (z0, z1) = F["near_box"]
    o = gb.box("m7c_haze_volume", ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), m)
    o.visible_shadow = False
    return o


def fog_curtains():
    """Terrain-following fog curtains over the drop and in front of the plate's lower edge: each a strip whose foot
    follows the ground (or a fixed depth beyond it), its alpha a soft vertical band broken by noise that drifts on the
    clock; colour from the valley fog to the level haze with height. M7c's replacement for coverage.fog_cards."""
    L = _look()
    level, valley, _ = fog_colours()
    F = P["fog"]
    made = 0
    for k, c in enumerate(F["curtains"]):
        m = _mat(f"m7c_curtain{k}")
        nb = L.NB(m)
        uv = nb.n("ShaderNodeUVMap", uv_map="UVMap")
        u, v, _ = nb.sep(uv.outputs[0])
        clk = L.clock_node(nb)
        n1, _ = nb.noise(nb.comb(nb.add(nb.mul(u, c["noise_u"]), nb.mul(clk, c["drift"])), nb.mul(v, 2.2), 3.7 * k), 1.0, 3.0, 0.55)
        prof = nb.mul(nb.maprange(v, 0.0, c["fade_in"], 0.0, 1.0, smooth=True), nb.maprange(v, c["fade_out"], 1.0, 1.0, 0.0, smooth=True))
        ends = nb.mul(nb.maprange(u, 0.0, 0.12, 0.0, 1.0, smooth=True), nb.maprange(u, 0.88, 1.0, 1.0, 0.0, smooth=True))
        a = nb.mul(nb.mul(nb.mul(prof, ends), nb.maprange(n1, 0.32, 0.72, 0.15, 1.0)), c["opacity"])
        Pw, _ = nb.world_pos()
        _, _, z = nb.sep(Pw)
        w = nb.maprange(z, F["valley_top"], F["valley_top"] - F["valley_blend"], 0.0, 1.0, smooth=True)
        col = nb.mix(w, tuple(level) + (1.0,), tuple(valley) + (1.0,))
        e = nb.n("ShaderNodeEmission")
        nb.put(e.inputs["Color"], col)
        tp = nb.n("ShaderNodeBsdfTransparent")
        mx = nb.n("ShaderNodeMixShader")
        nb.put(mx.inputs[0], a)
        nb.nt.links.new(tp.outputs[0], mx.inputs[1])
        nb.nt.links.new(e.outputs[0], mx.inputs[2])
        nb.out(mx.outputs[0])
        m.surface_render_method = "BLENDED"
        xs = np.linspace(c["x"][0], c["x"][1], 121)
        verts, faces, uvs = [], [], []
        for i, x in enumerate(xs):
            y = c["y"] + c.get("bow", 0.0) * (x / max(abs(c["x"][0]), abs(c["x"][1]))) ** 2
            foot = float(ground_z(x, y)) + c["clear"] if c.get("follow", True) else c["foot"]
            verts += [(x, y, foot), (x, y, foot + c["h"])]
        for i in range(len(xs) - 1):
            f = (2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1)
            faces.append(f)
            u0, u1 = i / (len(xs) - 1), (i + 1) / (len(xs) - 1)
            uvs += [(u0, 0.0), (u1, 0.0), (u1, 1.0), (u0, 1.0)]
        o = _obj(f"m7c_curtain{k}", _mesh(f"m7c_curtain{k}", verts, faces, [m], uvs=uvs))
        o.visible_shadow = False
        made += 1
    return made


# ---------------------------------------------------------------- the lamp post

def lamp_post(old):
    """A generic cast-iron park lamp in place of M3's prop post: an octagonal plinth, a fluted tapering shaft with two
    collars, a flared neck, a four-sided glazed lantern (frosted, warm, the 'lamp_glow' material coverage.lamp_flicker
    keys) under a pyramid cap and finial; M3's weatherproof outlet box and its propped cover, at the height M7b had
    them, so Switch's plane (moved back down to its M7b place) sits on it exactly as before."""
    L = P["lamp"]
    lx, ly = S.PARK["lamp"]
    z0 = float(ground_z(lx, ly))
    zo = _old_hill_z(lx, ly)                         # M7b's base: the box and Switch keep their M7b height
    old.hide_render = old.hide_viewport = True
    sw = S.OBJ.get("switch")
    if sw is not None:
        sw.location.z = zo + 1.1
    iron = painted_mat("m7c_lamp_iron", L["colour"], 0.45, 0.55)
    box = bpy.data.materials.get("m_outlet_box_0") or K.mat("outlet_box")
    glow = bpy.data.materials.get("lamp_glow")
    for nd in glow.node_tree.nodes:
        if nd.type == "BSDF_PRINCIPLED":
            nd.inputs["Base Color"].default_value = gb.lin("#f3e6cf")
            nd.inputs["Emission Color"].default_value = gb.lin(L["glow_colour"])
            nd.inputs["Emission Strength"].default_value = L["glow"]
            nd.inputs["Roughness"].default_value = 0.35
    b = PR.B([iron, box, glow])
    # plinth: octagonal, moulded
    b.cyl((0, 0, z0 + 0.2 - 0.1), 0.17, 0.6, 0, r2=0.15, segs=8)
    b.cyl((0, 0, z0 + 0.52), 0.155, 0.05, 0, r2=0.11, segs=8)
    # fluted shaft: 16 flutes (alternating radii), tapering
    import bmesh
    bm = b.bm
    n, rows = 32, 12
    zs0, zs1 = z0 + 0.54, z0 + 3.22
    ring = []
    for j in range(rows + 1):
        t = j / rows
        z = zs0 + (zs1 - zs0) * t
        rr = 0.072 - 0.022 * t
        ring.append([bm.verts.new((rr * (1 - 0.1 * (q % 2)) * math.cos(2 * math.pi * q / n),
                                   rr * (1 - 0.1 * (q % 2)) * math.sin(2 * math.pi * q / n), z)) for q in range(n)])
    for j in range(rows):
        for q in range(n):
            f = bm.faces.new((ring[j][q], ring[j][(q + 1) % n], ring[j + 1][(q + 1) % n], ring[j + 1][q]))
            f.material_index, f.smooth = 0, True
    for zc, rc in ((z0 + 0.62, 0.09), (z0 + 2.35, 0.07)):
        b.cyl((0, 0, zc), rc, 0.05, 0, segs=24)
    b.cyl((0, 0, z0 + 3.3), 0.05, 0.18, 0, r2=0.115, segs=24)       # the flared neck
    # the lantern: a tray, four frosted panes (tapering out to the top), corner posts, a pyramid cap and finial
    zl0, zl1 = z0 + 3.42, z0 + 3.86
    b.cyl((0, 0, zl0 - 0.02), 0.13, 0.04, 0, segs=4)
    for q in range(4):
        a = math.pi / 4 + q * math.pi / 2
        a1 = a + math.pi / 2
        p0 = [(0.1 * math.cos(a), 0.1 * math.sin(a), zl0), (0.1 * math.cos(a1), 0.1 * math.sin(a1), zl0),
              (0.15 * math.cos(a1), 0.15 * math.sin(a1), zl1), (0.15 * math.cos(a), 0.15 * math.sin(a), zl1)]
        f = bm.faces.new([bm.verts.new(v) for v in p0])
        f.material_index = 2
        b.rod((0.105 * math.cos(a), 0.105 * math.sin(a), zl0), (0.155 * math.cos(a), 0.155 * math.sin(a), zl1), 0.008, 0, segs=6)
    b.cyl((0, 0, zl1 + 0.015), 0.18, 0.03, 0, segs=4)
    b.cyl((0, 0, zl1 + 0.12), 0.17, 0.18, 0, r2=0.015, segs=4)
    b.cyl((0, 0, zl1 + 0.25), 0.012, 0.08, 0, segs=8)
    b.ball((0, 0, zl1 + 0.3), 0.022, 0)
    # M3's outlet box and its propped cover (aso_props.lamp_post), at M7b's height
    b.bx((0, -0.11, zo + 1.1), (0.3, 0.11, 0.42), 1)
    b.bx((0, -0.16, zo + 1.33), (0.31, 0.08, 0.025), 1, rot=(0.5, 0, 0))
    o = b.obj("m7c_lamp_post", None, (lx, ly, 0))
    lt = bpy.data.lights.new("m7c_lantern_light", "POINT")
    lt.energy, lt.shadow_soft_size, lt.color = L["light"], 0.08, gb.lin(L["glow_colour"])[:3]
    lt.volume_factor = 0.3
    lo = gb.link(bpy.data.objects.new("m7c_lantern_light", lt))
    lo.location = (lx, ly, (zl0 + zl1) / 2)
    return o


# ---------------------------------------------------------------- build

def build(st, R):
    """look.park's M7c body: called after the sun is set (look.park); hides M3's ground, path, trees, skyline and
    lamp post and builds M7c's. Returns notes."""
    notes = []
    for nm in ("ground", "path", "skyline", "park_trees", "skyline_m7", "park_fog_volume"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            o.hide_render = o.hide_viewport = True
    rng = gb.rng("m7c_park")
    layout()
    o, nv = build_ground(lawn_mat())
    kerbs, wall = build_path(gravel_mat(), stone_mat(), gb.rng("m7c_path"))
    npud = puddles(water_mat(), gb.rng("m7c_puddles"))
    nbl = grass_fringe(fringe_mat(), gb.rng("m7c_fringe"))
    placed, nf, nbp = trees(lambda nb, sh: park_fog(nb, sh))
    STATE["trees"] = placed
    if _brow_cfg():
        notes += brow_cues(placed, [fir_proto(k, None, "park") for k in range(10)],
                           bpy.data.materials["m7c_gravel"], bpy.data.materials["m7c_stone"])
    walls = [painted_mat(f"m7c_wall{k}", c, 0.8) for k, c in enumerate(P["houses"]["walls"])]
    nh = houses(gb.rng("m7c_houses"), walls, painted_mat("m7c_roof", P["houses"]["roof"], 0.7))
    if (TEX / "park_backdrop.png").exists():
        backdrop()
        world(R)
        notes.append("the far plate on its cylinder")
    else:
        _look().park_world(R)
        notes.append("NO far plate (assets/gen/tex/m7c/park_backdrop.png missing)")
    fog_volume()
    nc = fog_curtains()
    old = bpy.data.objects.get("lamp_post")
    if old is not None:
        lamp_post(old)
    nfir = sum(1 for q in placed if q[0] == "fir")
    notes.append(f"M7c park: ground {nv} verts, path with {kerbs} kerbs and a {wall}-block wall, {npud} puddles, "
                 f"{nbl} blades, {nfir} firs ({nf} prototypes) and {len(placed) - nfir} bare trees, {nh} houses, "
                 f"{nc} fog curtains")
    STATE["notes"] = notes
    return notes


def fog_cards(n):
    """coverage.fog_cards' M7c replacement (the curtains are built with the set and drift on the clock)."""
    return "M7c fog curtains drift on the clock"


def o19b_keys(n_build, n_sub):
    """O19b's camera (M5's keys replaced, M7 only): from low on the back slope among young firs, rising up and over
    the crest's back edge to the crowd, the band, the brow and the city beyond. The keys' fractions are of the O19b
    sub-shot (its n_sub frames, the dissolve included); the build runs on under O19c-e's closes (n_build frames), where
    the camera holds its last key."""
    C = P["cameras"]["o19b"]
    k = (n_sub - 1) / max(1, n_build - 1)
    out = []
    for fr, (x, y, dz), tgt, lens in C["keys"]:
        z = float(ground_z(x, y)) + dz if C.get("relative", True) else dz
        out.append((fr * k, (x, y, z), tuple(tgt), lens))
    out.append((1.0,) + out[-1][1:])
    return out
