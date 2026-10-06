#!/usr/bin/env python3
"""Compare complete TYCHOS exports while ignoring generation metadata."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IGNORED_PREFIXES = ("Generated on:",)


def normalized_lines(path: Path) -> tuple[list[str], list[str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    ignored = [line for line in lines if line.strip().startswith(IGNORED_PREFIXES)]
    retained = [
        line for line in lines if not line.strip().startswith(IGNORED_PREFIXES)
    ]
    return retained, ignored


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "00-backup/full-binary-baseline/tychos_ephemerides.txt",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "edits/data/raw/tychos_ephemerides.txt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "edits/reports/full_binary_all_bodies_equivalence_report.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    baseline, baseline_ignored = normalized_lines(args.baseline.resolve())
    candidate, candidate_ignored = normalized_lines(args.candidate.resolve())
    line_count_equal = len(baseline) == len(candidate)
    mismatches = []
    for index, (old, new) in enumerate(zip(baseline, candidate), start=1):
        if old != new:
            mismatches.append((index, old, new))
            if len(mismatches) == 10:
                break
    accepted = line_count_equal and not mismatches

    report = [
        "# Full binary all-body TYCHOS export equivalence",
        "",
        f"Status: **{'PASS' if accepted else 'FAIL'}**  ",
        f"Baseline: `{args.baseline.resolve().as_posix()}`  ",
        f"Candidate: `{args.candidate.resolve().as_posix()}`",
        "",
        "Generation timestamps are excluded; every other exported line is compared exactly.",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Baseline retained lines | {len(baseline)} |",
        f"| Candidate retained lines | {len(candidate)} |",
        f"| Ignored metadata lines | {len(baseline_ignored)} / {len(candidate_ignored)} |",
        f"| First-ten exact-line mismatches | {len(mismatches)} |",
        "",
    ]
    if mismatches:
        report.extend(["## First mismatches", ""])
        for line_number, old, new in mismatches:
            report.extend(
                [
                    f"- Retained line `{line_number}`",
                    f"  - baseline: `{old}`",
                    f"  - candidate: `{new}`",
                ]
            )
        report.append("")
    report.extend(
        [
            "A pass establishes exact formatted export equivalence for every body in the",
            "combined TYCHOS file. It is a structural migration gate, not a JPL accuracy test.",
            "",
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"Wrote {args.output.resolve()}")
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
