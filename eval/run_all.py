"""Run all evaluations, compare baselines against Airlock, and output real script-generated metrics."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from airlock.gate1 import gate1
from airlock.handler import AirlockPipeline
from eval.baselines import NaiveKeywordBaseline, NaiveLLMJudgeBaseline, NoDefenseBaseline
from eval.metrics import calculate_metrics


def load_dataset(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL dataset rows."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def evaluate_airlock(rows: List[Dict[str, Any]]) -> List[str]:
    """Evaluate Airlock Gate 1 pipeline predictions."""
    pipeline = AirlockPipeline()
    preds = []
    for r in rows:
        route, _, verdict = pipeline.inspect_incoming(r["text"])
        if verdict["label"] == "ai_instruction" or (verdict["label"] == "unclear" and verdict["tries_action"]):
            preds.append("attack")
        else:
            preds.append("benign")
    return preds


def run_benchmark(dataset_path: str) -> Dict[str, Any]:
    rows = load_dataset(dataset_path)
    ground_truth = [r["label"] if r["label"] == "attack" else "benign" for r in rows]

    no_defense = NoDefenseBaseline()
    keyword_baseline = NaiveKeywordBaseline()
    judge_baseline = NaiveLLMJudgeBaseline()

    no_def_preds = [no_defense.predict(r["text"]) for r in rows]
    kw_preds = [keyword_baseline.predict(r["text"]) for r in rows]
    judge_preds = [judge_baseline.predict(r["text"]) for r in rows]
    airlock_preds = evaluate_airlock(rows)

    results = {
        "dataset": dataset_path,
        "sample_count": len(rows),
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "measured",  # strictly labeled: measured / planned / hypothesis
        "defenses": {
            "no_defense": calculate_metrics(no_def_preds, ground_truth),
            "naive_keyword": calculate_metrics(kw_preds, ground_truth),
            "naive_llm_judge": calculate_metrics(judge_preds, ground_truth),
            "airlock_gates": calculate_metrics(airlock_preds, ground_truth),
        }
    }
    return results


def print_markdown_table(results: Dict[str, Any]) -> None:
    print(f"\n### Evaluation Results ({results['dataset']}) - [Status: {results['status']}]\n")
    print("| Defense System | Accuracy | Precision | Recall (Detection) | F1 | False Positive Rate | Attack Bypass Rate |")
    print("|---|---|---|---|---|---|---|")
    for name, m in results["defenses"].items():
        print(f"| {name:<16} | {m['accuracy']:.4f}   | {m['precision']:.4f}    | {m['recall']:.4f}             | {m['f1']:.4f} | {m['false_positive_rate']:.4f}              | {m['attack_bypass_rate']:.4f}             |")
    print("\n*Note: Numbers above are script-generated; claims reflect measured defense performance without claiming prompt injection is solved.*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Airlock Benchmark Evaluation Runner")
    parser.add_argument("--data", default="data/dev.jsonl", help="Path to jsonl evaluation dataset")
    parser.add_argument("--output", default="eval/results.json", help="Path to output results json")
    args = parser.parse_args()

    results = run_benchmark(args.data)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print_markdown_table(results)
