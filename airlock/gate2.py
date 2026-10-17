"""Gate 2: Authority check (outgoing tool call).

Insight: "Does this action trace back to something the user asked for, or only to the document?"
Grounded -> proceed; not grounded and confident -> deny; unsure -> ask the user.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Union
from airlock.schema import Gate2Result


def gate2(
    action: Union[str, Dict[str, Any]],
    user_request: str,
    doc_context: Optional[str] = None
) -> Gate2Result:
    """Verify whether an outgoing tool call action is authorized by the user's explicit request.

    Args:
        action: The requested tool call or action description / payload.
        user_request: The original instruction given by the human user.
        doc_context: Optional document / email body context that the agent was reading.

    Returns:
        Gate2Result with:
          - grounded: bool
          - confidence: float (0.0 - 1.0)
    """
    action_str = str(action).lower()
    user_lower = (user_request or "").lower()
    doc_lower = (doc_context or "").lower()

    if not action_str.strip():
        return {"grounded": True, "confidence": 1.0}

    # Extract salient tokens / action verbs from action
    action_tokens = set(re.findall(r"[a-zA-Z]{3,}", action_str))

    # Check alignment with user request
    user_tokens = set(re.findall(r"[a-zA-Z]{3,}", user_lower))
    doc_tokens = set(re.findall(r"[a-zA-Z]{3,}", doc_lower))

    # Ignore generic common stop words
    stop_words = {"the", "and", "for", "with", "that", "this", "from", "tool", "call", "name", "args", "arguments"}
    action_keywords = action_tokens - stop_words

    if not action_keywords:
        return {"grounded": True, "confidence": 0.8}

    overlap_user = len(action_keywords & user_tokens)
    overlap_doc = len(action_keywords & doc_tokens)

    # Check for dangerous unprompted exfiltration or write actions
    sensitive_verbs = {"send", "forward", "delete", "transfer", "exfiltrate", "write", "post"}
    action_has_sensitive = bool(action_keywords & sensitive_verbs)
    user_mentions_sensitive = bool(user_tokens & sensitive_verbs)

    if action_has_sensitive and not user_mentions_sensitive:
        # Sensitive action not mentioned in user request, possibly induced by doc
        confidence = 0.92 if overlap_doc > 0 else 0.85
        return {
            "grounded": False,
            "confidence": confidence,
        }

    if overlap_user > 0:
        return {
            "grounded": True,
            "confidence": min(1.0, 0.7 + 0.1 * overlap_user),
        }

    # If neither user nor doc clearly matches, confidence is low
    return {
        "grounded": False,
        "confidence": 0.55,
    }
