"""
R₀ Decision Formula v4

    R₀ = k · λ · R · (1-F) · S / V^0.3

Six forces that determine whether a system grows or decays.
Products, habits, businesses, historical decisions — same formula.

R₀ > 1 = grows. R₀ < 1 = decays. Any variable at zero kills it.
"""


def r0(k: float, lam: float, R: float, one_minus_F: float, S: float, V: float, alpha: float = 0.3) -> float:
    """
    Compute R₀ — the basic reproduction number of any decision/system.

    Args:
        k:           Amplification — new cycles per successful cycle.
                     Products: viral coefficient (ChatGPT ≈ 5, Clubhouse ≈ 0.3).
                     Habits: usually ≈ 1.
        lam:         Persistence (λ) — probability of continuing without active push.
                     Auto-debit ≈ 0.99, gym ≈ 0.30, New Year's resolution ≈ 0.08.
        R:           Resilience — probability of surviving a 1-week disruption.
                     Marriage ≈ 0.90, exercise habit ≈ 0.25, Duolingo streak ≈ 0.10.
        one_minus_F: Friction freedom (1-F) — is continuing the default?
                     Subscription ≈ 0.98, going to gym ≈ 0.12, quitting smoking ≈ 0.04.
        S:           Secular trend — environmental tailwind (>1) or headwind (<1).
                     AI tools 2026 ≈ 1.5, physical bookstore ≈ 0.3.
        V:           Outcome velocity — how fast is the real result perceptible?
                     ChatGPT answer ≈ 0.95, weight loss ≈ 0.15, PhD value ≈ 0.02.
                     INVERSE: fast feedback slightly lowers R₀ (dopamine trap).
        alpha:       Habituation exponent (default 0.3).
                     Derived from Stevens' Power Law (0.33), hyperbolic discounting (0.31),
                     and forgetting power law (~0.3-0.4). Not a fitted constant —
                     it's the perceptual compression exponent for passively received stimuli.

    Returns:
        R₀ value. > 1 = self-sustaining growth, < 1 = decay.

    Examples:
        >>> r0(k=5, lam=0.85, R=0.95, one_minus_F=0.90, S=1.5, V=0.95)  # ChatGPT
        5.31
        >>> r0(k=0.15, lam=0.25, R=0.20, one_minus_F=0.30, S=0.4, V=0.85)  # Quibi
        0.00094
        >>> r0(k=1, lam=0.99, R=0.99, one_minus_F=0.98, S=1.1, V=0.04)  # Auto-invest
        2.78
    """
    if V <= 0:
        raise ValueError("V must be > 0")
    return k * lam * R * one_minus_F * S / (V ** alpha)


def classify(r0_value: float) -> str:
    """
    Classify an R₀ value into growth regime.

    Returns one of:
        'exponential'  — R₀ > 2: explosive growth, no sales team needed
        'linear'       — 1 < R₀ ≤ 2: steady growth, some sales helps
        'struggling'   — 0.1 < R₀ ≤ 1: needs paid acquisition to survive
        'dead'         — R₀ ≤ 0.1: almost certainly fails
    """
    if r0_value > 2:
        return "exponential"
    elif r0_value > 1:
        return "linear"
    elif r0_value > 0.1:
        return "struggling"
    else:
        return "dead"


def decompose(k: float, lam: float, R: float, one_minus_F: float, S: float, V: float, alpha: float = 0.3) -> dict:
    """
    Compute R₀ and show the contribution of each force.

    Returns a dict with R₀, classification, and the weakest link.
    """
    r0_value = r0(k, lam, R, one_minus_F, S, V, alpha)

    forces = {
        "k (amplification)": k,
        "λ (persistence)": lam,
        "R (resilience)": R,
        "(1-F) (friction freedom)": one_minus_F,
        "S (secular trend)": S,
        "1/V^α (habituation)": 1 / (V ** alpha),
    }

    # Find weakest link (lowest contribution, excluding S and 1/V^α which can be > 1)
    bounded_forces = {
        "k": k,
        "λ": lam,
        "R": R,
        "(1-F)": one_minus_F,
    }
    weakest = min(bounded_forces, key=bounded_forces.get)

    return {
        "R0": round(r0_value, 4),
        "classification": classify(r0_value),
        "forces": {name: round(val, 4) for name, val in forces.items()},
        "weakest_link": weakest,
        "recommendation": _recommendation(weakest, bounded_forces[weakest]),
    }


def _recommendation(weakest: str, value: float) -> str:
    recs = {
        "k": "Increase viral coefficient — make the product naturally spread through usage.",
        "λ": "Increase persistence — automate, create defaults, reduce need for re-decision.",
        "(1-F)": "Reduce friction — make continuing easier than stopping.",
        "R": "Increase resilience — ensure the system survives disruptions and bad weeks.",
    }
    return recs.get(weakest, "")
