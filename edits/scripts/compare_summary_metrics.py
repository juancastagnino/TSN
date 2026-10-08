#!/usr/bin/env python3
"""Compare generated body-summary metrics with a preserved report baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METRICS = (
    ("RA mean", "ra_residual", "mean_deg", True),
    ("RA RMS", "ra_residual", "rms_deg", False),
    ("Dec mean", "declination_residual", "mean_deg", True),
    ("Dec RMS", "declination_residual", "rms_deg", False),
    ("Angular mean", "angular_separation", "mean_deg", False),
    ("Angular RMS", "angular_separation", "rms_deg", False),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "00-backup/full-binary-baseline",
    )
    parser.add_argument(
        "--candidate", type=Path, default=ROOT / "edits/reports"
    )
    parser.add_argument("bodies", nargs="*")
    return parser.parse_args()


def score(value: float, signed_bias: bool) -> float:
    return abs(value) if signed_bias else value


def main() -> None:
    args = parse_args()
    bodies = args.bodies or sorted(
        path.name.removesuffix("_apparent_of_date_summary.json")
        for path in args.baseline.glob("*_apparent_of_date_summary.json")
    )

    print("| Body | Metric | Baseline | Candidate | Change | Assessment |")
    print("|---|---|---:|---:|---:|---|")
    for body in bodies:
        name = f"{body}_apparent_of_date_summary.json"
        baseline = json.loads((args.baseline / name).read_text(encoding="utf-8"))
        candidate = json.loads((args.candidate / name).read_text(encoding="utf-8"))
        for label, group, field, signed_bias in METRICS:
            old = float(baseline[group][field])
            new = float(candidate[group][field])
            old_score = score(old, signed_bias)
            new_score = score(new, signed_bias)
            delta = new - old
            tolerance = 1e-12
            if new_score < old_score - tolerance:
                assessment = "improved"
            elif new_score > old_score + tolerance:
                assessment = "worse"
            else:
                assessment = "unchanged"
            print(
                f"| {body.title()} | {label} | {old:.9f}° | {new:.9f}° | "
                f"{delta:+.9f}° | {assessment} |"
            )


if __name__ == "__main__":
    main()
