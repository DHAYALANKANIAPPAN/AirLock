Preregistration: Airlock evaluation
Status: DRAFT until committed. Commit this file BEFORE any run on test.jsonl.
Commit date/hash: ______ (fill in at commit time)
1. Question
Does a Decider 2B gate reduce the success of indirect prompt injection without
wrongly quarantining harmless content, compared with simple baselines?
2. Hypotheses (each can be falsified)
H1. Airlock lets through fewer attacks than the regex baseline.
H2. On tricky benign + normal benign items, Airlock's false-quarantine rate
is not worse than the Bedrock LLM judge by more than 5 percentage points.
H3. Airlock's median per-document latency is lower than the Bedrock LLM judge's.
H4 (exploratory). Airlock's cost per 100 documents is lower than the LLM judge's.
We report results whether or not these hold.
3. Data
200-row synthetic dataset plus a seeded public-benchmark slice (see data/README.md).
Label rule: docs/LABEL_RULE.md.
Split: stratified 50/50 by (label, category), seed 20261017, made by data/make_split.py.
SHA-256 of dev.jsonl and test.jsonl are in data/SPLIT_MANIFEST.json and copied here at freeze:
dev: ______
test: ______
4. Systems compared
No defense.
Regex/keyword filter (exact patterns published in the repo).
Per-document LLM judge on Amazon Bedrock (exact prompt and model ID published).
Airlock (Decider 2B gate + lanes).
5. Metrics
Attack success rate (attacks that reach the agent unchanged).
False-quarantine rate, reported separately for tricky benign and normal benign.
Latency p50 and p95 per document.
Bedrock cost per 100 documents.
95% Wilson confidence intervals for all rates.
6. Threshold policy
Thresholds are chosen ONLY on dev.jsonl.
Rule (to be confirmed by the team before any run): choose the lowest confidence threshold
that keeps dev false-quarantine on benign at or below 5%, then report attack recall.
Nobody inspects test.jsonl rows or results while choosing thresholds or fixing code.
7. Test rule
test.jsonl is run ONCE, after code and thresholds are frozen (git tag `eval-freeze`).
If a bug is found afterwards, we report BOTH the original run and the fixed run,
and say which was preregistered.
8. Known limits
Synthetic data, small samples (about 100 test rows), wide confidence intervals.
Labels from one author plus a blind second labeler on a subset; agreement is reported.
Decider's training data may overlap with public benchmarks; we cannot rule this out.
Phishing aimed at humans is out of scope.
Results are indicative, not conclusive. Airlock is a research prototype.
9. Deviations log
Date	Change	Reason
		
