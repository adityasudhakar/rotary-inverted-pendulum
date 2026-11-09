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
- [x] Missing AS5600 magnet identified; multiple magnets have now been tested.
- [x] USB power-only cable identified; Micro-USB data/sync cable ordered.
- [x] Micro-USB data/sync cable arrived and confirmed working (Nano detected
  at `/dev/cu.usbserial-1420`).
- [ ] **AS5600 sensing is not functionally reliable.** Multiple magnets and two
  encoder boards have been tested. Some fixed positions produce strong, stable
  readings, but small alignment changes cause large strength changes and a
  controlled 180-degree pendulum rotation was not reconciled reliably with the
  captured readout. Do not proceed to sysid, training or balance control until
  the encoder passes the acceptance test below.
- [x] Replacement AS5600 board obtained and A/B tested. It behaves similarly to
  the original board, making a single damaged encoder board an unlikely full
  explanation. The root cause remains unresolved.
- [x] **AS5600 supply moved from 5 V to 3.3 V (2026-11-09).** All earlier
  encoder tests ran the module from the Uno's 5 V pin. A product review for
  this module family warns that the boards ship wired for 3.3 V and that R1
  must be open for safe 5 V use (the same open TODO as issue #4 in
  `website/src/content/docs/build/electronics.md`). R1's state on our boards
  was **not** verified (no continuity check done yet). At 3.3 V the chip
  reports the field as too weak (AGC pinned at its maximum, "too weak" flag)
  almost continuously. The earlier 5 V "healthy magnitude ~2070" readings are
  now treated as unreliable: magnitude is AGC-regulated, not a strength gauge.
- [ ] **Replacement diametric magnets ordered; awaiting arrival.** K&J
  Magnetics D42DIA-type discs, 1/4" x 1/8" (6.35 x 3.18 mm), diametrically
  magnetised (N42 and/or N52 grade; confirm what arrives). Verify on arrival
  that the field is really diametric (strongest centred over the chip, raw
  angle sweeps 0-4095 when spun in place) before trusting the listing.
- [ ] **Pendulum CAD: widen the magnet pocket and add a magnet push-out hole.**
  Measured from the real `pendulum.stl` (the copy in a fresh clone is a Git
  LFS pointer; the real file must be pulled): the shaft is 8.1 mm OD with a
  magnet pocket of only about 4.1 mm diameter x ~1.5 mm deep at the free end,
  so the 6.35 x 3.18 mm replacement discs do not fit. A 2.5 mm axial bore
  already runs most of the shaft, closed by a ~0.5 mm wall behind the pocket
  and a ~1 mm cap at the far hub face. Proposed change: pocket about
  6.45-6.5 mm diameter x ~3.3 mm deep (about 0.8 mm wall remains, and the
  deeper pocket breaks into the bore), plus a 2.5 mm hole through the far
  cap so a ~2 mm rod can push the magnet out. Edit in Onshape, then re-export
  the STL/URDF and re-run sysid (the replacement magnet is about 3 g against a
  pendulum under 50 g).
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
- [ ] Mount the AS5600 loosely; do not glue or permanently position it until a
  complete-revolution test establishes a repeatable air gap and centering.
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

Electronics bring-up:

- [ ] Transfer the proven interim Uno wiring to the final Nano/protoboard after
  the encoder problem is resolved. Driver, motor, power and AS5600 have been
  exercised from the Uno, but the final electronics assembly is not complete.
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
  are solved before final assembly. `TestMotor` compiled and flashed
  successfully to an Arduino Uno (used as stand-in; same ATmega328P).
  AccelStepper and FastAccelStepper libraries confirmed installed.

Encoder work:

- [ ] Pass `TestEncoder`; tested configurations have not yet reported angle
  correctly over a controlled rotation even when magnet strength is healthy.
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
- AS5600 air gap and mounting notes: tested on the chip side at several gaps
  and X/Y offsets. Detection is highly sensitive to centering and gap; no
  repeatable accepted geometry has been established. Header pins were removed
  and reoriented to clear the chip side, and the magnet was moved closer in the
  printed pendulum holder.
- AS5600 status: original and replacement HW-993/AS5600 boards and multiple
  magnets have been tried on the Uno. Static readings can be strong and stable,
  but angle tracking through real pendulum motion is not yet usable.
- AS5600 supply: **3.3 V from the Uno's 3V3 pin** (since 2026-11-09; was 5 V).
  The Uno's internal I2C pull-ups were disabled in the diagnostic sketch so
  SDA/SCL are pulled up only by the module to 3.3 V. R1 state unverified.

### AS5600 troubleshooting record (through 2026-11-09)

The encoder is the current hardware blocker. The tests below supersede the
earlier assumptions that the magnet was merely missing or that the original
board alone had been damaged.

- Wiring used for the tests: AS5600 at I2C address `0x36`, VCC/GND connected to
  the Uno, SDA=A4, SCL=A5, DIR tied to GND, and OUT/GPO unused. The old encoder
  was disconnected during replacement-board tests, so there was no duplicate
  I2C address. The replacement board's headers were soldered.
- Both the original and replacement encoder boards communicate successfully.
  Several magnets/configurations were tried, including moving the installed
  magnet closer to the chip and testing it by hand outside the holder.
- Sensing through the back of the PCB was weak (roughly 720-1213 magnitude), so
  testing moved to the chip side. On the chip side, small changes in X/Y
  centering or gap could change magnitude from almost zero/no detection to
  roughly 2450/healthy detection. This sensitivity persisted in a fixture with
  no nearby metal jaws, so metal interference was considered but not proven as
  the primary cause.
- Some fixed alignments were excellent: repeated samples held near magnitude
  2086-2088, and a replacement-board configuration held near 2020-2025 with
  raw angle 455. Another static run held magnitude 1937-1944 and raw angle 407.
  Other fixed positions were repeatably weak, including magnitudes around
  245-249, 679-682 and 1380-1385. This shows that the I2C link can be stable,
  but it does not establish correct angular sensing.
- One fixtured test retained healthy detection throughout (magnitude roughly
  1828-2143) while the pendulum was physically rotated 180 degrees. The live
  analysis initially identified only about 106 counts (9.3 degrees) between
  selected samples, but the operator confirmed the physical motion was 180
  degrees and challenged that interpretation. Because the capture window or
  sample selection may have been wrong, this is an unresolved mismatch, not a
  trustworthy measurement. A correct endpoint test should show about 2048 of
  4096 counts. Earlier hand-held tests that swept large raw-angle ranges were
  also confounded by changing gap and lateral alignment.
- Static fixture settling also shifted one plateau from raw 455/magnitude 2025
  to raw 407/magnitude 1938 (about 48 counts or 4.2 degrees) without an intended
  rotation. Loose wiring alone is not a sufficient explanation because long
  static runs were otherwise rock solid, but mechanical alignment/relative
  motion remains a possible contributor.
- Current conclusion: the system can produce valid-looking AS5600 readings,
  but the output is too alignment-sensitive and inconsistent with known motion
  to support feedback control. No conclusion about a single bad board or a
  specific magnetization fault has yet been proven.

#### 2026-11-09 independent re-test (Uno, motor driver disabled)

An ad-hoc direct-register logger (reads raw angle, magnitude, AGC and status at
`0x36`; kept outside the repo) was flashed to the Uno so the earlier library and
sketch results could be checked independently. Findings:

- **Magnitude is not a strength gauge; AGC is.** Magnitude stays near ~2100
  whenever the chip has enough signal, because the AGC regulates it (hand-held
  close to the chip: AGC 32-40 with magnitude ~2100; in the rig: AGC pinned at
  255 with magnitude ~2070). The 5 V rig readings therefore sat at the
  weakest-field limit, and the earlier "healthy magnitude" labels in this
  record are superseded. Aim for AGC roughly mid-range (about 128 at 5 V; the
  range is 0-128 at 3.3 V, so roughly 40-90 there) with only the
  magnet-detected flag set.
- **5 V static baseline:** raw 424-425, magnitude 2067-2073, AGC 255, status
  `0x67`, 338 samples, 0 I2C errors. The status byte has bits set outside the
  datasheet's bits 5:3 and registers 0x10-0x19 read non-zero; config registers
  0x00-0x0A are all zero. This may indicate a clone or stressed part; not proven.
- **5 V guided rotation test** (audio-cued, assuming the cued motion was
  performed): raw-angle range over a 180-degree turn was only 5.1 degrees, over
  the return turn 7.5 degrees, and over one full slow revolution 11.7 degrees,
  while magnitude (1811-2147) and AGC (207-255) wobbled. Something moved, but
  the angle did not follow. A correct result is about 180 degrees and 360 degrees.
- **Hand-spinning the magnet** (two attempts) was inconclusive: it was in range
  only ~2 s in the first and never in the second. The apparent full 0-4095
  sweeps occurred while magnitude was 2-7 (no magnet in range), i.e. noise.
- **3.3 V test:** AS5600 VCC moved to the Uno 3V3 pin, internal pull-ups off.
  I2C works with 0 errors. AGC sits at its 3.3 V maximum (128) with the
  "too weak" flag set; raw angle wanders widely (e.g. 1054-3527 in an 8 s
  nominally static capture) and magnitude is 241-1710. A 60 s audio gap-meter
  run (spoken weak/good/strong + AGC) reported "weak" for most of the run
  (about 85% of readings), with only two brief "good" readings (once at AGC 59).
- **Interpretation (hypotheses, not confirmed):** (1) the included magnet is
  too small/weak for the gap and/or not diametric; an axial magnet gives a weak
  differential signal when centred and an angle that follows lateral position
  rather than rotation, which matches the alignment sensitivity seen; (2)
  running a 3.3 V-wired module at 5 V with R1 closed may have inflated the 5 V
  readings and could have stressed the chip. A closed-R1 continuity check
  (power off) has not been done. Both boards come from the same listing, which
  would explain why swapping boards and magnets changed nothing.
- **Pendulum geometry** (from the real `pendulum.stl`; see Current state): the
  existing magnet pocket is about 4.1 mm x ~1.5 mm, consistent with a small
  ~4 mm disc and a weak field at the chip.

Encoder acceptance gate before sysid or policy work:

- [ ] With board and magnet axes rigidly fixed, magnet detection remains healthy
  over the pendulum's complete revolution (detected, neither weak nor strong).
- [ ] A controlled 180-degree rotation changes raw angle by approximately 2048
  counts, and a full revolution smoothly traverses/wraps the 0-4095 range.
- [ ] Multiple forward/reverse sweeps are repeatable, without dropouts, large
  discontinuities or dependence on tiny unavoidable mounting shifts.
- [ ] Repeat the 180-degree endpoint test using the freshly uploaded minimal
  direct-register diagnostic sketch. Its clean baseline was raw 425-426,
  37.35-37.44 degrees, magnitude 2049-2052 with valid I2C reads; the controlled
  180-degree endpoint has not yet been captured with this sketch.
- [ ] Power-off continuity check across R1 on each AS5600 board; remove R1 only
  if the module must run from 5 V (the final Nano build), otherwise keep it on
  3.3 V.
- [ ] When the replacement diametric magnets arrive: confirm they are diametric
  (best signal centred over the chip, raw angle sweeps 0-4095 as the magnet is
  spun in place), find a gap with AGC mid-range and no weak/strong flags using
  an audio gap meter, then repeat the 180-degree and full-revolution tests.
- [ ] Apply the pendulum CAD change (wider/deeper pocket plus push-out hole) so
  the new magnets fit and are retrievable.
- [ ] If the direct-register result still fails, isolate magnetization and
  mechanics with a rigid off-pendulum rotation jig. Consider a shaft-mounted
  optical quadrature encoder if the magnetic arrangement cannot pass this gate.

Electrical gate:

- [ ] All four test sketches pass independently.
- [ ] Motor and driver remain warm, not too hot to touch.
- [ ] No buzzing, grinding, skipped steps, encoder jumps, or cable interference.

## Phase 3 — identify this rig

- [ ] Set up the Python environment from `policy/` with `uv` while resolving the
  encoder blocker.
- [ ] Run software-only smoke tests and prepare the sysid command while encoder
  troubleshooting continues.
- [ ] **Encoder dependency:** do not start real sysid until the AS5600 passes the
  full acceptance gate above (or is replaced by a validated encoder design).
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
| 2026-10-29 | Review | — | AS5600 board may have been damaged during reversed-polarity incident; pendulum CAD lacks a through-hole for magnet removal | Order replacement AS5600 as precaution; modify pendulum CAD to add magnet push-out hole |
| 2026-10-29 to 2026-11-05 | AS5600 alignment experiments | Original board; several magnet placements; hand-held and fixtured tests; chip-side and PCB-back tests | Chip-side magnitude ranged from no detection to about 2450 depending on gap/centering; PCB-back sensing was weak. Some static positions were very stable, but motion tests were inconsistent | Reorient headers for chip-side clearance, move magnet closer, remove nearby metal from the fixture, and A/B test replacement hardware |
| 2026-11-05 | Replacement magnet test | Original AS5600 with new/repositioned magnet and non-metallic clearance around the sensing area | Strong detection could be obtained, but reliable angle tracking was not established | A different magnet alone did not resolve the issue; test a replacement encoder board |
| 2026-11-09 | Replacement encoder A/B test | New soldered AS5600 board on Uno; old board disconnected; magnet fixtured above chip | Static output could hold raw 455 and magnitude 2020-2025, then raw 407 and magnitude 1937-1944. During a known 180-degree pendulum rotation, the live analysis selected samples only about 106 counts apart despite healthy magnitude; the operator correctly challenged this result, so the capture/interpretation is inconclusive | Two boards and multiple magnets/configurations have not yet produced a trustworthy functional-motion pass. Block sysid/policy work and run a controlled minimal direct-register endpoint test |
| 2026-11-09 | Minimal direct-register baseline | Fresh Uno sketch reading AS5600 raw angle/status/magnitude directly at `0x36`, 100 kHz I2C, 50 ms samples; motor disabled | Clean static baseline: raw 425-426, 37.35-37.44 degrees, magnitude 2049-2052, valid healthy detection | Capture controlled 180-degree endpoint next; baseline alone is not a pass |
| 2026-11-09 | Direct-register guided rotation (5 V) | Own register-level logger on the Uno; AS5600 on 5 V; audio-cued 180-degree, return and full-revolution turns | Raw angle moved only 5.1 / 7.5 / 11.7 degrees over the three motions while magnitude and AGC wobbled; AGC pinned at 255 at rest | Encoder still not tracking rotation. Magnitude is AGC-regulated and was a misleading "health" metric; use AGC |
| 2026-11-09 | Hand-spin magnet tests (5 V) | Magnet held and spun by hand over the chip, two attempts | Mostly out of range; only ~35 healthy samples, angle moved ~20 degrees; apparent full sweeps were noise at magnitude 2-7 | Inconclusive; stop relying on hand tests |
| 2026-11-09 | AS5600 supply change to 3.3 V | VCC moved from Uno 5V to 3V3; Uno internal I2C pull-ups disabled; same fixture; audio gap meter for 60 s | I2C fine; AGC pinned at 128 (maximum), "too weak" flag most of the time (about 85% of readings), raw angle wandering | The true field at this magnet/gap is too weak; 5 V readings were likely misleading (R1 closed? unverified). Stay on 3.3 V |
| 2026-11-09 | Pendulum geometry / magnet fit | Real `pendulum.stl` pulled from LFS and sliced; K&J D42DIA 6.35 x 3.18 mm diametric discs ordered | Existing pocket ~4.1 x ~1.5 mm; new discs do not fit; 2.5 mm bore nearly through the shaft | Widen/deepen pocket and open the bore end in Onshape; re-run sysid after the swap; test new magnets for true diametric behaviour on arrival |

## Definition of done

- The rig passes mechanical, electrical, sysid, simulation, real-teacher,
  distillation, and standalone gates.
- Its own sysid parameters and promoted Arduino policy header are committed.
- Training configuration and evaluation metrics are recorded well enough to
  reproduce the result.
- The pendulum can swing up and balance standalone without a laptop while
  respecting travel, timing, thermal, and supervision constraints.
