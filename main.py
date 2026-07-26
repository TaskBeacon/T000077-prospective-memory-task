from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import build_plans, pm_order, run_trial, summarize

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _run_block(
    *,
    block_name,
    block_index,
    plans,
    settings,
    win,
    kb,
    bank,
    triggers,
    sink,
):
    (
        BlockUnit(
            block_id=block_name,
            block_idx=block_index,
            settings=settings,
            window=win,
            keyboard=kb,
        )
        .add_condition(plans)
        .on_start(lambda _: triggers.send(settings.triggers.get("block_start")))
        .on_end(lambda _: triggers.send(settings.triggers.get("block_end")))
        .run_trial(
            partial(
                run_trial,
                stim_bank=bank,
                trigger_runtime=triggers,
                block_id=block_name,
                block_idx=block_index,
            )
        )
        .to_dict(sink)
    )


def _show_screen(name, win, kb, bank, triggers, *, terminate=False):
    (
        StimUnit(name, win, kb, runtime=triggers)
        .add_stim(bank.get(name))
        .wait_and_continue(terminate=terminate)
    )


def _show_intention(block_type, win, kb, bank, triggers):
    name = f"{block_type}_instruction"
    (
        StimUnit(name, win, kb, runtime=triggers)
        .add_stim(bank.get(name))
        .wait_and_continue()
    )


def _show_distractor(settings, win, kb, bank, triggers):
    (
        StimUnit("embedded_figures_distractor", win, kb, runtime=triggers)
        .add_stim(bank.get("distractor_instruction"))
        .add_stim(bank.get("embedded_figures"))
        .show(
            duration=float(settings.distractor_duration),
            onset_trigger=settings.triggers.get("distractor"),
        )
    )


def run(options):
    root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa"}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(config)
        )
        win, kb = initialize_exp(settings)
        bank = StimBank(win, config["stim_config"]).preload_all()
        settings.save_to_json()
        triggers.send(settings.triggers.get("experiment_start"))

        _show_screen("instruction", win, kb, bank, triggers)
        seed = int(settings.random_seed)
        rows = []

        _run_block(
            block_name="practice",
            block_index=-1,
            plans=build_plans(
                root,
                block_type="baseline",
                count=int(settings.practice_trials),
                target_positions=[],
                seed=seed,
                block_index=-1,
                practice=True,
            ),
            settings=settings,
            win=win,
            kb=kb,
            bank=bank,
            triggers=triggers,
            sink=rows,
        )
        _show_screen("practice_summary", win, kb, bank, triggers)

        _run_block(
            block_name="baseline",
            block_index=0,
            plans=build_plans(
                root,
                block_type="baseline",
                count=int(settings.trials_per_block),
                target_positions=[],
                seed=seed,
                block_index=0,
            ),
            settings=settings,
            win=win,
            kb=kb,
            bank=bank,
            triggers=triggers,
            sink=rows,
        )
        _show_screen("baseline_complete", win, kb, bank, triggers)

        order = pm_order(subject.get("subject_id"), seed)
        target_positions = [int(value) for value in settings.target_positions]
        for order_index, block_type in enumerate(order, start=1):
            _show_intention(block_type, win, kb, bank, triggers)
            _show_distractor(settings, win, kb, bank, triggers)
            _run_block(
                block_name=block_type,
                block_index=order_index,
                plans=build_plans(
                    root,
                    block_type=block_type,
                    count=int(settings.trials_per_block),
                    target_positions=target_positions,
                    seed=seed,
                    block_index=order_index,
                ),
                settings=settings,
                win=win,
                kb=kb,
                bank=bank,
                triggers=triggers,
                sink=rows,
            )
            if order_index < len(order):
                _show_screen("interblock_break", win, kb, bank, triggers)

        results = summarize(rows)
        (
            StimUnit("good_bye", win, kb, runtime=triggers)
            .add_stim(
                bank.get_and_format(
                    "good_bye",
                    lexical_accuracy=f"{results['lexical_accuracy']:.1%}",
                    focal_pm=f"{results['focal_pm_accuracy']:.1%}",
                    nonfocal_pm=f"{results['nonfocal_pm_accuracy']:.1%}",
                )
            )
            .wait_and_continue(terminate=True)
        )

        triggers.send(settings.triggers.get("experiment_end"))
        pd.DataFrame(rows).to_csv(settings.res_file, index=False)
        triggers.close()
        core.quit()


def main():
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the classic event-based prospective memory task",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
