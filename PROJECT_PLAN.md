# Build, train, and deploy plan

Started: 2026-10-21

## Goal

Assemble the newly arrived parts into a working rotary inverted pendulum,
measure this specific rig, train and fine-tune its own RL policy, distill the
policy for the Arduino Nano, and validate safe standalone swing-up and balance.

This checklist supplements the documentation in `website/src/content/docs/`.
The build guides and the canonical RL pipeline remain the source of truth.

## Current state

- [x] Initial parts have arrived and were photographed for inventory.
- [x] Repository is available locally.
- [x] Reference firmware and Ferrolho's trained policy headers are present.
- [x] Missing AS5600 diametric magnet identified and reordered.
- [ ] **Waiting on the AS5600 magnet.** Encoder testing, sysid, real-rig
  fine-tuning and standalone deployment are blocked until it arrives.
- [ ] Mechanical assembly complete.
- [ ] Electronics wired and inspected.
- [ ] This rig has its own system-identification file.
- [ ] This rig has its own trained, fine-tuned, and distilled policy.
- [ ] Standalone deployment passes the on-device balance gate.

## Safety rules

- Work with motor power disconnected while assembling or changing wiring.
- Set and verify the driver's current limit before commanding the motor.
- Clamp or weight the base so swing-up cannot move the whole rig.
- Route wires outside the arm's full travel and preserve the software hard-stop
  clearance.
- For every first motion test, keep clear of the arm, keep the power switch in
  reach, and be ready to cut motor power immediately.
- Do not leave the autonomous rig running unattended.
- Stop on grinding, skipped steps, excessive vibration, hot electronics, hot
  motor, erratic encoder readings, or unexpected travel.

## Phase 1 — inventory and mechanical assembly

- [x] Check the photographed parts against the bill of materials.
- [x] Confirm a suitable supply: 12 V DC, 3 A, centre-positive.
- [x] Confirm the recommended TMC2209 V2.0 stepper driver is present.
- [x] Confirm the Arduino Nano, AS5600 board, motor heatsink, 608 bearing,
  printed arm/pendulum subassembly and decoupling capacitors are present.
- [ ] Obtain or locate the female 5.5 × 2.1 mm panel-mount barrel socket; the
  photographed male screw-terminal plug cannot mate with the supply's male
  plug.
- [ ] Obtain or locate the rocker switch, 40 × 60 mm protoboard, female 2.54 mm
  headers, hookup wire, printed base, lid and encoder boss.
- [ ] Replace the physically oversized 22 µF 400 V electrolytic with a compact
  22 µF, 25–50 V part suitable for the protoboard.
- [ ] Confirm the ceramic capacitors are marked `104` (100 nF).
- [ ] Confirm the printed pendulum contains the 2p coin specified by the model.
- [x] Record the actual stepper driver: TMC2209 V2.0.
- [ ] Confirm the stepper is the short-body 17HS4023 by label or approximately
  22 mm body-depth measurement.
- [ ] Record 1/32 as the intended microstepping and later make the TMC2209
  MS1/MS2 wiring and every firmware `MICROSTEPS` value agree.
- [ ] Photograph the parts and wiring labels before assembly.
- [ ] Mount the NEMA17 motor and motor plate.
- [ ] Finish the mechanical assembly except for permanent AS5600 alignment.
- [ ] Mount the AS5600 loosely; do not glue or permanently position it until the
  replacement diametric magnet can be used to set the air gap.
- [ ] Fit the arm to the motor shaft and establish a repeatable mechanical zero.
- [ ] Fit the pendulum bearing/shaft with minimal play and friction.
- [ ] Route the encoder wires so they remain slack throughout arm travel.
- [ ] Secure the enclosure and clamp or weight the base.
- [ ] Hold the motor securely and confirm the pendulum coasts for many
  oscillations without rubbing, sticking or obvious bearing wobble.
- [ ] Confirm the arm is tight on the motor shaft with no rotational slip.

The upstream assembly page still has unresolved details. Before tightening or
gluing anything, verify and record here or in that page:

- [ ] NEMA17 and motor-plate fastener sizes and orientation.
- [ ] AS5600 mounting method, magnet retention, and measured air gap.
- [ ] Arm-to-shaft coupling and zeroing method.
- [ ] Pendulum bearing, shaft retention, fit, and free play.
- [ ] Final cable route across the full travel range.

Mechanical gate:

- [ ] Arm moves freely by hand without binding or pulling wires.
- [ ] Pendulum hangs straight down repeatably.
- [ ] Pendulum released from horizontal swings freely for many oscillations.

## Phase 2 — electronics and first power-on

Work that can be completed while waiting for the magnet:

- [ ] Wire the Nano, driver, motor, AS5600, power switch, barrel jack, and
  decoupling capacitors exactly as documented.
- [ ] Leave the AS5600 mechanically adjustable even after wiring it.
- [ ] Verify supply polarity, driver orientation, common ground, motor coil
  pairs, STEP/DIR/ENABLE pins, and AS5600 voltage requirements with power off.
- [ ] Wire the driver's microstep pins for the selected 1/32 setting and make
  every firmware `MICROSTEPS` value match.
- [ ] Set driver current limit before connecting motor power:
  - TMC2209 reference: about 0.9 V Vref / 0.64 A RMS.
  - DRV8825 reference: about 0.45 V Vref / 0.9 A peak.
- [ ] Identify the Nano port with `arduino-cli board list` and record it below.
- [ ] Flash and pass `TestHeartbeat`.
- [ ] Flash and pass `TestMotor`; confirm direction, roughly ±90° travel, smooth
  sound, no lost steps, and safe temperatures. Do this only with the motor and
  base secured, the arm's full sweep clear, and Vref already set.
- [ ] Flash and pass `TestSerial`; target roughly 2.5 ms round-trip latency.
- [ ] Compile all firmware sketches so missing libraries or toolchain problems
  are solved before the magnet arrives.

Work that waits for the magnet:

- [ ] Flash and pass `TestEncoder`; adjust the magnet for stable readings over a
  complete revolution before fixing it permanently.
- [ ] Permanently secure the AS5600 and magnet only after the strength and
  full-rotation tests pass.
- [ ] Boot-check `LowLevelServer` and `RLControl`; both intentionally wait for
  valid magnet detection during startup.

Rig record:

- Rig name: `________________`
- Arduino port: `________________`
- Driver: `________________`
- Microsteps: `________________`
- Vref/current setting: `________________`
- AS5600 air gap and mounting notes: `________________`

Electrical gate:

- [ ] All four test sketches pass independently.
- [ ] Motor and driver remain warm, not too hot to touch.
- [ ] No buzzing, grinding, skipped steps, encoder jumps, or cable interference.

## Phase 3 — identify this rig

- [ ] Set up the Python environment from `policy/` with `uv` while waiting for
  the magnet.
- [ ] Run software-only smoke tests and prepare the sysid command while waiting.
- [ ] **Magnet dependency:** do not start real sysid until `TestEncoder` passes.
- [ ] Flash `firmware/LowLevelServer` using the selected microstep setting.
- [ ] Run the guided system-identification workflow:

  ```bash
  cd policy
  uv run python sysid_wizard.py --out-json sysid_params_<rig>.json
  ```

- [ ] Complete the hanging tare, three free-swing recordings, and motor ±90°
  sanity sweep.
- [ ] Inspect `freeswing_compare.png` and `motor_sweep.png` rather than accepting
  the fitted numbers blindly.
- [ ] Commit the resulting `sysid_params_<rig>.json`; keep raw recordings locally.

Sysid gate:

- [ ] Real and simulated free-swing traces agree closely.
- [ ] CAD-predicted and measured inertia differ by no more than the documented
  10% warning threshold, or the discrepancy has been explained.
- [ ] Motor sweep reaches its targets without skipped steps.

## Phase 4 — train the SAC teacher in simulation

Keep the canonical production settings together: 50 Hz, velocity mode,
±3.5 rad/s, four observation frames, four-tap action smoothing, mirror
augmentation, and observation-staleness randomization over 2–20 ms.

- [ ] While waiting for the magnet, verify the simulation environment and run a
  short smoke training/evaluation if desired.
- [ ] Postpone the full curriculum until sysid produces this rig's parameter
  file; training now against another rig's defaults would need to be repeated.
- [ ] Start the three-stage curriculum using this rig's sysid parameters and a
  descriptive run name:

  ```bash
  cd policy
  PARAMS_PATH=sysid_params_<rig>.json \
    uv run bash curriculum_train.sh <rig>_v1
  ```

- [ ] Confirm the printed run header shows the canonical settings before waiting
  for training to finish.
- [ ] Preserve `runs/<rig>_v1_stage3/best_model.zip` and its `config.json`.
- [ ] Run the documented symmetry and observation-sensitivity checks.
- [ ] If the teacher is brittle, retrain with a different seed before spending
  time on real-rig fine-tuning.

Simulation gate:

- [ ] The stage-3 `best_model.zip` reliably swings up and balances in randomized
  simulation.
- [ ] Clean-observation sensitivity does not collapse.
- [ ] Policy self-starts and does not show a severe one-direction bias.

## Phase 5 — fine-tune and test on the real rig

- [ ] Reconfirm the base is secured, travel is clear, and motor power can be cut
  immediately.
- [ ] Flash `firmware/LowLevelServer`.
- [ ] Run an initial 50-episode async fine-tune from the simulation teacher:

  ```bash
  cd policy
  uv run python finetune_async.py \
    --policy runs/<rig>_v1_stage3/best_model.zip \
    --port <PORT> \
    --episodes 50 \
    --run-name <rig>_async_v1
  ```

- [ ] Listen through the first episodes and stop immediately on grinding or
  skipped steps.
- [ ] Test `best_model.zip`, never `last.zip`, in a 30-second tethered run:

  ```bash
  uv run python run_policy.py \
    --policy runs/<rig>_async_v1/best_model.zip \
    --port <PORT> \
    --duration-s 30 \
    --log recordings/<rig>_ft.npz
  ```

- [ ] If balanced fraction is 0.4–0.85 and still improving, add 30-episode
  blocks while resuming `replay_buffer.pkl`.
- [ ] If below 0.4, stop and diagnose sysid, transport delay, and sim-to-real
  mismatch before spending more rig time.

Real-rig teacher gate:

- [ ] Balanced fraction is at least 0.85 with verdict `BALANCED`.
- [ ] No uncontrolled revolutions, repeated hard-limit trips, or severe arm lean.
- [ ] The observation-sensitivity gate still passes after fine-tuning.

## Phase 6 — distill for the Nano

- [ ] Run behaviour cloning plus device-transport DAgger:

  ```bash
  cd policy
  uv run bash distill_student.sh <rig>_async_v1
  ```

- [ ] Compare the student's device-transport simulation gate with its teacher;
  judge it relatively, as documented, rather than using an arbitrary cutoff.
- [ ] Run both firmware-model ON and OFF sensitivity checks on `student.pt`.
- [ ] Optionally test the student tethered for gross behavioural errors.

Distillation gate:

- [ ] The H=16 student fits the Nano's 20 ms control tick.
- [ ] DAgger student approximately matches or beats its teacher's device gate.
- [ ] Clean-observation sensitivity does not collapse.

## Phase 7 — export, flash, and let it balance

- [ ] Export to the development header first; do not overwrite a known champion:

  ```bash
  cd policy
  uv run python export_weights.py \
    --student runs/<rig>_async_v1/distill_h16_dagger_dev/student.pt \
    --header ../firmware/RLControl/policy_weights_dev.h \
    --source-name <rig>_async_v1/distill_h16_dagger_dev
  ```

- [ ] Compile and upload `firmware/RLControl`, explicitly selecting
  `policy_weights_dev.h`.
- [ ] Hold the pendulum motionless and hanging during the one-second boot tare.
- [ ] Perform a short guarded run with a hand on the power switch.
- [ ] Capture and score 60 seconds of standalone telemetry:

  ```bash
  cd policy
  uv run python analyze_onboard.py \
    --port <PORT> \
    --duration-s 60 \
    --log recordings/onboard_<rig>_v1.npz
  ```

- [ ] Confirm the measured loop rate is approximately 50 Hz and the measured
  sample-to-command latency lies within the training distribution.
- [ ] Only after a clean short run, increase the duration and test recovery from
  small, controlled disturbances.
- [ ] When validated, export to a named per-rig header and commit it together
  with its provenance and headline metrics.

Standalone acceptance gate:

- [ ] Verdict is `BALANCED`, with no drops or hard-limit trips during the agreed
  acceptance duration.
- [ ] Loop frequency, latency, action level, pendulum deviation, arm sway, and
  arm lean are recorded.
- [ ] Motor, driver, wiring, and mount remain mechanically and thermally sound.

## Run log

Add one row after each meaningful attempt so failed experiments remain useful.

| Date | Phase/run | Hardware/config | Result | Decision/next step |
| --- | --- | --- | --- | --- |
| 2026-10-21 | Planning | Parts arrived | Build not started | Inventory and assemble |
| 2026-10-21 | Inventory | TMC2209; 12 V/3 A supply; partial mechanical assembly | AS5600 magnet absent | Magnet reordered; continue assembly, wiring and isolated bring-up |

## Definition of done

- The rig passes mechanical, electrical, sysid, simulation, real-teacher,
  distillation, and standalone gates.
- Its own sysid parameters and promoted Arduino policy header are committed.
- Training configuration and evaluation metrics are recorded well enough to
  reproduce the result.
- The pendulum can swing up and balance standalone without a laptop while
  respecting travel, timing, thermal, and supervision constraints.
