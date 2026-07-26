# Paradigm Logic Audit

## 1. Paradigm Intent

This task measures event-based prospective memory: remembering to execute a delayed
intention when a future cue occurs while an ongoing activity is being performed.
The canonical implementation follows Brewer et al. (2010): an ongoing lexical-decision
task is completed first as a baseline and then while participants hold either a focal
or a nonfocal prospective-memory intention.

The primary within-participant factors are:

- `block_type`: baseline, focal, or nonfocal.
- `lexicality`: English word or pronounceable nonword.
- `pm_target`: whether the current word is a prospective-memory cue.
- `cue_focality`: exact target word `PACKET` (focal) versus the syllable `TOR`
  embedded in a word (nonfocal).

Primary outcomes are focal and nonfocal cue detection, false alarms, lexical-decision
accuracy/latency, and the ongoing-task latency cost relative to baseline.

## 2. Block/Trial Workflow

Block-level state machine:

1. Collect participant information and show Chinese task instructions.
2. Complete a short ongoing-task practice block.
3. Complete the 105-trial baseline lexical-decision block without a PM intention.
4. Present one PM intention (focal or nonfocal; order counterbalanced by participant).
5. Complete a 120-second embedded-figures distractor interval; do not remind the
   participant of the intention afterward.
6. Complete the corresponding 105-trial PM block.
7. Show a neutral inter-block break.
8. Repeat steps 4-6 for the other PM intention.
9. Show the completion screen and save one reduced row per logical trial.

Human trial-level state machine:

1. `lexical_decision`: show one uppercase letter string at screen center. The
   participant presses `F` for nonword or `J` for English word.
2. `waiting`: show the neutral word `WAITING`. The participant normally presses
   `SPACE` to advance. If the just-classified word is a PM cue, the intended action
   is to press `/` during this screen.
3. `continue` (conditional): after any `/` response, keep the neutral waiting screen
   visible and collect `SPACE` to start the next trial.

Brewer et al. fixed PM cues at trials 25, 50, 75, and 100 of each PM block. The
baseline has the same 105-trial lexical structure but no PM cue requirement. A
custom, deterministic schedule is required because target identity and exact target
positions cannot be represented by label-only weighted generation.

## 3. Condition Semantics

- `baseline_word`: ordinary English word; `J` is correct; no PM action is active.
- `baseline_nonword`: pronounceable nonword; `F` is correct; no PM action is active.
- `focal_target`: the word `PACKET`; `J` is the ongoing response and `/` on the
  following waiting screen fulfills the intention.
- `focal_filler_word`: ordinary word in the focal block; `J`, then `SPACE`.
- `focal_nonword`: nonword in the focal block; `F`, then `SPACE`.
- `nonfocal_target`: a word containing `TOR` (`DOCTOR`, `FACTOR`, `PASTOR`, or
  `TRACTOR`); `J`, then `/` on the waiting screen.
- `nonfocal_filler_word`: ordinary word without `TOR`; `J`, then `SPACE`.
- `nonfocal_nonword`: nonword without `TOR`; `F`, then `SPACE`.

The focal and nonfocal blocks are counterbalanced. All concrete items are scheduled
before `run_trial()` from a stable task/block seed.

## 4. Response and Scoring Rules

- Ongoing lexical decision: `F = NONWORD`, `J = WORD`.
- Prospective-memory response: `/` during the post-decision waiting screen.
- Advancement response: `SPACE` during the waiting screen.
- A PM hit requires `/` on a scheduled target trial in a PM block.
- Pressing `SPACE` first on a target trial is a PM miss.
- Pressing `/` on a nontarget or baseline trial is a false alarm.
- Lexical accuracy is scored independently of PM detection.
- No correctness feedback is shown during scored blocks.
- Practice provides brief correct/incorrect feedback for the lexical decision only.
- The source does not report a lexical response deadline or a waiting timeout.
  Finite 3-second and 10-second safety windows are conservative implementation
  inferences and are logged as such.

## 5. Stimulus Layout Plan

- All trial stimuli use a light-gray full-screen background.
- Letter strings are uppercase, dark charcoal, centered at `[0, 0]`, and use a
  monospaced Latin font with a height of approximately 1 visual degree.
- The waiting screen contains only `WAITING`, centered at `[0, 0]`; it never displays
  condition labels, target reminders, or key mappings.
- Chinese instruction and break text uses `SimHei`, centered, with explicit
  `wrapWidth` and no concurrent text objects.
- The embedded-figures distractor uses a single centered line-drawing image with a
  Chinese instruction line above it. The two elements have separate vertical anchors
  so they cannot overlap.
- PM instructions show one compact cue-action rule at center. The focal instruction
  identifies `PACKET`; the nonfocal instruction identifies the syllable `TOR`.

## 6. Trigger Plan

- Experiment lifecycle: `experiment_start=1`, `experiment_end=99`.
- Block lifecycle: `block_start=10`, `block_end=90`.
- Lexical stimuli: baseline/focal/nonfocal word and nonword onset codes `20-25`;
  PM target onset codes `26-27`.
- Lexical responses: `F=30`, `J=31`, lexical timeout `32`.
- Waiting onset `40`; PM response `/=41`; advance response `SPACE=42`;
  waiting timeout `43`.
- Practice feedback `50`; distractor onset `60`; instruction/intention onset `70-72`.

Onset, response, and timeout triggers flow through `StimUnit` public APIs.

## 7. Architecture Decisions (Auditability)

- `main.py` owns block order, intention instructions, distractor intervals, and block
  lifecycle.
- `src/utils.py` owns CSV loading, participant counterbalancing, deterministic
  fixed-position trial planning, and summary calculations.
- `src/run_trial.py` is a thin layer that only sequences lexical decision, waiting,
  optional continue, practice feedback, and trial data assembly.
- Trial identity comes from `psyflow.next_trial_id()`.
- Concrete condition factors are fully formed before `run_trial()` and passed as a
  `TrialPlan`.
- All participant-facing instructions and static labels are stored in YAML; concrete
  letter strings come from the audited CSV stimulus pool.
- No controller is needed because the task has no adaptive state.

## 8. Inference Log

| Decision | Type | Rationale | Source |
|---|---|---|---|
| Use the Brewer et al. baseline/focal/nonfocal within-participant paradigm | direct | It provides a complete classic event-based PM manipulation and explicit trial positions. | SRC001 |
| Use 105 strings with 52 words and 53 nonwords per block | direct | Reported in the primary protocol. | SRC001 |
| Use uppercase centered strings and F/J lexical keys | direct | Reported in the primary protocol. | SRC001 |
| Use `/` during the waiting screen and `SPACE` to advance | direct | Reported in the primary protocol. | SRC001 |
| Use a 120-second embedded-figures distractor after intention encoding | direct/adapted | Duration and puzzle class are reported; the exact historical puzzle artwork is unavailable, so an original non-placeholder embedded-figures line drawing is used. | SRC001 |
| Use a 3-second lexical response safety window | inferred | The paper reports response-contingent progression but no deadline; a finite window prevents unattended runs while preserving ordinary RTs. | SRC001 |
| Use a 10-second waiting safety window | inferred | The paper describes participant-paced advancement but no timeout; 10 seconds is a conservative operational bound. | SRC001 |
| Reuse an audited filler pool across blocks | inferred | The paper does not publish the full 105-item lists; target identity, lexicality ratio, uppercase format, and fixed positions remain exact. | SRC001 |
| Present Chinese instructions while retaining English lexical stimuli | adapted | User-facing default is Chinese, but English word/nonword judgments and the `TOR` cue must remain English to preserve the protocol. | SRC001 |
