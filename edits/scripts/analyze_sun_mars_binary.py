#!/usr/bin/env python3
"""Summarize the Phase 2.5 Sun-Mars common-centre diagnostic export."""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "edits" / "data" / "raw" / "sun_mars_binary.csv"
DEFAULT_OUTPUT = ROOT / "edits" / "reports" / "sun_mars_binary_report.md"


@dataclass(frozen=True)
class Centre:
    prefix: str
    label: str
    interpretation: str


CENTRES = (
    Centre(
        "earth",
        "Legacy Earth pivot",
        "Existing shared parent inherited by the Sun and Mars chains.",
    ),
    Centre(
        "pvp",
        "PVP / SystemCenter",
        "Existing model origin; independent of the sampled Sun and Mars positions.",
    ),
    Centre(
        "midpoint",
        "Geometric midpoint",
        "Per-sample mathematical control derived from the Sun and Mars positions.",
    ),
)


def finite(values: list[float]) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    return data[np.isfinite(data)]


def column(rows: list[dict[str, str]], name: str) -> np.ndarray:
    values = []
    for row in rows:
        text = row.get(name, "").strip()
        if not text:
            continue
        try:
            values.append(float(text))
        except ValueError as exc:
            raise ValueError(f"Invalid numeric value in {name!r}: {text!r}") from exc
    return finite(values)


def stats(values: np.ndarray) -> dict[str, float]:
    if values.size == 0:
        return {key: math.nan for key in ("mean", "std", "rms", "min", "max")}
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "rms": float(np.sqrt(np.mean(values * values))),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def fmt(value: float, digits: int = 6) -> str:
    return "n/a" if not math.isfinite(value) else f"{value:.{digits}f}"


def relative_std(values: np.ndarray) -> float:
    if values.size == 0:
        return math.nan
    mean = float(np.mean(values))
    return math.nan if abs(mean) < 1e-15 else 100.0 * float(np.std(values)) / abs(mean)


def centre_excursion(rows: list[dict[str, str]], prefix: str) -> float:
    axes = [column(rows, f"{prefix}_center_{axis}") for axis in "xyz"]
    if not axes or any(axis.size != len(rows) for axis in axes):
        return math.nan
    points = np.column_stack(axes)
    mean_point = np.mean(points, axis=0)
    return float(np.max(np.linalg.norm(points - mean_point, axis=1)))


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []

    required = {"date", "time", "sun_mars_separation"}
    for centre in CENTRES:
        required.update(
            {
                f"{centre.prefix}_sun_radius",
                f"{centre.prefix}_mars_radius",
                f"{centre.prefix}_radius_ratio",
                f"{centre.prefix}_opposition_error_deg",
                *(f"{centre.prefix}_center_{axis}" for axis in "xyz"),
            }
        )
    missing = sorted(required.difference(fields))
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    if not rows:
        raise ValueError("CSV contains no diagnostic samples")
    return fields, rows


def build_report(source: Path, rows: list[dict[str, str]]) -> str:
    separation = stats(column(rows, "sun_mars_separation"))
    start = f"{rows[0]['date']} {rows[0]['time']}"
    end = f"{rows[-1]['date']} {rows[-1]['time']}"

    lines = [
        "# Sun-Mars binary diagnostic",
        "",
        f"Source: `{source.as_posix()}`  ",
        f"Interval: `{start}` to `{end}`  ",
        f"Samples: `{len(rows)}`",
        "",
        "All distances are TYCHOS scene units. This report measures the existing",
        "geometry; it does not fit or apply a new orbit.",
        "",
        "## Common-centre comparison",
        "",
        "| Candidate centre | Sun radius mean (CV) | Mars radius mean (CV) | Radius ratio mean +/- std | Opposition error RMS / max | Centre excursion |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for centre in CENTRES:
        prefix = centre.prefix
        sun = column(rows, f"{prefix}_sun_radius")
        mars = column(rows, f"{prefix}_mars_radius")
        ratio = column(rows, f"{prefix}_radius_ratio")
        opposition = column(rows, f"{prefix}_opposition_error_deg")
        sun_stats = stats(sun)
        mars_stats = stats(mars)
        ratio_stats = stats(ratio)
        opposition_stats = stats(opposition)
        excursion = centre_excursion(rows, prefix)
        lines.append(
            "| "
            + " | ".join(
                [
                    centre.label,
                    f"{fmt(sun_stats['mean'])} ({fmt(relative_std(sun), 3)}%)",
                    f"{fmt(mars_stats['mean'])} ({fmt(relative_std(mars), 3)}%)",
                    f"{fmt(ratio_stats['mean'])} +/- {fmt(ratio_stats['std'])}",
                    f"{fmt(opposition_stats['rms'])} deg / {fmt(opposition_stats['max'])} deg",
                    fmt(excursion),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "Sun-Mars separation is centre-independent:",
            f"mean `{fmt(separation['mean'])}`, range `{fmt(separation['min'])}` to `{fmt(separation['max'])}`.",
            "",
            "## Interpretation",
            "",
            "- The geometric midpoint must show equal radii and zero opposition error by definition. It is a control, not evidence for a physical barycentre.",
            "- The Earth pivot and PVP/SystemCenter are independent candidates already present in the model. Lower opposition error and a more stable radius ratio would make one a cleaner binary coordinate description.",
            "- Centre excursion describes motion in the current scene axes; it is not an ephemeris error and should not be minimized by itself.",
            "- A future constrained binary phase should be accepted only if it preserves or improves independent ephemerides and event checks, not merely these internal diagnostics.",
            "",
            "## Candidate definitions",
            "",
        ]
    )
    for centre in CENTRES:
        lines.append(f"- **{centre.label}:** {centre.interpretation}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a TYCHOS Phase 2.5 Sun-Mars binary CSV export."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    _, rows = load_rows(source)
    report = build_report(source, rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
