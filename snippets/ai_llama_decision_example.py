"""
JBS Mini-SOC — local Llama/Ollama decision example

This public sample demonstrates a safe pattern for using a local LLM as an
assistant around deterministic security signals.

It intentionally does NOT include:
- production prompts,
- private runtime data,
- real logs,
- GeoIP databases,
- firewall state,
- secrets,
- full JBS Platform application code.

The example works without Ollama. If Ollama is not reachable, it falls back to
a deterministic local decision so public validation can run anywhere.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SecuritySignal:
    ip: str
    failed_logins: int
    invalid_user_events: int
    already_blocked: bool
    trusted_source: bool
    country: str = "Example Country"
    asn: str = "AS64500"
    provider: str = "Example Provider"


@dataclass(frozen=True)
class AIDecision:
    decision: str
    confidence: str
    reason_code: str
    recommended_action: str
    explanation: str
    model_used: str
    source: str


def deterministic_policy(signal: SecuritySignal) -> AIDecision:
    """Small deterministic safety layer used before or instead of an LLM."""

    if signal.trusted_source:
        return AIDecision(
            decision="IGNORE",
            confidence="HIGH",
            reason_code="trusted_source",
            recommended_action="Do not block. Keep source on trusted list.",
            explanation="The source is explicitly trusted by local policy.",
            model_used="deterministic-policy",
            source="local",
        )

    if signal.already_blocked:
        return AIDecision(
            decision="IGNORE",
            confidence="HIGH",
            reason_code="already_blocked",
            recommended_action="No new action required. Continue monitoring.",
            explanation="The source is already blocked by operational controls.",
            model_used="deterministic-policy",
            source="local",
        )

    if signal.failed_logins >= 20 or signal.invalid_user_events >= 10:
        return AIDecision(
            decision="BLOCK",
            confidence="HIGH",
            reason_code="high_auth_failure_volume",
            recommended_action="Block source and continue monitoring.",
            explanation="Authentication failure volume exceeds the public sample threshold.",
            model_used="deterministic-policy",
            source="local",
        )

    return AIDecision(
        decision="MONITOR",
        confidence="MEDIUM",
        reason_code="low_signal",
        recommended_action="Do not block yet. Keep source visible for analyst review.",
        explanation="The signal is present but below the public sample block threshold.",
        model_used="deterministic-policy",
        source="local",
    )


def build_llama_prompt(signal: SecuritySignal, policy_decision: AIDecision) -> str:
    """Build a sanitized prompt using only synthetic/public-safe fields."""

    return f"""
You are a security analyst assistant for a Mini-SOC demo.

Analyze this sanitized security signal and explain the operational decision.

Signal:
{json.dumps(asdict(signal), indent=2)}

Deterministic policy decision:
{json.dumps(asdict(policy_decision), indent=2)}

Rules:
- Do not invent private evidence.
- Do not claim firewall action was executed.
- Keep the explanation short.
- Respect the deterministic policy decision.
""".strip()


def call_ollama(prompt: str) -> tuple[str, str]:
    """
    Call local Ollama using the standard /api/generate endpoint.

    Defaults:
    - OLLAMA_URL=http://127.0.0.1:11434
    - OLLAMA_MODEL=llama3.2:1b
    """

    ollama_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 180,
        },
    }

    request = urllib.request.Request(
        f"{ollama_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))

    return model, str(data.get("response", "")).strip()


def decide_with_optional_llama(signal: SecuritySignal) -> AIDecision:
    """
    Use deterministic policy first, then optionally ask local Llama for a short
    analyst explanation. If Ollama is unavailable, return the deterministic result.
    """

    policy_decision = deterministic_policy(signal)
    prompt = build_llama_prompt(signal, policy_decision)

    try:
        model, explanation = call_ollama(prompt)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return policy_decision

    if not explanation:
        return policy_decision

    return AIDecision(
        decision=policy_decision.decision,
        confidence=policy_decision.confidence,
        reason_code=policy_decision.reason_code,
        recommended_action=policy_decision.recommended_action,
        explanation=explanation,
        model_used=model,
        source="ollama",
    )


if __name__ == "__main__":
    sample_signal = SecuritySignal(
        ip="203.0.113.42",
        failed_logins=24,
        invalid_user_events=12,
        already_blocked=False,
        trusted_source=False,
    )

    decision = decide_with_optional_llama(sample_signal)
    print(json.dumps(asdict(decision), indent=2))
