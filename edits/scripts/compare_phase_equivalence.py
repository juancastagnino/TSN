#!/usr/bin/env python3
"""Compare a structural-refactor export with a saved numerical baseline."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "provenance":
                continue
            child_prefix = f"{prefix}.{key}" if prefix else key
            result.update(flatten(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.update(flatten(child, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def compare_summaries(baseline: Path, candidate: Path) -> list[dict[str, Any]]:
    rows = []
    for old_path in sorted(baseline.glob("*_summary.json")):
        new_path = candidate / old_path.name
        if not new_path.exists():
            rows.append({"body": old_path.stem.removesuffix("_summary"), "missing": True})
            continue
        old = flatten(json.loads(old_path.read_text(encoding="utf-8")))
        new = flatten(json.loads(new_path.read_text(encoding="utf-8")))
        fields = sorted(set(old) | set(new))
        numeric_deltas = []
        other_differences = []
        for field in fields:
            old_value, new_value = old.get(field), new.get(field)
            if (
                isinstance(old_value, (int, float))
                and not isinstance(old_value, bool)
                and isinstance(new_value, (int, float))
                and not isinstance(new_value, bool)
            ):
                numeric_deltas.append(abs(float(new_value) - float(old_value)))
            elif old_value != new_value:
                other_differences.append(field)
        rows.append(
            {
                "body": old_path.stem.removesuffix("_summary"),
                "missing": False,
                "max_numeric_delta": max(numeric_deltas, default=0.0),
                "other_differences": other_differences,
            }
        )
    return rows


def compare_binary_csv(baseline: Path, candidate: Path) -> dict[str, Any]:
    with baseline.open("r", encoding="utf-8-sig", newline="") as old_handle, candidate.open(
        "r", encoding="utf-8-sig", newline=""
    ) as new_handle:
        old_reader = csv.DictReader(old_handle)
        new_reader = csv.DictReader(new_handle)
        if old_reader.fieldnames != new_reader.fieldnames:
            raise ValueError("Binary CSV headers differ")
        fields = old_reader.fieldnames or []
        numeric_fields = [field for field in fields if field not in ("date", "time")]
        maxima = {field: 0.0 for field in numeric_fields}
        sums_squared = {field: 0.0 for field in numeric_fields}
        row_count = 0
        timestamp_mismatches = 0
        for old_row, new_row in zip(old_reader, new_reader):
            row_count += 1
            if (old_row["date"], old_row["time"]) != (
                new_row["date"],
                new_row["time"],
            ):
                timestamp_mismatches += 1
            for field in numeric_fields:
                delta = abs(float(new_row[field]) - float(old_row[field]))
                maxima[field] = max(maxima[field], delta)
                sums_squared[field] += delta * delta
        old_extra = next(old_reader, None)
        new_extra = next(new_reader, None)
        if old_extra is not None or new_extra is not None:
            raise ValueError("Binary CSV row counts differ")
    rms = {
        field: math.sqrt(total / row_count) if row_count else math.nan
        for field, total in sums_squared.items()
    }
    return {
        "rows": row_count,
        "timestamp_mismatches": timestamp_mismatches,
        "maxima": maxima,
        "rms": rms,
    }


def compare_numeric_artifacts(baseline: Path, candidate: Path) -> list[tuple[str, bool]]:
    names: set[str] = set()
    for pattern in ("*_residuals.csv", "*_annual_stats.csv", "*_fft_peaks.csv"):
        names.update(path.name for path in baseline.glob(pattern))
    moon_periodic = baseline / "moon_periodic_components.csv"
    if moon_periodic.exists():
        names.add(moon_periodic.name)
    return [
        (
            name,
            (candidate / name).exists()
            and (baseline / name).read_bytes() == (candidate / name).read_bytes(),
        )
        for name in sorted(names)
    ]
def generate_report(
    summary_rows: list[dict[str, Any]],
    binary: dict[str, Any],
    artifacts: list[tuple[str, bool]],
    args: argparse.Namespace,
) -> tuple[str, bool]:
    worst = sorted(binary["maxima"], key=binary["maxima"].get, reverse=True)
    endpoint_angle_fields = {
        "midpoint_opposition_angle_deg",
        "midpoint_opposition_error_deg",
    }
    binary_within_tolerance = all(
        delta
        <= (
            args.endpoint_angle_tolerance
            if field in endpoint_angle_fields
            else args.tolerance
        )
        for field, delta in binary["maxima"].items()
    )
    max_summary = max(
        (row.get("max_numeric_delta", 0.0) for row in summary_rows), default=0.0
    )
    non_numeric = sum(len(row.get("other_differences", [])) for row in summary_rows)
    accepted = (
        bool(summary_rows)
        and bool(artifacts)
        and binary["timestamp_mismatches"] == 0
        and binary_within_tolerance
        and max_summary <= args.tolerance
        and non_numeric == 0
        and not any(row.get("missing") for row in summary_rows)
        and all(identical for _, identical in artifacts)
    )
    lines = [
        "# Phase export-equivalence comparison",
        "",
        f"Status: **{'PASS' if accepted else 'FAIL'}**  ",
        f"Coordinate/numeric tolerance: `{args.tolerance:.3e}`  ",
        f"Constructed midpoint endpoint-angle tolerance: `{args.endpoint_angle_tolerance:.3e} deg`",
        "",
        "## Scientific summary fields",
        "",
        "Provenance fields are intentionally excluded.",
        "",
    ]
    if not summary_rows:
        lines.extend(
            [
                "**ERROR: no baseline `*_summary.json` files were found. This gate cannot pass.**",
                "",
            ]
        )
    lines.extend([
        "| Body | Maximum numeric delta | Other differences |",
        "|---|---:|---|",
    ])
    for row in summary_rows:
        if row.get("missing"):
            lines.append(f"| {row['body']} | — | candidate missing |")
        else:
            other = ", ".join(row["other_differences"]) or "none"
            lines.append(
                f"| {row['body']} | {row['max_numeric_delta']:.12g} | {other} |"
            )
    lines.extend(
        [
            "",
            "## Per-sample and spectral artifacts",
            "",
            f"Byte-identical files: `{sum(identical for _, identical in artifacts)}` of `{len(artifacts)}`.",
            "",
        ]
    )
    if not artifacts:
        lines.extend(
            [
                "**ERROR: no baseline numeric artifacts were found. This gate cannot pass.**",
                "",
            ]
        )
    lines.extend(
        [
            "Non-identical files: "
            + (", ".join(f"`{name}`" for name, identical in artifacts if not identical) or "none"),
            "",
            "## Sun-Mars binary CSV",
            "",
            f"Rows: `{binary['rows']}`; timestamp mismatches: `{binary['timestamp_mismatches']}`.",
            "",
            "| Field | Maximum absolute delta | RMS delta |",
            "|---|---:|---:|",
        ]
    )
    for field in worst[:15]:
        lines.append(
            f"| {field} | {binary['maxima'][field]:.12g} | {binary['rms'][field]:.12g} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This gate compares TYCHOS outputs before and after a structural refactor; it does not measure agreement with JPL.",
            "- Different export hashes or decimal strings are acceptable only when timestamp-aligned numeric values remain within tolerance.",
            "- The midpoint is defined from the two endpoints, so its opposition is exactly 180 degrees by construction. Its relaxed angle tolerance covers only floating-point sensitivity of `acos` at that endpoint; it does not relax any position field.",
            "- A pass supports coordinate equivalence at the declared tolerance; it does not prove physical correctness.",
            "",
        ]
    )
    return "\n".join(lines), accepted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-reports", type=Path, default=ROOT / "00-backup" / "native-relative-baseline")
    parser.add_argument("--candidate-reports", type=Path, default=ROOT / "edits" / "reports")
    parser.add_argument("--baseline-binary", type=Path, default=ROOT / "00-backup" / "native-relative-baseline" / "sun_mars_binary.csv")
    parser.add_argument("--candidate-binary", type=Path, default=ROOT / "edits" / "data" / "raw" / "sun_mars_binary.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "edits" / "reports" / "full_binary_equivalence_report.md")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--endpoint-angle-tolerance", type=float, default=2e-6)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = compare_summaries(args.baseline_reports, args.candidate_reports)
    binary = compare_binary_csv(args.baseline_binary, args.candidate_binary)
    artifacts = compare_numeric_artifacts(args.baseline_reports, args.candidate_reports)
    report, accepted = generate_report(summaries, binary, artifacts, args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {args.output.resolve()}")
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
