"""Millimetres. Adapted from ferrolho's 42.2 mm four-corner motor plate.

The motor underside is the seat datum. Open grips are a snug slip/press fit,
not a positive latch; final fit depends on printer calibration and motor size.
"""
from __future__ import annotations

from cadgen import build123d as bd

MOTOR_SIZE = 42.0
SOCKET_SIZE = 42.2  # measured upstream: parallel inner faces at +/-21.1
OUTSIDE = 46.0     # measured upstream: parallel outer faces at +/-23
CORNER_CHAMFER = 3.5  # measured upstream: inner straight ends at +/-17.6
GRIP_HEIGHT = 9.0
SEAT_HEIGHT = 55.0
BOTTOM_THICKNESS = 5.0
WIRE_GAP = 16.4


def rounded_profile(size, radius):
    return bd.RectangleRounded(size, size, radius)


def cavity_profile(size):
    h = size / 2
    k = h - CORNER_CHAMFER
    return bd.Polygon((-k,-h),(k,-h),(h,-k),(h,k),(k,h),(-k,h),(-h,k),(-h,-k), align=None)


def box(x,y,z,at=(0,0,0)):
    return bd.Pos(*at) * bd.Box(x,y,z,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))


def socket(seat):
    # Four compliant corner grips, retaining the upstream envelope and flats.
    ring = bd.Pos(0,0,seat) * bd.extrude(rounded_profile(OUTSIDE,6), amount=GRIP_HEIGHT)
    inner = bd.Pos(0,0,seat-.1) * bd.extrude(cavity_profile(SOCKET_SIZE), amount=GRIP_HEIGHT+.2)
    ring -= inner
    # 0.6 mm 45-degree insertion lead-in. Full-size land remains below it.
    lead = bd.loft([
        bd.Pos(0,0,seat+GRIP_HEIGHT-.6)*cavity_profile(SOCKET_SIZE),
        bd.Pos(0,0,seat+GRIP_HEIGHT+.1)*cavity_profile(SOCKET_SIZE+1.4),
    ])
    ring -= lead
    ring -= box(WIRE_GAP,OUTSIDE+4,GRIP_HEIGHT+2,(0,0,seat-1))
    ring -= box(OUTSIDE+4,WIRE_GAP,GRIP_HEIGHT+2,(0,0,seat-1))
    return ring


def make_pedestal():
    body = bd.extrude(rounded_profile(OUTSIDE,6), amount=SEAT_HEIGHT)
    # Hollow column, a 4 mm seat, and a central ventilation/rear-shaft opening.
    body -= box(38,38,SEAT_HEIGHT-4-BOTTOM_THICKNESS,(0,0,BOTTOM_THICKNESS))
    body -= bd.Pos(0,0,-1)*bd.Cylinder(14,SEAT_HEIGHT+2,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    body += socket(SEAT_HEIGHT)
    body.label = "55mm_motor_seat_pedestal"
    assert body.is_valid and len(body.solids()) == 1
    return body


def make_fit_test():
    # The identical seat/grips, without the tall column or clamping foot.
    body = bd.extrude(rounded_profile(OUTSIDE,6), amount=3)
    body -= bd.Pos(0,0,-1)*bd.Cylinder(14,5,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    body += socket(3)
    body.label = "motor_fit_test_42p2mm"
    assert body.is_valid and len(body.solids()) == 1
    return body
