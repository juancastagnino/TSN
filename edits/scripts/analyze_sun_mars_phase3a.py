#!/usr/bin/env python3
"""Phase 3A: screen fixed-ratio Sun-Mars common-centre paths."""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "edits" / "data" / "raw" / "sun_mars_binary.csv"
DEFAULT_REPORT = ROOT / "edits" / "reports" / "sun_mars_phase3a_report.md"
DEFAULT_TABLE = ROOT / "edits" / "reports" / "sun_mars_phase3a_candidates.csv"


@dataclass
class Candidate:
    ratio: float
    pvp_radius_mean: float
    pvp_radius_rms: float
    pvp_radius_cv_pct: float
    center_motion_rms: float
    center_excursion: float
    plane_rms: float
    circle_radius: float
    circle_residual_pct: float


def load_export(path: Path) -> tuple[list[datetime], np.ndarray, np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("The Phase 2.5 CSV contains no samples")

    required = [
        "date",
        "time",
        *(f"sun_world_{axis}" for axis in "xyz"),
        *(f"mars_world_{axis}" for axis in "xyz"),
        *(f"pvp_center_{axis}" for axis in "xyz"),
    ]
    missing = [name for name in required if name not in rows[0]]
    if missing:
        raise ValueError("CSV is missing required fields: " + ", ".join(missing))

    times = [
        datetime.fromisoformat(f"{row['date']}T{row['time']}") for row in rows
    ]

    def vectors(prefix: str) -> np.ndarray:
        return np.asarray(
            [[float(row[f"{prefix}_{axis}"]) for axis in "xyz"] for row in rows],
            dtype=float,
        )

    return times, vectors("sun_world"), vectors("mars_world"), vectors("pvp_center")


def ratio_to_weight(ratio: float) -> float:
    """Return the Sun coefficient in C = a*Sun + (1-a)*Mars."""
    if math.isinf(ratio):
        return 1.0
    return ratio / (1.0 + ratio)


def weight_to_ratio(weight: float) -> float:
    if weight <= 0.0:
        return 0.0
    if weight >= 1.0:
        return math.inf
    return weight / (1.0 - weight)


def weighted_center(sun: np.ndarray, mars: np.ndarray, ratio: float) -> np.ndarray:
    weight = ratio_to_weight(ratio)
    return weight * sun + (1.0 - weight) * mars


def optimal_weight(mars: np.ndarray, difference: np.ndarray) -> float:
    denominator = float(np.sum(difference * difference))
    if denominator <= 0.0:
        return 0.5
    return float(np.clip(-np.sum(mars * difference) / denominator, 0.0, 1.0))


def closest_pvp_ratio(sun_rel: np.ndarray, mars_rel: np.ndarray) -> float:
    return weight_to_ratio(optimal_weight(mars_rel, sun_rel - mars_rel))


def least_motion_ratio(sun_rel: np.ndarray, mars_rel: np.ndarray) -> float:
    sun_centered = sun_rel - np.mean(sun_rel, axis=0)
    mars_centered = mars_rel - np.mean(mars_rel, axis=0)
    return weight_to_ratio(
        optimal_weight(mars_centered, sun_centered - mars_centered)
    )


def path_metrics(center_rel: np.ndarray, ratio: float) -> Candidate:
    pvp_radii = np.linalg.norm(center_rel, axis=1)
    radius_mean = float(np.mean(pvp_radii))
    radius_rms = float(np.sqrt(np.mean(pvp_radii**2)))
    radius_cv = (
        100.0 * float(np.std(pvp_radii)) / radius_mean
        if radius_mean > 1e-15
        else math.nan
    )

    mean_center = np.mean(center_rel, axis=0)
    centered = center_rel - mean_center
    distances_from_mean = np.linalg.norm(centered, axis=1)
    motion_rms = float(np.sqrt(np.mean(distances_from_mean**2)))
    excursion = float(np.max(distances_from_mean))

    covariance = centered.T @ centered / len(centered)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    basis = eigenvectors[:, order]
    projected = centered @ basis
    x = projected[:, 0]
    y = projected[:, 1]
    z = projected[:, 2]
    plane_rms = float(np.sqrt(np.mean(z**2)))

    design = np.column_stack((2.0 * x, 2.0 * y, np.ones_like(x)))
    circle_x, circle_y, constant = np.linalg.lstsq(
        design, x * x + y * y, rcond=None
    )[0]
    radius_squared = constant + circle_x**2 + circle_y**2
    circle_radius = math.sqrt(max(float(radius_squared), 0.0))
    in_plane_radius = np.sqrt((x - circle_x) ** 2 + (y - circle_y) ** 2)
    radial_error = in_plane_radius - circle_radius
    residual = float(np.sqrt(np.mean(radial_error**2 + z**2)))
    residual_pct = (
        100.0 * residual / circle_radius if circle_radius > 1e-15 else math.nan
    )

    return Candidate(
        ratio=ratio,
        pvp_radius_mean=radius_mean,
        pvp_radius_rms=radius_rms,
        pvp_radius_cv_pct=radius_cv,
        center_motion_rms=motion_rms,
        center_excursion=excursion,
        plane_rms=plane_rms,
        circle_radius=circle_radius,
        circle_residual_pct=residual_pct,
    )


def dominant_periods(
    times: list[datetime], center_rel: np.ndarray, count: int = 4
) -> list[tuple[float, float]]:
    if len(times) < 8:
        return []
    day_positions = np.asarray(
        [(time - times[0]).total_seconds() / 86400.0 for time in times]
    )
    steps = np.diff(day_positions)
    step = float(np.median(steps))
    if step <= 0.0 or np.max(np.abs(steps - step)) > max(1e-7, step * 1e-6):
        return []

    sample_axis = np.arange(len(times), dtype=float)
    detrended = np.empty_like(center_rel)
    for axis in range(3):
        slope, intercept = np.polyfit(sample_axis, center_rel[:, axis], 1)
        detrended[:, axis] = center_rel[:, axis] - (
            slope * sample_axis + intercept
        )
    window = np.hanning(len(times))[:, None]
    spectrum = np.fft.rfft(detrended * window, axis=0)
    power = np.sum(np.abs(spectrum) ** 2, axis=1)
    frequencies = np.fft.rfftfreq(len(times), d=step)
    power[0] = 0.0

    duration = day_positions[-1] - day_positions[0]
    periods = np.full_like(frequencies, np.inf)
    np.divide(1.0, frequencies, out=periods, where=frequencies > 0.0)
    valid = (frequencies > 0.0) & (periods >= 2.0 * step)
    valid &= periods <= max(duration, step)
    indices = np.where(valid)[0]
    local = [
        index
        for index in indices
        if 0 < index < len(power) - 1
        and power[index] >= power[index - 1]
        and power[index] >= power[index + 1]
    ]
    total_power = float(np.sum(power[valid]))
    selected: list[tuple[float, float]] = []
    for index in sorted(local, key=lambda item: power[item], reverse=True):
        period = 1.0 / frequencies[index]
        if any(abs(period - prior[0]) / prior[0] < 0.03 for prior in selected):
            continue
        fraction = 100.0 * float(power[index]) / total_power if total_power else 0.0
        if fraction < 0.01:
            continue
        selected.append((float(period), fraction))
        if len(selected) == count:
            break
    return selected


def unique_ratios(values: list[float]) -> list[float]:
    result = []
    for value in values:
        if math.isnan(value) or value <= 0.0:
            continue
        if math.isinf(value):
            if not any(math.isinf(existing) for existing in result):
                result.append(value)
            continue
        if not any(
            math.isfinite(existing)
            and abs(math.log(value / existing)) < 1e-8
            for existing in result
        ):
            result.append(value)
    return result


def write_table(path: Path, candidates: list[Candidate]) -> None:
    fields = list(Candidate.__dataclass_fields__)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(candidate.__dict__)


def fmt(value: float, digits: int = 6) -> str:
    return "n/a" if not math.isfinite(value) else f"{value:.{digits}f}"


def fmt_ratio(value: float) -> str:
    if math.isinf(value):
        return "infinity (Sun endpoint)"
    return fmt(value)


def build_report(
    source: Path,
    times: list[datetime],
    sun_rel: np.ndarray,
    mars_rel: np.ndarray,
    named: list[tuple[str, Candidate]],
    ratio_min: float,
    ratio_max: float,
) -> str:
    lines = [
        "# Sun-Mars Phase 3A weighted-centre screen",
        "",
        f"Source: `{source.as_posix()}`  ",
        f"Interval: `{times[0].isoformat(sep=' ')}` to `{times[-1].isoformat(sep=' ')}`  ",
        f"Samples: `{len(times)}`",
        "",
        "For a fixed radius ratio `k = Mars radius / Sun radius`, every candidate",
        "is constructed on the instantaneous Sun-Mars line as",
        "`C = (k*Sun + Mars)/(1+k)`. Exact opposition and a constant ratio are",
        "therefore construction constraints, not evidence. The discriminating",
        "measurements are the resulting centre path relative to PVP/SystemCenter.",
        f"The finite grid covers `k={ratio_min:g}` through `k={ratio_max:g}`.",
        "",
        "## Candidate comparison",
        "",
        "| Candidate | k | PVP radius mean / RMS | PVP radius CV | Motion RMS / max excursion | Plane RMS | Best-circle radius | 3-D circle residual |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, candidate in named:
        lines.append(
            "| "
            + " | ".join(
                [
                    label,
                    fmt_ratio(candidate.ratio),
                    f"{fmt(candidate.pvp_radius_mean)} / {fmt(candidate.pvp_radius_rms)}",
                    f"{fmt(candidate.pvp_radius_cv_pct, 3)}%",
                    f"{fmt(candidate.center_motion_rms)} / {fmt(candidate.center_excursion)}",
                    fmt(candidate.plane_rms),
                    fmt(candidate.circle_radius),
                    f"{fmt(candidate.circle_residual_pct, 3)}%",
                ]
            )
            + " |"
        )

    by_label = dict(named)
    pvp_optimum = by_label["Minimum PVP RMS (analytic)"]
    motion_optimum = by_label["Minimum center motion (analytic)"]
    cv_optimum = by_label["Minimum PVP-radius CV (grid)"]
    circle_optimum = by_label["Minimum circle residual (grid)"]
    lines.extend(["", "## Screening result", ""])
    if math.isinf(pvp_optimum.ratio) and math.isinf(motion_optimum.ratio):
        lines.append(
            "- Both analytic objectives collapse to the Sun endpoint (`k -> infinity`), not to an interior common centre."
        )
    else:
        lines.append(
            f"- The analytic PVP-distance optimum is `k={fmt_ratio(pvp_optimum.ratio)}` and the minimum-motion optimum is `k={fmt_ratio(motion_optimum.ratio)}`."
        )
    if math.isclose(cv_optimum.ratio, ratio_max) and math.isclose(
        circle_optimum.ratio, ratio_max
    ):
        lines.append(
            "- Both finite-grid shape criteria improve through the upper search boundary, so the scan identifies no finite preferred ratio."
        )
    else:
        lines.append(
            f"- The PVP-radius-CV optimum is `k={fmt_ratio(cv_optimum.ratio)}` and the circle-residual optimum is `k={fmt_ratio(circle_optimum.ratio)}`."
        )
    lines.append(
        "- This means the current exported geometry does not naturally reduce to a compact, single-orbit interior binary centre under these tests."
    )

    lines.extend(
        [
            "",
            "## Dominant centre-path periods",
            "",
            "Finite-window FFT peaks after removing a linear trend. Percentages are",
            "fractions of the combined three-axis spectral power and are diagnostic",
            "only.",
            "",
            "| Candidate | Dominant periods |",
            "|---|---|",
        ]
    )
    reported = set()
    for label, candidate in named:
        key = math.inf if math.isinf(candidate.ratio) else round(
            math.log(candidate.ratio), 10
        )
        if key in reported:
            continue
        reported.add(key)
        center = weighted_center(sun_rel, mars_rel, candidate.ratio)
        periods = dominant_periods(times, center)
        period_text = "; ".join(
            f"{period:.2f} d ({fraction:.2f}%)" for period, fraction in periods
        ) or "not available"
        lines.append(f"| {label} | {period_text} |")

    lines.extend(
        [
            "",
            "## Methodological limits",
            "",
            "- Minimizing PVP distance assumes that a useful common centre should stay near the existing fixed PVP origin.",
            "- Minimizing motion assumes that the common centre should occupy the smallest region, regardless of its absolute offset.",
            "- Minimizing the circle residual assumes that a simple planar circle is the relevant compact geometry.",
            "- These are competing geometric hypotheses. A low value in one column is not permission to alter the hierarchy.",
            "- Any retained ratio must next reproduce independent Sun, Mars and event ephemerides after implementation.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Screen fixed-ratio Sun-Mars weighted centres from Phase 2.5."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--ratio-min", type=float, default=0.05)
    parser.add_argument("--ratio-max", type=float, default=20.0)
    parser.add_argument("--grid-size", type=int, default=1201)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.ratio_min <= 0.0 or args.ratio_max <= args.ratio_min:
        raise ValueError("Require 0 < ratio-min < ratio-max")
    if args.grid_size < 3:
        raise ValueError("grid-size must be at least 3")

    source = args.input.resolve()
    times, sun_world, mars_world, pvp_world = load_export(source)
    sun_rel = sun_world - pvp_world
    mars_rel = mars_world - pvp_world

    analytic_pvp = closest_pvp_ratio(sun_rel, mars_rel)
    analytic_motion = least_motion_ratio(sun_rel, mars_rel)
    grid = np.geomspace(args.ratio_min, args.ratio_max, args.grid_size)
    screened = [path_metrics(weighted_center(sun_rel, mars_rel, ratio), ratio) for ratio in grid]
    best_cv = min(screened, key=lambda item: item.pvp_radius_cv_pct)
    best_circle = min(screened, key=lambda item: item.circle_residual_pct)

    ratios = unique_ratios(
        [
            0.5,
            1.0,
            1.5,
            2.0,
            5.0,
            10.0,
            analytic_pvp,
            analytic_motion,
            best_cv.ratio,
            best_circle.ratio,
        ]
    )
    evaluated = {
        ratio: path_metrics(weighted_center(sun_rel, mars_rel, ratio), ratio)
        for ratio in ratios
    }

    definitions = [
        ("Reference k=0.5", 0.5),
        ("Equal-radius midpoint", 1.0),
        ("Reference k=1.5", 1.5),
        ("Reference k=2", 2.0),
        ("Reference k=5", 5.0),
        ("Reference k=10", 10.0),
        ("Minimum PVP RMS (analytic)", analytic_pvp),
        ("Minimum center motion (analytic)", analytic_motion),
        ("Minimum PVP-radius CV (grid)", best_cv.ratio),
        ("Minimum circle residual (grid)", best_circle.ratio),
    ]
    named = [(label, evaluated[ratio]) for label, ratio in definitions]

    report = build_report(
        source,
        times,
        sun_rel,
        mars_rel,
        named,
        args.ratio_min,
        args.ratio_max,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    write_table(args.table, screened)
    print(f"Wrote {args.report.resolve()}")
    print(f"Wrote {args.table.resolve()}")


if __name__ == "__main__":
    main()
