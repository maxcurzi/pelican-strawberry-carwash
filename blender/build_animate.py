"""Animation: the pelican pedals up to the Strawberry carwash at night.

Frames 1-288 at 24 fps (12 s). The rider rolls in along +X and brakes to a
stop at the entrance by STOP_FRAME. Wheels, cranks and legs are driven by the
distance travelled, so the pedalling always matches the speed. The camera
tracks side-on (lighthouse visible behind), then pulls out to a wide shot.
"""
import math

from mathutils import Vector

rig = collection("Rig")
F0, F1, STOP_FRAME = 1, 288, 250
X_START, X_STOP = -10.0, 1.0
GEAR = 1.5
HIP_OFF = Vector((0.05, 0.09, -0.12))
THIGH, SHIN = 0.34, 0.39


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.empty_display_size = 0.1
    rig.objects.link(e)
    if parent:
        e.parent = parent
    return e


def parent_keep(obj, par):
    bpy.context.view_layer.update()
    obj.parent = par
    obj.matrix_parent_inverse = par.matrix_world.inverted()


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rider_x(f):
    t = max(0.0, min(1.0, (f - F0) / (STOP_FRAME - F0)))
    return X_START + (X_STOP - X_START) * (1 - (1 - t) ** 2)


# --- Rig hierarchy --------------------------------------------------------
rider = empty("Rider", (0, 0, 0))
wheel_r = empty("Rear wheel pivot", REAR, rider)
wheel_f = empty("Front wheel pivot", FRONT, rider)
cranks = empty("Crankset pivot", BB, rider)
upper = empty("Pelican upper", (0, 0, 0), rider)

for obj in list(bike.objects):
    n = obj.name
    if n.startswith("Rear "):
        parent_keep(obj, wheel_r)
    elif n.startswith("Front "):
        parent_keep(obj, wheel_f)
    elif n.startswith(("Crank ", "Pedal ", "Chainring")):
        parent_keep(obj, cranks)
    else:
        parent_keep(obj, rider)

for obj in list(bird.objects):
    if obj.name.startswith(("Thigh", "Shin", "Knee", "Foot")):
        bpy.data.objects.remove(obj, do_unlink=True)
    else:
        parent_keep(obj, upper)

legs = {}
for s in ("L", "R"):
    thigh = blob_between(f"Thigh {s}", (0, 0, 0), (0, 0, 1), 0.05, body_brown, bird)
    shin = rod(f"Shin {s}", (0, 0, -0.5), (0, 0, 0.5), 0.017, leg_dark, bird)
    knee = blob(f"Knee {s}", (0, 0, 0), (0.028,) * 3, leg_dark, bird)
    foot = blob(f"Foot {s}", (0, 0, 0), (0.085, 0.05, 0.012), leg_dark, bird)
    for o in (thigh, shin, knee, foot):
        o.parent = rider
        o.rotation_mode = "QUATERNION"
    legs[s] = (thigh, shin, knee, foot)

# Bike headlamp and a soft fill that travels with the rider.
lamp_body = rod("Headlamp", BAR + Vector((0.02, 0, -0.07)), BAR + Vector((0.08, 0, -0.07)), 0.03, black, bike)
lens = blob("Headlamp lens", BAR + Vector((0.085, 0, -0.07)), (0.008, 0.028, 0.028),
            emissive("Headlamp glow", (1.0, 0.95, 0.8), 20.0), bike)
for o in (lamp_body, lens):
    parent_keep(o, rider)
hl = bpy.data.lights.new("Headlamp beam", "SPOT")
hl.energy, hl.spot_size, hl.color = 120, math.radians(45), (1.0, 0.95, 0.85)
hlo = bpy.data.objects.new("Headlamp beam", hl)
hlo.location = BAR + Vector((0.1, 0, -0.07))
hlo.rotation_euler = (0, math.radians(-80), 0)
rig.objects.link(hlo)
hlo.parent = rider
fill = bpy.data.lights.new("Rider fill", "AREA")
fill.energy, fill.size, fill.color = 70, 1.5, (0.8, 0.85, 1.0)
fillo = bpy.data.objects.new("Rider fill", fill)
fillo.location = (0.4, -2.8, 2.0)
fillo.rotation_euler = (Vector((0.1, 0, 1.0)) - fillo.location).to_track_quat("-Z", "Y").to_euler()
rig.objects.link(fillo)
fillo.parent = rider

# --- Carwash machinery ----------------------------------------------------
rib_mat = mat("Brush rib", (0.10, 0.45, 0.08), rough=0.6)
spinners = []
for s in ("L", "R"):
    brush = bpy.data.objects[f"Side brush {s}"]
    c = brush.location.copy()
    for k in range(6):
        a = 2 * math.pi * k / 6
        off = Vector((math.cos(a) * 0.31, math.sin(a) * 0.31, 0))
        r_ = rod(f"Brush rib {s}{k}", c + off + Vector((0, 0, -0.1)), c + off + Vector((0, 0, 1.6)),
                 0.03, rib_mat, wash, verts=8)
        parent_keep(r_, brush)
    spinners.append((brush, 2, 1 if s == "L" else -1))
top = bpy.data.objects["Top brush"]
c = top.location.copy()
for k in range(6):
    a = 2 * math.pi * k / 6
    off = Vector((math.cos(a) * 0.27, 0, math.sin(a) * 0.27))
    r_ = rod(f"Top rib {k}", c + off + Vector((0, -0.1, 0)), c + off + Vector((0, 1.9, 0)),
             0.028, rib_mat, wash, verts=8)
    parent_keep(r_, top)
spinners.append((top, 1, 1))
for obj, axis, direction in spinners:
    obj.rotation_euler[axis] = 0
    obj.keyframe_insert("rotation_euler", index=axis, frame=F0)
    obj.rotation_euler[axis] = direction * 2 * math.pi * (F1 - F0 + 1) / 24 * 0.8
    obj.keyframe_insert("rotation_euler", index=axis, frame=F1 + 1)

# Bubbles: the original ones plus extra, rising and drifting out, popping at the top.
bubbles = [o for o in wash.objects if o.name.startswith("Bubble ")]
for i in range(26):
    r = rng.uniform(0.02, 0.07)
    bubbles.append(blob(f"Bubble extra {i}", (X0 + rng.uniform(-0.6, 0.5), rng.uniform(-1.0, 1.0), 0.1),
                        (r, r, r), bubble, wash, segs=16))
bubble_paths = []
for b in bubbles:
    bubble_paths.append((b, b.location.copy(), b.scale[0], rng.uniform(0.25, 0.6),
                         rng.uniform(0, 2.4), rng.uniform(0.1, 0.35), rng.uniform(0, 6.28)))

# --- Per-frame keys -------------------------------------------------------
cam = scene.camera
CAM_END, LOOK_END = Vector((-3.5, -7.5, 1.8)), Vector((2.2, 0.8, 2.0))
prev_euler = None
for f in range(F0, F1 + 1):
    x = rider_x(f)
    wheel = (x - X_START) / WHEEL_R
    phi = wheel / GEAR
    bob = 0.012 * math.sin(2 * phi)

    rider.location = (x, 0, 0)
    rider.keyframe_insert("location", index=0, frame=f)
    for piv in (wheel_r, wheel_f):
        piv.rotation_euler = (0, wheel, 0)
        piv.keyframe_insert("rotation_euler", index=1, frame=f)
    cranks.rotation_euler = (0, phi, 0)
    cranks.keyframe_insert("rotation_euler", index=1, frame=f)
    upper.location = (0, 0, bob)
    upper.keyframe_insert("location", index=2, frame=f)

    for s, a0, y in (("R", CRANK_ANGLE, -PEDAL_Y), ("L", CRANK_ANGLE + math.pi, PEDAL_Y)):
        a = a0 - phi
        pedal = BB + Vector((CRANK_LEN * math.cos(a), 1.1 * y, CRANK_LEN * math.sin(a)))
        sign = 1 if s == "L" else -1
        hip = BODY + Vector((HIP_OFF.x, sign * HIP_OFF.y, HIP_OFF.z + bob))
        ankle = pedal + Vector((0, 0, 0.04))
        knee = two_bone_knee(hip, ankle, THIGH, SHIN, (1, 0, 0.3))
        thigh, shin, knee_o, foot = legs[s]
        for obj, p, q in ((thigh, hip, knee), (shin, knee, ankle)):
            d = q - p
            obj.location = (p + q) / 2
            obj.rotation_quaternion = d.to_track_quat("Z", "Y")
            obj.scale = (0.05, 0.05, d.length / 2) if obj is thigh else (1, 1, d.length)
            obj.keyframe_insert("location", frame=f)
            obj.keyframe_insert("rotation_quaternion", frame=f)
            obj.keyframe_insert("scale", frame=f)
        knee_o.location = knee
        knee_o.keyframe_insert("location", frame=f)
        foot.location = pedal + Vector((0.03, 0, 0.028))
        foot.keyframe_insert("location", frame=f)

    for b, base, r, speed, phase, drift, wob in bubble_paths:
        h = (phase + speed * f / 24) % 2.4
        b.location = (base.x - drift * h + 0.04 * math.sin(wob + f / 9), base.y + 0.05 * math.cos(wob + f / 11), 0.05 + h)
        pop = min(1.0, (2.4 - h) / 0.25, h / 0.1)
        b.scale = (r * pop,) * 3
        b.keyframe_insert("location", frame=f)
        b.keyframe_insert("scale", frame=f)

    w = smoothstep((f - 100) / 140)
    cam_track = Vector((x + 0.6, -4.6, 1.15))
    look_track = Vector((x + 0.4, 0, 1.0))
    cam.location = cam_track.lerp(CAM_END, w)
    look = look_track.lerp(LOOK_END, w)
    q = (look - cam.location).to_track_quat("-Z", "Y")
    cam.rotation_euler = q.to_euler("XYZ", prev_euler) if prev_euler else q.to_euler("XYZ")
    prev_euler = cam.rotation_euler.copy()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)

for light in bpy.data.lights:
    light.use_shadow = light.name in SHADOW_LIGHTS

scene.frame_set(F0)
