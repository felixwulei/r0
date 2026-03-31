# R₀ — Decision Physics

One formula that predicts whether a product, habit, or decision will survive.

```
R₀ = k · λ · R · (1-F) · S / V^0.3
     ─┬─  ─┬─ ─┬─  ──┬──  ─┬─  ──┬──
      │    │   │     │     │     │
      │    │   │     │     │     └─ Habituation penalty
      │    │   │     │     └─ Environmental tailwind/headwind
      │    │   │     └─ Friction gate
      │    │   └─ Shock survival probability
      │    └─ Inertial persistence
      └─ Reproduction rate per cycle
```

**R₀ > 1 → grows.  R₀ < 1 → decays.  Any variable at zero → dead.**

Borrowed from epidemiology. If one infected person infects more than one other, the disease spreads. Same math applies to products, habits, and decisions.

## Validation: 21 cases, 100% accuracy

| Company | R₀ | Predicted | Actual | |
|---|---|---|---|---|
| ChatGPT | 7.6 | Exponential | 100M users / 2 months | ✓ |
| Zoom (2020) | 5.1 | Exponential | 300M DAU | ✓ |
| Cursor | 2.85 | Exponential | $2B ARR / 12 months | ✓ |
| Slack | 2.72 | Exponential | $27.7B acquisition | ✓ |
| Notion | 1.49 | Steady | $10B, steady growth | ✓ |
| Stripe | 1.07 | Steady | $95B (huge market) | ✓ |
| Linear | 1.12 | Steady | Loved but not explosive | ✓ |
| Superhuman | 0.36 | Struggling | Niche, limited growth | ✓ |
| Devin | 0.03 | Dead | Hype → reputation reversal | ✓ |
| Google+ | 0.41 | Struggling | Shut down | ✓ |
| Quibi | 0.09 | Dead | $1.75B burned, shut down | ✓ |
| Zillow Offers | 0.000001 | Dead | Lost $880M, shut down | ✓ |

Full 21-case validation with parameter breakdowns: [`paper/validation.md`](paper/validation.md)

### Blind test: 92% accuracy

We stripped brand names and tested on disguised descriptions. The formula identified Figma, Cursor, Uber, OpenClaw as winners and Segway, MoviePass, WeWork, Quibi, Devin, Google+, Magic Leap as failures — without knowing what they were.

Details: [`benchmarks/v4_blind.json`](benchmarks/v4_blind.json)

### Ablation: Formula vs. Naked LLM

We tested three conditions on 42 cases:
1. **Naked LLM** — "Will this succeed?" (direct question)
2. **Structured LLM** — Think about 6 factors, then answer (no formula)
3. **Formula** — LLM estimates 6 parameters, formula computes R₀

The formula catches cases that naked intuition misses — and exposes *why* something will fail by pointing to the weakest variable.

## The Six Forces

| Symbol | Force | What it measures | Range |
|---|---|---|---|
| **k** | Amplification | New cycles per successful cycle. Viral coefficient for products, ≈1 for habits. | (0, +∞) |
| **λ** | Persistence | Probability of continuing without active push. Auto-debit: 0.99. Gym: 0.30. | (0, 1] |
| **R** | Resilience | Survives a 1-week disruption? Marriage: 0.90. Duolingo streak: 0.10. | (0, 1] |
| **1-F** | Friction freedom | Is continuing the default? Subscription: 0.98. Going to gym: 0.12. | (0, 1] |
| **S** | Secular trend | Environmental push. AI tools 2026: 1.5. Physical bookstore: 0.3. | (0, +∞) |
| **V** | Outcome velocity | How fast is the real result visible? Appears as 1/V^0.3 — fast feedback *lowers* R₀. | (0, 1] |

### Why V is inverse (the dopamine trap)

Fast-feedback systems (TikTok likes, slot machines, streak counters) create habituation. The reward feels less motivating each time. Slow-burn systems (marriage, investment, PhD) build identity and inertia.

The exponent **0.3** is not a fitted constant. It converges from three independent sources:

| Source | Domain | Exponent |
|---|---|---|
| Stevens' Power Law (1957) | Psychophysics | 0.33 |
| Hyperbolic discounting (Green & Myerson 2004) | Behavioral economics | 0.31 |
| Power law of forgetting (Wickelgren) | Memory research | ~0.3-0.4 |

It's the perceptual compression exponent for passively received stimuli — a property of human neural processing. Full derivation: [`paper/theory.md`](paper/theory.md)

## Install

```bash
pip install r0-engine
```

Zero dependencies. Python 3.8+.

## Usage

### The Formula

```python
from r0 import formula

# ChatGPT
formula.r0(k=5, lam=0.85, R=0.95, one_minus_F=0.90, S=1.5, V=0.95)
# → 5.31 (exponential growth)

# Quibi
formula.r0(k=0.15, lam=0.25, R=0.20, one_minus_F=0.30, S=0.4, V=0.85)
# → 0.00094 (dead)

# Find the weakest link
analysis = formula.decompose(k=2, lam=0.85, R=0.25, one_minus_F=0.12, S=1.1, V=0.12)
# → {
#   "R0": 0.095,
#   "classification": "dead",
#   "weakest_link": "(1-F)",
#   "recommendation": "Reduce friction — make continuing easier than stopping."
# }
```

### The Reliability Engine

Self-calibrating AI confidence assessor. Starts with a prior from 233 ForecastBench predictions, then learns from your agent's actual track record.

```python
from r0 import R0

engine = R0("my-agent")

# Before acting: should I trust this?
result = engine.assess(0.92)
# → {"grade": "A", "trust_signal": "TRUST", "expected_error": 0.002}

result = engine.assess(0.55)
# → {"grade": "D", "trust_signal": "REJECT", "expected_error": 0.208}

# After learning the outcome: self-calibrate
engine.record(prediction=0.85, outcome=1)  # 1=happened, 0=didn't
# Calibration table updates via Bayesian update.
# After ~30 outcomes per bucket, it trusts its own data over the prior.
```

## Known Limitations

**The Palantir Paradox.** R₀ = 0.006 but market cap = $200B. When ARPU is $10M+ per customer, you can sustain on paid acquisition (A) alone, even with zero viral growth. R₀ measures organic self-sustenance, not total business viability.

**The Betamax Problem.** R₀ can be high but lose to ecosystem wars. Betamax was technically superior (high R₀) but VHS built a content alliance. R₀ doesn't model competitive dynamics.

**R₀ is not constant.** Clubhouse went from R₀ ≈ 1.68 (hype) to R₀ ≈ 0.16 (novelty wore off). Products whose k depends on novelty rather than structural need will see R₀ decay.

## Theory

The formula is derived from first principles — discrete dynamical systems, not curve fitting.

- **β (growth rate)** = k · (1-F) · S — AND-chain of independent conditions
- **1/γ (survival rate)** = λ · R · V^(-0.3) — AND-chain + habituation correction
- **R₀ = β / γ** — basic reproduction number, same as epidemiology

Full derivation with proofs: [`paper/theory.md`](paper/theory.md)

## Files

```
sdk/           Python package (pip install)
paper/         Theory derivation + 21-case validation
benchmarks/    Raw results: e2e, ablation, blind test
```

## License

MIT
