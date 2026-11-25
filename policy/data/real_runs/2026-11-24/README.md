# Rig 3 real-hardware logs

These captures were recorded on 2026-11-24 with the Uno, TMC2209, Rig 3
pendulum, and the `rig3_v1_stage3/best_model.zip` SAC teacher unless noted.
They are raw analysis data; no trained model is included here.

- `rig3_teacher_real_1.npz`: initial 6-second teacher attempt.
- `rig3_teacher_real_20s_1.npz` through `_4.npz`: standard 20-second teacher
  trials. `_2` and `_3` were explicitly prepared as clean trials. `_4` followed
  reseating of loose motor connector leads and a smooth position sweep.
- `rig3_teacher_clean_2.npz` and `_3.npz`: additional clean-start trials.
- `rig3_signflip_real_20s_1.npz` and `_2.npz`: exploratory tests with the
  pendulum angle and velocity signs flipped before policy observation. These
  are experimental and do not establish that sign flipping is correct.
- `rig3_video_take_1.npz`: unmodified policy run made for a video attempt.
- `sysid_accel_gentle.npz`: 50 Hz, low-amplitude motor-to-pendulum probe.
- `step_response.png`: bounded 10/20/30 rad/s² motor acceleration calibration.
- `sysid_accel_gentle.png`: gentle pulse comparison plot.

The policy logs store firmware angle/velocity, motor position/velocity,
actions, acceleration commands, host timestamps, control rate and policy path.
For encoder angle in radians, see `pendulum_pos_rad`; the run summary's
"turn-equivalents" is cumulative absolute travel and is not net revolutions.

Observed outcome across the 20-second teacher trials: substantial repeated
pendulum motion, but no stable upright catch in the recorded balance metric.
Several trials had many visible revolutions; net rotation alone does not
represent total turns when the pendulum reverses.
