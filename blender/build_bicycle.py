"""Bicycle: diamond frame, spoked wheels, drivetrain, bars and saddle.

Run through build.py, which provides the helpers from build_common.py.
"""
import math

from mathutils import Vector

bike = collection("Bicycle")

WHEEL_R = 0.35
REAR = Vector((-0.55, 0, WHEEL_R))
FRONT = Vector((0.55, 0, WHEEL_R))
BB = Vector((0.0, 0, 0.30))
SEAT_TOP = Vector((-0.12, 0, 0.78))
HEAD_TOP = Vector((0.40, 0, 0.80))
HEAD_BOT = Vector((0.44, 0, 0.64))
STEM_TOP = Vector((0.43, 0, 0.90))
BAR = Vector((0.50, 0, 0.92))
BAR_HALF = 0.24
SADDLE = Vector((-0.14, 0, 0.815))
CRANK_LEN = 0.17
CRANK_ANGLE = math.radians(-25)  # right crank, measured from +X
PEDAL_Y = 0.13

frame_red = mat("Frame red", (0.75, 0.05, 0.04), rough=0.25, metal=0.4)
chrome = mat("Chrome", (0.8, 0.8, 0.82), rough=0.15, metal=1.0)
rubber = mat("Tyre rubber", (0.02, 0.02, 0.02), rough=0.8)
black = mat("Black plastic", (0.04, 0.04, 0.045), rough=0.5)
leather = mat("Saddle leather", (0.22, 0.10, 0.04), rough=0.6)

# Wheels: tyre, rim, hub, 20 spokes crossing between two hub flanges.
for label, c in (("Rear", REAR), ("Front", FRONT)):
    ring(f"{label} tyre", c, WHEEL_R - 0.02, 0.024, rubber, bike)
    ring(f"{label} rim", c, WHEEL_R - 0.045, 0.010, chrome, bike)
    rod(f"{label} hub", c + Vector((0, -0.05, 0)), c + Vector((0, 0.05, 0)), 0.018, chrome, bike)
    for i in range(20):
        ang = 2 * math.pi * i / 20
        rim_pt = c + Vector((math.cos(ang), 0, math.sin(ang))) * (WHEEL_R - 0.05)
        side = 0.035 if i % 2 else -0.035
        rod(f"{label} spoke {i:02d}", c + Vector((0, side, 0)), rim_pt, 0.0025, chrome, bike, verts=6)

# Frame tubes.
tubes = {
    "Seat tube": (BB, SEAT_TOP, 0.018),
    "Top tube": (SEAT_TOP, HEAD_TOP, 0.017),
    "Down tube": (BB, HEAD_BOT, 0.021),
    "Head tube": (HEAD_BOT, HEAD_TOP, 0.024),
}
for name, (a, b, r) in tubes.items():
    rod(name, a, b, r, frame_red, bike)
for s, y in (("L", 0.05), ("R", -0.05)):
    off = Vector((0, y, 0))
    rod(f"Chainstay {s}", REAR + off, BB + off * 0.4, 0.011, frame_red, bike)
    rod(f"Seatstay {s}", REAR + off, SEAT_TOP + Vector((-0.01, 0, -0.03)) + off * 0.3, 0.010, frame_red, bike)
    rod(f"Fork {s}", HEAD_BOT + off * 0.5, FRONT + off, 0.013, frame_red, bike)
rod("Fork crown", HEAD_BOT + Vector((0, -0.035, 0)), HEAD_BOT + Vector((0, 0.035, 0)), 0.016, frame_red, bike)
rod("Bottom bracket", BB + Vector((0, -0.045, 0)), BB + Vector((0, 0.045, 0)), 0.026, frame_red, bike)

# Cockpit.
rod("Stem", HEAD_TOP, STEM_TOP, 0.015, chrome, bike)
rod("Stem reach", STEM_TOP, BAR, 0.014, chrome, bike)
rod("Handlebar", BAR + Vector((0, -BAR_HALF, 0)), BAR + Vector((0, BAR_HALF, 0)), 0.012, chrome, bike)
for s in (-1, 1):
    rod(f"Grip {'L' if s > 0 else 'R'}", BAR + Vector((0, s * (BAR_HALF - 0.1), 0)),
        BAR + Vector((0, s * (BAR_HALF + 0.005), 0)), 0.017, black, bike)
rod("Seatpost", SEAT_TOP, SADDLE + Vector((0, 0, -0.02)), 0.013, chrome, bike)
blob("Saddle", SADDLE, (0.13, 0.065, 0.025), leather, bike)
blob("Saddle nose", SADDLE + Vector((0.09, 0, 0.002)), (0.07, 0.03, 0.02), leather, bike)

# Drivetrain on the -Y (camera) side.
ring("Chainring", BB + Vector((0, -0.07, 0)), 0.09, 0.008, chrome, bike)
ring("Cassette", REAR + Vector((0, -0.07, 0)), 0.04, 0.007, chrome, bike)
top_off, bot_off = Vector((0, -0.07, 0.09)), Vector((0, -0.07, -0.09))
rod("Chain top", BB + top_off, REAR + Vector((0, -0.07, 0.04)), 0.005, black, bike, verts=8)
rod("Chain bottom", BB + bot_off, REAR + Vector((0, -0.07, -0.04)), 0.005, black, bike, verts=8)

PEDALS = {}
for s, ang, y in (("R", CRANK_ANGLE, -PEDAL_Y), ("L", CRANK_ANGLE + math.pi, PEDAL_Y)):
    tip = BB + Vector((CRANK_LEN * math.cos(ang), y * 0.75, CRANK_LEN * math.sin(ang)))
    rod(f"Crank {s}", BB + Vector((0, y * 0.6, 0)), tip, 0.012, chrome, bike)
    pedal = tip + Vector((0, y * 0.35, 0))
    rod(f"Pedal {s}", pedal + Vector((0, -0.045, 0)), pedal + Vector((0, 0.045, 0)), 0.02, black, bike, verts=8)
    PEDALS[s] = pedal

GRIPS = {"L": BAR + Vector((0, BAR_HALF - 0.05, 0)), "R": BAR + Vector((0, -(BAR_HALF - 0.05), 0))}
