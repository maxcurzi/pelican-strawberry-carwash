"""Rebuild the whole pelican-on-a-bicycle scene from scratch.

Open pelican_bicycle.blend (or set PELICAN_DIR to this folder), then in
Blender's Python console:  exec(open(bpy.path.abspath("//build.py")).read())
"""
import os

import bpy

HERE = os.environ.get("PELICAN_DIR") or os.path.dirname(bpy.data.filepath)
PARTS = os.environ.get("PELICAN_PARTS", "bicycle,pelican,carwash,scene,lighthouse,animate").split(",")

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
for block in (bpy.data.meshes, bpy.data.curves, bpy.data.lights, bpy.data.cameras, bpy.data.actions):
    for item in list(block):
        block.remove(item)

prefs = bpy.context.preferences.edit
old_interp = prefs.keyframe_new_interpolation_type
prefs.keyframe_new_interpolation_type = "LINEAR"

ns = {"__name__": "pelican_build"}
try:
    exec(open(f"{HERE}/build_common.py").read(), ns)
    for part in PARTS:
        path = f"{HERE}/build_{part}.py"
        if os.path.exists(path):
            exec(open(path).read(), ns)
finally:
    prefs.keyframe_new_interpolation_type = old_interp
