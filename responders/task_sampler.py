from __future__ import annotations

from psyflow.sim.contracts import Action


class TaskSamplerResponder:
    def __init__(
        self,
        lexical_accuracy=0.94,
        focal_detection=0.90,
        nonfocal_detection=0.70,
        false_alarm_rate=0.01,
        lexical_rt_s=0.55,
        waiting_rt_s=0.35,
    ):
        self.lexical_accuracy = float(lexical_accuracy)
        self.focal_detection = float(focal_detection)
        self.nonfocal_detection = float(nonfocal_detection)
        self.false_alarm_rate = float(false_alarm_rate)
        self.lexical_rt_s = float(lexical_rt_s)
        self.waiting_rt_s = float(waiting_rt_s)
        self.rng = None

    def start_session(self, session, rng):
        self.rng = rng

    def on_feedback(self, feedback):
        pass

    def end_session(self):
        pass

    def _draw(self):
        return self.rng.random() if self.rng else 0.0

    def act(self, observation):
        keys = [str(key) for key in (observation.valid_keys or [])]
        if not keys:
            return Action(key=None, rt_s=None)
        if keys == ["space"] or ("space" in keys and len(keys) == 1):
            return Action(key="space", rt_s=0.02)

        factors = dict(getattr(observation, "task_factors", {}) or {})
        stage = str(factors.get("stage", getattr(observation, "phase", "")))
        if stage == "lexical_decision":
            correct_key = str(factors.get("correct_key", keys[0]))
            if self._draw() <= self.lexical_accuracy:
                response = correct_key
            else:
                response = next((key for key in keys if key != correct_key), keys[0])
            return Action(key=response, rt_s=self.lexical_rt_s)

        if stage == "waiting":
            pm_target = bool(factors.get("pm_target"))
            block_type = str(factors.get("block_type", "baseline"))
            if pm_target and block_type == "focal":
                use_pm = self._draw() <= self.focal_detection
            elif pm_target and block_type == "nonfocal":
                use_pm = self._draw() <= self.nonfocal_detection
            else:
                use_pm = self._draw() <= self.false_alarm_rate
            return Action(
                key="slash" if use_pm and "slash" in keys else "space",
                rt_s=self.waiting_rt_s,
            )

        return Action(key=keys[0], rt_s=0.02)
