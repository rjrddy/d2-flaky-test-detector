"""Detect same-revision flaky outcomes and model a bounded quarantine policy."""

import json
import random
from collections import defaultdict
from pathlib import Path


def detect(history: list[dict], min_flips: int = 2) -> set[str]:
    by_revision: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in history:
        by_revision[(row["test"], row["sha"])].append(row)
    evidence: dict[str, int] = defaultdict(int)
    for (name, _), rows in by_revision.items():
        attempts = sorted(rows, key=lambda r: r["attempt"])
        failures = [r for r in attempts if r["outcome"] == "fail"]
        passes = [r for r in attempts if r["outcome"] == "pass"]
        if failures and passes:
            evidence[name] += min(len(failures), len(passes))
    return {name for name, count in evidence.items() if count >= min_flips}


def generate(seed: int = 42) -> tuple[list[dict], set[str]]:
    rng = random.Random(seed)
    history = []
    truth = {f"test_{i}" for i in range(20)}
    for i in range(100):
        for revision in range(10):
            for attempt in range(3):
                outcome = (
                    ("fail" if rng.random() < 0.3 else "pass")
                    if i < 20
                    else ("fail" if i < 30 else "pass")
                )
                history.append(
                    {
                        "test": f"test_{i}",
                        "sha": f"synthetic-{revision}",
                        "attempt": attempt,
                        "outcome": outcome,
                        "duration_s": rng.uniform(0.01, 0.1),
                    }
                )
    return history, truth


def benchmark() -> dict:
    history, truth = generate()
    detected = detect(history)
    tp = len(detected & truth)
    precision = tp / len(detected) if detected else 0
    recall = tp / len(truth)
    # Quarantined tests still run once; only automatic reruns are avoided.
    saved = sum(r["duration_s"] for r in history if r["test"] in detected and r["attempt"] > 0)
    report = {
        "injected_flakes": len(truth),
        "detected": len(detected),
        "precision": precision,
        "recall": recall,
        "modeled_rerun_seconds_avoided": saved,
        "quarantine": sorted(detected),
        "policy": {"min_mixed_outcomes": 2, "expires_days": 7, "continues_nightly": True},
    }
    Path("evidence/history.json").write_text(json.dumps(history, indent=2))
    Path("evidence/comment.md").write_text(
        f"Flake detector on synthetic history: precision {precision}, recall {recall}.\n\n"
        f"{len(detected)} tests proposed for seven-day quarantine; nightly runs continue.\n"
        f"Modeled rerun time avoided: {saved:.3f}s. This is simulated cost, not production savings.\n"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2))
