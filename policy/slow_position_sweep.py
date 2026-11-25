"""Run a slow, bounded position-mode motor sweep with no policy involved."""

from __future__ import annotations

import argparse
import math
import time

from lowlevel_client import LowLevelClient


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", required=True)
    p.add_argument("--duration-s", type=float, default=8.0)
    p.add_argument("--travel-deg", type=float, default=45.0,
                   help="total travel from the starting position")
    p.add_argument("--cycles", type=float, default=2.0)
    p.add_argument("--rate-hz", type=float, default=50.0)
    args = p.parse_args()

    travel = math.radians(args.travel_deg)
    period = args.duration_s / args.cycles
    dt = 1.0 / args.rate_hz

    with LowLevelClient(args.port) as client:
        if not client.wait_until_ready():
            raise RuntimeError("Arduino did not respond")

        s0 = client.get_state()
        start = s0.motor_pos_rad
        end = start + travel
        safe = math.radians(120.0)
        if not (-safe <= start <= safe and -safe <= end <= safe):
            raise RuntimeError(
                f"requested sweep [{math.degrees(start):.1f}°, "
                f"{math.degrees(end):.1f}°] exceeds the ±120° guard"
            )

        print(f"Start {math.degrees(start):+.1f}°, "
              f"sweeping to {math.degrees(end):+.1f}° and back, "
              f"{args.cycles:g} cycles in {args.duration_s:g}s")

        client.engage_motor()
        client.set_target(start)
        time.sleep(0.4)

        t0 = time.monotonic()
        next_tick = t0
        while True:
            now = time.monotonic()
            if now < next_tick:
                time.sleep(next_tick - now)
            now = time.monotonic()
            elapsed = now - t0
            if elapsed >= args.duration_s:
                break

            # Raised cosine: zero velocity at both ends, range start..end.
            phase = 2.0 * math.pi * elapsed / period
            target = start + 0.5 * travel * (1.0 - math.cos(phase))
            client.set_target(target)

            s = client.get_state()
            if abs(s.motor_pos_rad) > safe:
                raise RuntimeError("motor crossed the ±120° safety guard")

            next_tick += dt
            if next_tick < time.monotonic():
                next_tick = time.monotonic() + dt

        client.set_target(start)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            s = client.get_state()
            if abs(s.motor_pos_rad - start) < math.radians(1.0) and abs(s.motor_vel_rad_s) < 0.2:
                break
            time.sleep(0.02)

        client.disengage_motor()
        print("Sweep complete; motor disengaged.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
