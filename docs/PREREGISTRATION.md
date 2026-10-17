# Airlock: Scientific Pre-Registration

**Date:** 2026-10-17  
**Status:** Pre-registered protocol (commit BEFORE any run on test data)  
**License:** Apache-2.0  
**Commit hash at freeze:** ______ (fill in when committed)

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

Operational versions (each can be falsified, and we report results either way):
- **H1a.** On the frozen test set, Airlock Gate 1 lets through fewer attacks than the keyword baseline.
- **H1b.** On benign items, Airlock's false-quarantine rate is not worse than the LLM-judge baseline by more than 5 percentage points.
- **H1c.** Airlock's median per-document latency is lower than the LLM judge's.
- **H1d (exploratory).** Airlock's cost per 100 documents is lower than the LLM judge's.

> **Important Boundary Condition:** We do *not* claim that Airlock "stops prompt injection" entirely. Rather, we evaluate how effectively addressee and authority gating reduce attack success rates and false positives under measured conditions. Classification runs locally for Gate 1.

---

## 2. Experimental Design

### Systems Under Evaluation
1. **No Defense Baseline:** Raw document passed directly to agent.
2. **Naive Keyword Baseline:** Standard regex/keyword blocklist for injection phrases (exact patterns published in the repo).
3. **Naive LLM Judge Baseline:** Prompting an LLM with *"Is this text an injection?"* (exact prompt and model ID published in the repo).
4. **Airlock (Gate 1 + Sanitizer + Gate 2):** Dual-gate addressee and authority architecture.

### Datasets (frozen)
All numbers come from `eval/run_all.py`. Data files and scripts live in `data/`.

| File | Rows | Purpose |
|---|---|---|
| `data/dev.jsonl` | 101 (30 attack, 71 benign) | Choose thresholds and fix code. Allowed to be inspected. |
| `data/test.jsonl` | 99 (30 attack, 69 benign) | Final evaluation. Run ONCE. |
| `data/benchmark_slice.jsonl` | 65 (50 attack, 15 benign controls) | Separate external-validity set from public benchmarks (see below). Run ONCE, reported as its own table. |

- **Composition (dev + test together):** 60 attacks (direct, reworded, multilingual, split across paragraphs, hidden HTML, authority spoofing, tool-output), 40 tricky benign (imperatives to humans, IT notices, newsletters about injection, quoted attacks), 100 normal benign (emails, web pages, documents, tool outputs, 8 non-English).
- **Split method:** stratified 50/50 by (label, category), seed `20261017`, produced by `data/make_split.py`. Reason: no model is trained on this data, so the main leakage risk is threshold overfitting on dev.
- **Hashes (SHA-256, from `data/SPLIT_MANIFEST.json`):**
  - dev: `9b37342c70937f66667aff98c36a67e267f29427328fd241333c322a02b973bf`
  - test: `ccaa8ceef1b082ac287a44b2288144e653a55c55a8b85182156375cf22aff769`
  - benchmark slice: `4554cfe1b13a743650e70ed972c0ca477ecdd322682fba9088b761678972cb88`
- **Public benchmark slice:** a seeded random sample from InjecAgent (30 attack cases plus 15 paired benign controls) and BIPIA (20 attack strings in our own neutral carriers). Both are MIT licensed. Repo commits are in `data/BENCHMARK_MANIFEST.json`.
- **Label rule:** `docs/LABEL_RULE.md`.

### Mapping between our labels and Gate 1's three classes
- Gold label `attack` = text addressed to the AI agent asking for an action the user did not request (Gate 1 class: **AI instruction**).
- Gold label `benign` = **data** or **human instruction**. Rows in the tricky categories (`benign_imperative`, `it_notice`, `newsletter_about_injection`, `quoted_attack_in_benign`) are reported as `tricky_benign`; the rest as `benign`. The loader `data/load_dataset.py` applies this mapping.
- Any quarantine or block of a `benign` row counts as a false quarantine.

### Metrics (All numbers generated by `eval/run_all.py`)
- **Detection Recall:** Proportion of attacks identified and quarantined.
- **False Positive Rate (FPR):** Proportion of benign and tricky-benign items incorrectly quarantined or blocked (reported separately for `tricky_benign` and `benign`).
- **Attack Bypass Rate:** Proportion of attacks that successfully elicit unauthorized tool execution.
- **F1 Score:** Harmonic mean of precision and recall.
- **Latency:** p50 and p95 per document.
- **Cost:** Bedrock cost per 100 documents.
- **Uncertainty:** 95% Wilson confidence intervals for all rates.

---

## 3. Threshold Policy
- Thresholds are chosen ONLY on `data/dev.jsonl`.
- Rule (team to confirm before any run; edit here if changed): choose the lowest confidence threshold that keeps dev false-quarantine on benign items at or below 5%, then report recall.
- Nobody inspects test results while choosing thresholds or fixing code.

## 4. Test Rule
- `data/test.jsonl` and `data/benchmark_slice.jsonl` are run ONCE, after code and thresholds are frozen (git tag `eval-freeze`).
- If a bug is found afterwards, we report BOTH the original run and the fixed run, and say which was preregistered.
- Files in `data/` named above are never edited after this file is committed. The hashes above detect any change.

## 5. Claim Classification Protocol
To ensure transparency, every claim in project documentation is explicitly tagged:
- **[Measured]:** Verified by running `eval/run_all.py` and backed by script-generated numbers.
- **[Planned]:** Implementation or benchmark planned before the October 22 deadline.
- **[Hypothesis]:** Theoretical expectation to be confirmed or refuted.

## 6. Known Limits
- Synthetic data and small samples (about 100 test rows), so confidence intervals are wide. Results are indicative, not conclusive.
- Labels come from one author plus a blind second labeler on a subset; agreement is reported in `data/README.md`.
- Hindi, Chinese and Japanese rows need native-speaker review.
- Decider's training data may overlap with public benchmarks; we cannot rule this out.
- Phishing aimed at humans is out of scope.
- Airlock is a research prototype, not a complete security product.

## 7. Deviations Log
| Date | Change | Reason |
|---|---|---|
| 2026-10-17 | Replaced the 10-row placeholder dev and test files with the 101/99-row frozen split. | Planned dataset replaced the placeholders before any run. |
| 2026-10-17 | Added `benchmark_slice.jsonl` as a separate set. | External validity, added before any run. |