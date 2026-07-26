# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| block_types | `task.phase_order` / `main.py` | baseline, focal, nonfocal | `SRC001` | Methods describes baseline lexical decision followed by both focal and nonfocal conditions. | `direct` | Focal/nonfocal order is counterbalanced by participant parity. |
| trials_per_block | `task.trials_per_block` | 105 | `SRC001` | Methods reports 105 letter strings in baseline and unchanged lexical-task parameters in PM blocks. | `direct` | QA and simulation shorten each block to 16 trials. |
| lexical_balance | `src/utils.py::build_plans` | 52 words, 53 nonwords | `SRC001` | Methods reports 52 valid English words and 53 pronounceable nonwords. | `direct` | Ratio is preserved by the deterministic planner. |
| target_positions | `task.target_positions` | 25, 50, 75, 100 | `SRC001` | Methods states that all four cues occurred on trials 25, 50, 75, and 100. | `direct` | QA/simulation use 4, 8, 12, and 16 for mechanism-complete short runs. |
| focal_target | `src/utils.py::FOCAL_TARGET` | `PACKET` | `SRC001` | Methods identifies `PACKET` as the focal target word. | `direct` | Repeated at all four focal target positions. |
| nonfocal_targets | `src/utils.py::NONFOCAL_TARGETS` | `DOCTOR`, `FACTOR`, `PASTOR`, `TRACTOR` | `SRC001` | Methods lists words containing the syllable `TOR`. | `direct` | One target is assigned to each fixed position. |
| lexical_keys | `task.key_list` / `src/run_trial.py` | `F` nonword; `J` word | `SRC001` | Methods specifies F for nonword and J for word. | `direct` | Config-driven and identical across modes. |
| pm_key | `task.key_list` / `src/run_trial.py` | `/` (`slash`) | `SRC001` | Methods specifies a special slash keypress during the waiting message. | `direct` | PsychoPy key token is `slash`. |
| advance_key | `task.key_list` / `src/run_trial.py` | `SPACE` | `SRC001` | Methods states that space initiated the next lexical-decision trial. | `direct` | A slash response is followed by a separate space response. |
| distractor_duration | `timing.distractor_duration` | 120 s | `SRC001` | Methods reports a 2-minute distractor after each intention was formed. | `direct` | QA/simulation shorten to 1 s before timing scaling. |
| distractor_class | `stimuli.embedded_figures` | embedded-figures puzzle | `SRC001` | Methods identifies the distractor as an embedded-figures puzzle. | `adapted` | Original artwork was not published; an original line drawing avoids proprietary materials. |
| lexical_response_window | `timing.lexical_response_window` | 3.0 s | `SRC001` | The task is response-contingent; no explicit deadline is reported. | `inferred` | Finite unattended-run safety bound; ordinary RTs are unaffected. |
| waiting_window | `timing.waiting_window` | 10.0 s | `SRC001` | The waiting display is participant-paced; no timeout is reported. | `inferred` | Conservative operational safety bound. |
| string_case | `assets/stimuli.csv` / `src/run_trial.py` | uppercase | `SRC001` | Methods states that all words and nonwords were uppercase. | `direct` | Concrete strings are audited before scheduling. |
| ongoing_priority | `stimuli.focal_instruction` / `stimuli.nonfocal_instruction` | lexical decision emphasized as primary | `SRC003` | Design guidance recommends emphasizing the ongoing task when studying PM retrieval. | `adapted` | Prevents the PM intention from replacing the ongoing task. |
