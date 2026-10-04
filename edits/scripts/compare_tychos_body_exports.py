"""Compare one TYCHOS body before and after a structural refactor."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np

from ephemeris_io import tychos_blocks


ROOT = Path(__file__).resolve().parents[2]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RA = re.compile(r"^(\d{2})h(\d{2})m(\d{2})s$")
DEC = re.compile(r"^(-?)(\d{2})°(\d{2})'(\d{2})\"$")
DISTANCE = re.compile(r"^([0-9.]+)\s+([A-Za-z]+)$")


def parse_ra(value: str) -> float:
    match = RA.match(value)
    if not match:
        raise ValueError(f"Invalid RA: {value}")
    hours, minutes, seconds = map(int, match.groups())
    return 15.0 * (hours + minutes / 60.0 + seconds / 3600.0)


def parse_dec(value: str) -> float:
    match = DEC.match(value)
    if not match:
        raise ValueError(f"Invalid declination: {value}")
    sign, degrees, minutes, seconds = match.groups()
    result = int(degrees) + int(minutes) / 60.0 + int(seconds) / 3600.0
    return -result if sign == "-" else result


def load_rows(path: Path, body: str) -> list[dict]:
    blocks = tychos_blocks(path.read_text(encoding="utf-8-sig"))
    key = body.lower()
    if key not in blocks:
        raise ValueError(f"{path} has no PLANET: {body.upper()} section")
    rows = []
    for line in blocks[key].splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 6 or not DATE.match(parts[0]):
            continue
        distance_match = DISTANCE.match(parts[4])
        if not distance_match or not parts[5].endswith("°"):
            raise ValueError(f"Malformed TYCHOS row: {line}")
        rows.append(
            {
                "timestamp": f"{parts[0]}T{parts[1]}",
                "ra_text": parts[2],
                "dec_text": parts[3],
                "distance_text": parts[4],
                "elongation_text": parts[5],
                "ra_deg": parse_ra(parts[2]),
                "dec_deg": parse_dec(parts[3]),
                "distance": float(distance_match.group(1)),
                "distance_unit": distance_match.group(2),
                "elongation_deg": float(parts[5][:-1]),
            }
        )
    if not rows:
        raise ValueError(f"No {body} rows parsed from {path}")
    return rows


def directions(rows: list[dict]) -> np.ndarray:
    ra = np.deg2rad([row["ra_deg"] for row in rows])
    dec = np.deg2rad([row["dec_deg"] for row in rows])
    return np.column_stack(
        (np.sin(ra) * np.cos(dec), np.sin(dec), np.cos(ra) * np.cos(dec))
    )


def compare(baseline: Path, candidate: Path, body: str) -> tuple[str, bool]:
    old = load_rows(baseline, body)
    new = load_rows(candidate, body)
    count_equal = len(old) == len(new)
    count = min(len(old), len(new))
    timestamp_mismatches = sum(
        old[index]["timestamp"] != new[index]["timestamp"] for index in range(count)
    )
    fields = ("ra_text", "dec_text", "distance_text", "elongation_text")
    mismatches = {
        field: sum(old[index][field] != new[index][field] for index in range(count))
        for field in fields
    }

    angular = np.rad2deg(
        np.arccos(
            np.clip(
                np.sum(directions(old[:count]) * directions(new[:count]), axis=1),
                -1.0,
                1.0,
            )
        )
    )
    same_units = all(
        old[index]["distance_unit"] == new[index]["distance_unit"]
        for index in range(count)
    )
    distance_delta = max(
        (abs(old[index]["distance"] - new[index]["distance"]) for index in range(count)),
        default=math.nan,
    )
    elongation_delta = max(
        (
            abs(
                ((new[index]["elongation_deg"] - old[index]["elongation_deg"] + 180.0) % 360.0)
                - 180.0
            )
            for index in range(count)
        ),
        default=math.nan,
    )
    accepted = (
        count_equal
        and timestamp_mismatches == 0
        and same_units
        and all(value == 0 for value in mismatches.values())
    )
    lines = [
        f"# {body} TYCHOS export-equivalence comparison",
        "",
        f"Status: **{'PASS' if accepted else 'FAIL'}**  ",
        f"Baseline: `{baseline.as_posix()}`  ",
        f"Candidate: `{candidate.as_posix()}`",
        "",
        "This compares formatted TYCHOS output before and after a structural refactor.",
        "It does not compare either export with JPL.",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Baseline / candidate rows | {len(old)} / {len(new)} |",
        f"| Timestamp mismatches | {timestamp_mismatches} |",
        f"| RA text mismatches | {mismatches['ra_text']} |",
        f"| Declination text mismatches | {mismatches['dec_text']} |",
        f"| Distance text mismatches | {mismatches['distance_text']} |",
        f"| Elongation text mismatches | {mismatches['elongation_text']} |",
        f"| Direction RMS / maximum | {math.sqrt(float(np.mean(angular * angular))):.12g} / {float(np.max(angular)):.12g} deg |",
        f"| Maximum displayed-distance numeric delta | {distance_delta:.12g} |",
        f"| Maximum elongation delta | {elongation_delta:.12g} deg |",
        f"| Distance units identical | {'yes' if same_units else 'no'} |",
        "",
        "A pass means every timestamp and every displayed RA, declination, distance and",
        "elongation field is identical. It supports export equivalence at TYCHOS text",
        "precision; it does not establish physical correctness.",
        "",
    ]
    return "\n".join(lines), accepted


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body", default="eros")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "00-backup/new-baseline/eros_ephemerides_before.txt",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "edits/data/raw/eros_ephemerides_after.txt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "edits/reports/declarative_hierarchy_eros_equivalence_report.md",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        report, accepted = compare(
            args.baseline.resolve(), args.candidate.resolve(), args.body
        )
    except (OSError, ValueError) as error:
        accepted = False
        report = "\n".join(
            [
                f"# {args.body} TYCHOS export-equivalence comparison",
                "",
                "Status: **INCOMPLETE**  ",
                f"Baseline: `{args.baseline.resolve().as_posix()}`  ",
                f"Candidate: `{args.candidate.resolve().as_posix()}`",
                "",
                f"The direct comparison could not run: `{error}`",
                "",
                "This is a missing/invalid-input result, not a scientific mismatch.",
                "",
            ]
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {args.output.resolve()}")
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
