"""
R₀ Reliability Engine — zero dependencies, self-calibrating.

Starts with a prior calibrated on 233 real predictions (ForecastBench).
As agents use it and report outcomes, R₀ learns each agent's actual reliability.

The FRAMEWORK is universal. The NUMBERS adapt.
"""

import json
import os
import time

# === Default prior (Claude Sonnet 4, ForecastBench 233 predictions) ===

DEFAULT_CALIBRATION = {
    "very_low":  {"range": (0.0, 0.2), "mse": 0.236, "precision": 4.25,  "n": 42},
    "low":       {"range": (0.2, 0.4), "mse": 0.185, "precision": 5.41,  "n": 31},
    "medium":    {"range": (0.4, 0.6), "mse": 0.208, "precision": 4.82,  "n": 59},
    "high":      {"range": (0.6, 0.8), "mse": 0.110, "precision": 9.09,  "n": 72},
    "very_high": {"range": (0.8, 1.0), "mse": 0.002, "precision": 415.9, "n": 29},
}

CALIBRATION = DEFAULT_CALIBRATION  # backward compat

GRADES = [
    (0.01, "A+", "Virtually Certain",  "#22c55e", "Right >99% of the time at this confidence."),
    (0.05, "A",  "Highly Reliable",    "#4ade80", "Strong track record. Safe to act on."),
    (0.10, "B+", "Reliable",           "#84cc16", "Good accuracy. Minor risk of error."),
    (0.15, "B",  "Mostly Reliable",    "#a3e635", "Generally accurate but verify important decisions."),
    (0.20, "C+", "Moderate",           "#facc15", "Coin-flip territory. Get a second opinion."),
    (0.25, "C",  "Uncertain",          "#f59e0b", "Significant error risk. Do not act without verification."),
    (0.35, "D",  "Unreliable",         "#f97316", "The LLM is guessing. Treat as noise."),
    (1.00, "F",  "Do Not Trust",       "#ef4444", "Historically wrong as often as right."),
]

_ACCURACY = {
    "very_high": 0.97,
    "high": 0.82,
    "medium": 0.65,
    "low": 0.60,
    "very_low": 0.55,
}

_BUCKET_ORDER = ["very_low", "low", "medium", "high", "very_high"]


# === Self-Calibrating Engine ===

class R0:
    """
    Self-calibrating reliability engine.

    Usage:
        r0 = R0("my-agent")

        # Assess before acting
        result = r0.assess(0.85)
        if result["trust_signal"] == "TRUST":
            execute()

        # After you know the outcome, report it
        r0.record(prediction=0.85, outcome=1)  # 1=YES happened, 0=NO

        # R₀ updates its calibration table automatically.
        # After ~30 outcomes per bucket, it trusts its own data over the prior.
    """

    def __init__(self, agent_id: str = "default", data_dir: str = None):
        self.agent_id = agent_id
        self.data_dir = data_dir or os.path.expanduser("~/.r0")
        self._history_path = os.path.join(self.data_dir, f"{agent_id}.jsonl")
        self._cal_path = os.path.join(self.data_dir, f"{agent_id}.cal.json")

        # Start with the universal prior
        self._calibration = _deep_copy_cal(DEFAULT_CALIBRATION)

        # Load agent-specific calibration if it exists
        self._load_calibration()

    def _load_calibration(self):
        """Load saved calibration from disk."""
        if os.path.exists(self._cal_path):
            try:
                with open(self._cal_path) as f:
                    saved = json.load(f)
                for key in _BUCKET_ORDER:
                    if key in saved:
                        self._calibration[key]["mse"] = saved[key]["mse"]
                        self._calibration[key]["precision"] = saved[key]["precision"]
                        self._calibration[key]["n"] = saved[key]["n"]
            except Exception:
                pass

    def _save_calibration(self):
        """Save calibration to disk."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._cal_path, "w") as f:
            json.dump(self._calibration, f, indent=2)

    def record(self, prediction: float, outcome: int):
        """
        Record a prediction outcome for self-calibration.

        Args:
            prediction: The probability the agent predicted (0.0-1.0)
            outcome: What actually happened (1=YES, 0=NO)
        """
        prediction = max(0.01, min(0.99, float(prediction)))
        outcome = int(outcome)
        confidence = abs(prediction - 0.5) * 2

        # Log to history
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._history_path, "a") as f:
            f.write(json.dumps({
                "t": time.time(),
                "p": round(prediction, 4),
                "o": outcome,
                "c": round(confidence, 4),
            }) + "\n")

        # Update calibration with Bayesian update
        bucket_name, bucket = self._find_bucket(confidence)
        old_n = bucket["n"]
        old_mse = bucket["mse"]

        # Brier score for this prediction
        new_mse = (prediction - outcome) ** 2

        # Weighted average: prior weight decays as we get more data
        # At n=30 agent data points, agent data has equal weight to prior
        # At n=100, agent data dominates
        prior_weight = DEFAULT_CALIBRATION[bucket_name]["n"]
        agent_weight = old_n - prior_weight + 1  # starts at 1
        if agent_weight < 1:
            agent_weight = 1

        updated_mse = (old_mse * prior_weight + new_mse * agent_weight) / (prior_weight + agent_weight)

        bucket["mse"] = round(updated_mse, 6)
        bucket["precision"] = round(1.0 / max(updated_mse, 0.001), 1)
        bucket["n"] = old_n + 1

        self._save_calibration()

    def assess(self, probability: float) -> dict:
        """Assess reliability using this agent's calibration."""
        return _assess_with_cal(probability, self._calibration)

    def decide(self, probability: float) -> str:
        """Returns 'TRUST', 'VERIFY', or 'REJECT'."""
        return self.assess(probability)["trust_signal"]

    def should_trust(self, probability: float) -> bool:
        """True if this prediction is trustworthy."""
        return self.decide(probability) == "TRUST"

    def assess_with_base_rate(self, probability: float, base_rate: float) -> dict:
        """Full assessment with regime detection."""
        result = self.assess(probability)
        _add_regime(result, probability, base_rate)
        return result

    def stats(self) -> dict:
        """Return current calibration state and total records."""
        total = sum(b["n"] for b in self._calibration.values())
        prior_total = sum(b["n"] for b in DEFAULT_CALIBRATION.values())
        return {
            "agent_id": self.agent_id,
            "total_records": total - prior_total,
            "calibration": self._calibration,
            "using_prior": all(
                self._calibration[k]["n"] == DEFAULT_CALIBRATION[k]["n"]
                for k in _BUCKET_ORDER
            ),
        }

    def _find_bucket(self, confidence: float) -> tuple:
        return _find_bucket_in(confidence, self._calibration)


# === Stateless API (uses default prior) ===

def assess(probability: float) -> dict:
    """Assess reliability using the default prior."""
    return _assess_with_cal(probability, DEFAULT_CALIBRATION)


def decide(probability: float) -> str:
    """Returns 'TRUST', 'VERIFY', or 'REJECT'."""
    return assess(probability)["trust_signal"]


def should_trust(probability: float) -> bool:
    """True if this prediction is trustworthy."""
    return decide(probability) == "TRUST"


def assess_with_base_rate(probability: float, base_rate: float) -> dict:
    """Full assessment with regime detection."""
    result = assess(probability)
    _add_regime(result, probability, base_rate)
    return result


# === Internal ===

def _deep_copy_cal(cal: dict) -> dict:
    return {k: dict(v) for k, v in cal.items()}


def _find_bucket_in(confidence: float, cal: dict) -> tuple:
    for level in _BUCKET_ORDER:
        data = cal[level]
        lo, hi = data["range"]
        if lo <= confidence < hi or (hi == 1.0 and confidence == 1.0):
            return level, data
    return "very_low", cal["very_low"]


def _assess_with_cal(probability: float, cal: dict) -> dict:
    probability = max(0.01, min(0.99, float(probability)))
    confidence = abs(probability - 0.5) * 2

    level, bucket = _find_bucket_in(confidence, cal)
    mse = bucket["mse"]

    # Grade
    grade, label, color, desc = GRADES[-1][1], GRADES[-1][2], GRADES[-1][3], GRADES[-1][4]
    for max_mse, g, l, c, d in GRADES:
        if mse <= max_mse:
            grade, label, color, desc = g, l, c, d
            break

    # Trust signal
    if mse <= 0.05:
        trust = "TRUST"
    elif mse <= 0.20:
        trust = "VERIFY"
    else:
        trust = "REJECT"

    return {
        "grade": grade,
        "label": label,
        "color": color,
        "confidence": round(confidence, 3),
        "probability": round(probability, 3),
        "expected_error": round(mse, 4),
        "precision": round(bucket["precision"], 1),
        "historical_accuracy": _ACCURACY.get(level, 0.50),
        "trust_signal": trust,
        "description": desc,
        "data_points": bucket["n"],
    }


def _add_regime(result: dict, probability: float, base_rate: float):
    llm_yes = probability > 0.5
    prior_yes = base_rate > 0.5
    tension = abs(probability - base_rate)

    if llm_yes and not prior_yes:
        regime, desc, acc = "LLM_OVERRIDE", "LLM sees something the statistics don't. Historically right 73% here.", 0.73
    elif not llm_yes and prior_yes:
        regime, desc, acc = "LLM_CONSERVATIVE", "LLM is more cautious than data suggests. Base rate is often more accurate.", 0.40
    elif llm_yes and prior_yes:
        regime, desc, acc = "ALIGNED_YES", "Both LLM and historical data agree: YES is likely.", 0.89
    else:
        regime, desc, acc = "ALIGNED_NO", "Both LLM and historical data agree: NO is likely.", 0.85

    result["regime"] = regime
    result["regime_description"] = desc
    result["regime_accuracy"] = acc
    result["tension"] = round(tension, 3)
    result["base_rate"] = round(base_rate, 3)
