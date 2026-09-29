"""Shared helpers for the pelican-on-a-bicycle build scripts.

Units are metres. The bike runs along +X (front wheel at +X), Z is up, and the
camera side of the bike is -Y.
"""
import math

import bpy
from mathutils import Vector


def mat(name, color, rough=0.5, metal=0.0, emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.0
    m.diffuse_color = (*color, 1.0)
    return m


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def _finish(obj, name, material, col, smooth=True):
    obj.name = name
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def rod(name, a, b, r, material, col, verts=16):
    """Cylinder of radius r from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length,
                                        location=(a + b) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("Z", "Y")
    return _finish(obj, name, material, col)


def blob(name, loc, scale, material, col, rot=(0, 0, 0), segs=32):
    """UV sphere scaled into an ellipsoid; rot is Euler degrees."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2,
                                         radius=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = scale
    obj.rotation_euler = [math.radians(v) for v in rot]
    return _finish(obj, name, material, col)


def blob_between(name, a, b, width, material, col, flat=1.0):
    """Ellipsoid whose long axis runs from a to b (a limb or wing segment)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0,
                                         location=(a + b) / 2)
    obj = bpy.context.active_object
    obj.scale = (width, width * flat, d.length / 2)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("Z", "Y")
    return _finish(obj, name, material, col)


def ring(name, loc, major, minor, material, col, axis="Y", segs=64):
    rot = {"Y": (math.pi / 2, 0, 0), "X": (0, math.pi / 2, 0), "Z": (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=segs, minor_segments=12,
                                     location=loc, rotation=rot)
    return _finish(bpy.context.active_object, name, material, col)


def tube_curve(name, points, radius, material, col, taper=None):
    """Smooth bezier tube through points; taper is a list of per-point radii."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for i, p in enumerate(points):
        bp = sp.bezier_points[i]
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        if taper:
            bp.radius = taper[i]
    obj = bpy.data.objects.new(name, cu)
    obj.data.materials.append(material)
    col.objects.link(obj)
    return obj


def two_bone_knee(hip, foot, l1, l2, bend_dir):
    """Knee position for a two-segment leg, bending toward bend_dir."""
    hip, foot = Vector(hip), Vector(foot)
    d = foot - hip
    dist = min(d.length, l1 + l2 - 1e-4)
    along = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - along * along, 0.0))
    axis = d.normalized()
    perp = Vector(bend_dir) - axis * Vector(bend_dir).dot(axis)
    return hip + axis * along + perp.normalized() * h
