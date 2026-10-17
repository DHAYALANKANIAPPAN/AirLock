"""Gate 1: Addressee check (incoming content).

Insight: Instead of asking "is this text malicious?", ask "who is this text talking to?"
(a human reader vs the AI agent). Legit documents almost never address the AI.

Classification runs locally (e.g. Decider 2B model / local pipeline).
"""
from __future__ import annotations

from airlock.decider_client import DeciderClient
from airlock.schema import Gate1Label, Gate1Result

_default_decider_client = DeciderClient()


def gate1(text: str, model_path: Optional[str] = None) -> Gate1Result:
    """Classify incoming content to determine addressee and intent.

    Evaluates text using local Decider 2B decision model or calibrated local probes.

    Args:
        text: The incoming email / document text to inspect.
        model_path: Optional local Decider 2B model path or endpoint identifier.

    Returns:
        Gate1Result with:
          - label: "data" | "human_instruction" | "ai_instruction" | "unclear"
          - confidence: float (0.0 - 1.0)
          - tries_action: bool (tries to make an AI take an action)
          - claims_authority: bool (claims authority or false urgency)
    """
    if model_path:
        client = DeciderClient(endpoint_url=model_path)
        return client.evaluate(text)
    return _default_decider_client.evaluate(text)

