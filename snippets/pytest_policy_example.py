"""
JBS Mini-SOC — pytest example

This public sample demonstrates how deterministic policy decisions can be tested
without exposing private production data or operational artifacts.
"""

from policy_decision_example import AttackSourceSignal, decide_attack_source


def test_trusted_source_is_ignored():
    signal = AttackSourceSignal(
        ip="203.0.113.10",
        failed_logins=100,
        invalid_user_events=50,
        already_blocked=False,
        trusted_source=True,
    )

    decision = decide_attack_source(signal)

    assert decision.decision == "IGNORE"
    assert decision.confidence == "HIGH"
    assert "trusted" in " ".join(decision.rationale).lower()


def test_high_auth_failure_source_is_blocked():
    signal = AttackSourceSignal(
        ip="203.0.113.42",
        failed_logins=24,
        invalid_user_events=12,
        already_blocked=False,
        trusted_source=False,
        asn="AS64500",
        provider="Example Provider",
    )

    decision = decide_attack_source(signal)

    assert decision.decision == "BLOCK"
    assert decision.severity == "HIGH"
    assert decision.recommended_action == "Block source and continue monitoring."


def test_low_signal_source_is_monitored():
    signal = AttackSourceSignal(
        ip="203.0.113.77",
        failed_logins=1,
        invalid_user_events=0,
        already_blocked=False,
        trusted_source=False,
    )

    decision = decide_attack_source(signal)

    assert decision.decision == "MONITOR"
    assert decision.severity == "LOW"
