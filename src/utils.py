from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

FOCAL_TARGET = "PACKET"
NONFOCAL_TARGETS = ("DOCTOR", "FACTOR", "PASTOR", "TRACTOR")


class TrialPlan(str):
    def __new__(
        cls,
        *,
        condition_id: str,
        stimulus: str,
        lexicality: str,
        correct_key: str,
        block_type: str,
        pm_target: bool,
        cue_type: str,
        practice: bool,
        index: int,
    ):
        obj = str.__new__(cls, condition_id)
        obj.stimulus = str(stimulus)
        obj.lexicality = str(lexicality)
        obj.correct_key = str(correct_key)
        obj.block_type = str(block_type)
        obj.pm_target = bool(pm_target)
        obj.cue_type = str(cue_type)
        obj.practice = bool(practice)
        obj.index = int(index)
        return obj

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition": str(self),
            "condition_id": str(self),
            "stimulus": self.stimulus,
            "lexicality": self.lexicality,
            "correct_key": self.correct_key,
            "block_type": self.block_type,
            "pm_target": self.pm_target,
            "cue_type": self.cue_type,
            "is_practice": self.practice,
            "trial_index_in_block": self.index,
        }


def _load_pool(root: Path, phase: str) -> tuple[list[str], list[str]]:
    path = root / "assets" / "stimuli.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["phase"] == phase]
    words = [row["item"].strip().upper() for row in rows if row["lexicality"] == "word"]
    nonwords = [
        row["item"].strip().upper() for row in rows if row["lexicality"] == "nonword"
    ]
    if not words or not nonwords:
        raise ValueError(f"Stimulus pool is empty or invalid: {path}")
    if any("TOR" in word or word == FOCAL_TARGET for word in words):
        raise ValueError("Filler word pool must exclude PACKET and words containing TOR")
    return words, nonwords


def _condition_id(block_type: str, lexicality: str, pm_target: bool) -> str:
    if block_type == "baseline":
        return f"baseline_{lexicality}"
    if pm_target:
        return f"{block_type}_target"
    return f"{block_type}_{'filler_word' if lexicality == 'word' else 'nonword'}"


def pm_order(subject_id: Any, seed: int) -> tuple[str, str]:
    digits = "".join(character for character in str(subject_id) if character.isdigit())
    value = int(digits) if digits else int(seed)
    return ("focal", "nonfocal") if value % 2 else ("nonfocal", "focal")


def build_plans(
    root: Path,
    *,
    block_type: str,
    count: int,
    target_positions: list[int],
    seed: int,
    block_index: int,
    practice: bool = False,
) -> list[TrialPlan]:
    if block_type not in {"baseline", "focal", "nonfocal"}:
        raise ValueError(f"Unknown block type: {block_type}")
    count = int(count)
    if count < 2:
        raise ValueError("Each block requires at least two trials")
    positions = sorted({int(value) for value in target_positions})
    if any(value < 1 or value > count for value in positions):
        raise ValueError("Target positions must be one-based indices inside the block")
    if block_type == "baseline" and positions:
        raise ValueError("Baseline blocks cannot contain PM target positions")

    phase = "practice" if practice else "scored"
    words, nonwords = _load_pool(root, phase)
    rng = random.Random(int(seed) + int(block_index) * 1009 + (17 if practice else 71))

    target_count = len(positions)
    word_count = count // 2
    nonword_count = count - word_count
    filler_word_count = word_count - target_count
    if filler_word_count < 0:
        raise ValueError("Too many PM targets for the requested block length")
    if filler_word_count > len(words) or nonword_count > len(nonwords):
        raise ValueError("Stimulus pool does not contain enough unique fillers")

    selected_words = rng.sample(words, filler_word_count)
    selected_nonwords = rng.sample(nonwords, nonword_count)
    fillers = [
        {"stimulus": item, "lexicality": "word", "pm_target": False, "cue_type": "none"}
        for item in selected_words
    ] + [
        {
            "stimulus": item,
            "lexicality": "nonword",
            "pm_target": False,
            "cue_type": "none",
        }
        for item in selected_nonwords
    ]
    rng.shuffle(fillers)

    slots: list[dict[str, Any] | None] = [None] * count
    if block_type == "focal":
        target_items = [FOCAL_TARGET] * target_count
    elif block_type == "nonfocal":
        target_items = [
            NONFOCAL_TARGETS[index % len(NONFOCAL_TARGETS)]
            for index in range(target_count)
        ]
    else:
        target_items = []
    for position, target in zip(positions, target_items):
        slots[position - 1] = {
            "stimulus": target,
            "lexicality": "word",
            "pm_target": True,
            "cue_type": block_type,
        }
    filler_iter = iter(fillers)
    for index, record in enumerate(slots):
        if record is None:
            slots[index] = next(filler_iter)

    return [
        TrialPlan(
            condition_id=_condition_id(
                block_type, str(record["lexicality"]), bool(record["pm_target"])
            ),
            stimulus=str(record["stimulus"]),
            lexicality=str(record["lexicality"]),
            correct_key="j" if record["lexicality"] == "word" else "f",
            block_type=block_type,
            pm_target=bool(record["pm_target"]),
            cue_type=str(record["cue_type"]),
            practice=practice,
            index=index + 1,
        )
        for index, record in enumerate(slots)
        if record is not None
    ]


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    scored = [row for row in rows if not bool(row.get("is_practice"))]

    def rate(items: list[dict[str, Any]], field: str) -> float:
        return (
            sum(bool(item.get(field)) for item in items) / len(items)
            if items
            else 0.0
        )

    targets = [row for row in scored if bool(row.get("pm_target"))]
    focal = [row for row in targets if row.get("block_type") == "focal"]
    nonfocal = [row for row in targets if row.get("block_type") == "nonfocal"]
    return {
        "lexical_accuracy": rate(scored, "ongoing_correct"),
        "focal_pm_accuracy": rate(focal, "pm_hit"),
        "nonfocal_pm_accuracy": rate(nonfocal, "pm_hit"),
    }
