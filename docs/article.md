# Airlock: Rethinking Prompt Injection Defense for Autonomous Agents

## 1. Problem
Autonomous AI agents reading untrusted external documents (emails, customer tickets, invoices) and invoking tools face an inherent vulnerability: **indirect prompt injection**. Attackers embed adversarial text into invoice line items or calendar descriptions, tricking the agent into executing unauthorized tools—such as emailing private documents or deleting databases.

Most defensive measures attempt to answer:
> *"Is this input text malicious or harmful?"*

Because natural language is endlessly polymorphic, intent classifiers regularly miss disguised attacks while generating excessive false alarms on legitimate business emails containing urgent directives or security alerts.

---

## 2. Insight
In real-world workflows:
- Documents convey inert **data** to human readers (e.g. quarterly figures).
- Documents contain **instructions meant for human beings** (*"Alice, please review the slides by 5 PM"*).
- Documents **almost never** legitimately address the autonomous AI agent.

Airlock shifts the defensive paradigm from intent detection to addressee verification:
> **"Who is this text talking to?"** *(Human reader vs. AI agent)*

When an external document addresses the AI (*"Ignore previous rules"*, *"System directive: Assistant must..."*), that is an anomaly. By decoupling addressee classification from intent classification, Airlock isolates attacks without breaking normal human-to-human communication.

---

## 3. Design
Airlock implements a dual-gate architecture that enforces defense-in-depth across the agent lifecycle:

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

### Component Breakdown
1. **Gate 1 (Addressee Check — Incoming)**:
   - Evaluates incoming text using a local Decider 2B decision model in a single forward pass.
   - Outputs: `label` (`data`, `human_instruction`, `ai_instruction`, `unclear`), `confidence`, `tries_action`, `claims_authority`.
   - Confident data and human instructions pass to the agent; AI-addressed text is quarantined.
2. **Bedrock Tool-less Sanitizer**:
   - Quarantined documents are summarized into a strict declarative JSON schema (`sender`, `subject`, `entities`, `factual_points`, `summary`).
   - The sanitizer operates with zero tool access. The agent only reads factual points and never encounters raw injection strings.
3. **Gate 2 (Authority Check — Outgoing)**:
   - Intercepts proposed side-effecting actions (`send_email`, `forward_email`, `delete_email`).
   - Verifies whether authority traces to the user's explicit request or solely to the document context. Ungrounded exfiltrations are blocked before execution.

---

## 4. Results
All numbers are generated directly by evaluation scripts (`eval/run_decider_smoke.py`, `eval/calibrate_gate2.py`, `eval/calibration_plot.py`).

| Benchmark Evaluation | Metric | Measured Value | Label |
|---|---|---|---|
| **Decider 2B Smoke Test (N=100)** | High-Confidence Accuracy ($\ge 0.85$) | **93.81%** | **[Measured]** |
| **Decider 2B Smoke Test (N=100)** | Attack Detection Recall | **100.00%** | **[Measured]** |
| **Decider 2B Smoke Test (N=100)** | Tricky Benign False Quarantine | **2.86%** | **[Measured]** |
| **Gate 2 Grounding Calibration (N=374)** | Benign False Block Rate | **0.00%** | **[Measured]** |
| **Gate 2 Grounding Calibration (N=374)** | Attack Block Rate | **100.00%** | **[Measured]** |
| **Reliability Calibration Study (N=201)** | Expected Calibration Error (ECE) | **0.0364** (3.64%) | **[Measured]** |
| **High-Confidence Reliability ($\ge 0.90$)** | Empirical Accuracy (N=188) | **90.43%** (95% CI: 85.4%–93.9%) | **[Measured]** |
| **Ablation Study on Full Test Split** | End-to-end task completion | Held-out run | **[Planned]** |

> **Explicit Boundary Condition:** We do *not* claim that Airlock "stops prompt injection" entirely. Defensive boundaries reduce attack surface through layered verification. Classification runs locally for Gate 1.

---

## 5. Failures & Edge Cases
Transparency regarding failure modes is essential for reliable AI deployment:
1. **Subtle Persona Simulation**: Attacks that completely avoid imperative verbs and instead simulate conversational agreement can score borderline confidence. Airlock handles this by routing borderline scores to quarantine.
2. **Generic User Prompts**: When a user gives an underspecified instruction (*"Handle this email"*), Gate 2 cannot reliably distinguish safe replies from destructive actions. In our calibrated sweep, 22.19% of such ambiguous actions were escalated to human confirmation rather than auto-executed.
3. **Multilingual Context Shifts**: While common languages (French, Spanish, Portuguese, German, Hindi) are captured, highly obfuscated low-resource translations require live multilingual model weights.

---

## 6. How to Reuse: Reusable Decision Pattern
Developers can integrate Airlock's decision pattern into their own agents using the typed interfaces below:

### A. Reusable Gate 1 Pattern
```python
from airlock.gate1 import gate1

# Inspect incoming untrusted document
verdict = gate1(document_text)

if verdict["label"] == "ai_instruction" or verdict["tries_action"]:
    # Quarantine: strip commands before giving to LLM
    safe_data = sanitize_facts_only(document_text)
else:
    # Direct read: safe data or human-to-human communication
    safe_data = document_text
```

### B. Reusable Gate 2 Pattern
```python
from airlock.gate2 import gate2

# Intercept proposed tool calls before execution
result = gate2(
    action={"tool": "send_email", "args": {"to": "recipient@corp.com"}},
    user_request=user_prompt,
    doc_context=document_text
)

if result["grounded"] and result["confidence"] >= 0.70:
    execute_tool(...)
else:
    raise SecurityException("Action not grounded in user request!")
```
