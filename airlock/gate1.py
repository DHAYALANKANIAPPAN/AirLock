"""Gate 1: Addressee check (incoming content).

Insight: Instead of asking "is this text malicious?", ask "who is this text talking to?"
(a human reader vs the AI agent). Legit documents almost never address the AI.

Classification runs locally (e.g. Decider 2B model / local pipeline).
"""
from __future__ import annotations

import re
from typing import Optional
from airlock.schema import Gate1Result, Gate1Label


def gate1(text: str, model_path: Optional[str] = None) -> Gate1Result:
    """Classify incoming content to determine addressee and intent.

    Args:
        text: The incoming email / document text to inspect.
        model_path: Optional local Decider 2B model path or identifier.

    Returns:
        Gate1Result with:
          - label: "data" | "human_instruction" | "ai_instruction" | "unclear"
          - confidence: float (0.0 - 1.0)
          - tries_action: bool (tries to make an AI take an action)
          - claims_authority: bool (claims authority or false urgency)
    """
    if not text or not text.strip():
        return {
            "label": "data",
            "confidence": 1.0,
            "tries_action": False,
            "claims_authority": False,
        }

    # Baseline addressee and instruction heuristic detector
    # (can be backed by local Decider 2B weights when loaded)
    ai_patterns = [
        r"(?:ignore|disregard|override|forget)\s+(?:previous|all|prior)\s+(?:instructions|rules|prompts)",
        r"(?:system\s+prompt|system\s+message|assistant\s+directive|developer\s+mode)",
        r"(?:you\s+must|you\s+are\s+instructed\s+to|as\s+an\s+ai|assistant\s+must)\s+(?:send|forward|delete|fetch|execute|exfiltrate|browse)",
        r"<\s*(?:system|instruction|prompt)\s*>",
        r"(?:print|output|return)\s+(?:the\s+following|password|api\s+key|token|credentials)",
    ]

    action_patterns = [
        r"(?:send|forward|post|delete|drop|execute|curl|wget|fetch|transfer|write_to|run_command)",
        r"(?:email|message)\s+(?:all|everyone|to\s+external)",
    ]

    authority_patterns = [
        r"(?:immediate\s+action\s+required|urgent|ceo\s+directive|system\s+administrator|high\s+priority|do\s+not\s+verify)",
        r"(?:authorized\s+by|security\s+override|under\s+penalty\s+of)",
    ]

    human_patterns = [
        r"(?:please\s+find\s+attached|hope\s+you\s+are\s+well|best\s+regards|sincerely|hi\s+[a-z]+|dear\s+[a-z]+)",
        r"(?:can\s+we\s+meet|let\s+me\s+know\s+your\s+thoughts|please\s+review\s+the\s+deck|see\s+the\s+notes)",
    ]

    text_lower = text.lower()

    ai_hits = any(re.search(pat, text_lower) for pat in ai_patterns)
    action_hits = any(re.search(pat, text_lower) for pat in action_patterns)
    auth_hits = any(re.search(pat, text_lower) for pat in authority_patterns)
    human_hits = any(re.search(pat, text_lower) for pat in human_patterns)

    if ai_hits:
        label: Gate1Label = "ai_instruction"
        confidence = 0.95
    elif human_hits and not action_hits:
        label = "human_instruction"
        confidence = 0.88
    elif not ai_hits and not action_hits and not auth_hits:
        label = "data"
        confidence = 0.90
    else:
        label = "unclear"
        confidence = 0.50

    return {
        "label": label,
        "confidence": confidence,
        "tries_action": bool(action_hits),
        "claims_authority": bool(auth_hits),
    }
