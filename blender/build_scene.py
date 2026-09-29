"""Night stage: land, shoreline, sea, starry sky, moon, streetlamps, camera.

The road runs along X; the sea starts past the shoreline at +Y, where the
lighthouse island sits (build_lighthouse.py). The daytime version of this
stage is kept in build_scene_day.py.
"""
import math
import random

stage = collection("Stage")
scene = bpy.context.scene

SHORE_Y = 7.0
SEA_Z = -0.6


def emissive(name, color, strength):
    m = mat(name, color, rough=0.4)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    return m


# Land up to the shoreline, a sloping beach, then the sea.
box("Land", (-150, -150, -0.02), (150, SHORE_Y, 0.0), mat("Grass at night", (0.06, 0.09, 0.05), rough=0.95), stage)
bpy.ops.mesh.primitive_plane_add(size=1)
beach = bpy.context.active_object
beach.data.vertices[0].co = (-150, SHORE_Y, 0.0)
beach.data.vertices[1].co = (150, SHORE_Y, 0.0)
beach.data.vertices[2].co = (-150, SHORE_Y + 4, SEA_Z - 0.3)
beach.data.vertices[3].co = (150, SHORE_Y + 4, SEA_Z - 0.3)
_finish(beach, "Beach", mat("Wet sand", (0.25, 0.22, 0.17), rough=0.6), stage, smooth=False)

sea_mat = mat("Night sea", (0.01, 0.025, 0.06), rough=0.06)
nt = sea_mat.node_tree
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.noise_dimensions = "4D"
noise.inputs["Scale"].default_value = 0.35
noise.inputs["Detail"].default_value = 6
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.25
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
noise.inputs["W"].default_value = 0.0
noise.inputs["W"].keyframe_insert("default_value", frame=1)
noise.inputs["W"].default_value = 3.0
noise.inputs["W"].keyframe_insert("default_value", frame=288)
box("Sea", (-400, SHORE_Y, SEA_Z - 0.02), (400, 500, SEA_Z), sea_mat, stage)

# A few shoreline rocks.
rng_scene = random.Random(3)
rock_mat = mat("Rock", (0.10, 0.10, 0.11), rough=0.9)
for i in range(9):
    x = -20 + i * 5.5 + rng_scene.uniform(-1.5, 1.5)
    s = rng_scene.uniform(0.5, 1.2)
    blob(f"Shore rock {i}", (x, SHORE_Y + 2.2 + rng_scene.uniform(-0.6, 0.6), SEA_Z),
         (s * 1.3, s, s * 0.6), rock_mat, stage, rot=(0, 0, rng_scene.uniform(0, 180)), segs=10)

# Night sky: dark gradient plus procedural stars.
world = bpy.data.worlds.get("Night sky") or bpy.data.worlds.new("Night sky")
world.use_nodes = True
wn = world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
coord = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
wn.links.new(coord.outputs["Generated"], sep.inputs["Vector"])
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.035, 0.05, 0.12, 1)
ramp.color_ramp.elements[1].position = 0.45
ramp.color_ramp.elements[1].color = (0.004, 0.006, 0.025, 1)
wn.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
vor = wn.nodes.new("ShaderNodeTexVoronoi")
vor.inputs["Scale"].default_value = 260
wn.links.new(coord.outputs["Generated"], vor.inputs["Vector"])
is_star = wn.nodes.new("ShaderNodeMath")
is_star.operation = "LESS_THAN"
is_star.inputs[1].default_value = 0.035
wn.links.new(vor.outputs["Distance"], is_star.inputs[0])
twinkle = wn.nodes.new("ShaderNodeSeparateColor")
wn.links.new(vor.outputs["Color"], twinkle.inputs["Color"])
star_amt = wn.nodes.new("ShaderNodeMath")
star_amt.operation = "MULTIPLY"
wn.links.new(is_star.outputs[0], star_amt.inputs[0])
wn.links.new(twinkle.outputs["Red"], star_amt.inputs[1])
star_gain = wn.nodes.new("ShaderNodeMath")
star_gain.operation = "MULTIPLY"
star_gain.inputs[1].default_value = 3.0
wn.links.new(star_amt.outputs[0], star_gain.inputs[0])
add = wn.nodes.new("ShaderNodeMixRGB")
add.blend_type = "ADD"
add.inputs["Fac"].default_value = 1.0
wn.links.new(ramp.outputs["Color"], add.inputs["Color1"])
wn.links.new(star_gain.outputs[0], add.inputs["Color2"])
bg = wn.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 1.0
wn.links.new(add.outputs["Color"], bg.inputs["Color"])
out = wn.nodes.new("ShaderNodeOutputWorld")
wn.links.new(bg.outputs["Background"], out.inputs["Surface"])
scene.world = world

# Moon: a glowing disc far away plus a cool, dim sun from the same direction.
MOON = Vector((-8, 260, 60))
blob("Moon", MOON, (5, 5, 5), emissive("Moonlight", (0.95, 0.93, 0.82), 6.0), stage)
moon_data = bpy.data.lights.new("Moon light", "SUN")
moon_data.energy = 0.35
moon_data.color = (0.65, 0.75, 1.0)
moon_data.angle = math.radians(1)
moon = bpy.data.objects.new("Moon light", moon_data)
moon.rotation_euler = (Vector((0, 0, 0)) - MOON).to_track_quat("-Z", "Y").to_euler()
stage.objects.link(moon)

# Streetlamps on the far side of the road.
pole = mat("Lamp pole", (0.08, 0.08, 0.09), rough=0.4, metal=0.8)
bulb = emissive("Lamp glow", (1.0, 0.78, 0.45), 12.0)
for i, x in enumerate((-13, -7, -4, 7)):
    base = Vector((x, 1.45, 0))
    top = base + Vector((0, 0, 3.3))
    head = top + Vector((0, -0.55, -0.05))
    rod(f"Lamp pole {i}", base, top, 0.05, pole, stage)
    rod(f"Lamp arm {i}", top, head, 0.035, pole, stage)
    blob(f"Lamp head {i}", head + Vector((0, 0, -0.06)), (0.16, 0.12, 0.07), bulb, stage)
    ld = bpy.data.lights.new(f"Lamp light {i}", "POINT")
    ld.energy = 260
    ld.color = (1.0, 0.75, 0.45)
    ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(f"Lamp light {i}", ld)
    lo.location = head + Vector((0, 0, -0.2))
    stage.objects.link(lo)

# Carwash at night: pink tunnel lights and a floodlight on the sign and berry.
for name, color, energy, loc in (("Tunnel light A", (1.0, 0.45, 0.6), 220, (3.2, 0, 1.9)),
                                 ("Tunnel light B", (1.0, 0.45, 0.6), 160, (4.6, 0, 1.9)),
                                 ("Sign floodlight", (1.0, 0.85, 0.9), 180, (1.3, 0, 2.2)),
                                 ("Berry light", (1.0, 0.55, 0.5), 120, (3.0, -1.2, 3.6))):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = energy, color, 0.3
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    stage.objects.link(lo)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_data.clip_end = 1000
cam = bpy.data.objects.new("Camera", cam_data)
stage.objects.link(cam)
cam.location = (-3.5, -7.5, 1.8)
cam.rotation_euler = (Vector((2.2, 0.8, 2.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 288
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
scene.eevee.taa_render_samples = 48
scene.eevee.shadow_pool_size = "1024"
# Only the key lights cast shadows; the rest are fills, which keeps the shadow pool from overflowing.
SHADOW_LIGHTS = {"Moon light", "Beam spot", "Headlamp beam", "Tunnel light A", "Lamp light 1", "Lamp light 2"}
scene.eevee.use_raytracing = True
scene.render.use_motion_blur = True

# Bloom on the lights and neon via the compositor.
glow = bpy.data.node_groups.new("Night glow", "CompositorNodeTree")
glow.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
rl = glow.nodes.new("CompositorNodeRLayers")
glare = glow.nodes.new("CompositorNodeGlare")
gout = glow.nodes.new("NodeGroupOutput")
glow.links.new(rl.outputs["Image"], glare.inputs["Image"])
glow.links.new(glare.outputs["Image"], gout.inputs[0])
for key, val in (("Type", "Bloom"), ("Quality", "Medium")):
    if key in glare.inputs:
        glare.inputs[key].default_value = val
for key, val in (("Threshold", 1.0), ("Strength", 0.6), ("Size", 0.6)):
    if key in glare.inputs:
        glare.inputs[key].default_value = val
scene.compositing_node_group = glow
