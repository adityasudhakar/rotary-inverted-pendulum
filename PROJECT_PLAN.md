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
- [x] USB power-only cable identified; Micro-USB data/sync cable ordered.
- [x] Micro-USB data/sync cable arrived and confirmed working (Nano detected
  at `/dev/cu.usbserial-1420`).
- [ ] **Waiting on the AS5600 magnet.** Encoder testing, sysid, real-rig
  fine-tuning and standalone deployment are blocked until it arrives.
- [x] **TMC2209 survived and passes the guarded motor test.** The earlier
  VS-to-GND "short" diagnosis was caused by reversed 12 V polarity, not an
  internal driver short. After correcting the polarity, VS-to-GND measured
  open unpowered, the board accepted 5 V + 12 V, Vref adjusted normally, and
  `TestMotor` turned the motor successfully from the interim Uno.
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
  Actual board is labelled V985; only DIR, GND and EN are silk-screened.
- [x] Confirm the Arduino Nano, AS5600 board, motor heatsink, 608 bearing,
  printed arm/pendulum subassembly and decoupling capacitors are present.
- [x] 12 V barrel-jack cable cut and stripped. **Correct, meter-confirmed
  polarity: white wire = +12 V; black wire = GND.** This counterintuitive
  colour reversal is intentional on this cable. An earlier note stated the
  exact opposite and was incorrect. Never infer this cable's polarity from
  wire colour: with the cable isolated, red probe on white and black probe on
  black must read approximately +12 V before it is connected to the rig.
- [ ] Obtain or locate the rocker switch, 40 × 60 mm protoboard, female 2.54 mm
  headers, hookup wire, printed base, lid and encoder boss.
- [x] Replace the physically oversized 22 µF 400 V electrolytic with a compact
  22 µF, 25–50 V part suitable for the protoboard.
- [x] Confirm the ceramic capacitors are marked `104` (100 nF).
- [ ] Confirm the printed pendulum contains the 2p coin specified by the model.
- [x] Record the actual stepper driver: TMC2209 V2.0 (board label V985).
- [x] Confirm the stepper is a short-body NEMA17. Label reads 42BL233.0-21A
  (non-standard naming); confirmed as a stepper by strong detent torque
  (notchy shaft). 6-pin connector; coil pairs identified by multimeter:
  pins 1+4 and 3+6; centre taps on pins 2 and 5 (left unconnected for
  bipolar drive).
- [x] Record 1/32 as the intended microstepping and make the TMC2209
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
- [ ] Verify supply polarity with a meter immediately before connection, then
  verify driver orientation, common ground, motor coil pairs,
  STEP/DIR/ENABLE pins, and AS5600 voltage requirements with power off. On this
  specific cut cable, **white is +12 V and black is GND**; the colours must not
  be treated as a general convention.
- [x] Wire the driver's microstep pins for the selected 1/32 setting and make
  every firmware `MICROSTEPS` value match.
- [x] Set driver current limit before connecting motor power:
  - TMC2209 reference: about 0.9 V Vref / 0.64 A RMS.
  - DRV8825 reference: about 0.45 V Vref / 0.9 A peak.
- [x] Identify the Nano port with `arduino-cli board list`: `/dev/cu.usbserial-1420`.
- [x] Micro-USB data cable arrived and Nano detected successfully.
- [ ] Flash and pass `TestHeartbeat`.
- [x] Flash and pass a guarded `TestMotor` motion check from the interim Uno at
  1/32 microstepping and 0.91 V Vref. The motor turned under 12 V and was
  stopped with the motor-power switch. A longer mounted thermal/roughly ±90°
  acceptance run remains part of the electrical gate below.
- [ ] Flash and pass `TestSerial`; target roughly 2.5 ms round-trip latency.
- [x] Compile all firmware sketches so missing libraries or toolchain problems
  are solved before the magnet arrives. `TestMotor` compiled and flashed
  successfully to an Arduino Uno (used as stand-in; same ATmega328P).
  AccelStepper and FastAccelStepper libraries confirmed installed.

Work that waits for the magnet:

- [ ] Flash and pass `TestEncoder`; adjust the magnet for stable readings over a
  complete revolution before fixing it permanently.
- [ ] Permanently secure the AS5600 and magnet only after the strength and
  full-rotation tests pass.
- [ ] Boot-check `LowLevelServer` and `RLControl`; both intentionally wait for
  valid magnet detection during startup.

Rig record:

- Rig name: `________________`
- Arduino Nano port: `/dev/cu.usbserial-1420`
- Arduino Uno port (interim): `/dev/cu.usbmodem14701`
- Driver: TMC2209 V985 (survived the brief reverse-polarity connections;
  unpowered VS-to-GND reads open and guarded `TestMotor` motion passed)
- Motor: 42BL233.0-21A, 6-pin unipolar, coils on pins 1+4 and 3+6
- Microsteps: 1/32 (MS1=HIGH, MS2=LOW)
- Vref/current setting: **0.91 V** (target about 0.9 V / 0.64 A RMS). The
  trimpot was not damaged: it had been resting against its clockwise end stop,
  which is the minimum-Vref end on this carrier; anticlockwise raises Vref.
- 12 V supply: KDT-1230, 12 V 3 A; barrel jack cut; **meter-confirmed
  white=+12 V, black=GND**. This intentional, nonstandard colour assignment is
  the reverse of the original incorrect project note.
- AS5600 air gap and mounting notes: `________________`
- AS5600 status: board and magnet are not yet in the circuit; `TestEncoder`,
  sysid and any policy deployment remain blocked until they are installed.

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
| 2026-10-21 | Nano bring-up | Nano powers on; Mac sees no USB device | Cable is charging-only | Data/sync cable ordered; defer flashing and serial tests |
| 2026-10-22 | Nano cable test | Micro-USB data cable arrived | Nano detected at `/dev/cu.usbserial-1420` | Nano cable blocker resolved |
| 2026-10-22 | Motor ID | Motor label 42BL233.0-21A, 6-pin connector | Confirmed stepper by detent; coils: pins 1+4, 3+6; centre taps 2+5 | Wire bipolar (skip pins 2, 5) |
| 2026-10-22 | Motor test (Uno) — superseded diagnosis | Uno as stand-in; TestMotor compiled and flashed; TMC2209 wired via breadboard; cut 12 V lead was mistakenly recorded as black=+12 V and white=GND | Adapter entered overcurrent protection when TMC ground completed the circuit; this was initially misdiagnosed as an internal VS-to-GND short | **Original diagnosis invalid:** the supply polarity was reversed at the driver because the recorded wire colours were wrong |
| 2026-10-23 | 12 V polarity correction | Re-measured the isolated cut lead with red probe on white and black probe on black | Meter reads approximately +12 V: **white=+12 V, black=GND** | The reversed-looking colour assignment is intentional on this cable; do not power the TMC again until an unpowered VS-to-GND check establishes whether it survived the reverse-polarity connections |
| 2026-10-26 | TMC2209 recovery + current limit | Motor disconnected; 22 µF/25 V electrolytic and `104` ceramic fitted across VM/GND; Uno provides 5 V/VIO; corrected 12 V polarity | VS-to-GND reads open unpowered; VIO measures 5 V and VM measures 12 V; TMC accepts both rails without the adapter tripping; Vref adjusts normally and is set to **0.91 V** | Driver survived. The trimpot's clockwise stop is minimum Vref; turn anticlockwise to raise it |
| 2026-10-26 | USB overcurrent investigation | Uno connected to Mac at `/dev/cu.usbmodem14701`; TMC powered at 5 V + 12 V; motor disconnected; Vref probing in progress | macOS logged a real overcurrent on the Uno's physical USB port (`0x14700000`) at 09:59:51, disconnected the Uno, then re-enumerated it five seconds later. With probes removed, the untouched circuit subsequently ran both rails for about 90 seconds with no recurrence | A momentary probe/jumper bridge is the leading explanation, but is not proven. Avoid thick live probes near adjacent pads; power down before repositioning test leads. Use an inline USB power meter or a non-Mac USB supply for further current diagnosis if the warning recurs |
| 2026-10-26 | Guarded motor test (Uno) | `TestMotor`; TMC2209; 1/32 microstepping (`MS1=HIGH`, `MS2=LOW`); Vref 0.91 V; motor coils pins 1+4 and 3+6, centre taps 2+5 omitted | Motor turns under command; 12 V switch stops it correctly | Actuator chain is functional. Next hardware blocker is the unwired AS5600 + missing diametric magnet; pass `TestEncoder` before sysid or policy deployment |

## Definition of done

- The rig passes mechanical, electrical, sysid, simulation, real-teacher,
  distillation, and standalone gates.
- Its own sysid parameters and promoted Arduino policy header are committed.
- Training configuration and evaluation metrics are recorded well enough to
  reproduce the result.
- The pendulum can swing up and balance standalone without a laptop while
  respecting travel, timing, thermal, and supervision constraints.
