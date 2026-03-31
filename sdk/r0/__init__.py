"""
R₀ — Decision Physics Engine

Two things in one package:

1. **The Formula** — R₀ = k · λ · R · (1-F) · S / V^0.3
   Predicts whether any system (product, habit, business, decision) will grow or decay.
   Validated on 42+ real cases with 85-92% accuracy.

2. **The Reliability Engine** — Self-calibrating AI confidence assessor.
   Knows when to trust AI predictions, calibrated on 233 ForecastBench questions.

Usage:
    # The Formula
    from r0 import formula
    result = formula.r0(k=5, lam=0.85, R=0.95, one_minus_F=0.90, S=1.5, V=0.95)
    # → 5.31 (ChatGPT-level explosive growth)

    analysis = formula.decompose(k=1, lam=0.30, R=0.25, one_minus_F=0.12, S=1.1, V=0.12)
    # → R₀=0.016, classification='dead', weakest_link='(1-F)'

    # The Reliability Engine
    from r0 import assess, decide, R0

    r = assess(0.85)
    print(r["grade"])         # "B"
    print(r["trust_signal"])  # "VERIFY"

    action = decide(0.85)     # "VERIFY"
"""

from r0.engine import (
    R0,
    assess,
    decide,
    should_trust,
    assess_with_base_rate,
    CALIBRATION,
    GRADES,
)

from r0 import formula

__version__ = "0.1.0"
__all__ = [
    "formula",
    "R0",
    "assess",
    "decide",
    "should_trust",
    "assess_with_base_rate",
    "CALIBRATION",
    "GRADES",
]
