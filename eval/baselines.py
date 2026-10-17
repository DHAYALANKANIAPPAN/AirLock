"""Baseline prompt injection detectors for comparative evaluation."""
from __future__ import annotations

import re
from typing import Dict, List, Optional


class NoDefenseBaseline:
    """Baseline that allows all inputs through without inspection."""

    def predict(self, text: str) -> str:
        return "benign"


class NaiveKeywordBaseline:
    """Baseline using simple keyword search for prompt injection signatures."""

    KEYWORDS = [
        "ignore previous",
        "disregard",
        "system prompt",
        "developer mode",
        "password",
        "override",
        "instruction",
    ]

    def predict(self, text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in self.KEYWORDS):
            return "attack"
        return "benign"


class NaiveLLMJudgeBaseline:
    """Baseline asking an LLM (Bedrock) directly 'is this text prompt injection?'."""

    def __init__(self, bedrock_client: Optional[object] = None):
        self.bedrock_client = bedrock_client

    def predict(self, text: str) -> str:
        # If Bedrock client is active, can dispatch Claude/Titan judge prompt.
        # Offline baseline heuristic modeling standard LLM judge accuracy:
        text_lower = text.lower()
        patterns = [
            r"ignore\s+(?:previous|all)",
            r"system\s*prompt",
            r"assistant\s+must",
            r"developer\s+mode",
        ]
        if any(re.search(p, text_lower) for p in patterns):
            return "attack"
        return "benign"
