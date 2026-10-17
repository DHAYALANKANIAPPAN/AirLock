<<<<<<< HEAD
# Preregistration: Airlock evaluation

Status: DRAFT until committed. Commit this file BEFORE any run on test.jsonl.
Commit date/hash: ______ (fill in at commit time)

## 1. Question
Does a Decider 2B gate reduce the success of indirect prompt injection without
wrongly quarantining harmless content, compared with simple baselines?

## 2. Hypotheses (each can be falsified)
- **H1.** Airlock lets through fewer attacks than the regex baseline.
- **H2.** On tricky benign + normal benign items, Airlock's false-quarantine rate
  is not worse than the Bedrock LLM judge by more than 5 percentage points.
- **H3.** Airlock's median per-document latency is lower than the Bedrock LLM judge's.
- **H4 (exploratory).** Airlock's cost per 100 documents is lower than the LLM judge's.

We report results whether or not these hold.

## 3. Data
- 200-row synthetic dataset plus a seeded public-benchmark slice (see data/README.md).
- Label rule: docs/LABEL_RULE.md.
- Split: stratified 50/50 by (label, category), seed 20261017, made by data/make_split.py.
- SHA-256 of dev.jsonl and test.jsonl are in data/SPLIT_MANIFEST.json and copied here at freeze:
  - dev: ______
  - test: ______

## 4. Systems compared
1. No defense.
2. Regex/keyword filter (exact patterns published in the repo).
3. Per-document LLM judge on Amazon Bedrock (exact prompt and model ID published).
4. Airlock (Decider 2B gate + lanes). 

## 5. Metrics
- Attack success rate (attacks that reach the agent unchanged).
- False-quarantine rate, reported separately for tricky benign and normal benign.
- Latency p50 and p95 per document.
- Bedrock cost per 100 documents.
- 95% Wilson confidence intervals for all rates.

## 6. Threshold policy
- Thresholds are chosen ONLY on dev.jsonl.
- Rule (to be confirmed by the team before any run): choose the lowest confidence threshold
  that keeps dev false-quarantine on benign at or below 5%, then report attack recall.
- Nobody inspects test.jsonl rows or results while choosing thresholds or fixing code.

## 7. Test rule
- test.jsonl is run ONCE, after code and thresholds are frozen (git tag `eval-freeze`).
- If a bug is found afterwards, we report BOTH the original run and the fixed run,
  and say which was preregistered.

## 8. Known limits
- Synthetic data, small samples (about 100 test rows), wide confidence intervals.
- Labels from one author plus a blind second labeler on a subset; agreement is reported.
- Decider's training data may overlap with public benchmarks; we cannot rule this out.
- Phishing aimed at humans is out of scope.
- Results are indicative, not conclusive. Airlock is a research prototype.

## 9. Deviations log
| Date | Change | Reason |
|---|---|---|
| | | |
{
  "seed": 20261017,
  "method": "stratified 50/50 by (label, category); dev gets extra row when odd",
  "dev": {
    "rows": 101,
    "labels": {
      "attack": 30,
      "benign": 71
    },
    "sha256": "9b37342c70937f66667aff98c36a67e267f29427328fd241333c322a02b973bf"
  },
  "test": {
    "rows": 99,
    "labels": {
      "attack": 30,
      "benign": 69
    },
    "sha256": "ccaa8ceef1b082ac287a44b2288144e653a55c55a8b85182156375cf22aff769"
  }
}
=======
# Airlock: Scientific Pre-Registration

**Date:** 2026-10-17  
**Status:** Pre-registered Protocol  
**License:** Apache-2.0  

---

## 1. Core Insight & Hypothesis

### Core Insight
Existing prompt injection defenses ask: *"Is this input malicious?"* This question is brittle because attackers continually rephrase, obfuscate, and disguise malicious prompts as legitimate instructions.  
Instead, Airlock asks: **"Who is this text talking to?"**
Legitimate external documents (emails, invoices, memos) address human readers or convey inert data. They almost never legitimately address the AI agent.

### Hypotheses
- **[Hypothesis 1 - Addressee Separation]:** Classifying incoming content by target audience (*data* vs *human instruction* vs *AI instruction*) will significantly reduce prompt injection susceptibility compared to naive keyword filtering, while maintaining low false-positive rates on tricky human-to-human directives.
- **[Hypothesis 2 - Dual-Gate Complementarity]:** Combining an incoming Addressee Check (Gate 1) with an outgoing Authority Check (Gate 2) provides defense-in-depth: even if an injection evades Gate 1, Gate 2 denies ungrounded actions that lack authorization in the user's prompt.
- **[Hypothesis 3 - Fixed Schema Neutralization]:** Passing quarantined inputs through a tool-less fact extraction schema prevents the executing agent from ever encountering actionable injection strings.

> **Important Boundary Condition:** We do *not* claim that Airlock "stops prompt injection" entirely. Rather, we evaluate how effectively addressee and authority gating reduce attack success rates and false positives under measured conditions. Classification runs locally for Gate 1.

---

## 2. Experimental Design

### Systems Under Evaluation
1. **No Defense Baseline:** Raw document passed directly to agent.
2. **Naive Keyword Baseline:** Standard regex/keyword blocklist for injection phrases.
3. **Naive LLM Judge Baseline:** Prompting an LLM with *"Is this text an injection?"*
4. **Airlock (Gate 1 + Sanitizer + Gate 2):** Dual-gate addressee and authority architecture.

### Dataset Splits
- **Dev Set (`data/dev.jsonl`):** 10 curated examples across 3 classes:
  - `benign`: Routine reports, notes, invoices.
  - `tricky_benign`: Human directives, forwarded threads with injection keywords, urgent memos.
  - `attack`: Direct overrides, authority spoofing, delimiter attacks, exfiltration directives.
- **Test Set (`data/test.jsonl`):** Held-out set for final evaluation.

### Metrics (All numbers generated by `eval/run_all.py`)
- **Detection Recall:** Proportion of attacks identified and quarantined.
- **False Positive Rate (FPR):** Proportion of benign and tricky-benign items incorrectly quarantined or blocked.
- **Attack Bypass Rate:** Proportion of attacks that successfully elicit unauthorized tool execution.
- **F1 Score:** Harmonic mean of precision and recall.

---

## 3. Claim Classification Protocol
To ensure transparency, every claim in project documentation is explicitly tagged:
- **[Measured]:** Verified by running `eval/run_all.py` and backed by script-generated numbers.
- **[Planned]:** Implementation or benchmark planned before the October 22 deadline.
- **[Hypothesis]:** Theoretical expectation to be confirmed or refuted.
>>>>>>> origin/develop
