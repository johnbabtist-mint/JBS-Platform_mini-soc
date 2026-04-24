"""
JBS Mini-SOC — deterministic policy decision example

This is a simplified public code sample. It demonstrates the decision style:
deterministic rules first, explainable output, and no dependency on raw LLM
judgement for enforcement decisions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AttackSourceSignal:
    ip: str
    failed_logins: int
    invalid_user_events: int
    already_blocked: bool
    trusted_source: bool
    geoip_country: str | None = None
    asn: str | None = None
    provider: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    target: str
    decision: str
    severity: str
    confidence: str
    rationale: list[str]
    recommended_action: str


def decide_attack_source(signal: AttackSourceSignal) -> PolicyDecision:
    rationale: list[str] = []

    if signal.trusted_source:
        return PolicyDecision(
            target=signal.ip,
            decision="IGNORE",
            severity="LOW",
            confidence="HIGH",
            rationale=["Source is marked as trusted."],
            recommended_action="No action required.",
        )

    if signal.already_blocked:
        return PolicyDecision(
            target=signal.ip,
            decision="IGNORE",
            severity="MEDIUM",
            confidence="HIGH",
            rationale=["Source is already blocked by an existing control."],
            recommended_action="Keep existing block and monitor.",
        )

    if signal.failed_logins >= 20 or signal.invalid_user_events >= 10:
        rationale.append("High authentication failure volume.")
        if signal.asn:
            rationale.append(f"ASN context available: {signal.asn}.")
        if signal.provider:
            rationale.append(f"Provider context available: {signal.provider}.")

        return PolicyDecision(
            target=signal.ip,
            decision="BLOCK",
            severity="HIGH",
            confidence="HIGH",
            rationale=rationale,
            recommended_action="Block source and continue monitoring.",
        )

    if signal.failed_logins >= 5:
        return PolicyDecision(
            target=signal.ip,
            decision="INVESTIGATE",
            severity="MEDIUM",
            confidence="MEDIUM",
            rationale=["Repeated authentication failures detected."],
            recommended_action="Review trace context before enforcement.",
        )

    return PolicyDecision(
        target=signal.ip,
        decision="MONITOR",
        severity="LOW",
        confidence="MEDIUM",
        rationale=["Low signal volume; keep observing."],
        recommended_action="No immediate enforcement.",
    )


if __name__ == "__main__":
    sample = AttackSourceSignal(
        ip="203.0.113.42",
        failed_logins=24,
        invalid_user_events=12,
        already_blocked=False,
        trusted_source=False,
        geoip_country="Example Country",
        asn="AS64500",
        provider="Example Provider",
    )

    print(decide_attack_source(sample))
