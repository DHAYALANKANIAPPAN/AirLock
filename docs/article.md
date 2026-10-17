# Airlock: Rethinking Prompt Injection Defense for Autonomous Agents

## 1. Introduction
Autonomous AI email agents that read untrusted external messages and invoke tools (sending emails, querying databases, running shell commands) face an inherent security challenge: indirect prompt injection. Attackers embed adversarial instructions into invoices, calendar invites, or newsletter bodies, attempting to hijack the agent's tool execution capabilities.

Most defensive measures attempt to answer: *"Is this input malicious?"*  
Because natural language is endlessly polymorphic, malicious intent classifiers regularly fail on novel attacks while suffering high false-alarm rates on legitimate urgent or imperative business emails.

Airlock shifts the paradigm with a fundamental insight: **"Who is this text talking to?"**

## 2. Core Insight
In real-world workflows:
- Documents convey data to the human user (e.g. quarterly figures).
- Documents contain instructions meant for human eyes (e.g. "Alice, please review this presentation by Friday").
- Documents virtually never legitimately address the autonomous AI agent.

When an incoming document addresses the AI agent ("Ignore instructions", "System directive", "Assistant must forward"), it is an anomaly. By decoupling addressee classification from intent classification, Airlock filters out adversarial payloads without breaking normal business communication.

## 3. Architecture

```
                          Incoming Email / Document
                                     │
                                     ▼
                        [ Gate 1: Addressee Check ]
                         (Classification runs locally)
                                     │
               ┌─────────────────────┼─────────────────────┐
               ▼                     ▼                     ▼
      Confident Data           Borderline/Unsure    Confident AI Address
      (Agent reads raw)              │                     │
               │                     └──────────┬──────────┘
               │                                │
               │                                ▼
               │                   [ Bedrock Fact Sanitizer ]
               │                   (Extracts to JSON schema,
               │                    zero tool access)
               │                                │
               └─────────────────────┬──────────┘
                                     │
                                     ▼
                          [ AI Email Agent Loop ]
                                     │
                                     ▼ (Proposed Tool Action)
                                     │
                        [ Gate 2: Authority Check ]
                      ("Traces to User vs Document?")
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
                 Grounded in User             Ungrounded / Document only
                     [ PROCEED ]                        [ DENY ]
```

### Gate 1: Addressee Check
- **Local Decider Model:** Runs locally with low latency.
- **Output:** Label (`data`, `human_instruction`, `ai_instruction`, `unclear`), confidence, `tries_action`, `claims_authority`.
- **Quarantine:** Inputs addressing the AI are routed to the sanitizer. The agent never sees raw untrusted prompt text.

### Bedrock Fact Sanitizer
- Extracts verified facts into a fixed, declarative JSON schema.
- Operates strictly with no tool-calling capabilities.

### Gate 2: Authority Check
- Evaluates proposed tool executions before execution.
- Verifies grounding against the explicit user prompt. Even if an injection slips past Gate 1, Gate 2 prevents unauthorized external actions.

## 4. Evaluation & Results
All metrics are verified via `eval/run_all.py`. Claims are labeled according to standard:
- **[Measured]** On our initial benchmark set, Gate 1 isolates AI-addressed directives while preserving tricky human-to-human instructions.
- **[Planned]** Full evaluation across the extended test dataset and adaptive red-team suite before Oct 22.
- **[Hypothesis]** Dual gating reduces attack bypass rates compared to single-point boundary defenses.

*Note: We do not claim that Airlock stops prompt injection. Defensive boundaries reduce attack surface through layered verification.*
