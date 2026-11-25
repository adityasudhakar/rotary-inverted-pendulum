"""Replay a measured real-rig motor path through MuJoCo.

This isolates pendulum coupling from the host controller and stepper model:
the simulated arm is driven along the motor position trajectory actually
recorded on the rig, then its pendulum response is compared modulo 2*pi.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import mujoco
import numpy as np

from pendulum_env import RotaryInvertedPendulumEnv


def wrap_pi(x: np.ndarray) -> np.ndarray:
    return (x + math.pi) % (2.0 * math.pi) - math.pi


def replay(log_path: Path, params_path: Path) -> dict[str, np.ndarray]:
    d = np.load(log_path)
    t = d["host_time_s"].astype(np.float64)
    t -= t[0]
    real_motor = d["motor_pos_rad"].astype(np.float64)
    real_pen = d["pendulum_pos_rad"].astype(np.float64)
    real_motor_vel = d["motor_vel_rad_s"].astype(np.float64)
    real_pen_vel = d["pendulum_vel_rad_s"].astype(np.float64)

    env = RotaryInvertedPendulumEnv(
        params_path=params_path,
        control_freq_hz=float(d["control_freq_hz"]),
        domain_randomization=False,
        firmware_obs_model=False,
        episode_length_s=float(t[-1] + 1.0),
    )
    env.reset(seed=0)
    env.data.qpos[env._motor_qpos_addr] = real_motor[0]
    env.data.qpos[env._pen_qpos_addr] = real_pen[0]
    env.data.qvel[env._motor_qvel_addr] = real_motor_vel[0]
    env.data.qvel[env._pen_qvel_addr] = real_pen_vel[0]
    mujoco.mj_forward(env.model, env.data)

    sim_motor = np.empty_like(real_motor)
    sim_pen = np.empty_like(real_pen)
    sim_motor[0] = real_motor[0]
    sim_pen[0] = real_pen[0]
    physics_dt = float(env.model.opt.timestep)

    for i in range(len(t) - 1):
        interval = max(physics_dt, float(t[i + 1] - t[i]))
        n_sub = max(1, int(round(interval / physics_dt)))
        start = real_motor[i]
        end = real_motor[i + 1]
        for k in range(n_sub):
            env.data.ctrl[0] = start + (end - start) * (k + 1) / n_sub
            mujoco.mj_step(env.model, env.data)
        sim_motor[i + 1] = env.data.qpos[env._motor_qpos_addr]
        sim_pen[i + 1] = env.data.qpos[env._pen_qpos_addr]

    return {
        "t": t,
        "real_motor": real_motor,
        "real_pen": real_pen,
        "sim_motor": sim_motor,
        "sim_pen": sim_pen,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("logs", type=Path, nargs="+")
    p.add_argument("--params-path", type=Path, required=True)
    args = p.parse_args()

    for path in args.logs:
        r = replay(path, args.params_path)
        print(path)
        for seconds in (0.5, 1.0, 2.0, 3.0):
            k = min(len(r["t"]), int(seconds * 50))
            motor_rmse = float(np.sqrt(np.mean(
                (r["sim_motor"][:k] - r["real_motor"][:k]) ** 2
            )))
            pen_rmse = float(np.sqrt(np.mean(
                wrap_pi(r["sim_pen"][:k] - r["real_pen"][:k]) ** 2
            )))
            print(f"  first {seconds:>3.1f}s: motor {motor_rmse:.4f} rad, "
                  f"pendulum {pen_rmse:.4f} rad")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
