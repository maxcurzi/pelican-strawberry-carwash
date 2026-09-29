"""Lighthouse on a rock at night, out at sea behind the carwash.

Stacked in the benchmark's order: sea, rock, striped tower, gallery, lantern,
roof, plus a rotating beam. Needs SEA_Z and emissive() from build_scene.py.
"""
import math
import random

import bmesh

lh = collection("Lighthouse")
rng_lh = random.Random(11)

ISLAND = Vector((15, 62, SEA_Z))
TOWER_H = 10.0
R_BASE, R_TOP = 1.35, 0.95

# Rock: a lumpy, flattened icosphere poking out of the sea.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0, location=ISLAND)
rock = bpy.context.active_object
bm = bmesh.new()
bm.from_mesh(rock.data)
for v in bm.verts:
    v.co *= 1.0 + rng_lh.uniform(-0.12, 0.12)
    if v.co.z > 0.55:
        v.co.z = 0.55 + (v.co.z - 0.55) * 0.3   # flat top for the tower
bm.to_mesh(rock.data)
bm.free()
rock.scale = (9, 6.5, 4.8)
_finish(rock, "Lighthouse rock", mat("Island rock", (0.09, 0.085, 0.08), rough=0.95), lh, smooth=False)
for i in range(7):
    a = rng_lh.uniform(0, 2 * math.pi)
    s = rng_lh.uniform(0.8, 1.8)
    blob(f"Boulder {i}", ISLAND + Vector((math.cos(a) * 8.5, math.sin(a) * 6, 0.1)),
         (s * 1.4, s, s * 0.8), mat("Island rock", (0.09, 0.085, 0.08)), lh, segs=10)
foam = emissive("Surf foam", (0.55, 0.6, 0.7), 0.15)
ring("Surf ring", ISLAND + Vector((0, 0, 0.02)), 8.6, 0.25, foam, lh, axis="Z", segs=64).scale = (1, 0.76, 0.2)

# Tower: tapered, alternating red and white bands.
BASE = ISLAND + Vector((0, 0, 4.8 * 0.55 * 0.97))
red = mat("Lighthouse red", (0.55, 0.03, 0.03), rough=0.5)
white = mat("Lighthouse white", (0.85, 0.85, 0.82), rough=0.5)
bands = 6
for i in range(bands):
    z0, z1 = TOWER_H * i / bands, TOWER_H * (i + 1) / bands
    r0 = R_BASE + (R_TOP - R_BASE) * i / bands
    r1 = R_BASE + (R_TOP - R_BASE) * (i + 1) / bands
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r0, radius2=r1, depth=z1 - z0,
                                    location=BASE + Vector((0, 0, (z0 + z1) / 2)))
    _finish(bpy.context.active_object, f"Tower band {i}", red if i % 2 else white, lh)
window_glow = emissive("Window glow", (1.0, 0.75, 0.4), 4.0)
for k, z in enumerate((2.5, 5.2, 7.8)):
    r = R_BASE + (R_TOP - R_BASE) * z / TOWER_H
    blob(f"Tower window {k}", BASE + Vector((0, -r, z)), (0.14, 0.05, 0.24), window_glow, lh, segs=12)

# Gallery, railing, lantern room, roof.
TOP = BASE + Vector((0, 0, TOWER_H))
dark = mat("Lighthouse iron", (0.05, 0.05, 0.05), rough=0.4, metal=0.7)
rod("Gallery deck", TOP, TOP + Vector((0, 0, 0.18)), R_TOP + 0.45, dark, lh, verts=48)
ring("Gallery rail", TOP + Vector((0, 0, 0.75)), R_TOP + 0.4, 0.035, dark, lh, axis="Z")
for k in range(16):
    a = 2 * math.pi * k / 16
    p = TOP + Vector((math.cos(a) * (R_TOP + 0.4), math.sin(a) * (R_TOP + 0.4), 0.18))
    rod(f"Rail post {k}", p, p + Vector((0, 0, 0.57)), 0.025, dark, lh, verts=6)
LAMP = TOP + Vector((0, 0, 0.18 + 0.75))
lantern = emissive("Lantern glass", (1.0, 0.85, 0.5), 25.0)
rod("Lantern room", TOP + Vector((0, 0, 0.18)), TOP + Vector((0, 0, 1.68)), 0.72, lantern, lh, verts=32)
for k in range(8):
    a = 2 * math.pi * k / 8
    p = TOP + Vector((math.cos(a) * 0.73, math.sin(a) * 0.73, 0.18))
    rod(f"Lantern mullion {k}", p, p + Vector((0, 0, 1.5)), 0.03, dark, lh, verts=6)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1.0, radius2=0.08, depth=0.9,
                                location=TOP + Vector((0, 0, 1.68 + 0.45)))
_finish(bpy.context.active_object, "Lantern roof", red, lh)
blob("Roof ball", TOP + Vector((0, 0, 2.65)), (0.14,) * 3, dark, lh, segs=12)

# Keeper's cottage beside the tower.
cottage = BASE + Vector((-2.8, -0.6, 0))
box("Cottage", cottage + Vector((-1.1, -0.9, -0.3)), cottage + Vector((1.1, 0.9, 1.6)), white, lh)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.65, radius2=0, depth=1.0,
                                location=cottage + Vector((0, 0, 2.1)), rotation=(0, 0, math.radians(45)))
roof = bpy.context.active_object
roof.scale = (1.0, 0.8, 1.0)
_finish(roof, "Cottage roof", red, lh, smooth=False)
box("Cottage window", cottage + Vector((-0.35, -0.92, 0.5)), cottage + Vector((0.35, -0.9, 1.1)), window_glow, lh)

# Rotating beam: two opposed light cones plus a real spot light, on one pivot.
pivot = bpy.data.objects.new("Beam pivot", None)
pivot.location = LAMP
lh.objects.link(pivot)
beam_mat = bpy.data.materials.new("Beam glow")
beam_mat.use_nodes = True
bn = beam_mat.node_tree
for n in list(bn.nodes):
    bn.nodes.remove(n)
tc = bn.nodes.new("ShaderNodeTexCoord")
sz = bn.nodes.new("ShaderNodeSeparateXYZ")
bn.links.new(tc.outputs["Generated"], sz.inputs["Vector"])
fade = bn.nodes.new("ShaderNodeMath")
fade.operation = "POWER"
fade.inputs[1].default_value = 3.0
bn.links.new(sz.outputs["Z"], fade.inputs[0])
strength = bn.nodes.new("ShaderNodeMath")
strength.operation = "MULTIPLY"
strength.inputs[1].default_value = 0.9
bn.links.new(fade.outputs[0], strength.inputs[0])
em = bn.nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.9, 0.6, 1)
bn.links.new(strength.outputs[0], em.inputs["Strength"])
tr = bn.nodes.new("ShaderNodeBsdfTransparent")
addsh = bn.nodes.new("ShaderNodeAddShader")
bn.links.new(tr.outputs[0], addsh.inputs[0])
bn.links.new(em.outputs[0], addsh.inputs[1])
mo = bn.nodes.new("ShaderNodeOutputMaterial")
bn.links.new(addsh.outputs[0], mo.inputs["Surface"])
beam_mat.surface_render_method = "BLENDED"
BEAM_LEN = 70
for k, sign in enumerate((1, -1)):
    # Cone tip at the lamp, opening outward along ±X of the pivot.
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6.0, radius2=0.25, depth=BEAM_LEN,
                                    location=LAMP + Vector((sign * BEAM_LEN / 2, 0, 0)),
                                    rotation=(0, math.radians(90 * -sign), 0))
    beam = _finish(bpy.context.active_object, f"Beam {k}", beam_mat, lh)
    beam.parent = pivot
    beam.matrix_parent_inverse = pivot.matrix_world.inverted()
spot_data = bpy.data.lights.new("Beam spot", "SPOT")
spot_data.energy = 60000
spot_data.spot_size = math.radians(10)
spot_data.color = (1.0, 0.9, 0.65)
spot = bpy.data.objects.new("Beam spot", spot_data)
spot.location = LAMP
spot.rotation_euler = (0, math.radians(-90), 0)   # -Z of the light -> +X
lh.objects.link(spot)
spot.parent = pivot
spot.matrix_parent_inverse = pivot.matrix_world.inverted()
lamp_data = bpy.data.lights.new("Lantern light", "POINT")
lamp_data.energy = 3000
lamp_data.color = (1.0, 0.85, 0.55)
lamp_obj = bpy.data.objects.new("Lantern light", lamp_data)
lamp_obj.location = LAMP + Vector((0, 0, 2.2))
lh.objects.link(lamp_obj)

# One full sweep every 4 seconds.
pivot.rotation_euler = (0, 0, 0)
pivot.keyframe_insert("rotation_euler", index=2, frame=1)
pivot.rotation_euler = (0, 0, 2 * math.pi * 288 / 96)
pivot.keyframe_insert("rotation_euler", index=2, frame=289)
