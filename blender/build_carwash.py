"""Strawberry carwash: a strawberry-themed wash tunnel ahead of the bike (+X).

Red seeded walls, a green leafy roof edge, pink sign and trim, pink/red
brushes, and a giant strawberry on the roof. The entrance faces -X, toward
the pelican.
"""
import math
import os
import random

import bmesh
from mathutils import Vector

wash = collection("Carwash")
rng = random.Random(7)

berry_red = mat("Strawberry red", (0.78, 0.03, 0.06), rough=0.35)
berry_dark = mat("Strawberry dark red", (0.45, 0.01, 0.03), rough=0.4)
seed_yellow = mat("Seed yellow", (0.95, 0.80, 0.25), rough=0.4)
leaf_green = mat("Leaf green", (0.10, 0.45, 0.08), rough=0.6)
cream_pink = mat("Candy pink", (0.95, 0.38, 0.52), rough=0.5)
milk = mat("Strawberry milk", (1.0, 0.86, 0.88), rough=0.5)
asphalt = mat("Asphalt", (0.07, 0.07, 0.08), rough=0.9)
puddle = mat("Pink suds water", (0.85, 0.40, 0.55), rough=0.05)
bubble = mat("Bubble", (1.0, 0.85, 0.92), rough=0.05)
bubble_bsdf = bubble.node_tree.nodes["Principled BSDF"]
bubble_bsdf.inputs["Alpha"].default_value = 0.3
bubble_bsdf.inputs["Transmission Weight"].default_value = 1.0
bubble_bsdf.inputs["IOR"].default_value = 1.05

X0, X1 = 2.2, 5.2          # tunnel front / back
HALF_W, WALL = 1.3, 0.2    # outer half-width, wall thickness
H = 2.3                    # wall height
DOOR_H = 1.95


def box(name, lo, hi, material, col=wash):
    lo, hi = Vector(lo), Vector(hi)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lo + hi) / 2)
    obj = bpy.context.active_object
    obj.scale = hi - lo
    bpy.ops.object.transform_apply(scale=True)
    return _finish(obj, name, material, col, smooth=False)


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


# Driveway leading from the pelican into the tunnel, with a pink centre dash.
box("Driveway", (-12.0, -1.0, 0.0), (14.0, 1.0, 0.004), asphalt)
dashes = [box(f"Dash {i}", (x, -0.04, 0.004), (x + 0.4, 0.04, 0.006), cream_pink)
          for i, x in enumerate((-2.6, -1.8, 1.4, 2.0))]
join(dashes, "Lane dashes")

# Tunnel shell: side walls, facade pillars and lintel, roof slab.
for s, sign in (("L", 1), ("R", -1)):
    box(f"Side wall {s}", (X0, sign * (HALF_W - WALL) if sign > 0 else -HALF_W, 0),
        (X1, HALF_W if sign > 0 else -(HALF_W - WALL), H), berry_red)
box("Lintel", (X0 - 0.05, -HALF_W, DOOR_H), (X0 + 0.25, HALF_W, H), cream_pink)
for s, sign in (("L", 1), ("R", -1)):
    y0, y1 = sorted((sign * (HALF_W - 0.22), sign * (HALF_W + 0.02)))
    box(f"Pillar {s}", (X0 - 0.05, y0, 0), (X0 + 0.2, y1, DOOR_H), cream_pink)
box("Roof", (X0 - 0.12, -HALF_W - 0.12, H), (X1 + 0.12, HALF_W + 0.12, H + 0.1), leaf_green)
box("Back wall top", (X1 - 0.1, -HALF_W, DOOR_H), (X1, HALF_W, H), berry_dark)

# Leafy calyx fringe hanging over the roof edge, like the top of a strawberry.
leaves = []
edge = []
for i in range(14):
    edge.append((Vector((X0 - 0.12, -HALF_W + 2 * HALF_W * (i + 0.5) / 14, H + 0.05)), Vector((-1, 0, 0))))
for sign in (1, -1):
    for i in range(12):
        edge.append((Vector((X0 + (X1 - X0) * (i + 0.5) / 12, sign * (HALF_W + 0.12), H + 0.05)),
                     Vector((0, sign, 0))))
for i, (p, out) in enumerate(edge):
    tip = p + out * 0.12 + Vector((0, 0, -0.22 - 0.05 * (i % 2)))
    leaves.append(blob_between(f"Leaf {i}", p, tip, 0.09, leaf_green, wash, flat=0.25))
join(leaves, "Calyx fringe")

# Yellow seeds on the camera-facing wall and the facade pillars.
seeds = []
for ix in range(13):
    for iz in range(9):
        x = X0 + 0.3 + ix * 0.21 + (0.1 if iz % 2 else 0) + rng.uniform(-0.02, 0.02)
        z = 0.2 + iz * 0.2 + rng.uniform(-0.02, 0.02)
        if x < X1 - 0.1:
            seeds.append(blob(f"Seed {ix}-{iz}", (x, -HALF_W - 0.005, z), (0.022, 0.012, 0.035),
                              seed_yellow, wash, rot=(0, rng.uniform(-20, 20), 0), segs=12))
join(seeds, "Wall seeds")

# Entrance curtain: pink and green strips hanging from the lintel.
strips = []
for i in range(18):
    y = -HALF_W + 0.3 + i * (2 * HALF_W - 0.6) / 17
    strips.append(box(f"Strip {i}", (X0 + 0.12, y - 0.045, DOOR_H - 0.55 - 0.08 * (i % 3)),
                      (X0 + 0.14, y + 0.045, DOOR_H), cream_pink if i % 2 else leaf_green))
join(strips, "Curtain")

# Spinning brushes: stacks of fluffy rings, alternating pink and red.
for s, y in (("L", 0.72), ("R", -0.72)):
    rings = [ring(f"Brush {s} {k}", (X0 + 1.0, y, 0.15 + k * 0.13), 0.24, 0.07,
                  berry_red if k % 2 else cream_pink, wash, axis="Z", segs=32) for k in range(13)]
    join(rings, f"Side brush {s}")
    rod(f"Brush axle {s}", (X0 + 1.0, y, 0), (X0 + 1.0, y, H), 0.03, milk, wash)
top_rings = [ring(f"Top brush {k}", (X0 + 1.8, -0.9 + k * 0.15, 1.72), 0.2, 0.07,
                  berry_red if k % 2 else cream_pink, wash, axis="Y", segs=32) for k in range(13)]
join(top_rings, "Top brush")

# Suds: a pink puddle and bubbles drifting out of the entrance.
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1.0, fill_type="NGON",
                                  location=(X0 - 0.3, 0.1, 0.007))
p = _finish(bpy.context.active_object, "Puddle", puddle, wash, smooth=False)
p.scale = (0.5, 0.75, 1)
for i in range(16):
    r = rng.uniform(0.02, 0.06)
    loc = (X0 + rng.uniform(-0.9, 0.4), rng.uniform(-1.1, 1.1), rng.uniform(0.05, 2.0))
    blob(f"Bubble {i}", loc, (r, r, r), bubble, wash, segs=16)

# Giant strawberry on the roof: sphere tapered to a point, seeded, with a calyx.
BERRY = Vector((3.9, 0, H + 0.1 + 0.62))
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0, location=BERRY)
berry = bpy.context.active_object
bm = bmesh.new()
bm.from_mesh(berry.data)
for v in bm.verts:
    t = (v.co.z + 1) / 2                      # 0 at the tip, 1 at the top
    v.co.x *= 0.55 * (0.35 + 0.65 * t ** 0.6)
    v.co.y *= 0.55 * (0.35 + 0.65 * t ** 0.6)
    v.co.z *= 0.62
    if v.co.z > 0.5:
        v.co.z = 0.5 + (v.co.z - 0.5) * 0.4  # flatten the shoulders
bm.to_mesh(berry.data)
bm.free()
_finish(berry, "Giant strawberry", berry_red, wash)
berry.rotation_euler = (0, math.radians(-8), 0)
bpy.context.view_layer.update()
berry_seeds = []
mw = berry.matrix_world
for i, v in enumerate(berry.data.vertices):
    if i % 7 == 0 and -0.55 < v.co.z < 0.45:
        berry_seeds.append(blob(f"Berry seed {i}", mw @ (v.co * 1.01), (0.018, 0.018, 0.026),
                                seed_yellow, wash, segs=10))
join(berry_seeds, "Berry seeds")
top = mw @ Vector((0, 0, 0.52))
calyx = []
for k in range(8):
    a = 2 * math.pi * k / 8
    calyx.append(blob_between(f"Sepal {k}", top, top + Vector((math.cos(a) * 0.42, math.sin(a) * 0.42, -0.1)),
                              0.1, leaf_green, wash, flat=0.25))
join(calyx, "Berry calyx")
rod("Berry stem", top, top + Vector((0.03, 0, 0.22)), 0.03, leaf_green, wash)

# The sign: pink board with a red border, standing on the front roof edge.
SIGN_C = Vector((X0 - 0.05, 0, H + 0.62))
box("Sign border", SIGN_C + Vector((-0.02, -1.42, -0.42)), SIGN_C + Vector((0.08, 1.42, 0.42)), berry_red)
lightbox = mat("Sign board dark", (0.06, 0.01, 0.025), rough=0.6)
box("Sign board", SIGN_C + Vector((-0.05, -1.34, -0.34)), SIGN_C + Vector((0.0, 1.34, 0.34)), lightbox)
for sign in (1, -1):
    rod(f"Sign leg {'L' if sign > 0 else 'R'}", (X0, sign * 1.0, H + 0.1), (X0, sign * 1.0, H + 0.25),
        0.03, cream_pink, wash)

txt = bpy.data.curves.new("Sign text", "FONT")
txt.body = "Strawberry carwash"
txt.align_x = "CENTER"
txt.align_y = "CENTER"
txt.extrude = 0.015
txt.size = 0.3
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(font_path):
    txt.font = bpy.data.fonts.load(font_path, check_existing=True)
text = bpy.data.objects.new("Sign text", txt)
neon = mat("Neon red", (0.9, 0.02, 0.08), rough=0.3, emit=(1.0, 0.08, 0.2))
neon.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 12.0
text.data.materials.append(neon)
wash.objects.link(text)
text.rotation_euler = (math.radians(90), 0, math.radians(-90))
text.location = SIGN_C + Vector((-0.07, 0, 0))
bpy.context.view_layer.update()
fit = min(2.4 / text.dimensions.x, 0.5 / text.dimensions.y)
text.scale = (fit, fit, 1)
