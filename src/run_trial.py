from __future__ import annotations

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import TrialPlan


def _set_context(
    unit,
    *,
    trial_id,
    block_id,
    plan,
    phase,
    deadline,
    keys,
    stim_id,
):
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=deadline,
        valid_keys=keys,
        block_id=block_id,
        condition_id=str(plan),
        task_factors={**plan.to_dict(), "stage": phase},
        stim_id=stim_id,
    )


def _onset_code(settings, plan):
    if plan.pm_target:
        return settings.triggers.get(f"{plan.block_type}_target")
    return settings.triggers.get(f"{plan.block_type}_{plan.lexicality}")


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    if not isinstance(condition, TrialPlan):
        raise TypeError("Prospective memory task requires TrialPlan")

    plan = condition
    trial_id = next_trial_id()
    block_name = str(block_id or plan.block_type)
    factors = plan.to_dict()
    data = {
        "trial_id": trial_id,
        "phase": "prospective_memory",
        "block_id": block_name,
        "block_idx": int(block_idx or 0),
        **factors,
    }

    lexical = StimUnit(
        "lexical_decision", win, kb, runtime=trigger_runtime
    ).add_stim(stim_bank.rebuild("letter_string", text=plan.stimulus))
    lexical_window = float(settings.lexical_response_window)
    _set_context(
        lexical,
        trial_id=trial_id,
        block_id=block_name,
        plan=plan,
        phase="lexical_decision",
        deadline=lexical_window,
        keys=["f", "j"],
        stim_id=f"letter_string_{plan.stimulus.lower()}",
    )
    lexical.capture_response(
        keys=["f", "j"],
        correct_keys=[plan.correct_key],
        duration=lexical_window,
        onset_trigger=_onset_code(settings, plan),
        response_trigger={
            "f": settings.triggers.get("response_nonword"),
            "j": settings.triggers.get("response_word"),
        },
        timeout_trigger=settings.triggers.get("lexical_timeout"),
        terminate_on_response=True,
    ).to_dict(data)
    lexical_response = lexical.get_state("response", None)
    ongoing_correct = lexical_response == plan.correct_key

    waiting = StimUnit("waiting", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("waiting")
    )
    waiting_window = float(settings.waiting_window)
    pm_required = bool(plan.pm_target and plan.block_type in {"focal", "nonfocal"})
    _set_context(
        waiting,
        trial_id=trial_id,
        block_id=block_name,
        plan=plan,
        phase="waiting",
        deadline=waiting_window,
        keys=["slash", "space"],
        stim_id="waiting",
    )
    waiting.capture_response(
        keys=["slash", "space"],
        correct_keys=["slash"] if pm_required else ["space"],
        duration=waiting_window,
        onset_trigger=settings.triggers.get("waiting"),
        response_trigger={
            "slash": settings.triggers.get("pm_response"),
            "space": settings.triggers.get("advance_response"),
        },
        timeout_trigger=settings.triggers.get("waiting_timeout"),
        terminate_on_response=True,
    ).to_dict(data)
    waiting_response = waiting.get_state("response", None)

    if waiting_response == "slash":
        continuation = StimUnit(
            "continue", win, kb, runtime=trigger_runtime
        ).add_stim(stim_bank.get("waiting"))
        continue_window = float(settings.continue_window)
        _set_context(
            continuation,
            trial_id=trial_id,
            block_id=block_name,
            plan=plan,
            phase="continue",
            deadline=continue_window,
            keys=["space"],
            stim_id="waiting",
        )
        continuation.capture_response(
            keys=["space"],
            correct_keys=["space"],
            duration=continue_window,
            response_trigger={"space": settings.triggers.get("advance_response")},
            timeout_trigger=settings.triggers.get("waiting_timeout"),
            terminate_on_response=True,
        ).to_dict(data)

    pm_hit = bool(pm_required and waiting_response == "slash")
    pm_miss = bool(pm_required and waiting_response != "slash")
    pm_false_alarm = bool(not pm_required and waiting_response == "slash")
    data.update(
        lexical_response_key=str(lexical_response or ""),
        lexical_rt=lexical.get_state("rt", None),
        ongoing_correct=ongoing_correct,
        waiting_response_key=str(waiting_response or ""),
        waiting_rt=waiting.get_state("rt", None),
        pm_required=pm_required,
        pm_hit=pm_hit,
        pm_miss=pm_miss,
        pm_false_alarm=pm_false_alarm,
        outcome=(
            "pm_hit"
            if pm_hit
            else "pm_miss"
            if pm_miss
            else "pm_false_alarm"
            if pm_false_alarm
            else "ongoing_only"
        ),
    )

    if plan.practice:
        feedback_name = (
            "feedback_correct" if ongoing_correct else "feedback_incorrect"
        )
        feedback = StimUnit(
            "practice_feedback", win, kb, runtime=trigger_runtime
        ).add_stim(stim_bank.get(feedback_name))
        _set_context(
            feedback,
            trial_id=trial_id,
            block_id=block_name,
            plan=plan,
            phase="practice_feedback",
            deadline=float(settings.feedback_duration),
            keys=[],
            stim_id=feedback_name,
        )
        feedback.show(
            duration=float(settings.feedback_duration),
            onset_trigger=settings.triggers.get("practice_feedback"),
        ).to_dict(data)

    return data
