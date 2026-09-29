"""California brown pelican in breeding plumage, riding the bicycle.

Needs PEDALS, GRIPS and SADDLE from build_bicycle.py.
"""
from mathutils import Vector

bird = collection("Pelican")

body_brown = mat("Body grey-brown", (0.20, 0.15, 0.11), rough=0.8)
belly_dark = mat("Belly dark brown", (0.10, 0.08, 0.07), rough=0.85)
wing_silver = mat("Wing silver-grey", (0.24, 0.22, 0.20), rough=0.7)
primaries = mat("Primaries black", (0.04, 0.035, 0.03), rough=0.7)
neck_white = mat("Neck white", (0.93, 0.92, 0.88), rough=0.7)
hindneck = mat("Hindneck chestnut", (0.28, 0.10, 0.05), rough=0.8)
crown_yellow = mat("Crown yellow", (0.95, 0.78, 0.25), rough=0.6)
bill_grey = mat("Bill grey", (0.32, 0.27, 0.19), rough=0.4)
bill_tip = mat("Bill tip red", (0.75, 0.18, 0.08), rough=0.4)
pouch_red = mat("Pouch red", (0.55, 0.04, 0.03), rough=0.35)
leg_dark = mat("Legs dark grey", (0.08, 0.08, 0.08), rough=0.6)
eye_pale = mat("Eye pale", (0.85, 0.85, 0.75), rough=0.2)
pupil = mat("Pupil", (0.01, 0.01, 0.01), rough=0.1)

# Body, leaning forward over the top tube.
BODY = Vector((-0.07, 0, 1.03))
blob("Body", BODY, (0.30, 0.18, 0.185), body_brown, bird, rot=(0, 14, 0))
blob("Belly", BODY + Vector((0.02, 0, -0.07)), (0.25, 0.15, 0.12), belly_dark, bird, rot=(0, 14, 0))
blob("Tail", BODY + Vector((-0.31, 0, 0.07)), (0.11, 0.075, 0.025), primaries, bird, rot=(0, -12, 0))

# Wings: folded coverts along the flanks, then arms reaching down to the grips.
for s, sign in (("L", 1), ("R", -1)):
    shoulder = BODY + Vector((0.15, sign * 0.14, 0.07))
    wrist = Vector((0.30, sign * 0.23, 1.00))
    grip = GRIPS[s]
    blob_between(f"Wing coverts {s}", shoulder, BODY + Vector((-0.30, sign * 0.13, 0.04)),
                 0.075, wing_silver, bird, flat=0.45)
    blob_between(f"Upper wing {s}", shoulder, wrist, 0.05, wing_silver, bird, flat=0.6)
    blob_between(f"Outer wing {s}", wrist, grip + Vector((0.01, 0, 0.02)), 0.04, wing_silver, bird, flat=0.6)
    for i, (dx, dz) in enumerate(((0.05, 0.02), (0.07, -0.01), (0.06, -0.04))):
        blob_between(f"Primary {s}{i}", grip + Vector((-0.02, 0, 0.0)),
                     grip + Vector((dx, sign * 0.02 * i, dz)), 0.018, primaries, bird, flat=0.5)

# S-curved neck: white front with a chestnut stripe down the back.
neck_pts = [BODY + Vector((0.20, 0, 0.06)), Vector((0.20, 0, 1.25)),
            Vector((0.13, 0, 1.39)), Vector((0.19, 0, 1.52))]
tube_curve("Neck", neck_pts, 0.055, neck_white, bird, taper=[1.1, 0.9, 0.8, 0.75])
tube_curve("Hindneck stripe", [p + Vector((-0.022, 0, 0)) for p in neck_pts[1:]],
           0.045, hindneck, bird, taper=[0.85, 0.8, 0.75])

# Head with the yellow breeding crown and eyes.
HEAD = Vector((0.22, 0, 1.555))
blob("Head", HEAD, (0.08, 0.058, 0.065), neck_white, bird)
blob("Crown", HEAD + Vector((-0.005, 0, 0.04)), (0.06, 0.047, 0.03), crown_yellow, bird)
for s, sign in (("L", 1), ("R", -1)):
    blob(f"Eye {s}", HEAD + Vector((0.035, sign * 0.05, 0.012)), (0.013,) * 3, eye_pale, bird)
    blob(f"Pupil {s}", HEAD + Vector((0.041, sign * 0.061, 0.012)), (0.006,) * 3, pupil, bird)

# The famous bill and pouch.
BILL_BASE = HEAD + Vector((0.06, 0, -0.01))
BILL_TIP = Vector((0.74, 0, 1.43))
tube_curve("Upper bill", [BILL_BASE, BILL_BASE.lerp(BILL_TIP, 0.5) + Vector((0, 0, 0.012)), BILL_TIP],
           0.03, bill_grey, bird, taper=[1.0, 0.8, 0.55])
blob("Bill hook", BILL_TIP + Vector((0.008, 0, -0.012)), (0.02, 0.012, 0.022), bill_tip, bird)
pouch_mid = BILL_BASE.lerp(BILL_TIP, 0.42) + Vector((0, 0, -0.058))
blob("Pouch", pouch_mid, (0.19, 0.034, 0.045), pouch_red, bird, rot=(0, 16, 0))
blob("Pouch sag", pouch_mid + Vector((-0.04, 0, -0.02)), (0.10, 0.032, 0.04), pouch_red, bird, rot=(0, 25, 0))

# Legs pushing the pedals, bent knees forward, feet flat on the pedals.
for s, sign in (("L", 1), ("R", -1)):
    hip = BODY + Vector((0.05, sign * 0.09, -0.12))
    ankle = PEDALS[s] + Vector((0.0, 0, 0.04))
    knee = two_bone_knee(hip, ankle, 0.34, 0.39, (1, 0, 0.3))
    blob_between(f"Thigh {s}", hip, knee, 0.05, body_brown, bird)
    rod(f"Shin {s}", knee, ankle, 0.017, leg_dark, bird)
    blob(f"Knee {s}", knee, (0.028,) * 3, leg_dark, bird)
    blob(f"Foot {s}", PEDALS[s] + Vector((0.03, 0, 0.028)), (0.085, 0.05, 0.012), leg_dark, bird)
