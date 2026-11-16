"""M7 look: the final look for the four Session 503 rooms, built into the shared set code (plan M7; the M7a look board,
production log 30+). enable() hooks it into blender/sets.py, blender/aso_kit.py and blender/aso_props.py; it is off by
default, so the M3-M5c3 renders stay reproducible. blender/coverage_m7.py turns it on for the M5c3 cut, cameras and
performances, which it doesn't touch.

Brief ("Look, cast and series callbacks", the shot list, "Rapid-response rendering plan"): grey Seattle daylight through
big windows (or sky) backlights every performer, so people read as silhouettes; rain on glass, drizzle, fog and the
string lights are shaders, particles and emission, not clips; everything rendered (no generated textures or set images).

What it changes, per build (sets.build's post-build hook, then again after the performances add their props):
- materials: every grey-box palette role (aso_kit.mat: m_<role>_<n>), the fog materials and the instruments' (inst_*)
  are rebuilt in place as procedural materials: wood planks, plaster, brick, fabric panels, woven rugs, ceramic,
  cedar boards, moss, painted and brushed metal, wet grass and gravel, needles and bark;
- windows: rain on glass (rivulets that run, beaded drops that invert the sky, a soft out-of-focus outside) or steamed
  glass with clear drip trails; the panes cast no shadow, so the daylight outside comes in through the openings;
- geometry: conifers in place of the cone stacks (aso_props.evergreen hook: ten seeded prototypes, instanced), a
  fog-flattened skyline massing in place of the boxes, finer drizzle (sets.drizzle hook), and set dressing per room;
- light: per room (config/look_m7.json): daylight beams through each window opening into a haze volume (spots
  outside each window), lower front fill and darker values, so performers go to silhouette with a rim;
- render settings: Eevee (64 samples, raytracing, fine volumetrics, motion blur) or Cycles (GPU, seeded from
  config/seeds.json), bloom in the compositor.
The grade is a separate logged step on the rendered frames (scripts/grade.py). Nothing here is random but through
gb.rng (config/seeds.json main=41).
Guardrails kept: no water, boats, fountain or tower in the skyline; no logos or text but the existing Remotion
textures; Little Switch's plane is untouched; the station's look stays generic (log decisions 21+).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import aso_kit as K  # noqa: E402
import aso_props as PR  # noqa: E402
import gb  # noqa: E402
import sets as S  # noqa: E402

CFG = json.loads((gb.ROOT / "config" / "look_m7.json").read_text())
ROOMS = CFG["rooms"]
ENGINE = ["eevee"]
SAMPLES = [None]               # a --samples override (tests)
STATE = {"room": None}


def enable(engine="eevee"):
    ENGINE[0] = engine
    S.POST_BUILD.append(post_build)
    PR.TREE_HOOK = conifer
    S.DRIZZLE_HOOK = drizzle


# ---------------------------------------------------------------- node helpers

class NB:
    """A small builder for shader node trees. Values are sockets or plain numbers/tuples."""

    def __init__(self, m, clear=True):
        m.use_nodes = True
        self.m, self.nt = m, m.node_tree
        if clear:
            self.nt.nodes.clear()

    def n(self, kind, **kw):
        nd = self.nt.nodes.new(kind)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def put(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.nt.links.new(v, sock)
        elif isinstance(v, str):
            sock.default_value = gb.lin(v) if len(sock.default_value) == 4 else gb.lin(v)[:3]
        else:
            sock.default_value = v

    def math(self, op, a, b=0.0, c=None, clamp=False):
        nd = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        self.put(nd.inputs[0], a)
        self.put(nd.inputs[1], b)
        if c is not None:
            self.put(nd.inputs[2], c)
        return nd.outputs[0]

    def add(self, a, b):
        return self.math("ADD", a, b)

    def mul(self, a, b):
        return self.math("MULTIPLY", a, b)

    def madd(self, a, b, c):
        return self.math("MULTIPLY_ADD", a, b, c)

    def maprange(self, v, a, b, c=0.0, d=1.0, smooth=False, clamp=True):
        nd = self.n("ShaderNodeMapRange", clamp=clamp, interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        for i, x in enumerate((v, a, b, c, d)):
            self.put(nd.inputs[i], x)
        return nd.outputs[0]

    def sep(self, v):
        nd = self.n("ShaderNodeSeparateXYZ")
        self.put(nd.inputs[0], v)
        return nd.outputs[0], nd.outputs[1], nd.outputs[2]

    def comb(self, x, y, z):
        nd = self.n("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self.put(nd.inputs[i], v)
        return nd.outputs[0]

    def mix(self, fac, a, b, blend="MIX"):
        nd = self.n("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        self.put(nd.inputs[0], fac)
        self.put(nd.inputs[6], a)
        self.put(nd.inputs[7], b)
        return nd.outputs[2]

    def noise(self, vec, scale=1.0, detail=2.0, rough=0.5, dist=0.0):
        nd = self.n("ShaderNodeTexNoise")
        if vec is not None:
            self.put(nd.inputs["Vector"], vec)
        nd.inputs["Scale"].default_value = scale
        nd.inputs["Detail"].default_value = detail
        nd.inputs["Roughness"].default_value = rough
        nd.inputs["Distortion"].default_value = dist
        return nd.outputs[0], nd.outputs[1]

    def voronoi(self, vec, scale=1.0, rand=1.0):
        nd = self.n("ShaderNodeTexVoronoi")
        if vec is not None:
            self.put(nd.inputs["Vector"], vec)
        nd.inputs["Scale"].default_value = scale
        nd.inputs["Randomness"].default_value = rand
        return nd.outputs[0], nd.outputs[1], nd.outputs[2]

    def white(self, vec):
        nd = self.n("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
        self.put(nd.inputs["Vector"], vec)
        return nd.outputs[0], nd.outputs[1]

    def ramp(self, fac, stops):
        nd = self.n("ShaderNodeValToRGB")
        self.put(nd.inputs[0], fac)
        els = nd.color_ramp.elements
        for i, (p, c) in enumerate(stops):
            e = els[i] if i < 2 else els.new(p)
            e.position, e.color = p, gb.lin(c)
        return nd.outputs[0]

    def bump(self, height, strength=0.3, distance=0.02, normal=None):
        nd = self.n("ShaderNodeBump")
        nd.inputs["Strength"].default_value = strength
        nd.inputs["Distance"].default_value = distance
        self.put(nd.inputs["Height"], height)
        if normal is not None:
            self.put(nd.inputs["Normal"], normal)
        return nd.outputs[0]

    def principled(self, base, rough=0.5, metal=0.0, coat=0.0, coat_rough=0.08, sheen=0.0, spec=0.5, normal=None,
                   emit=None, emit_strength=0.0):
        b = self.n("ShaderNodeBsdfPrincipled")
        self.put(b.inputs["Base Color"], base)
        self.put(b.inputs["Roughness"], rough)
        self.put(b.inputs["Metallic"], metal)
        self.put(b.inputs["Specular IOR Level"], spec)
        self.put(b.inputs["Coat Weight"], coat)
        b.inputs["Coat Roughness"].default_value = coat_rough
        self.put(b.inputs["Sheen Weight"], sheen)
        if normal is not None:
            self.put(b.inputs["Normal"], normal)
            if coat:
                self.put(b.inputs["Coat Normal"], normal)
        if emit is not None:
            self.put(b.inputs["Emission Color"], emit)
            self.put(b.inputs["Emission Strength"], emit_strength)
        return b

    def out(self, shader, volume=None):
        o = self.n("ShaderNodeOutputMaterial")
        if shader is not None:
            self.nt.links.new(shader, o.inputs["Surface"])
        if volume is not None:
            self.nt.links.new(volume, o.inputs["Volume"])
        return o

    def world_pos(self):
        g = self.n("ShaderNodeNewGeometry")
        return g.outputs["Position"], g.outputs["Normal"]

    def planar(self, obj=False):
        """(u, v, w): a box projection of the position (world, or object space with obj=True) onto the face's plane:
        floors and ceilings (x, y), walls (along the wall, up). w is the coordinate along the face normal."""
        if obj:
            tc = self.n("ShaderNodeTexCoord")
            P, N = tc.outputs["Object"], tc.outputs["Normal"]
        else:
            P, N = self.world_pos()
        px, py, pz = self.sep(P)
        nx, ny, nz = self.sep(N)
        ax, ay, az = (self.math("ABSOLUTE", c) for c in (nx, ny, nz))
        flo = self.math("GREATER_THAN", az, 0.6)
        isy = self.math("GREATER_THAN", ay, ax)
        u = self.add(self.mul(px, isy), self.mul(py, self.math("SUBTRACT", 1.0, isy)))
        u = self.add(u, self.mul(self.math("SUBTRACT", px, u), flo))
        v = self.add(pz, self.mul(self.math("SUBTRACT", py, pz), flo))
        w = self.add(self.mul(py, isy), self.mul(px, self.math("SUBTRACT", 1.0, isy)))
        w = self.add(w, self.mul(self.math("SUBTRACT", pz, w), flo))
        return u, v, w


def tint(hexcol, k):
    """A hex colour scaled by k (display-referred, for simple darker or lighter variants)."""
    h = hexcol.lstrip("#")
    c = [min(255, max(0, int(int(h[i:i + 2], 16) * k))) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(c)


# ---------------------------------------------------------------- procedural materials (rebuilt in place)

def wood(m, base, plank_w=0.13, plank_l=2.0, rough=0.45, coat=0.0, gap=0.0025, grain=1.0, obj=False, vary=0.22,
         gap_col=None, vertical=False):
    """Planks (or boards on walls) with per-plank tint, stretched grain and dark joints."""
    nb = NB(m)
    u, v, w = nb.planar(obj)
    if vertical:
        u, v = v, u
    row = nb.math("FLOOR", nb.math("DIVIDE", v, plank_w))
    off, _ = nb.white(nb.comb(row, 3.7, 1.3))
    uu = nb.math("DIVIDE", nb.madd(off, plank_l, u), plank_l)
    pid = nb.math("FLOOR", uu)
    rnd, rcol = nb.white(nb.comb(row, pid, 5.1))
    fv = nb.math("FRACT", nb.math("DIVIDE", v, plank_w))
    fu = nb.math("FRACT", uu)
    ev = nb.mul(nb.math("MINIMUM", fv, nb.math("SUBTRACT", 1.0, fv)), plank_w)
    eu = nb.mul(nb.math("MINIMUM", fu, nb.math("SUBTRACT", 1.0, fu)), plank_l)
    g1 = nb.maprange(ev, 0.0, gap, 1.0, 0.0, smooth=True)
    g2 = nb.maprange(eu, 0.0, gap * 1.4, 1.0, 0.0, smooth=True)
    gm = nb.math("MAXIMUM", g1, g2)
    gv = nb.comb(nb.madd(u, 0.9, nb.mul(rnd, 17.0)), nb.madd(v, 70.0 * grain, nb.mul(rnd, 31.0)), nb.mul(w, 3.0))
    gr, _ = nb.noise(gv, 1.0, 8.0, 0.62, 0.4)
    knot, _ = nb.noise(nb.comb(nb.mul(u, 3.0), nb.mul(v, 9.0), rnd), 1.0, 2.0, 0.5)
    gr = nb.math("MULTIPLY_ADD", knot, 0.35, nb.mul(gr, 0.75))
    col = nb.ramp(gr, [(0.25, tint(base, 0.72)), (0.55, base), (0.85, tint(base, 1.22))])
    t = nb.maprange(rnd, 0.0, 1.0, 1.0 - vary, 1.0 + vary)
    col = nb.mix(1.0, col, nb.comb(t, nb.mul(t, 0.98), nb.mul(t, 0.95)), "MULTIPLY")
    col = nb.mix(gm, col, gap_col or tint(base, 0.3))
    r = nb.add(nb.madd(gr, 0.18, rough - 0.09), nb.mul(gm, 0.4))
    hgt = nb.math("SUBTRACT", nb.mul(gr, 0.25), gm)
    nrm = nb.bump(hgt, 0.35, 0.004)
    b = nb.principled(col, r, coat=coat, coat_rough=0.12, normal=nrm)
    nb.out(b.outputs[0])
    return m


def plaster(m, base, rough=0.9, var=0.08, scale=1.5):
    nb = NB(m)
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, scale, 4.0, 0.55)
    n2, _ = nb.noise(P, 40.0, 3.0, 0.6)
    t = nb.add(nb.madd(n1, var * 2, 1.0 - var), nb.mul(nb.math("SUBTRACT", n2, 0.5), 0.05))
    col = nb.mix(1.0, base, nb.comb(t, t, t), "MULTIPLY")
    nrm = nb.bump(n2, 0.08, 0.003)
    b = nb.principled(col, rough, normal=nrm)
    nb.out(b.outputs[0])
    return m


def fabric(m, base, rough=0.95, var=0.1, sheen=0.35, weave=260.0):
    nb = NB(m)
    u, v, w = nb.planar()
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 4.0, 3.0, 0.6)
    t = nb.madd(n1, var * 2, 1.0 - var)
    col = nb.mix(1.0, base, nb.comb(t, t, t), "MULTIPLY")
    wu = nb.math("SINE", nb.mul(u, weave))
    wv = nb.math("SINE", nb.mul(v, weave))
    h = nb.math("ABSOLUTE", nb.mul(wu, wv))
    fz, _ = nb.noise(P, 300.0, 2.0, 0.6)
    nrm = nb.bump(nb.madd(fz, 0.5, h), 0.12, 0.002)
    b = nb.principled(col, rough, sheen=sheen, normal=nrm, spec=0.3)
    nb.out(b.outputs[0])
    return m


def rug(m, c1, c2, c3, pattern=0):
    """A flat-woven rug: border bands, a stepped field pattern on a woven grid, fibre noise (Generated coords)."""
    nb = NB(m)
    tc = nb.n("ShaderNodeTexCoord")
    x, y, _ = nb.sep(tc.outputs["Generated"])
    qx = nb.math("DIVIDE", nb.math("FLOOR", nb.mul(x, 90.0)), 90.0)
    qy = nb.math("DIVIDE", nb.math("FLOOR", nb.mul(y, 60.0)), 60.0)
    e = nb.math("MINIMUM", nb.math("MINIMUM", qx, nb.math("SUBTRACT", 1.0, qx)),
                nb.math("MINIMUM", qy, nb.math("SUBTRACT", 1.0, qy)))
    border = nb.math("LESS_THAN", e, 0.085)
    stripe = nb.math("GREATER_THAN", nb.math("SINE", nb.mul(e, 150.0 + 40 * pattern)), 0.2)
    k = (4.0, 3.0, 6.0)[pattern % 3]
    dx = nb.math("ABSOLUTE", nb.math("SUBTRACT", nb.math("FRACT", nb.mul(qx, k)), 0.5))
    dy = nb.math("ABSOLUTE", nb.math("SUBTRACT", nb.math("FRACT", nb.mul(qy, k * 0.6)), 0.5))
    d = nb.add(dx, dy)
    dia = nb.math("LESS_THAN", d, 0.32)
    dia2 = nb.math("LESS_THAN", d, 0.16)
    col = nb.mix(dia, c1, c2)
    col = nb.mix(dia2, col, c3)
    bcol = nb.mix(stripe, c2, c3)
    col = nb.mix(border, col, bcol)
    P, _ = nb.world_pos()
    fib, _ = nb.noise(P, 220.0, 2.0, 0.7)
    wear, _ = nb.noise(P, 1.2, 3.0, 0.6)
    t = nb.madd(fib, 0.25, nb.madd(wear, 0.2, 0.68))
    col = nb.mix(1.0, col, nb.comb(t, t, t), "MULTIPLY")
    nrm = nb.bump(fib, 0.25, 0.003)
    b = nb.principled(col, 1.0, sheen=0.5, spec=0.2, normal=nrm)
    nb.out(b.outputs[0])
    return m


def brick(m, c1="#6e3a2a", c2="#5a2e22", mortar="#8a8276", rough=0.92):
    nb = NB(m)
    u, v, w = nb.planar()
    br = nb.n("ShaderNodeTexBrick", offset=0.5, squash_frequency=2)
    nb.put(br.inputs["Vector"], nb.comb(nb.add(u, nb.mul(w, 0.0)), v, 0.0))
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.009
    br.inputs["Mortar Smooth"].default_value = 0.2
    br.inputs["Brick Width"].default_value = 0.215
    br.inputs["Row Height"].default_value = 0.0725
    br.inputs["Bias"].default_value = 0.0
    nb.put(br.inputs["Color1"], c1)
    nb.put(br.inputs["Color2"], c2)
    nb.put(br.inputs["Mortar"], mortar)
    P, _ = nb.world_pos()
    g, _ = nb.noise(P, 2.0, 4.0, 0.6)
    f, _ = nb.noise(P, 60.0, 3.0, 0.7)
    blk, _ = nb.noise(nb.comb(nb.math("FLOOR", nb.math("DIVIDE", u, 0.11)), nb.math("FLOOR", nb.math("DIVIDE", v, 0.0725)), w),
                      3.0, 1.0, 0.5)                        # brick-sized blocks of tint (alignment is loose on purpose)
    t = nb.madd(g, 0.3, nb.madd(f, 0.15, nb.madd(blk, 0.45, 0.35)))
    col = nb.mix(1.0, br.outputs[0], nb.comb(t, t, t), "MULTIPLY")
    h = nb.math("SUBTRACT", nb.mul(f, 0.3), br.outputs[1])
    nrm = nb.bump(h, 0.5, 0.006)
    b = nb.principled(col, rough, normal=nrm)
    nb.out(b.outputs[0])
    return m


def ceramic(m, base, rough=0.16):
    nb = NB(m)
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 30.0, 2.0, 0.5)
    t = nb.madd(n1, 0.08, 0.96)
    col = nb.mix(1.0, base, nb.comb(t, t, t), "MULTIPLY")
    b = nb.principled(col, rough, coat=0.5, coat_rough=0.05)
    nb.out(b.outputs[0])
    return m


def painted(m, base, rough=0.5, metal=0.0, coat=0.0, var=0.05):
    nb = NB(m)
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 8.0, 3.0, 0.6)
    t = nb.madd(n1, var * 2, 1.0 - var)
    col = nb.mix(1.0, base, nb.comb(t, t, t), "MULTIPLY")
    r = nb.madd(n1, 0.15, rough - 0.07)
    b = nb.principled(col, r, metal=metal, coat=coat)
    nb.out(b.outputs[0])
    return m


def brushed(m, base, rough=0.3):
    nb = NB(m)
    tc = nb.n("ShaderNodeTexCoord")
    x, y, z = nb.sep(tc.outputs["Object"])
    s, _ = nb.noise(nb.comb(nb.mul(x, 400.0), y, nb.mul(z, 3.0)), 1.0, 3.0, 0.6)
    r = nb.madd(s, 0.15, rough - 0.07)
    b = nb.principled(base, r, metal=1.0)
    nb.out(b.outputs[0])
    return m


def moss(m, base="#4f6a2a"):
    nb = NB(m)
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 18.0, 4.0, 0.6)
    n2, _ = nb.noise(P, 160.0, 2.0, 0.7)
    col = nb.ramp(n1, [(0.3, tint(base, 0.55)), (0.55, base), (0.8, tint(base, 1.3))])
    nrm = nb.bump(n2, 0.6, 0.004)
    b = nb.principled(col, 1.0, sheen=0.8, spec=0.2, normal=nrm)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.put(tr.inputs["Color"], tint(base, 0.8))
    mx = nb.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.2
    nb.nt.links.new(b.outputs[0], mx.inputs[1])
    nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    nb.out(mx.outputs[0])
    return m


def fog_wrap(nb, shader, fogc, dist, emit=1.0, height=None):
    """Mix a surface into the fog colour with distance from the camera (aso_kit.fog_mat's aerial perspective); with
    height=(z0, hz) the fog also thickens above z0 (cloud base, the skyline's tops dissolve)."""
    cam = nb.n("ShaderNodeCameraData")
    ex = nb.math("EXPONENT", nb.math("DIVIDE", cam.outputs["View Distance"], -dist))
    if height:
        P, _ = nb.world_pos()
        _, _, z = nb.sep(P)
        hz = nb.math("EXPONENT", nb.math("DIVIDE", nb.math("MAXIMUM", nb.math("SUBTRACT", z, height[0]), 0.0), -height[1]))
        ex = nb.mul(ex, hz)
    f = nb.math("SUBTRACT", 1.0, ex)
    e = nb.n("ShaderNodeEmission")
    nb.put(e.inputs["Color"], fogc)
    e.inputs["Strength"].default_value = emit
    mx = nb.n("ShaderNodeMixShader")
    nb.put(mx.inputs[0], f)
    nb.nt.links.new(shader, mx.inputs[1])
    nb.nt.links.new(e.outputs[0], mx.inputs[2])
    return mx.outputs[0]


def foliage(m, base, fogc, dist, emit=1.0):
    """Conifer needles: per-tree tint (Object Info random), clumped noise, a little translucency for the backlight's
    rim, faded into the fog with distance."""
    nb = NB(m)
    oi = nb.n("ShaderNodeObjectInfo")
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 3.0, 4.0, 0.6)
    n2, _ = nb.noise(P, 40.0, 2.0, 0.6)
    t = nb.madd(oi.outputs["Random"], 0.35, nb.madd(n1, 0.45, nb.madd(n2, 0.25, 0.55)))
    col = nb.ramp(t, [(0.2, tint(base, 0.55)), (0.6, base), (1.0, tint(base, 1.45))])
    b = nb.principled(col, 0.75, spec=0.3)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.put(tr.inputs["Color"], tint(base, 1.2))
    mx = nb.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.25
    nb.nt.links.new(b.outputs[0], mx.inputs[1])
    nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    sh = fog_wrap(nb, mx.outputs[0], fogc, dist, emit)
    # the spray's fringe (prototype UVs: u along the branch, v out from its spine): needles as a comb along u,
    # ragged by noise, so the edges fray instead of cutting a clean polygon
    uv = nb.n("ShaderNodeUVMap", uv_map="UVMap")
    u, v, _ = nb.sep(uv.outputs[0])
    comb = nb.math("POWER", nb.math("ABSOLUTE", nb.math("SINE", nb.mul(u, 70.0))), 0.6)
    rag, _ = nb.noise(nb.comb(nb.mul(u, 9.0), nb.mul(v, 2.0), oi.outputs["Random"]), 1.0, 2.0, 0.6)
    edge = nb.add(nb.madd(comb, 0.35, 0.42), nb.mul(nb.math("SUBTRACT", rag, 0.5), 0.5))
    keep = nb.math("LESS_THAN", v, edge)
    tp = nb.n("ShaderNodeBsdfTransparent")
    mk = nb.n("ShaderNodeMixShader")
    nb.put(mk.inputs[0], keep)
    nb.nt.links.new(tp.outputs[0], mk.inputs[1])
    nb.nt.links.new(sh, mk.inputs[2])
    nb.out(mk.outputs[0])
    m.surface_render_method = "DITHERED"
    return m


def bark(m, base, fogc, dist, emit=1.0):
    nb = NB(m)
    tc = nb.n("ShaderNodeTexCoord")
    x, y, z = nb.sep(tc.outputs["Object"])
    n1, _ = nb.noise(nb.comb(nb.mul(x, 30.0), nb.mul(y, 30.0), nb.mul(z, 3.0)), 1.0, 5.0, 0.6)
    col = nb.ramp(n1, [(0.3, tint(base, 0.6)), (0.7, tint(base, 1.2))])
    b = nb.principled(col, 0.9, normal=nb.bump(n1, 0.5, 0.01))
    nb.out(fog_wrap(nb, b.outputs[0], fogc, dist, emit))
    return m


def grass(m, base, fogc, dist, emit=1.0):
    """Wet park grass: patchy olive and brown, fine blades as noise, a damp sheen; into the fog with distance."""
    nb = NB(m)
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 0.6, 4.0, 0.6)
    n2, _ = nb.noise(P, 7.0, 3.0, 0.6)
    n3, _ = nb.noise(P, 120.0, 2.0, 0.7)
    t = nb.madd(n1, 0.5, nb.mul(n2, 0.5))
    col = nb.ramp(t, [(0.25, "#222b18"), (0.5, base), (0.72, "#46522e"), (0.9, "#4c4a30")])
    v = nb.madd(n3, 0.35, 0.78)
    col = nb.mix(1.0, col, nb.comb(v, v, v), "MULTIPLY")
    b = nb.principled(col, nb.madd(n2, 0.15, 0.78), spec=0.15, normal=nb.bump(n3, 0.4, 0.01))
    nb.out(fog_wrap(nb, b.outputs[0], fogc, dist, emit))
    return m


def gravel(m, base, fogc, dist, emit=1.0):
    nb = NB(m)
    P, _ = nb.world_pos()
    d, c, _ = nb.voronoi(P, 55.0)
    s, _, _ = nb.sep(c)
    n1, _ = nb.noise(P, 2.0, 3.0, 0.6)
    t = nb.madd(s, 0.45, nb.madd(n1, 0.3, 0.45))
    col = nb.mix(1.0, base, nb.comb(t, t, nb.mul(t, 0.96)), "MULTIPLY")
    h = nb.maprange(d, 0.0, 0.45, 1.0, 0.0, smooth=True)
    b = nb.principled(col, 0.42, normal=nb.bump(h, 0.6, 0.006))
    nb.out(fog_wrap(nb, b.outputs[0], fogc, dist, emit))
    return m


def facade(m, base, fogc, dist, height, k=0):
    """The skyline's buildings: faint floor bands and mullions, lost in the fog; the tops dissolve (height fog)."""
    nb = NB(m)
    u, v, w = nb.planar()
    fl = nb.math("GREATER_THAN", nb.math("FRACT", nb.math("DIVIDE", v, 3.6)), 0.72)
    mu = nb.math("GREATER_THAN", nb.math("FRACT", nb.math("DIVIDE", u, 1.6 + 0.4 * k)), 0.8)
    t = nb.math("SUBTRACT", 1.0, nb.mul(nb.math("MAXIMUM", fl, mu), 0.12))
    col = nb.mix(1.0, base, nb.comb(t, t, t), "MULTIPLY")
    b = nb.principled(col, 0.6)
    nb.out(fog_wrap(nb, b.outputs[0], fogc, dist, 1.0, height=height))
    return m


def rain_glass(m, top="#d9dde0", bottom="#b9bfc4", strength=3.0, rain=1.0, steam=0.0, seed=0.0, see=0.0):
    """Rain on glass, emissive (the grey sky seen through it), M7: a soft out-of-focus outside (a vertical gradient,
    large soft blotches, no shapes), rivulets that wander down the pane (contour lines of a stretched noise, broken
    up; the one Mapping node is what coverage.rain_flow keys, so they run), beaded drops that invert the sky (bright
    at the bottom, a dark rim) and fine mist. steam frosts it (pale and flat) except along clear drip trails.
    see > 0 lets the outside show through where it's dry (treehouse)."""
    nb = NB(m)
    tc = nb.n("ShaderNodeTexCoord")
    gx, gy, gz = nb.sep(tc.outputs["Generated"])
    P = tc.outputs["Object"]
    sky = nb.ramp(gz, [(0.0, bottom), (1.0, top)])
    blot, _ = nb.noise(nb.comb(nb.add(gx, seed), nb.add(gy, seed), gz), 1.6, 2.0, 0.4)
    bt = nb.madd(blot, 0.16, 0.92)
    sky = nb.mix(1.0, sky, nb.comb(bt, bt, bt), "MULTIPLY")
    # rivulets (the keyed Mapping: rain_flow moves Location z)
    mp = nb.n("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (seed, seed * 0.7, 0.0)
    nb.nt.links.new(P, mp.inputs["Vector"])
    qx, qy, qz = nb.sep(mp.outputs[0])
    sv = nb.comb(nb.mul(qx, 9.0), nb.mul(qy, 9.0), nb.mul(qz, 0.55))
    rn, _ = nb.noise(sv, 1.0, 3.0, 0.45, 0.2)
    line = nb.maprange(nb.math("ABSOLUTE", nb.math("SUBTRACT", rn, 0.5)), 0.0, 0.018, 1.0, 0.0, smooth=True)
    brk, _ = nb.noise(nb.comb(nb.mul(qx, 3.0), nb.mul(qy, 3.0), nb.mul(qz, 1.2)), 1.0, 1.0, 0.5)
    riv = nb.mul(line, nb.maprange(brk, 0.5, 0.62, 0.0, 1.0))
    riv = nb.mul(riv, rain)
    # beaded drops (static), each a tiny lens: the sky inverted, a dark rim
    d, dc, dp = nb.voronoi(P, 95.0, 1.0)
    rr, gg, _ = nb.sep(dc)
    rad = nb.madd(rr, 0.28, 0.12)
    keep = nb.math("LESS_THAN", gg, 0.55 * rain + 0.05)
    inside = nb.mul(nb.math("LESS_THAN", d, rad), keep)
    off = nb.math("SUBTRACT", nb.sep(P)[2], nb.sep(dp)[2])
    dz = nb.math("DIVIDE", nb.mul(off, 95.0), rad)
    lens = nb.maprange(dz, -1.0, 1.0, 1.2, 0.55)
    rim = nb.maprange(nb.math("DIVIDE", d, rad), 0.65, 1.0, 1.0, 0.45, smooth=True)
    dropv = nb.mul(lens, rim)
    # fine mist
    d2, c2, _ = nb.voronoi(P, 420.0, 1.0)
    r2, _, _ = nb.sep(c2)
    mist = nb.mul(nb.math("LESS_THAN", d2, nb.madd(r2, 0.15, 0.08)), nb.math("LESS_THAN", r2, 0.5 * rain))
    # combine (as a value multiplier on the sky)
    val = nb.math("SUBTRACT", 1.0, nb.mul(mist, 0.12))
    val = nb.add(val, nb.mul(inside, nb.math("SUBTRACT", dropv, 1.0)))
    val = nb.add(val, nb.mul(riv, -0.32))
    wet = nb.math("MAXIMUM", nb.math("MAXIMUM", riv, inside), nb.mul(mist, 0.5))
    if steam:
        # frost everywhere but along clear drip trails (straight, sparse, running down from beads)
        tx, _ = nb.noise(nb.comb(nb.mul(gx, 30.0), nb.mul(gy, 30.0), nb.mul(gz, 0.4)), 1.0, 1.0, 0.4)
        trail = nb.maprange(nb.math("ABSOLUTE", nb.math("SUBTRACT", tx, 0.5)), 0.0, 0.03, 1.0, 0.0, smooth=True)
        tb, _ = nb.noise(nb.comb(nb.mul(gx, 6.0), nb.mul(gy, 6.0), nb.mul(gz, 2.0)), 1.0, 1.0, 0.5)
        trail = nb.mul(trail, nb.maprange(tb, 0.45, 0.6, 0.0, 1.0))
        frost = nb.mul(steam, nb.math("SUBTRACT", 1.0, nb.math("MAXIMUM", trail, inside)))
        fz, _ = nb.noise(P, 6.0, 3.0, 0.6)
        fr = nb.madd(fz, 0.1, 0.95)
        pale = nb.mix(1.0, "#ece8e0", nb.comb(fr, fr, fr), "MULTIPLY")
        val = nb.add(val, nb.mul(trail, -0.12 * steam))
    col = nb.mix(1.0, sky, nb.comb(val, val, val), "MULTIPLY")
    if steam:
        col = nb.mix(nb.mul(frost, 0.7), col, pale)
    em = nb.n("ShaderNodeEmission")
    nb.put(em.inputs["Color"], col)
    em.inputs["Strength"].default_value = strength
    shader = em.outputs[0]
    if see:
        op = nb.math("MULTIPLY_ADD", wet, 0.55, 1.0 - see, clamp=True)
        tr = nb.n("ShaderNodeBsdfTransparent")
        mx = nb.n("ShaderNodeMixShader")
        nb.put(mx.inputs[0], op)
        nb.nt.links.new(tr.outputs[0], mx.inputs[1])
        nb.nt.links.new(shader, mx.inputs[2])
        shader = mx.outputs[0]
        m.surface_render_method = "DITHERED"
    nb.out(shader)
    m["window"] = True
    m["m7"] = True
    return m


# ---------------------------------------------------------------- the material upgrade

# role -> builder (colours from config/aso_look.json's palette unless given)
P_ = K.PAL
ROLE = {
    "floor_wood": lambda m: wood(m, "#4e3524", 0.12, 1.9, rough=0.36, coat=0.25),
    "wall": lambda m: plaster(m, "#5e5952", var=0.06),
    "wall_dark": lambda m: wood(m, "#3a2c22", 0.11, 3.2, rough=0.8),
    "ceiling": lambda m: plaster(m, "#3a3836", var=0.05),
    "panel": lambda m: fabric(m, "#4a3e34"),
    "panel2": lambda m: fabric(m, "#34403b"),
    "trim": lambda m: wood(m, "#2e231c", 0.08, 2.4, rough=0.5, coat=0.15, vary=0.08),
    "rug1": lambda m: rug(m, "#5a221a", "#2a1814", "#b08a5a", 0),
    "rug2": lambda m: rug(m, "#3f4a3a", "#1f2620", "#9a8a62", 1),
    "rug3": lambda m: rug(m, "#8a6a3a", "#4a2a1c", "#d0bf98", 2),
    "console": lambda m: painted(m, "#2a2624", 0.55),
    "metal": lambda m: painted(m, "#3a3b3e", 0.32, metal=0.85),
    "door": lambda m: wood(m, "#4a3626", 0.9, 2.2, rough=0.45, coat=0.2, vertical=True, vary=0.05),
    "conduit": lambda m: brushed(m, "#9a9a98", 0.35),
    "cafe_wall": lambda m: brick(m, "#74402e", "#4e2a22", "#6e665c"),
    "cafe_floor": lambda m: wood(m, "#3a281c", 0.09, 1.2, rough=0.4, coat=0.3),
    "counter": lambda m: wood(m, "#3a2a20", 0.11, 1.0, rough=0.45, coat=0.2, vertical=True),
    "table": lambda m: wood(m, "#6e4e34", 0.1, 0.9, rough=0.4, coat=0.35),
    "chair_a": lambda m: painted(m, "#6e2e24", 0.45, coat=0.2),
    "chair_b": lambda m: painted(m, "#2f4a3e", 0.45, coat=0.2),
    "chair_c": lambda m: wood(m, "#9a7444", 0.05, 0.6, rough=0.45, coat=0.2, obj=True),
    "chair_d": lambda m: painted(m, "#222226", 0.35, metal=0.6),
    "mug": lambda m: ceramic(m, "#e8e2d6"),
    "mug2": lambda m: ceramic(m, "#c46a3a"),
    "mug3": lambda m: ceramic(m, "#3f5a6a"),
    "frame": lambda m: wood(m, "#2a2018", 0.05, 0.8, rough=0.5, obj=True),
    "cedar": lambda m: wood(m, "#6a4430", 0.15, 3.2, rough=0.62, gap=0.004),
    "cedar_dark": lambda m: wood(m, "#4a3020", 0.15, 3.0, rough=0.62, gap=0.004),
    "moss": lambda m: moss(m),
    "whiteboard_frame": lambda m: brushed(m, "#c8c8c4", 0.3),
    "laptop": lambda m: brushed(m, "#9a9ca0", 0.32),
    "cable": lambda m: painted(m, "#141416", 0.55),
    "lamp_post": lambda m: painted(m, "#22282a", 0.45, metal=0.5),
    "outlet_box": lambda m: painted(m, "#565c5e", 0.5, metal=0.4),
    "umbrella": lambda m: painted(m, "#7a2a24", 0.6),
    "kick_shell": lambda m: painted(m, "#6a2a1e", 0.35, coat=0.8),
    "kick_hoop": lambda m: painted(m, "#2a1c14", 0.35, coat=0.6),
    "tamb": lambda m: wood(m, "#6a4a2c", 0.04, 0.5, rough=0.4, coat=0.5, obj=True),
    "phone_body": lambda m: painted(m, "#202124", 0.4),
    "brick": lambda m: painted(m, "#e4e2dc", 0.5),
    "paper": lambda m: painted(m, "#efe8da", 0.9),
    "spruce": lambda m: wood(m, "#c9a36a", 0.06, 0.6, rough=0.35, coat=0.7, obj=True, vary=0.05),
    "rosewood": lambda m: wood(m, "#3a2216", 0.06, 0.6, rough=0.4, coat=0.5, obj=True, vary=0.05),
}
INST = {
    "inst_top_spruce": lambda m: wood(m, "#c9a36a", 0.035, 0.6, rough=0.3, coat=0.75, obj=True, vary=0.03, gap=0.0),
    "inst_sides_mahogany": lambda m: wood(m, "#5a2c16", 0.03, 0.6, rough=0.35, coat=0.75, obj=True, vary=0.03, gap=0.0),
    "inst_neck": lambda m: wood(m, "#7a5230", 0.03, 0.6, rough=0.4, coat=0.4, obj=True, vary=0.02, gap=0.0),
    "inst_board": lambda m: wood(m, "#24160d", 0.02, 0.6, rough=0.45, obj=True, vary=0.02, gap=0.0),
    "inst_banjo_rim": lambda m: wood(m, "#5a3a22", 0.03, 0.6, rough=0.35, coat=0.7, obj=True, vary=0.03, gap=0.0),
    "inst_banjo_head": lambda m: painted(m, "#e6dfcc", 0.6, var=0.08),
    "inst_bridge_maple": lambda m: wood(m, "#d8b47c", 0.02, 0.6, rough=0.45, obj=True, vary=0.02, gap=0.0),
    "inst_strap": lambda m: fabric(m, "#1b1512", weave=600.0),
}


def upgrade_materials():
    """Rebuild every grey-box material in place (idempotent: done ones carry m["m7"])."""
    done = 0
    for m in list(bpy.data.materials):
        if m.get("m7") or m.library is not None:
            continue
        fn = None
        if m.name.startswith("m_"):
            role = m.name[2:].rsplit("_", 1)[0]
            b = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
            emitting = b is not None and b.inputs["Emission Strength"].default_value > 0
            if not emitting and role in ROLE:
                fn = ROLE[role]
        elif m.name in INST:
            fn = INST[m.name]
        elif m.get("window"):
            fn = window_upgrade
        elif m.get("fog") is not None:
            fn = fog_upgrade
        if fn is None:
            continue
        blend = m.surface_render_method
        fn(m)
        if blend == "BLENDED":
            m.surface_render_method = blend
        m["m7"] = True
        done += 1
    return done


def window_upgrade(m):
    p = m["win"].to_dict() if m.get("win") is not None else {}
    room = STATE["room"]
    if room in ROOMS and "window_emit" in ROOMS[room]:
        base = {"live": 6.0, "cafe": 4.0, "treehouse": 2.8}.get(room, 3.0)
        p["strength"] = p.get("strength", base) * ROOMS[room]["window_emit"] / base
        if m.name.startswith("skylight"):
            p["strength"] *= ROOMS[room].get("skylight_gain", 1.0)
    rain_glass(m, **{k: p[k] for k in ("top", "bottom", "strength", "rain", "steam", "seed", "see") if k in p})


def fog_upgrade(m):
    """The fog materials (aso_kit.fog_mat keeps its arguments in m["fog"]): textured, same fog (the treehouse forest's
    thinner by day, so the trees through the rainy glass stay dark green, config forest_fog). The old skyline's is
    left as it is (hidden in M7)."""
    f = m["fog"]
    fogc, dist, emit = f["fog"], f["dist"], f["emit"]
    R = ROOMS.get(STATE["room"], {})
    if STATE["room"] == "treehouse" and "forest_fog" in R and emit >= 1.0:
        fogc, dist = R["forest_fog"]
    nm = m.name
    if nm.startswith("evergreen"):
        foliage(m, "#22332a", fogc, dist, emit)
    elif nm.startswith("trunk"):
        bark(m, "#3a2a20", fogc, dist, emit)
    elif nm.startswith("forest_floor"):
        grass(m, "#2a2e22", fogc, dist, emit)
    elif nm == "grass":
        grass(m, "#3e4a2c", fogc, dist, emit)
    elif nm == "path":
        gravel(m, "#5e5a52", fogc, dist, emit)


# ---------------------------------------------------------------- geometry: conifers, skyline, drizzle

PROTOS = {}
CR = 0.14                      # conifer prototypes: crown radius / height


def _conifer_mesh(k, mats):
    """One conifer prototype, 1 m tall and 1 m crown radius (scaled per tree): a tapered trunk and whorls of drooping
    branches, each a flat serrated spray with a serrated curtain hanging under it (fir and hemlock skirts)."""
    import bmesh
    r = gb.rng(f"m7_conifer_{k}")
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")

    def face(vs, mi, uvs=None):
        f = bm.faces.new([bm.verts.new(v) for v in vs])
        f.material_index = mi
        f.smooth = True
        for lp, uv in zip(f.loops, uvs or [(0.0, 0.0)] * len(vs)):
            lp[uvl].uv = uv                     # u along the branch (0..1), v from its spine (0) to the fringe (1)
        return f
    # trunk (6 sides), to the top; the prototype is 1 unit tall with a crown radius of CR at the bottom
    n = 6
    ring0 = [bm.verts.new((0.013 * math.cos(2 * math.pi * i / n), 0.013 * math.sin(2 * math.pi * i / n), -0.02)) for i in range(n)]
    ring1 = [bm.verts.new((0.002 * math.cos(2 * math.pi * i / n), 0.002 * math.sin(2 * math.pi * i / n), 1.0)) for i in range(n)]
    for i in range(n):
        f = bm.faces.new((ring0[i], ring0[(i + 1) % n], ring1[(i + 1) % n], ring1[i]))
        f.material_index = 1
    z0 = 0.08 + 0.12 * r.random()
    whorls = int(30 + 10 * r.random())
    lean = r.uniform(-0.02, 0.02)
    for wi in range(whorls):
        t = wi / (whorls - 1)
        z = z0 + (0.99 - z0) * t
        crown = (1.0 - t) ** 0.92 * (0.95 + 0.1 * math.sin(7 * t + k))
        nb = int(5 + 3 * r.random()) if t < 0.85 else 4
        a0 = r.random() * 2 * math.pi
        for bi in range(nb):
            if r.random() < 0.12 and t < 0.9:
                continue                                    # gaps
            a = a0 + 2 * math.pi * bi / nb + r.uniform(-0.25, 0.25)
            L = max(0.004, CR * crown * r.uniform(0.62, 1.15))
            d = Vector((math.cos(a), math.sin(a), 0))
            side = Vector((-d.y, d.x, 0))
            e0 = math.radians(r.uniform(-4, 14) + 10 * t)
            droop = r.uniform(0.18, 0.42) * (1.2 - t)
            base = Vector((lean * z, 0, z))
            M = 6
            pts = []
            for s in range(M + 1):
                u = s / M
                p = base + d * (u * L) + Vector((0, 0, L * (u * math.tan(e0) - droop * u * u)))
                pts.append(p)
            W = 0.36 * L
            # flat serrated spray (alternate full and inner width along each edge)
            for s in range(M):
                u0, u1 = s / M, (s + 1) / M
                w0 = W * math.sin(math.pi * (0.12 + 0.88 * u0)) * (1.0 if s % 2 == 0 else 0.55)
                w1 = W * math.sin(math.pi * (0.12 + 0.88 * u1)) * (0.55 if s % 2 == 0 else 1.0)
                roll = r.uniform(-0.15, 0.15)
                a_, b_ = pts[s], pts[s + 1]
                l0, l1 = a_ + side * w0 + Vector((0, 0, roll * w0)), b_ + side * w1 + Vector((0, 0, roll * w1))
                r0, r1 = a_ - side * w0 - Vector((0, 0, roll * w0)), b_ - side * w1 - Vector((0, 0, roll * w1))
                face((r0, a_, b_, r1), 0, [(u0, 1.0), (u0, 0.0), (u1, 0.0), (u1, 1.0)])
                face((a_, l0, l1, b_), 0, [(u0, 0.0), (u0, 1.0), (u1, 1.0), (u1, 0.0)])
                # the hanging curtain under the spray, ragged at the bottom
                h0 = W * 0.7 * math.sin(math.pi * u0) * (1.0 if s % 2 else 0.6)
                h1 = W * 0.7 * math.sin(math.pi * u1) * (0.6 if s % 2 else 1.0)
                face((a_, b_, b_ - Vector((0, 0, h1)) + side * 0.01, a_ - Vector((0, 0, h0)) + side * 0.01), 0,
                     [(u0, 0.0), (u1, 0.0), (u1, 1.0), (u0, 1.0)])
    me = bpy.data.meshes.new(f"conifer_proto_{k}")
    bm.to_mesh(me)
    bm.free()
    for mt in mats:
        me.materials.append(mt)
    return me


def conifer(b, base, h, r, role="evergreen", trunk="trunk", tiers=5):
    """aso_props.evergreen's M7 hook: the tree becomes an instance of one of ten seeded conifer prototypes (scaled to
    the cone's height and radius, turned at random), with b's two materials (foliage, bark)."""
    mats = (b.mats[b.i(role)], b.mats[b.i(trunk)])
    key = (mats[0].name, mats[1].name)
    rr = gb.rng(f"m7_tree_{base[0]:.3f}_{base[1]:.3f}")
    k = int(rr.random() * 10)
    me = PROTOS.get((key, k))
    try:
        me = me if me is not None and bpy.data.meshes.get(me.name) == me else None
    except ReferenceError:                       # a previous build's (the file is reset per build)
        me = None
    if me is None:
        me = PROTOS[(key, k)] = _conifer_mesh(k, mats)
    o = bpy.data.objects.new(f"conifer_{len(bpy.data.objects)}", me)
    gb.link(o)
    o.location = (base[0], base[1], base[2])
    o.rotation_euler.z = rr.random() * 2 * math.pi
    o.visible_shadow = False
    hh = h * rr.uniform(0.95, 1.08)
    rad = hh * min(1.3, max(0.75, (r / h) / CR)) * rr.uniform(0.9, 1.1)
    if mats[0].name.startswith("evergreen_fog"):
        # the treehouse's forest: keep the crowns clear of the room, deck and railings (0.6 m), where they pass them
        dx = max(-3.7 - base[0], 0.0, base[0] - 7.0)
        dy = max(-0.6 - base[1], 0.0, base[1] - 6.4)
        clear = math.hypot(dx, dy) - 0.6
        t_low = max(0.0, (-0.6 - base[2]) / hh)            # the lowest point of the house, in tree height
        reach = 1.15 * CR * (1.0 - t_low) ** 0.92            # the prototype's longest branch there, per unit scale
        rad = min(rad, max(clear, 0.05) / reach)            # a slimmer crown where a tree stands close
    o.scale = (rad, rad, hh)                             # rad: the x-y scale (the prototype's crown is CR wide)
    return o


def drizzle(name, lo, hi, n, rng_name, length=(0.16, 0.3), alpha=0.35, emit=0.6):
    """sets.drizzle's M7 hook: finer, fainter streaks (1.5 mm, mostly short), 1.6x as many, cool grey, no shadow:
    drizzle, not a downpour. Same seeded stream, one merged mesh."""
    r = gb.rng(rng_name)
    m = bpy.data.materials.get(f"{name}_mat_m7")
    if m is None:
        m = gb.mat(f"{name}_mat_m7", "#e6eaee", 0.2, emit=emit * 0.55, alpha=alpha * 0.42)
        m["m7"] = True
    bb = gb.Builder([m])
    for _ in range(int(n * 1.6)):
        p = [lo[i] + (hi[i] - lo[i]) * r.random() for i in range(3)]
        L = 0.6 * (length[0] + (length[1] - length[0]) * r.random())
        bb.box(p, (0.0015, 0.0015, L), rot=(0.12, 0.05, 0))
    o = gb.mesh_obj(name, bb.to_mesh(name))
    o.visible_shadow = False
    return o


def skyline(fogc, base_z=-32.0):
    """A generic city in fog, three depth layers of massing (low-rise in front, towers, a pale far band): boxes with
    setbacks and rooftop plant, no landmark, no needle, nothing slender and tall; the tops dissolve into the cloud
    base. Seeded (gb.rng m7_skyline)."""
    r = gb.rng("m7_skyline")
    mats = [facade(bpy.data.materials.new(f"facade{k}"), c, fogc, d, (20.0, 60.0), k)
            for k, (c, d) in enumerate((("#4a525b", 400.0), ("#566069", 360.0), ("#646b71", 320.0)))]
    for mt in mats:
        mt["m7"] = True
    bld = PR.B(mats)
    bld.roles = [0, 1, 2]
    layers = [(300, 380, 22, (8, 30), (22, 60), 0.55), (420, 520, 34, (26, 82), (18, 44), 0.6), (620, 720, 28, (22, 60), (30, 70), 0.7)]
    count = 0
    for li, (y0, y1, n, (hmin, hmax), (wmin, wmax), xs) in enumerate(layers):
        for k in range(n):
            y = y0 + (y1 - y0) * r.random()
            span = xs * y
            x = -span + 2 * span * (k + r.random()) / n
            h = hmin + (hmax - hmin) * r.random() ** 1.7
            w = wmin + (wmax - wmin) * r.random()
            dpt = 14 + 20 * r.random()
            mi = min(2, li + (1 if r.random() < 0.3 else 0))
            z = base_z
            tiers = 1 if h < 45 else 2                                  # one setback at most: no spires
            for t in range(tiers):
                hh = h * (0.75 if tiers > 1 and t == 0 else 0.25 if t > 0 else 1.0)
                ww = w * (1.0 - 0.22 * t)
                dd = dpt * (1.0 - 0.2 * t)
                bld.bx((x, y, z + hh / 2), (ww, dd, hh), mi)
                z += hh
            if r.random() < 0.5:                                        # rooftop plant
                bld.bx((x + w * 0.15, y, z + 2.5), (w * 0.35, dpt * 0.4, 5.0), mi)
            count += 1
    o = bld.obj("skyline_m7")
    o.visible_shadow = False
    return count


# ---------------------------------------------------------------- per-room dressing and light

def _lights(prefix):
    return [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith(prefix)]


def _world(hexcol, strength):
    K.world(hexcol, strength)


def post_build(room, st):
    STATE["room"] = room
    upgrade_materials()
    fn = {"live": live, "cafe": cafe, "treehouse": treehouse, "park": park}.get(room)
    if fn:
        fn(st)


def live(st):
    R = ROOMS["live"]
    for o in _lights("wl_"):
        o.data.energy = R["window_area"]
    for o in _lights("bulb_light"):
        o.data.energy = R["bulb_light"]
    for o in _lights("lamp_light"):
        o.data.energy = R["lamp_light"]
    _world(*R["fill"])
    W, D, H = K.LOOK["rooms"]["live"]["size"]
    # sills under the five windows
    for k, x in enumerate([-5.2, -2.6, 0.0, 2.6, 5.2]):
        gb.box(f"m7_sill{k}", (x, D - 0.06, 0.53), (1.86, 0.2, 0.04), K.mat("trim", 0.6))
    # the mixer: fader strips, knobs and a row of meter LEDs (amber and green, small), monitors' dim screens
    mixer = bpy.data.objects.get("console_mixer")
    if mixer is not None:
        bk = PR.B(["metal", "console", gb.mat("m7_led_green", "#7ad36a", 0.4, emit=3.0),
                   gb.mat("m7_led_amber", "#ffb347", 0.4, emit=3.0)])
        for i in range(16):
            x = -0.62 + i * 0.083
            bk.bx((x, -0.12, 0.041), (0.012, 0.16, 0.004), "console")            # fader slot
            bk.bx((x, -0.16 + 0.08 * ((i * 7) % 5) / 5, 0.05), (0.03, 0.018, 0.02), "metal")   # cap
            for j in range(3):
                bk.cyl((x, 0.0 + 0.055 * j, 0.048), 0.009, 0.018, "console", segs=8)
            bk.bx((x, 0.21, 0.043), (0.01, 0.006, 0.006), 2 if i % 4 else 3)
        bk.obj("m7_mixer_detail", parent=mixer)
    for i in range(2):
        mon = bpy.data.objects.get(f"console_monitor{i}")
        if mon is not None:
            gb.plane(f"m7_monitor_screen{i}", (0, -0.101, 0.02), (0.17, 0.22),
                     gb.mat("m7_monitor_screen", "#9fb4c8", 0.4, emit=0.6), parent=mon, facing="-Y")
    # cables along the foot of the window wall, from the cases toward the band's back line (nobody stands there)
    r = gb.rng("m7_live_cables")
    cab = gb.Builder([K.mat("cable", 0.55)])
    for sx, x0, x1 in ((-1, -6.0, -1.1), (-1, -6.1, -2.3), (1, 6.0, 1.4)):
        prev = Vector((x0, 9.62 + r.uniform(-0.05, 0.05), 0.007))
        for s in range(1, 11):
            q = Vector((x0 + (x1 - x0) * s / 10, 9.68 + r.uniform(-0.1, 0.12), 0.007))
            cab.capsule(prev, q, 0.006)
            prev = q
    gb.mesh_obj("m7_cables", cab.to_mesh("m7_cables"))
    # an amp and two road cases against the window wall's ends (silhouettes against the glass)
    cases = PR.B(["console", "metal", "cable"])
    for x, w_, h_ in ((-6.35, 0.75, 0.55), (-6.3, 0.6, 0.5), (6.3, 0.7, 0.62)):
        cases.bx((x, D - 0.55, h_ / 2), (w_, 0.5, h_), "console")
        for z in (0.04, h_ - 0.04):
            cases.bx((x, D - 0.55, z), (w_ + 0.01, 0.51, 0.03), "metal")
    cases.bx((-6.3, D - 0.55, 0.55 + 0.25), (0.6, 0.45, 0.5), "console")       # the stacked case
    cases.obj("m7_cases")
    g = bpy.data.objects.get("onair_glow")
    if g is not None:
        g.data.energy = R["onair_glow"]                 # the darker room needs a stronger red spill to sell "it glows"
    # the doorway: a small warm sconce spill so Switch's wall isn't flat
    K.point("m7_door_spill", (-6.0, 1.2, 3.9), R["door_spill"], "#ffe4c4", radius=0.5)


def _blob_mesh(name, blobs, strands, mat, seg=8, rings=5):
    """Many small low-poly ellipsoids (centre, radii) and hanging strands (top, length) as one mesh, from arrays."""
    import numpy as np
    th = np.linspace(0, np.pi, rings + 1)[1:-1]
    ph = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    unit = [(0, 0, 1)] + [(math.sin(t) * math.cos(f), math.sin(t) * math.sin(f), math.cos(t)) for t in th for f in ph] + [(0, 0, -1)]
    unit = np.array(unit)
    nv = len(unit)
    uf = [(0, 1 + (j + 1) % seg, 1 + j) for j in range(seg)]
    for i in range(rings - 2):
        for j in range(seg):
            a_, b_ = 1 + i * seg + j, 1 + i * seg + (j + 1) % seg
            uf.append((a_, b_, b_ + seg, a_ + seg))
    last = nv - 1
    uf += [(last, 1 + (rings - 2) * seg + j, 1 + (rings - 2) * seg + (j + 1) % seg) for j in range(seg)]
    verts, faces = [], []
    for c, rr in blobs:
        base = len(verts)
        verts += [tuple(np.array(c) + unit[i] * np.array(rr)) for i in range(nv)]
        faces += [tuple(base + v for v in f) for f in uf]
    for (x, y, z), hl in strands:
        base = len(verts)
        w = 0.004
        verts += [(x - w, y, z), (x + w, y, z), (x, y + w, z), (x, y, z - hl)]
        faces += [(base, base + 1, base + 3), (base + 1, base + 2, base + 3), (base + 2, base, base + 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(mat)
    return gb.mesh_obj(name, me)


def cafe(st):
    R = ROOMS["cafe"]
    for o in _lights("wl_"):
        o.data.energy = R["window_area"] * (0.7 if "cafer" in o.name else 1.0)
    for o in _lights("strand_light"):
        o.data.energy = o.data.energy / 5.0 * R["strand_light"]
    for o in _lights("hub_light"):
        o.data.energy = R["strand_light"] * 0.8
    bm = bpy.data.materials.get("string_bulb")
    if bm is not None:
        for nd in bm.node_tree.nodes:
            if nd.type == "MATH" and nd.operation == "MULTIPLY":
                nd.inputs[1].default_value = R["bulbs"]
    _world(*R["fill"])
    W, D, H = K.LOOK["rooms"]["cafe"]["size"]
    # the Polaroid: the M7 photo (a Blender render of the band in this room, lit warm, framed by Remotion) if made,
    # and a small warm picture light on it
    pol = S.OBJ.get("polaroid")
    tex = K.TEX / "polaroid_m7.png"
    if pol is not None and tex.exists():
        pol.data.materials.clear()
        pol.data.materials.append(K.image_mat("tex_polaroid_m7", "polaroid_m7", "lit", 0.5))
    if pol is not None:
        sp = bpy.data.lights.new("m7_polaroid_light", "SPOT")
        sp.energy, sp.spot_size, sp.spot_blend = R["polaroid_light"], math.radians(48), 0.8
        sp.color = gb.lin("#ffc890")[:3]
        sp.shadow_soft_size = 0.05
        so = gb.link(bpy.data.objects.new("m7_polaroid_light", sp))
        so.location = (W / 2 - 0.45, 3.0, 1.95)
        so.rotation_euler = gb.look_rot(tuple(so.location), (W / 2, 3.0, 1.38))
        gb.cyl("m7_picture_lamp", (W / 2 - 0.12, 3.0, 1.68), 0.018, 0.22, K.mat("metal"), axis="X")
    # pendants over the counter (warm, dim), the espresso machine's group heads and drip tray
    for i, y in enumerate((2.1, 4.0)):
        x = -W / 2 + 0.55
        gb.cyl(f"m7_pend_cord{i}", (x, y, H - 0.45), 0.004, 0.9, K.mat("cable"), n=6)
        gb.cyl(f"m7_pend_shade{i}", (x, y, H - 0.98), 0.16, 0.16, K.mat("chair_d", 0.4), r2=0.05, n=20)
        gb.cyl(f"m7_pend_bulb{i}", (x, y, H - 1.07), 0.035, 0.05, gb.mat("m7_pend_glow", "#ffc27a", 0.3, emit=8.0), n=10)
        K.point(f"m7_pend_light{i}", (x, y, H - 1.12), 9.0, "#ffc27a", radius=0.05)
    esp = bpy.data.objects.get("espresso")
    if esp is not None:
        b = PR.B(["metal", "cable"])
        for k in (-1, 1):
            b.cyl((0.31, k * 0.12, -0.1), 0.035, 0.06, "metal", axis=(1, 0, 0), segs=12)
            b.cyl((0.37, k * 0.12, -0.13), 0.01, 0.07, "cable", axis=(0, 0, 1), segs=8)
        b.bx((0.36, 0, -0.21), (0.16, 0.42, 0.02), "metal")
        b.obj("m7_espresso_detail", parent=esp)
    # plants on the back sills (simple leaf fans in terracotta pots)
    r = gb.rng("m7_cafe_plants")
    pots = PR.B([gb.mat("m7_terracotta", "#9a5a3a", 0.8), gb.mat("m7_leaf", "#3a5a2a", 0.6)])
    for x in (-4.9, -2.5, 1.2, 4.9):
        pots.cyl((x, D - 0.1, 0.88), 0.07, 0.14, 0, r2=0.09, segs=14)
        for j in range(9):
            a = r.random() * 2 * math.pi
            el = r.uniform(0.3, 1.1)
            L = r.uniform(0.18, 0.32)
            tip = Vector((x + L * math.cos(a) * math.cos(el), D - 0.1 - abs(L * math.sin(a) * math.cos(el) * 0.4),
                          0.95 + L * math.sin(el)))
            pots.capsule((x, D - 0.1, 0.93), tuple(tip), 0.004, 1)
            pots.ball(tuple(tip), 0.035, 1, scale=(1.6, 0.4, 0.9))
    pots.obj("m7_plants")


def treehouse(st):
    R = ROOMS["treehouse"]
    night = st.get("night", False)
    if not night:
        for o in _lights("wl_"):
            o.data.energy = R["window_area"]
        _world(*R["fill"])
        wb = S.OBJ.get("whiteboard")
        if wb is not None:
            for nd in wb.active_material.node_tree.nodes:
                if nd.type == "BSDF_PRINCIPLED":
                    nd.inputs["Emission Strength"].default_value = R["whiteboard"]
                    nd.inputs["Roughness"].default_value = 0.25
                    nd.inputs["Coat Weight"].default_value = 0.4
    W, D, H = K.LOOK["rooms"]["treehouse"]["size"]
    # M3's roof slabs and skylights tilt the wrong way (rotation -s*ang: each slope rises toward its eave, a butterfly
    # roof with open gaps that read as skylights in the grey box). Turned the right way: the slopes fall from the
    # ridge to the eaves and close the roof; the two skylights sit under them.
    for nm in ("roof-1", "roof1", "skylight0", "skylight1"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            o.rotation_euler.y = -o.rotation_euler.y
    if not night:
        # a soft top light over the table only (the pendant stays off by day: it front-lit faces), so the speakerphone
        # and the chargers read in O18e
        tx, ty = S.TREE["table"]
        sp = bpy.data.lights.new("m7_table_light", "SPOT")
        sp.energy, sp.spot_size, sp.spot_blend = R["table_light"], math.radians(55), 0.6
        sp.shadow_soft_size, sp.color = 0.3, gb.lin("#f2ede4")[:3]
        so = gb.link(bpy.data.objects.new("m7_table_light", sp))
        so.location = (tx, ty - 0.1, 2.3)
        so.rotation_euler = gb.look_rot(tuple(so.location), (tx, ty + 0.05, 0.0))
    # markers in the whiteboard's tray
    cols = ["#c0392b", "#2d3a8c", "#1e1e1e", "#2e7d4f"]
    for i, c in enumerate(cols):
        gb.cyl(f"m7_marker{i}", (-0.25 + 0.14 * i, D - 0.07, 1.185), 0.009, 0.13,
               gb.mat(f"m7_marker{i}", c, 0.4), axis="X")
    # moss: cushions along the deck's outer edge and, finer, in drifts along the three top rails (M3's clumps stay
    # under them), with strands hanging off the rails' edges; one mesh from arrays (bmesh ops per blob are quadratic)
    r = gb.rng("m7_moss")
    x0, x1, y0, y1 = W / 2 + 0.1, W / 2 + 3.4, -0.4, 4.2
    blobs = []
    for k in range(260):
        side = r.integers(0, 3)
        if side == 0:
            p = (x1 + 0.02, r.uniform(y0, y1), 0.005)
        elif side == 1:
            p = (r.uniform(x0, x1), y0 - 0.02, 0.005)
        else:
            p = (r.uniform(x0, x1), y1 + 0.02, 0.005)
        rad = 0.012 + 0.03 * r.random()
        blobs.append((p, (1.8 * rad, 1.8 * rad, 0.5 * rad)))
    strands = []
    for (ax, ay), (bx_, by_) in (((x1, y0), (x1, y1)), ((x0, y0), (x1, y0)), ((x0, y1), (x1, y1))):
        a_, b_ = Vector((ax, ay, 0)), Vector((bx_, by_, 0))
        L = (b_ - a_).length
        d = (b_ - a_).normalized()
        sd = Vector((-d.y, d.x, 0))
        for k in range(int(L * 140)):
            t = r.random()
            dens = 0.5 + 0.5 * math.sin(t * L * 2.3 + 1.7)
            if r.random() > 0.35 + 0.65 * dens:
                continue
            p = a_.lerp(b_, t) + sd * r.uniform(-0.05, 0.05)
            rad = r.uniform(0.008, 0.024)
            blobs.append(((p.x, p.y, 1.056 + r.uniform(0.0, 0.01)), (1.4 * rad, 1.4 * rad, 0.7 * rad)))
            if r.random() < 0.18:
                side = sd * (0.055 if r.random() < 0.5 else -0.055)
                strands.append(((p.x + side.x, p.y + side.y, 1.05), r.uniform(0.03, 0.09)))
    _blob_mesh("m7_moss_deck", blobs, strands, K.mat("moss", 0.95))
    if not night:
        # rain beyond the back and left windows (seen through the glass), and drips off the eaves
        S.drizzle("drizzle_back", (-5.0, D + 0.4, -2.0), (5.0, D + 6.0, 3.4), 1400, "m7_back_drizzle", alpha=0.3)
        S.drizzle("drizzle_left", (-W / 2 - 6.0, -1.0, -2.0), (-W / 2 - 0.4, D + 1.0, 3.4), 1200, "m7_left_drizzle", alpha=0.3)


def park(st):
    R = ROOMS["park"]
    fogc = R["fog"]
    old = bpy.data.objects.get("skyline")
    if old is not None:
        old.hide_render = True
        old.hide_viewport = True
    skyline(fogc)
    for o in bpy.data.objects:
        if o.name == "overcast" and o.type == "LIGHT":
            # M3's overcast sun travelled toward +Y (from behind the camera: it lit the crowd's backs and the band's
            # faces); M7's comes from behind the band, high and soft, toward the camera
            o.data.energy = R["sun"]
            o.data.angle = math.radians(R.get("sun_angle", 30))
            o.data.color = gb.lin("#eef1f3")[:3]
            o.data.specular_factor = R.get("sun_spec", 0.2)      # into the lens: its glare turned the wet grass white
            o.rotation_euler = (math.radians(-R.get("sun_elev", 50)), 0.0, math.radians(R.get("sun_yaw", 8)))
    park_world(R)
    # a thin fog volume over the crest (people and props in it fade as the trees and ground do; the fog materials
    # carry the far distance), lit by the sky and the soft sun
    m = bpy.data.materials.new("park_fog")
    nb = NB(m)
    v = nb.n("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = R["near_fog"]
    v.inputs["Color"].default_value = (0.9, 0.92, 0.93, 1)
    v.inputs["Anisotropy"].default_value = 0.3
    nb.out(None, v.outputs[0])
    m["m7"] = True
    o = gb.box("park_fog_volume", (0, 0, 2.0), (60, 60, 16), m)
    o.visible_shadow = False


def park_world(R):
    """The overcast: bright toward the skyline and overhead behind the band (+Y), dim behind the camera (-Y) and below
    the horizon, so the people facing the camera are lit from the dim side (silhouettes). Camera rays see a flat
    bright fog grey."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputWorld")
    bg = N("ShaderNodeBackground")
    tc = N("ShaderNodeTexCoord")
    sep = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Generated"], sep.inputs[0])

    def m_(op, a, b=0.0, clamp=False):
        nd = N("ShaderNodeMath")
        nd.operation, nd.use_clamp = op, clamp
        for i, v in enumerate((a, b)):
            if isinstance(v, bpy.types.NodeSocket):
                L(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]
    y, z = sep.outputs[1], sep.outputs[2]
    back = m_("POWER", m_("ADD", m_("MULTIPLY", y, 0.5), 0.5), R["back_bias"])      # 1 toward +Y, 0 toward -Y
    up = m_("ADD", m_("MULTIPLY", m_("MAXIMUM", z, 0.0), 0.6), 0.4)
    below = m_("MULTIPLY", m_("LESS_THAN", z, 0.0), 0.75)
    lit = m_("MULTIPLY", m_("ADD", m_("MULTIPLY", back, 0.85), 0.08), up)
    lit = m_("MULTIPLY", lit, m_("SUBTRACT", 1.0, below))
    lit = m_("MULTIPLY", lit, R["sky_light"])
    lp = N("ShaderNodeLightPath")
    cam = m_("MULTIPLY", lp.outputs["Is Camera Ray"], R["sky_cam"])
    strength = m_("ADD", m_("MULTIPLY", m_("SUBTRACT", 1.0, lp.outputs["Is Camera Ray"]), lit), cam)
    bg.inputs["Color"].default_value = gb.lin(K.PAL["sky_top"])
    L(strength, bg.inputs["Strength"])
    L(bg.outputs[0], out.inputs["Surface"])


# ---------------------------------------------------------------- haze as beams (coverage.haze's M7 replacement)

def haze(room, density=0.02):
    """A haze volume over the room and the daylight coming in as shafts: one soft sun outside, behind the window wall
    and above it, so the only direct light inside is what comes through the openings (the panes cast no shadow; the
    walls, frames and mullions shape the shafts, parallel as daylight is). Only the sun scatters in the haze (every
    other light has volume factor 0), so the haze reads as beams, not a glow; the shafts land as window-shaped pools on
    the floor and rim the band from behind."""
    R = ROOMS.get(room)
    if R is None or "sun" not in R:
        return None
    size = {"live": ((0, 5, 2.3), (14, 10, 4.6)), "cafe": ((0, 4.5, 1.8), (12, 9, 3.6)),
            "treehouse": ((0, 3, 1.8), (7, 6, 3.6))}[room]
    m = bpy.data.materials.new("haze")
    nb = NB(m)
    v = nb.n("ShaderNodeVolumePrincipled")
    P, _ = nb.world_pos()
    n1, _ = nb.noise(P, 0.35, 3.0, 0.6)
    nb.put(v.inputs["Density"], nb.mul(nb.maprange(n1, 0.3, 0.7, 0.6, 1.4), R["haze"]))
    v.inputs["Color"].default_value = (0.92, 0.93, 0.95, 1)
    v.inputs["Anisotropy"].default_value = 0.55
    nb.out(None, v.outputs[0])
    m["m7"] = True
    c, s_ = size
    if ENGINE[0] == "cycles":                       # its back face sat on the panes' plane: Cycles darkened them
        s_ = tuple(v - 0.2 for v in s_)
    o = gb.box("haze_volume", c, s_, m)
    o.visible_shadow = False
    for L_ in [o_ for o_ in bpy.data.objects if o_.type == "LIGHT"]:
        L_.data.volume_factor = 0.0
    for pane in [p for p in bpy.data.objects if p.name.startswith("pane_") and p.type == "MESH"]:
        pane.visible_shadow = False
    pitch, yaw = math.radians(R["sun_pitch"]), math.radians(R["sun_yaw"])
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), -math.sin(pitch)))   # travel dir
    ld = bpy.data.lights.new("beam_sun", "SUN")
    ld.energy = R["sun"]
    ld.angle = math.radians(R.get("sun_angle", 2.5))
    ld.color = gb.lin("#e6ebf0")[:3]
    ld.volume_factor = R.get("sun_volume", 1.0)
    ld.specular_factor = 0.5
    so = gb.link(bpy.data.objects.new("beam_sun", ld))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return f"M7 haze {R['haze']} (noise-modulated), daylight shafts through the window openings (sun {R['sun']})"


# ---------------------------------------------------------------- render settings, compositor

def settings(b, room):
    """After coverage.main's render settings: a second material pass (the performances' props and the instruments
    were added after the set), then Eevee or Cycles settings and the bloom."""
    upgrade_materials()
    sc = bpy.context.scene
    rc = CFG["render"]
    sc.render.filter_size = rc["filter_size"]
    sc.render.use_motion_blur = rc["motion_blur"]
    sc.render.motion_blur_shutter = rc["shutter"]
    sc.render.image_settings.color_depth = "16"
    if ENGINE[0] == "cycles":
        cycles_settings(sc, SAMPLES[0] or rc["cycles_samples"])
    else:
        ee = sc.eevee
        ee.taa_render_samples = SAMPLES[0] or rc["eevee_samples"]
        ee.use_raytracing = True
        ee.ray_tracing_options.resolution_scale = "1"
        ee.use_fast_gi = True
        ee.fast_gi_method = "GLOBAL_ILLUMINATION"
        ee.volumetric_tile_size = rc["volumetric_tile"]
        ee.volumetric_samples = rc["volumetric_samples"]
        ee.volumetric_shadow_samples = rc["volumetric_shadow_samples"]
        ee.use_volumetric_shadows = True
        ee.volumetric_end = 40.0 if room != "park" else 120.0
        ee.use_overscan = True
        ee.overscan_size = 3.0
        ee.shadow_resolution_scale = 1.0
        ee.shadow_ray_count = 2
        ee.shadow_step_count = 8
        ee.motion_blur_steps = 1
    bl = rc["bloom"]
    K.bloom(bl["threshold"], bl["size"], bl["strength"])


def cycles_settings(sc, samples):
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    cy = sc.cycles
    cy.device = "GPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPTIX"
    cy.seed = gb.SEEDS["main"]
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 8, 3, 3
    cy.transmission_bounces, cy.volume_bounces, cy.transparent_max_bounces = 4, 1, 16
    cy.volume_step_rate = 2.0
    cy.blur_glossy = 1.0
    # the panes and the sky dome are seen by the camera and in reflections, but don't light the room twice: Eevee
    # doesn't light from emission, the area lights and the beams do that
    for o in bpy.data.objects:
        if o.name.startswith(("pane_", "skylight", "sky_dome")):
            o.visible_diffuse = False
            o.visible_volume_scatter = False
            o.visible_shadow = False
    # Cycles has no per-light volume factor (Eevee's): as in Eevee, only the daylight shafts scatter in the haze. The
    # sun is split in two: one lights the surfaces, a copy at energy x its Eevee volume factor lights only the haze.
    sun = bpy.data.objects.get("beam_sun")
    if sun is not None:
        for o in bpy.data.objects:
            if o.type == "LIGHT" and o.data.volume_factor == 0.0:
                o.visible_volume_scatter = False
        vol = sun.copy()
        vol.data = sun.data.copy()
        vol.name = "beam_sun_volume"
        vol.data.energy = sun.data.energy * sun.data.volume_factor
        for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission"):
            setattr(vol, k, False)
        for c in sun.users_collection:
            c.objects.link(vol)
        sun.visible_volume_scatter = False


def exposure(s, room, expo, cam):
    """The view exposure for one sub-shot: the room's (config/look_m7.json) plus the build's and the camera's offsets
    as M5b had them (they keep the people angles darker than the wides)."""
    R = ROOMS.get(room, {})
    return K.LOOK["exposure"] + R.get("exposure", 0.0) + expo + CFG["cam_expo_scale"] * cam.get("expo", 0.0)
