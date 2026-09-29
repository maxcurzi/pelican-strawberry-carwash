"""Rebuild, render the approach and behind-the-pelican stills, and save the .blend."""
import os

import bpy
from mathutils import Vector

HERE = os.environ.get("PELICAN_DIR") or os.path.dirname(bpy.data.filepath)
exec(open(os.path.join(HERE, "build.py")).read())
s = bpy.context.scene
s.render.resolution_percentage = 100
cam = s.camera
views = {"approach": ((-3.2, -8.6, 2.1), (1.9, 0, 1.45)), "behind": ((-5.2, -2.6, 1.8), (2.3, 0.1, 1.95))}
s.render.resolution_x, s.render.resolution_y = 1920, 1080
cam.data.lens = 44
for name, (loc, target) in views.items():
    cam.location = loc
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    s.render.filepath = os.path.join(HERE, f"pelican_bicycle_{name}.png")
    bpy.ops.render.render(write_still=True)
cam.location, target = views["approach"]
cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.wm.save_mainfile()
