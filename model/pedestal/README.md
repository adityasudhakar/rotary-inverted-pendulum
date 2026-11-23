# Pendulum motor pedestal — 55 mm seat

Print file: `STL/pendulum_pedestal_55mm.stl` (millimetres).
First-fit coupon: `STL/motor_fit_test.stl`.

The motor's **underside** sits 55 mm above the table. Total printed height is
64 mm because the four corner grips extend 9 mm above the seat. Motor height
and shaft height are additional. The column envelope is 46 × 46 mm, with
rounded corners. There is no flange or mounting foot: clamp the column directly.

## Fit and source

Adapted from the four-corner motor holder in Ferrolho's
[`motor plate.stl`](https://github.com/ferrolho/rotary-inverted-pendulum/blob/main/model/meshes/motor%20plate.stl),
inspected as real geometry rather than the Git LFS pointer. Its inner flats
are 42.2 mm apart, outer flats 46 mm apart, and inner corners have 3.5 mm
45-degree chamfers. Those dimensions are retained. This is intended for a
42 × 42 mm NEMA17 motor with chamfered corners, using a snug slip/press fit.
It is **not a positive locking latch**. The grips have a new 0.6 mm insertion
lead-in; four 16.4 mm side openings admit wiring and allow finger access.
The nominal clearance is 0.1 mm per side; a true interference/press fit is
not guaranteed. No grip force or torque retention has been measured.

The 9 mm grip height is a design choice, not an exact upstream copy. The
upstream motor seat is at z=2 mm and the grips reach z=12 mm, giving 10 mm
above its seat. Our seat remains at z=55 mm and the grips reach z=64 mm.

Print the 46 × 46 × 12 mm fit coupon first using the same material and profile
as the full pedestal. The motor must reach the flat seat without forcing or
cracking the grips and must not rock or rotate. Its physical corner bevels,
actual width and rear connector/shaft clearance have not been measured.
If loose or tight, change `SOCKET_SIZE` in `src/geometry.py` in 0.1–0.2 mm
increments and rebuild both models. Do not scale the full STL: that changes
the required 55 mm seat height too.

## Printing and use

- Print upright with the column bottom on the bed, at 100% scale, mm units.
- PETG is a sensible first choice for the compliant grips; start with 0.2 mm
  layers, 5 walls, 5–6 top/bottom layers, and 25–35% infill.
- The hollow column uses 4 mm walls and a 4 mm seat. The central 28 mm
  opening provides ventilation and rear-shaft relief. The seat roof has short
  bridges at its inner perimeter; try supports off with normal bridge settings.
  This has been checked geometrically, not sliced or physically printed.
- Secure the column in the clamp before active swing-up. Check the full swept volume
  with the assembled motor, pendulum and wires: the pedestal alone does not
  certify 270-degree travel, hard stops, or tip clearance.
- Confirm the motor cannot twist or lift in the printed grips before powered
  operation; if it moves, revise retention rather than relying on a loose fit.

## Rebuild

Run from `model/pedestal/`. Create a dedicated environment (separate from
the policy environment):

```sh
uv venv .venv
uv pip install --python .venv/bin/python "cadgen[snapshot]==0.7.4" trimesh scipy
```

```sh
.venv/bin/python src/pendulum_pedestal_55mm.py
.venv/bin/python src/motor_fit_test.py
.venv/bin/python checks/verify.py
```

Editable STEP files accompany the STLs. Reviewed snapshots and numerical
checks are saved under `review/`.
