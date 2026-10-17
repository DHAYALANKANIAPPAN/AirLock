# Airlock Evaluation Datasets

This directory contains evaluation datasets for measuring Gate 1 and Gate 2 defense performance.

## Schema
Every row is a JSON object with the following fields:
```json
{
  "id": "dev-001",
  "text": "Meeting notes from Tuesday...",
  "label": "benign",
  "attack_type": null,
  "split": "dev"
}
```

### Fields
- **id** (`str`): Unique identifier (e.g., `dev-001`, `test-042`).
- **text** (`str`): Incoming email or document content.
- **label** (`"attack" | "tricky_benign" | "benign"`):
  - `attack`: Text containing prompt injections, jailbreaks, or unauthorized directives aimed at the AI agent.
  - `tricky_benign`: Benign human-to-human instructions, urgent requests, forwarded chains, or text mentioning keywords like "AI", "instructions", or "action required" without targeting the agent.
  - `benign`: Plain data, reports, invoices, calendar invites, or neutral correspondence.
- **attack_type** (`str` or `null`): Subcategory of attack (e.g. `direct_override`, `data_exfiltration`, `authority_spoofing`, `indirect_injection`, or `null`).
- **split** (`"dev" | "test"`): Target split.

## Guidelines
- Numbers must only be generated via evaluation scripts (`eval/run_all.py`), never hand-typed.
- All evaluation claims are categorized as *measured*, *planned*, or *hypothesis*.
