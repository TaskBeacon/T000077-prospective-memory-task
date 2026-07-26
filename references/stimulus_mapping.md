# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `baseline_word` | lexical decision | `letter_string` | One centered uppercase English filler word | `SRC001` | Methods: uppercase strings presented one at a time in the center. | `psychopy_builtin` | `assets/stimuli.csv` | J is the correct ongoing response. |
| `baseline_nonword` | lexical decision | `letter_string` | One centered uppercase pronounceable nonword | `SRC001` | Methods: 53 pronounceable nonwords in baseline. | `psychopy_builtin` | `assets/stimuli.csv` | F is the correct ongoing response. |
| `focal_target` | lexical decision → waiting | `letter_string`, `waiting` | `PACKET`, then neutral `WAITING` | `SRC001` | Methods identifies `PACKET` and the slash response during waiting. | `psychopy_builtin` | none | J classifies the word; slash fulfills the intention. |
| `focal_filler_word` | lexical decision → waiting | `letter_string`, `waiting` | Uppercase filler word, then neutral `WAITING` | `SRC001` | Same lexical-decision parameters as baseline. | `psychopy_builtin` | `assets/stimuli.csv` | J, then SPACE. |
| `focal_nonword` | lexical decision → waiting | `letter_string`, `waiting` | Uppercase pronounceable nonword, then neutral `WAITING` | `SRC001` | Same lexical-decision parameters as baseline. | `psychopy_builtin` | `assets/stimuli.csv` | F, then SPACE. |
| `nonfocal_target` | lexical decision → waiting | `letter_string`, `waiting` | `DOCTOR`, `FACTOR`, `PASTOR`, or `TRACTOR`, then neutral `WAITING` | `SRC001` | Methods lists the four words containing the target syllable `TOR`. | `psychopy_builtin` | none | J classifies the word; slash fulfills the intention. |
| `nonfocal_filler_word` | lexical decision → waiting | `letter_string`, `waiting` | Uppercase word without `TOR`, then neutral `WAITING` | `SRC001` | Same lexical-decision parameters as baseline. | `psychopy_builtin` | `assets/stimuli.csv` | J, then SPACE. |
| `nonfocal_nonword` | lexical decision → waiting | `letter_string`, `waiting` | Uppercase nonword without `TOR`, then neutral `WAITING` | `SRC001` | Same lexical-decision parameters as baseline. | `psychopy_builtin` | `assets/stimuli.csv` | F, then SPACE. |
| `all_pm_blocks` | intention encoding | `focal_instruction`, `nonfocal_instruction` | Chinese cue-action rule naming `PACKET` or `TOR` and the slash action | `SRC001`, `SRC002` | Both sources describe explicit cue-action intention formation before the ongoing task. | `psychopy_builtin` | none | Instruction is not shown again after the distractor. |
| `all_pm_blocks` | distractor | `distractor_instruction`, `embedded_figures` | Embedded-figures search with a simple target shape at upper right | `SRC001` | Methods reports a 2-minute embedded-figures puzzle. | `generated_reference_asset` | `assets/embedded_figures.svg`, `assets/embedded_figures.png` | Original non-placeholder artwork; stimulus class and duration match the report. |
