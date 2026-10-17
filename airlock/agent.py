"""Airlock Agent: AI Email Agent operating with Bedrock or local fallback."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from airlock.handler import AirlockPipeline


class EmailAgent:
    """Email assistant agent protected by Airlock dual gates."""

    def __init__(self, pipeline: Optional[AirlockPipeline] = None):
        self.pipeline = pipeline or AirlockPipeline()

    def process_email(self, user_request: str, email_content: str) -> Dict[str, Any]:
        """Process an email request under Airlock defense.

        1. Inspect incoming content through Gate 1.
        2. Deliver safe representation to agent logic.
        3. Intercept proposed tool calls through Gate 2.
        """
        route, agent_input, gate1_verdict = self.pipeline.inspect_incoming(email_content)

        # Proposed action generation (stubbed or LLM driven)
        if isinstance(agent_input, dict):
            # Agent only sees sanitized facts, cannot follow embedded raw prompt injections
            action = {
                "tool": "summarize_email",
                "args": {"summary": agent_input.get("summary", "")}
            }
        else:
            action = {
                "tool": "read_and_reply",
                "args": {"subject": "Re: Email", "body": "Noted."}
            }

        decision, gate2_verdict = self.pipeline.inspect_outgoing_action(
            action=action,
            user_request=user_request,
            doc_context=email_content
        )

        return {
            "route": route,
            "gate1": gate1_verdict,
            "action": action,
            "gate2": gate2_verdict,
            "decision": decision,
        }
