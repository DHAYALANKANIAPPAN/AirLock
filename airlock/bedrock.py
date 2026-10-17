"""Thin Bedrock Converse wrapper. Raises BedrockError on any failure."""
from __future__ import annotations

import os
from typing import Any, Optional


class BedrockError(RuntimeError):
    pass


def model_id(explicit: Optional[str] = None) -> str:
    mid = explicit or os.environ.get("AIRLOCK_MODEL_ID")
    if not mid:
        raise BedrockError("Set AIRLOCK_MODEL_ID to a Bedrock model/inference-profile ID "
                           "you have access to.")
    return mid


def get_client(region: Optional[str] = None) -> Any:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as e:
        raise BedrockError("boto3 not installed: pip install boto3") from e
    cfg = Config(retries={"max_attempts": 3, "mode": "standard"}, read_timeout=60)
    return boto3.client("bedrock-runtime", config=cfg,
                        region_name=region or os.environ.get("AWS_REGION", "us-east-1"))


def converse(system: str, user: str, *, client: Any = None, model: Optional[str] = None,
             max_tokens: int = 1024, temperature: float = 0.0) -> str:
    """Single tool-less call; returns the model's text."""
    try:
        client = client or get_client()
        resp = client.converse(
            modelId=model_id(model),
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": user}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )
        return "".join(p.get("text", "") for p in resp["output"]["message"]["content"])
    except BedrockError:
        raise
    except Exception as e:  # ClientError, BotoCoreError, malformed response
        raise BedrockError(f"Bedrock call failed: {type(e).__name__}: {e}") from e
