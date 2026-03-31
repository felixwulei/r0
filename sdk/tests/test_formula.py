"""
Tests for R₀ formula and reliability engine.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from r0.formula import r0, classify, decompose


# === Formula correctness ===

def test_chatgpt():
    """ChatGPT should be exponential (R₀ > 2)."""
    result = r0(k=5, lam=0.85, R=0.95, one_minus_F=0.90, S=1.5, V=0.95)
    assert result > 2, f"ChatGPT R₀={result}, expected > 2"
    assert classify(result) == "exponential"


def test_quibi():
    """Quibi should be dead (R₀ << 1)."""
    result = r0(k=0.15, lam=0.25, R=0.20, one_minus_F=0.30, S=0.4, V=0.85)
    assert result < 0.01, f"Quibi R₀={result}, expected < 0.01"
    assert classify(result) == "dead"


def test_notion():
    """Notion should be steady growth (1 < R₀ < 2)."""
    result = r0(k=2.5, lam=0.75, R=0.80, one_minus_F=0.70, S=1.2, V=0.25)
    assert 1 < result < 2, f"Notion R₀={result}, expected 1-2"
    assert classify(result) == "linear"


def test_auto_invest():
    """Auto-invest habit should be self-sustaining (R₀ > 1)."""
    result = r0(k=1, lam=0.99, R=0.99, one_minus_F=0.98, S=1.1, V=0.04)
    assert result > 1, f"Auto-invest R₀={result}, expected > 1"


def test_gym_habit():
    """Gym habit should decay (R₀ < 1)."""
    result = r0(k=1, lam=0.30, R=0.25, one_minus_F=0.12, S=1.1, V=0.12)
    assert result < 1, f"Gym R₀={result}, expected < 1"


# === Formula properties ===

def test_zero_kills():
    """Any variable at zero should produce R₀ = 0."""
    assert r0(k=0, lam=0.5, R=0.5, one_minus_F=0.5, S=1.0, V=0.5) == 0
    assert r0(k=1, lam=0, R=0.5, one_minus_F=0.5, S=1.0, V=0.5) == 0
    assert r0(k=1, lam=0.5, R=0, one_minus_F=0.5, S=1.0, V=0.5) == 0
    assert r0(k=1, lam=0.5, R=0.5, one_minus_F=0, S=1.0, V=0.5) == 0
    assert r0(k=1, lam=0.5, R=0.5, one_minus_F=0.5, S=0, V=0.5) == 0


def test_v_inverse():
    """Higher V should produce lower R₀ (all else equal)."""
    r0_slow = r0(k=2, lam=0.5, R=0.5, one_minus_F=0.5, S=1.0, V=0.1)
    r0_fast = r0(k=2, lam=0.5, R=0.5, one_minus_F=0.5, S=1.0, V=0.9)
    assert r0_slow > r0_fast, "Slow feedback should produce higher R₀"


def test_monotonic_in_each_variable():
    """R₀ should increase when any growth variable increases."""
    base = dict(k=1, lam=0.5, R=0.5, one_minus_F=0.5, S=1.0, V=0.5)
    base_r0 = r0(**base)

    for var in ['k', 'lam', 'R', 'one_minus_F', 'S']:
        higher = {**base, var: base[var] * 1.5}
        assert r0(**higher) > base_r0, f"R₀ should increase with higher {var}"


def test_v_raises_on_zero():
    """V=0 should raise ValueError (division by zero)."""
    try:
        r0(k=1, lam=0.5, R=0.5, one_minus_F=0.5, S=1.0, V=0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# === Classification ===

def test_classify_thresholds():
    assert classify(3.0) == "exponential"
    assert classify(1.5) == "linear"
    assert classify(0.5) == "struggling"
    assert classify(0.05) == "dead"


# === Decompose ===

def test_decompose_finds_weakest():
    """Decompose should identify the weakest link."""
    result = decompose(k=5, lam=0.85, R=0.25, one_minus_F=0.90, S=1.5, V=0.95)
    assert result["weakest_link"] == "R", f"Expected R as weakest, got {result['weakest_link']}"

    result2 = decompose(k=5, lam=0.85, R=0.90, one_minus_F=0.05, S=1.5, V=0.95)
    assert result2["weakest_link"] == "(1-F)"


# === Reliability engine ===

def test_engine_assess():
    from r0.engine import assess, decide
    result = assess(0.92)
    assert "grade" in result
    assert "trust_signal" in result
    assert result["trust_signal"] in ("TRUST", "VERIFY", "REJECT")


def test_engine_high_confidence_trusts():
    from r0.engine import decide
    assert decide(0.95) == "TRUST"


def test_engine_low_confidence_rejects():
    from r0.engine import decide
    assert decide(0.52) == "REJECT"


# === Run all tests ===

if __name__ == "__main__":
    test_functions = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for fn in test_functions:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
