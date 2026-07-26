# Prospective Memory Task

| Field                | Value                        |
|----------------------|------------------------------|
| Name | Prospective Memory Task |
| Version | v0.1.0 |
| URL / Repository | https://github.com/TaskBeacon/T000077-prospective-memory-task |
| Short Description | Event-based focal versus nonfocal prospective-memory task embedded in lexical decision |
| Created By | TaskBeacon |
| Date Updated | 2026-07-27 |
| PsyFlow Version | local TaskBeacon checkout |
| PsychoPy Version | environment-managed |
| Modality | behavior |
| Language | Chinese instructions with English lexical stimuli |
| Voice Name | disabled |

## 1. Task Overview

This task measures prospective memory: remembering to perform an intended action
when a future event occurs while attention is occupied by an ongoing task. Participants
make lexical decisions throughout. After a baseline block, they complete focal and
nonfocal prospective-memory blocks in counterbalanced order.

The focal intention is triggered by the exact word `PACKET`. The nonfocal intention
is triggered by the letter sequence `TOR` embedded in a word such as `DOCTOR`.
The intended action is performed on the neutral `WAITING` screen after the lexical
decision, which keeps ongoing-task accuracy and delayed-intention execution separable.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Participant-visible flow | Implementation detail |
|---:|---|---|
| 1 | Lexical-decision instructions and practice | 10 trials from `assets/stimuli.csv`; lexical feedback only |
| 2 | Baseline lexical-decision block | 105 trials; no PM intention |
| 3 | Focal or nonfocal intention instruction | Order from participant parity; instruction stimulus matches block type |
| 4 | Embedded-figures distractor | `distractor_instruction` + `embedded_figures`; 120 s |
| 5 | Prospective-memory block | 105 trials; targets at positions 25, 50, 75, and 100 |
| 6 | Neutral break and second PM condition | Repeat steps 3-5 for the other cue focality |
| 7 | Completion and export | Summary screen; one reduced row per logical trial |

### Trial-Level Flow

| Phase | Stimulus ID | Duration / response | Result |
|---|---|---|---|
| Lexical decision | `letter_string` | Up to 3 s; `F` nonword, `J` word | Ongoing-task accuracy and RT |
| Waiting | `waiting` | Up to 10 s; `SPACE` normally, `/` for PM cue | PM hit, miss, or false alarm |
| Continue | `waiting` | Conditional after `/`; `SPACE`, up to 10 s | Advances to next trial |
| Practice feedback | `feedback_correct` / `feedback_incorrect` | 0.6 s; practice only | Lexical correctness |

### Controller Logic

| Component | Rule |
|---|---|
| Adaptive controller | None |
| Trial planner | Deterministic `build_plans()` preserves target positions, lexicality ratio, and target identity |
| Counterbalancing | Odd participant IDs receive focal first; even IDs receive nonfocal first |

### Other Logic

| Component | Rule |
|---|---|
| PM scoring | Hit, miss, and false alarm are scored independently of lexical accuracy |
| Data reduction | Each returned trial dictionary is one logical-trial row |
| Randomness | Concrete fillers are selected from a stable block seed before `run_trial()` |

## 3. Configuration Summary

Settings below are from `config/config.yaml`.

### a. Subject Info

| Field | Value |
|---|---|
| Participant ID | Three-digit integer |
| Counterbalancing | Odd ID: focal first; even ID: nonfocal first |

### b. Window Settings

| Setting | Value |
|---|---|
| Size | 1280 × 800 |
| Units | degrees |
| Background | `#f4f5f7` |
| Viewing distance | 57 cm |

### c. Stimuli

| Element | Participant-facing content | Response |
|---|---|---|
| Ongoing item | Uppercase English word or pronounceable nonword | `J` word; `F` nonword |
| Focal PM cue | `PACKET` | `/` on following `WAITING` |
| Nonfocal PM cue | A word containing `TOR` | `/` on following `WAITING` |
| Nontarget waiting | `WAITING` | `SPACE` |
| Distractor | Embedded-figures line drawing | Observe/search for 120 s |

### d. Timing

| Phase | Human duration |
|---|---:|
| Lexical response window | 3.0 s |
| Waiting safety window | 10.0 s |
| Post-PM continue window | 10.0 s |
| Embedded-figures distractor | 120.0 s |
| Practice feedback | 0.6 s |

### e. Triggers

| Range | Events |
|---|---|
| 1 / 99 | Experiment start / end |
| 10 / 90 | Block start / end |
| 20-27 | Lexical and PM-target onsets |
| 30-32 | Lexical responses / timeout |
| 40-43 | Waiting onset, PM response, advance, timeout |
| 50 / 60 | Practice feedback / distractor |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| Adaptive controller | Not applicable |
| Fixed schedule helper | `src/utils.py::build_plans` |

Run modes:

```powershell
python main.py human
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```

## 4. Methods (for academic publication)

The task adapts the event-based prospective-memory protocol of Brewer et al. (2010).
Participants first completed an ongoing lexical-decision baseline. Each trial presented
one uppercase letter string, and participants classified it as a word or nonword using
the `J` and `F` keys, respectively. After the response, a neutral waiting screen was
shown and `SPACE` advanced the task.

Participants then encoded focal and nonfocal delayed intentions in counterbalanced
blocks. For the focal intention, the exact word `PACKET` served as the PM cue. For
the nonfocal intention, any word containing `TOR` served as the cue. Participants
executed the intention by pressing `/` during the waiting screen after classifying the
cue. A 120-second embedded-figures distractor separated intention encoding from task
performance, and PM instructions were not repeated after the distractor. Each formal
block contained 105 trials, with PM cues at positions 25, 50, 75, and 100.

Primary dependent variables are cue-detection accuracy by focality, PM false-alarm
rate, ongoing lexical accuracy and latency, and PM-related ongoing-task cost relative
to baseline. The unpublished filler lists and response deadlines were not available;
the included filler pool and finite safety windows are documented as inferences in
the evidence mappings.

Selected sources:

- Brewer, G. A., Knight, J. B., Marsh, R. L., & Unsworth, N. (2010).
  *Memory & Cognition, 38*, 304-311. https://doi.org/10.3758/MC.38.3.304
- McDaniel, M. A., Howard, D. C., & Butler, K. M. (2008).
  *Memory & Cognition, 36*, 716-724. https://doi.org/10.3758/MC.36.4.716
- McDaniel, M. A., Umanath, S., Einstein, G. O., & Waldum, E. R. (2015).
  *Frontiers in Human Neuroscience, 9*, 392. https://doi.org/10.3389/fnhum.2015.00392
