"""Measure one manual encoder turn and stop after the endpoint is held."""

from __future__ import annotations

import argparse
import math
import time

from lowlevel_client import LowLevelClient


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", required=True)
    p.add_argument("--timeout-s", type=float, default=45.0)
    args = p.parse_args()

    with LowLevelClient(args.port) as client:
        if not client.wait_until_ready():
            raise RuntimeError("Arduino did not respond")
        time.sleep(0.5)
        start = client.get_state().pendulum_pos_rad
        print(f"READY start={math.degrees(start):+.2f} deg", flush=True)

        moved = False
        last_rel = 0.0
        last_motion = time.monotonic()
        peak_abs = 0.0
        deadline = time.monotonic() + args.timeout_s

        while time.monotonic() < deadline:
            rel = client.get_state().pendulum_pos_rad - start
            peak_abs = max(peak_abs, abs(rel))
            if abs(rel - last_rel) > math.radians(0.5):
                last_motion = time.monotonic()
            if abs(rel) > math.radians(30.0):
                moved = True
            last_rel = rel

            if moved and time.monotonic() - last_motion >= 2.0:
                print(f"FINAL relative={math.degrees(rel):+.2f} deg", flush=True)
                print(f"PEAK absolute={math.degrees(peak_abs):.2f} deg", flush=True)
                return 0
            time.sleep(0.02)

        print(f"TIMEOUT relative={math.degrees(last_rel):+.2f} deg", flush=True)
        print(f"PEAK absolute={math.degrees(peak_abs):.2f} deg", flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
