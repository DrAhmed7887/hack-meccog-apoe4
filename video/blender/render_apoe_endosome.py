"""Render two publication-grade Blender Cycles 3D shots for The APOE4 Endosome Bottleneck:

1. shot1_apoe_fold: Real atomic CA backbone ribbon + heavy-atom Arg112-Glu109 salt bridge
   (2.53 A) and displaced Arg61 from PDB 1B68 (APOE4) vs PDB 1NFN (APOE3) on deep obsidian #0B1215.
2. shot2_endosome_jam: Cutaway translucent early/late endosome vesicles containing cholesterol
   deposits and transmembrane ring complexes on archival paper #F6F4EE.

Run:
  blender -b -P video/blender/render_apoe_endosome.py -- --shot all --samples 24 --res 1920x1080
"""
from __future__ import annotations

import argparse
import gzip
import math
import shlex
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--shot", choices=("shot1", "shot2", "all"), default="all")
ap.add_argument("--engine", choices=("BLENDER_EEVEE", "CYCLES"), default="BLENDER_EEVEE")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--res", default="1920x1080")
ap.add_argument("--frames1", type=int, default=120)
ap.add_argument("--frames2", type=int, default=120)
ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "renders"))
args = ap.parse_args(argv)

ROOT = Path(__file__).resolve().parent.parent.parent
STRUCT_DIR = ROOT / "docs" / "structures"
OUT_ROOT = Path(args.out)


def srgb(hex_color: str) -> tuple[float, float, float, float]:
    h = hex_color.lstrip("#")
    c = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


def parse_atoms(cif_gz: Path) -> list[dict]:
    txt = gzip.decompress(cif_gz.read_bytes()).decode("utf-8")
    lines = txt.splitlines()
    atoms = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            cols = []
            j = i + 1
            while j < n and lines[j].lstrip().startswith("_"):
                cols.append(lines[j].strip())
                j += 1
            if cols and all(c.startswith("_atom_site.") for c in cols):
                idx = {c: pos for pos, c in enumerate(cols)}
                for k in range(j, n):
                    rs = lines[k].strip()
                    if not rs or rs.startswith("#") or rs == "loop_" or rs.startswith("_"):
                        break
                    tok = shlex.split(rs) if ("'" in rs or '"' in rs) else rs.split()
                    atoms.append(
                        {
                            "asym": tok[idx["_atom_site.auth_asym_id"]],
                            "seq": int(tok[idx["_atom_site.auth_seq_id"]]),
                            "atom": tok[idx["_atom_site.auth_atom_id"]],
                            "elem": tok[idx["_atom_site.type_symbol"]],
                            "xyz": Vector(
                                (
                                    float(tok[idx["_atom_site.Cartn_x"]]),
                                    float(tok[idx["_atom_site.Cartn_y"]]),
                                    float(tok[idx["_atom_site.Cartn_z"]]),
                                )
                            ),
                        }
                    )
                break
            i = j
            continue
        i += 1
    return atoms


def setup_render(bg_hex: str, n_frames: int, out_prefix: Path) -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    avail = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    if args.engine in avail:
        sc.render.engine = args.engine
    elif "BLENDER_EEVEE_NEXT" in avail:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        sc.render.engine = avail[0]
    w, h = map(int, args.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, n_frames
    if sc.render.engine == "CYCLES":
        sc.cycles.samples = args.samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 4
        sc.cycles.device = "CPU"
    elif hasattr(sc, "eevee"):
        if hasattr(sc.eevee, "taa_render_samples"):
            sc.eevee.taa_render_samples = args.samples
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(out_prefix)

    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = srgb(bg_hex)
    bg.inputs["Strength"].default_value = 1.0
    return sc


def make_mat(name: str, hex_c: str, roughness: float = 0.35, metallic: float = 0.1, emission: float = 0.0, alpha: float = 1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = srgb(hex_c)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    if emission > 0 and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = srgb(hex_c)
        bsdf.inputs["Emission Strength"].default_value = emission
    return m


def add_area_light(name: str, loc: tuple, target: Vector, energy: float, size: float, hex_c: str = "#FFFFFF"):
    ldata = bpy.data.lights.new(name, type="AREA")
    ldata.energy = energy
    ldata.size = size
    ldata.color = srgb(hex_c)[:3]
    obj = bpy.data.objects.new(name, ldata)
    bpy.context.collection.objects.link(obj)
    obj.location = Vector(loc)
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return obj


def add_backbone_curve(name: str, pts: list[Vector], radius: float, mat) -> bpy.types.Object:
    cdata = bpy.data.curves.new(name, type="CURVE")
    cdata.dimensions = "3D"
    cdata.resolution_u = 16
    cdata.bevel_depth = radius
    cdata.bevel_resolution = 8
    sp = cdata.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    obj = bpy.data.objects.new(name, cdata)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_sphere(name: str, center: Vector, radius: float, mat) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=20, radius=radius, location=center)
    obj = bpy.context.active_object
    obj.name = name
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.data.materials.append(mat)
    return obj


def add_rod(name: str, p1: Vector, p2: Vector, radius: float, mat) -> bpy.types.Object:
    mid = (p1 + p2) * 0.5
    diff = p2 - p1
    dist = diff.length
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=radius, depth=max(0.05, dist), location=mid)
    obj = bpy.context.active_object
    obj.name = name
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.rotation_euler = diff.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj


def render_shot1() -> None:
    out_dir = OUT_ROOT / "shot1"
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = setup_render("#0B1215", args.frames1, out_dir / "f_")

    atoms_4 = parse_atoms(STRUCT_DIR / "1b68.cif.gz")
    atoms_3 = parse_atoms(STRUCT_DIR / "1nfn.cif.gz")

    ca_4 = [a["xyz"] for a in atoms_4 if a["atom"] == "CA" and a["asym"] == "A"]
    center = sum(ca_4, Vector((0, 0, 0))) / len(ca_4)
    scale = 0.25

    def norm(v: Vector) -> Vector:
        return (v - center) * scale

    pts_4 = [norm(v) for v in ca_4]
    # Center APOE3 overlay slightly offset for side-by-side comparison depth
    ca_3 = [a["xyz"] for a in atoms_3 if a["atom"] == "CA" and a["asym"] == "A"]
    c3 = sum(ca_3, Vector((0, 0, 0))) / len(ca_3)
    pts_3 = [(v - c3) * scale + Vector((-4.2, 2.0, -0.8)) for v in ca_3]

    mat_4 = make_mat("APOE4_Ribbon", "#E8ECEA", roughness=0.28, metallic=0.25)
    mat_3 = make_mat("APOE3_Ghost", "#1E8875", roughness=0.45, metallic=0.1, emission=0.2)
    mat_r112 = make_mat("Arg112_Hot", "#F59E0B", roughness=0.2, metallic=0.15, emission=1.1)
    mat_e109 = make_mat("Glu109_Salt", "#10B981", roughness=0.25, metallic=0.15, emission=0.7)
    mat_r61 = make_mat("Arg61_Switch", "#EF4444", roughness=0.25, metallic=0.1, emission=0.8)
    mat_bridge = make_mat("SaltBridge", "#FBBF24", roughness=0.15, emission=2.2)

    add_backbone_curve("APOE4_1B68", pts_4, 0.11, mat_4)
    add_backbone_curve("APOE3_1NFN", pts_3, 0.08, mat_3)

    # Highlight key functional atoms in 1B68
    by_key = {(a["seq"], a["atom"]): norm(a["xyz"]) for a in atoms_4 if a["asym"] == "A"}
    for seq, atom, r, mat in (
        (112, "NH1", 0.34, mat_r112),
        (112, "CA", 0.25, mat_r112),
        (109, "OE2", 0.32, mat_e109),
        (109, "CA", 0.24, mat_e109),
        (61, "CZ", 0.30, mat_r61),
        (61, "CA", 0.24, mat_r61),
    ):
        if (seq, atom) in by_key:
            add_sphere(f"res_{seq}_{atom}", by_key[(seq, atom)], r, mat)

    if (112, "NH1") in by_key and (109, "OE2") in by_key:
        add_rod("Arg112_Glu109_Bridge", by_key[(112, "NH1")], by_key[(109, "OE2")], 0.085, mat_bridge)
    if (112, "CA") in by_key and (112, "NH1") in by_key:
        add_rod("Arg112_Stem", by_key[(112, "CA")], by_key[(112, "NH1")], 0.09, mat_r112)
    if (61, "CA") in by_key and (61, "CZ") in by_key:
        add_rod("Arg61_Stem", by_key[(61, "CA")], by_key[(61, "CZ")], 0.085, mat_r61)

    focus_pt = by_key.get((112, "NH1"), Vector((0, 0, 0)))

    add_area_light("KeyLight", (12, -14, 11), focus_pt, 2200, 7.0, "#FFF9EE")
    add_area_light("RimLight", (-13, 10, 8), focus_pt, 1500, 6.0, "#38BDF8")
    add_area_light("FillLight", (0, -10, -8), focus_pt, 900, 9.0, "#0F766E")

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    sc.camera = cam_obj

    target_obj = bpy.data.objects.new("Target", None)
    bpy.context.collection.objects.link(target_obj)
    target_obj.location = Vector((0, 0, 0))
    c = cam_obj.constraints.new("TRACK_TO")
    c.target = target_obj
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    # Keyframed smooth orbit & macro push-in toward Arg112-Glu109 salt bridge
    keyframes = [
        (1, Vector((-13.5, -17.5, 6.5)), Vector((-0.8, 0.2, 0.0))),
        (max(2, args.frames1 // 2), Vector((2.5, -13.5, 3.8)), focus_pt * 0.65),
        (args.frames1, focus_pt + Vector((7.2, -7.2, 2.8)), focus_pt),
    ]
    for f, cloc, tloc in keyframes:
        cam_obj.location = cloc
        cam_obj.keyframe_insert("location", frame=f)
        target_obj.location = tloc
        target_obj.keyframe_insert("location", frame=f)

    bpy.ops.render.render(animation=True)
    print(f"rendered shot1 -> {out_dir}")


def render_shot2() -> None:
    out_dir = OUT_ROOT / "shot2"
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = setup_render("#F6F4EE", args.frames2, out_dir / "f_")

    mat_shell = make_mat("Membrane", "#0B5D4B", roughness=0.25, metallic=0.18, alpha=1.0)
    mat_lyso = make_mat("LysoShell", "#29403A", roughness=0.28, metallic=0.22, alpha=1.0)
    mat_chol = make_mat("Cholesterol", "#D97706", roughness=0.18, metallic=0.15, emission=0.35)
    mat_rec = make_mat("Receptor", "#0284C7", roughness=0.22, metallic=0.25)
    mat_pump = make_mat("NHE6_ABCA1", "#9A3412", roughness=0.22, metallic=0.3)

    # Outer spherical vesicle (sculptural cutaway ring / early endosome on left)
    bpy.ops.mesh.primitive_torus_add(major_segments=72, minor_segments=28, major_radius=3.1, minor_radius=0.34, location=(-3.4, 0.0, 0.2))
    ring1 = bpy.context.active_object
    ring1.rotation_euler = (math.radians(66), math.radians(15), 0)
    for p in ring1.data.polygons:
        p.use_smooth = True
    ring1.data.materials.append(mat_shell)

    # Inner clustered trapped receptors + NHE6 exchanger nodes inside early endosome
    for k in range(6):
        ang = k * (2.0 * math.pi / 6.0)
        add_sphere(f"rec_{k}", Vector((-3.4 + 1.35 * math.cos(ang), 1.15 * math.sin(ang), 0.3)), 0.36, mat_rec)
    add_sphere("nhe6_dimer_a", Vector((-2.6, -1.8, 0.2)), 0.56, mat_pump)
    add_sphere("nhe6_dimer_b", Vector((-1.7, -2.0, 0.25)), 0.56, mat_pump)

    # Right organelle: swollen lysosome storing sequestered unesterified cholesterol clusters
    bpy.ops.mesh.primitive_torus_add(major_segments=72, minor_segments=28, major_radius=3.5, minor_radius=0.38, location=(3.5, 0.3, 0.1))
    ring2 = bpy.context.active_object
    ring2.rotation_euler = (math.radians(70), math.radians(-12), 0)
    for p in ring2.data.polygons:
        p.use_smooth = True
    ring2.data.materials.append(mat_lyso)

    for k in range(18):
        ang = k * 2.39996
        rad = 0.48 * math.sqrt(k + 1)
        pos = Vector((3.5 + rad * math.cos(ang), 0.3 + rad * math.sin(ang), 0.15 + 0.3 * math.sin(k)))
        add_sphere(f"chol_{k}", pos, 0.36, mat_chol)

    add_area_light("SunTop", (6, -9, 12), Vector((0, 0, 0)), 2200, 9.0, "#FFFFFF")
    add_area_light("CoolFill", (-8, 6, 8), Vector((0, 0, 0)), 1100, 7.0, "#E0F2FE")

    cam_data = bpy.data.cameras.new("Cam2")
    cam_data.lens = 42
    cam_obj = bpy.data.objects.new("Cam2", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    sc.camera = cam_obj

    target_obj = bpy.data.objects.new("Target2", None)
    bpy.context.collection.objects.link(target_obj)
    target_obj.location = Vector((0, 0, 0))
    c = cam_obj.constraints.new("TRACK_TO")
    c.target = target_obj
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    for f, cloc, tloc in (
        (1, Vector((-2.8, -16.8, 5.2)), Vector((-0.6, 0.0, 0.2))),
        (max(2, args.frames2 // 2), Vector((0.2, -15.5, 4.4)), Vector((0.4, 0.2, 0.2))),
        (args.frames2, Vector((3.2, -13.5, 4.0)), Vector((2.2, 0.3, 0.2))),
    ):
        cam_obj.location = cloc
        cam_obj.keyframe_insert("location", frame=f)
        target_obj.location = tloc
        target_obj.keyframe_insert("location", frame=f)

    bpy.ops.render.render(animation=True)
    print(f"rendered shot2 -> {out_dir}")


def main() -> None:
    if args.shot in ("shot1", "all"):
        render_shot1()
    if args.shot in ("shot2", "all"):
        render_shot2()


if __name__ == "__main__":
    main()
