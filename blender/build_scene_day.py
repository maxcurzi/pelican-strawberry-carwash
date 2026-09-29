"""Ground, sky, lights and camera."""
import math

stage = collection("Stage")

bpy.ops.mesh.primitive_circle_add(vertices=96, radius=40, fill_type="NGON", location=(0, 0, 0))
ground = _finish(bpy.context.active_object, "Ground",
                 mat("Road", (0.45, 0.40, 0.30), rough=0.9), stage, smooth=False)

world = bpy.data.worlds.get("Sky") or bpy.data.worlds.new("Sky")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.35, 0.58, 0.92, 1.0)
bg.inputs["Strength"].default_value = 0.6
bpy.context.scene.world = world

sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 2.4
sun_data.angle = math.radians(8)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
stage.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", "AREA")
fill_data.energy = 60
fill_data.size = 2.0
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (-1.5, -2.6, 2.0)
fill.rotation_euler = (Vector((0.1, 0, 1.0)) - fill.location).to_track_quat("-Z", "Y").to_euler()
stage.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (1.9, -3.6, 1.35)
stage.objects.link(cam)
target = Vector((0.02, 0, 0.78))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.view_settings.view_transform = "Standard"
