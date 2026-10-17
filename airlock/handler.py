"""Airlock Handler: Orchestrates Gate 1, Sanitizer, Agent execution, and Gate 2."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
from airlock.gate1 import gate1
from airlock.gate2 import gate2
from airlock.sanitizer import sanitize
from airlock.schema import Gate1Result, Gate2Result, SanitizedDocument


class AirlockPipeline:
    """End-to-end defense pipeline for AI email agents."""

    def __init__(self, confidence_threshold: float = 0.80):
        self.confidence_threshold = confidence_threshold

    def inspect_incoming(self, doc_text: str) -> Tuple[str, Any, Gate1Result]:
        """Gate 1: Addressee check on incoming document.

        Returns:
            Tuple of (route, content_for_agent, gate1_verdict):
            - route: 'direct' | 'quarantine' | 'unsure'
            - content_for_agent: raw text if direct, or SanitizedDocument dict if quarantined/unsure
            - gate1_verdict: Gate1Result dict
        """
        verdict = gate1(doc_text)
        label = verdict["label"]
        confidence = verdict["confidence"]

        if label == "data" and confidence >= self.confidence_threshold:
            # Confident data -> agent reads raw text
            return "direct", doc_text, verdict
        elif label == "ai_instruction" and confidence >= self.confidence_threshold:
            # Confident AI-addressed -> quarantine
            sanitized = sanitize(doc_text)
            return "quarantine", sanitized, verdict
        else:
            # Unsure or borderline -> quarantine, log, risky actions need confirmation
            sanitized = sanitize(doc_text)
            return "unsure", sanitized, verdict

    def inspect_outgoing_action(
        self,
        action: Any,
        user_request: str,
        doc_context: Optional[str] = None
    ) -> Tuple[str, Gate2Result]:
        """Gate 2: Authority check on outgoing tool calls.

        Returns:
            Tuple of (decision, gate2_verdict):
            - decision: 'proceed' | 'deny' | 'confirm_with_user'
            - gate2_verdict: Gate2Result dict
        """
        verdict = gate2(action, user_request, doc_context)
        grounded = verdict["grounded"]
        confidence = verdict["confidence"]

        if grounded and confidence >= self.confidence_threshold:
            return "proceed", verdict
        elif (not grounded) and confidence >= self.confidence_threshold:
            return "deny", verdict
        else:
            return "confirm_with_user", verdict
