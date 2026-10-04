#!/usr/bin/env python3
"""Phase 3B: analyze Mars as an asymmetric companion relative to the Sun."""

from __future__ import annotations

import argparse
import csv
import math
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "edits" / "data" / "raw" / "sun_mars_binary.csv"
DEFAULT_REPORT = ROOT / "edits" / "reports" / "sun_mars_asymmetric_report.md"
DEFAULT_RELATIVE = ROOT / "edits" / "data" / "derived" / "sun_mars_relative.csv"


def load_export(
    path: Path,
) -> tuple[list[datetime], np.ndarray, np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("The Phase 2.5 CSV contains no samples")

    required = [
        "date",
        "time",
        *(f"sun_world_{axis}" for axis in "xyz"),
        *(f"mars_world_{axis}" for axis in "xyz"),
        *(f"earth_center_{axis}" for axis in "xyz"),
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

    return (
        times,
        vectors("sun_world"),
        vectors("mars_world"),
        vectors("earth_center"),
    )


def day_axis(times: list[datetime]) -> tuple[np.ndarray, float]:
    days = np.asarray(
        [(timestamp - times[0]).total_seconds() / 86400.0 for timestamp in times]
    )
    steps = np.diff(days)
    step = float(np.median(steps))
    if step <= 0.0 or np.max(np.abs(steps - step)) > max(1e-7, step * 1e-6):
        raise ValueError("Phase 3B requires a uniformly sampled export")
    return days, step


def fit_origin_plane(relative: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    second_moment = relative.T @ relative / len(relative)
    eigenvalues, eigenvectors = np.linalg.eigh(second_moment)
    normal = eigenvectors[:, np.argmin(eigenvalues)]
    if normal[1] < 0.0:
        normal = -normal

    in_plane_moment = second_moment - np.outer(
        normal, second_moment @ normal
    )
    plane_values, plane_vectors = np.linalg.eigh(in_plane_moment)
    first_axis = plane_vectors[:, np.argmax(plane_values)]
    first_axis -= normal * np.dot(first_axis, normal)
    first_axis /= np.linalg.norm(first_axis)
    second_axis = np.cross(normal, first_axis)
    second_axis /= np.linalg.norm(second_axis)
    return normal, first_axis, second_axis


def dominant_periods(
    days: np.ndarray, relative: np.ndarray, count: int = 5
) -> list[tuple[float, float]]:
    step = float(np.median(np.diff(days)))
    index = np.arange(len(days), dtype=float)
    detrended = np.empty_like(relative)
    for axis in range(3):
        slope, intercept = np.polyfit(index, relative[:, axis], 1)
        detrended[:, axis] = relative[:, axis] - (slope * index + intercept)

    spectrum = np.fft.rfft(detrended * np.hanning(len(days))[:, None], axis=0)
    power = np.sum(np.abs(spectrum) ** 2, axis=1)
    frequencies = np.fft.rfftfreq(len(days), d=step)
    periods = np.full_like(frequencies, np.inf)
    np.divide(1.0, frequencies, out=periods, where=frequencies > 0.0)
    valid = (periods >= 2.0 * step) & (periods <= days[-1])
    power[~valid] = 0.0
    total_power = float(np.sum(power))

    peaks = [
        idx
        for idx in range(1, len(power) - 1)
        if power[idx] >= power[idx - 1] and power[idx] >= power[idx + 1]
    ]
    selected: list[tuple[float, float]] = []
    for idx in sorted(peaks, key=lambda item: power[item], reverse=True):
        if power[idx] <= 0.0:
            continue
        period = float(periods[idx])
        if any(abs(period - prior[0]) / prior[0] < 0.03 for prior in selected):
            continue
        fraction = 100.0 * float(power[idx]) / total_power if total_power else 0.0
        if fraction < 0.01:
            continue
        selected.append((period, fraction))
        if len(selected) == count:
            break
    return selected


def recurrence_error(relative: np.ndarray, period_days: float, step_days: float) -> float:
    lag = max(1, int(round(period_days / step_days)))
    if lag >= len(relative):
        return math.nan
    differences = relative[lag:] - relative[:-lag]
    rms = float(np.sqrt(np.mean(np.sum(differences**2, axis=1))))
    mean_radius = float(np.mean(np.linalg.norm(relative, axis=1)))
    return 100.0 * rms / mean_radius


def write_relative_csv(
    path: Path,
    times: list[datetime],
    relative: np.ndarray,
    distances: np.ndarray,
    plane_height: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["date", "time", "mars_from_sun_x", "mars_from_sun_y", "mars_from_sun_z", "distance", "plane_height"]
        )
        for timestamp, vector, distance, height in zip(
            times, relative, distances, plane_height
        ):
            writer.writerow(
                [
                    timestamp.date().isoformat(),
                    timestamp.time().isoformat(),
                    *vector,
                    distance,
                    height,
                ]
            )


def fmt(value: float, digits: int = 6) -> str:
    return "n/a" if not math.isfinite(value) else f"{value:.{digits}f}"


def analyze(
    source: Path,
    times: list[datetime],
    sun_world: np.ndarray,
    mars_world: np.ndarray,
    earth_world: np.ndarray,
    relative_output: Path,
) -> str:
    relative = mars_world - sun_world
    distances = np.linalg.norm(relative, axis=1)
    days, step = day_axis(times)
    minimum_index = int(np.argmin(distances))
    maximum_index = int(np.argmax(distances))
    observed_ratio = float(distances[maximum_index] / distances[minimum_index])

    earth_mars = np.linalg.norm(mars_world - earth_world, axis=1)
    earth_minimum_index = int(np.argmin(earth_mars))
    earth_maximum_index = int(np.argmax(earth_mars))
    earth_observed_ratio = float(
        earth_mars[earth_maximum_index] / earth_mars[earth_minimum_index]
    )

    normal, first_axis, second_axis = fit_origin_plane(relative)
    x = relative @ first_axis
    y = relative @ second_axis
    height = relative @ normal
    planar_radius = np.sqrt(x * x + y * y)
    plane_rms = float(np.sqrt(np.mean(height**2)))
    mean_distance = float(np.mean(distances))
    plane_rms_pct = 100.0 * plane_rms / mean_distance
    inclination = math.degrees(math.acos(float(np.clip(abs(normal[1]), 0.0, 1.0))))

    theta = np.unwrap(np.arctan2(y, x))
    angular_slope, angular_intercept = np.polyfit(days, theta, 1)
    angular_period = 2.0 * math.pi / abs(float(angular_slope))
    angular_residual = theta - (angular_slope * days + angular_intercept)
    angular_residual_rms = math.degrees(
        float(np.sqrt(np.mean(angular_residual**2)))
    )

    inverse_radius = 1.0 / planar_radius
    conic_design = np.column_stack((np.ones_like(theta), np.cos(theta), np.sin(theta)))
    inverse_p, cosine_term, sine_term = np.linalg.lstsq(
        conic_design, inverse_radius, rcond=None
    )[0]
    semi_latus_rectum = 1.0 / inverse_p
    eccentricity = math.sqrt(cosine_term**2 + sine_term**2) / inverse_p
    predicted_inverse = conic_design @ np.asarray(
        [inverse_p, cosine_term, sine_term]
    )
    predicted_radius = 1.0 / predicted_inverse
    conic_radial_rms = float(
        np.sqrt(np.mean((planar_radius - predicted_radius) ** 2))
    )
    conic_radial_pct = 100.0 * conic_radial_rms / float(np.mean(planar_radius))
    predicted_apse_ratio = (
        (1.0 + eccentricity) / (1.0 - eccentricity)
        if 0.0 <= eccentricity < 1.0
        else math.nan
    )

    velocity = np.gradient(relative, days, axis=0)
    angular_momentum = np.cross(relative, velocity)
    momentum_norm = np.linalg.norm(angular_momentum, axis=1)
    valid = momentum_norm > 1e-12
    unit_momentum = angular_momentum[valid] / momentum_norm[valid, None]
    signs = np.sign(unit_momentum @ normal)
    signs[signs == 0.0] = 1.0
    unit_momentum *= signs[:, None]
    plane_angles = np.degrees(
        np.arccos(np.clip(unit_momentum @ normal, -1.0, 1.0))
    )
    normal_median = float(np.median(plane_angles))
    normal_p95 = float(np.percentile(plane_angles, 95))

    periods = dominant_periods(days, relative)
    primary_period = periods[0][0] if periods else angular_period
    primary_recurrence = recurrence_error(relative, primary_period, step)
    angular_recurrence = recurrence_error(relative, angular_period, step)

    write_relative_csv(relative_output, times, relative, distances, height)

    period_text = "; ".join(
        f"`{period:.2f} d` ({fraction:.2f}% power)" for period, fraction in periods
    ) or "not available"

    interpretation = []
    if plane_rms_pct < 1.0:
        interpretation.append(
            "The Sun-relative path is strongly planar over this interval."
        )
    else:
        interpretation.append(
            "The Sun-relative path is not well described by one fixed plane."
        )
    if conic_radial_pct < 1.0:
        interpretation.append(
            "A focus-at-Sun ellipse is a strong first-order description of its radial geometry."
        )
    else:
        interpretation.append(
            "A single focus-at-Sun ellipse leaves substantial radial structure."
        )
    if abs(observed_ratio - 7.0) > 1.0:
        interpretation.append(
            "The measured Sun-Mars distance ratio is not 7:1; that value refers to the Earth-Mars observable instead."
        )
    if abs(earth_observed_ratio - 7.0) / 7.0 < 0.1:
        interpretation.append(
            "The measured Earth-Mars maximum/minimum distance ratio is close to the stated 7:1 relationship."
        )

    lines = [
        "# Sun-Mars asymmetric primary-companion diagnostic",
        "",
        f"Source: `{source.as_posix()}`  ",
        f"Interval: `{times[0].isoformat(sep=' ')}` to `{times[-1].isoformat(sep=' ')}`  ",
        f"Samples: `{len(times)}` at `{fmt(step, 3)}`-day cadence",
        "",
        "Mars is measured directly from the Sun using `Mars_world - Sun_world`.",
        "No model position, setting or hierarchy transform is changed.",
        "",
        "## Distance and apses",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Mean Sun-Mars distance | {fmt(mean_distance)} model units |",
        f"| Minimum distance | {fmt(float(distances[minimum_index]))} on {times[minimum_index].date().isoformat()} |",
        f"| Maximum distance | {fmt(float(distances[maximum_index]))} on {times[maximum_index].date().isoformat()} |",
        f"| Observed maximum/minimum ratio | {fmt(observed_ratio)} : 1 |",
        f"| Focus-ellipse eccentricity | {fmt(eccentricity)} |",
        f"| Focus-ellipse predicted apse ratio | {fmt(predicted_apse_ratio)} : 1 |",
        f"| Focus-ellipse radial residual | {fmt(conic_radial_rms)} ({fmt(conic_radial_pct, 3)}%) |",
        f"| Semi-latus rectum | {fmt(semi_latus_rectum)} model units |",
        "",
        "## Earth-Mars distance clarification",
        "",
        "The claimed `7:1` relationship concerns maximum versus minimum distance",
        "from Earth to Mars, not the Sun-relative ellipse measured above.",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Minimum Earth-Mars distance | {fmt(float(earth_mars[earth_minimum_index]))} on {times[earth_minimum_index].date().isoformat()} |",
        f"| Maximum Earth-Mars distance | {fmt(float(earth_mars[earth_maximum_index]))} on {times[earth_maximum_index].date().isoformat()} |",
        f"| Earth-Mars maximum/minimum ratio | {fmt(earth_observed_ratio)} : 1 |",
        "",
        "## Plane and period",
        "",
        "The inclination below is relative to the model's un-tilted XZ orbital plane",
        "(Y-axis normal). It is not automatically the solar-equator inclination.",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Best origin-plane normal | X `{fmt(float(normal[0]))}`, Y `{fmt(float(normal[1]))}`, Z `{fmt(float(normal[2]))}` |",
        f"| Plane inclination to model XZ plane | {fmt(inclination)} deg |",
        f"| Out-of-plane RMS | {fmt(plane_rms)} ({fmt(plane_rms_pct, 3)}%) |",
        f"| Instantaneous plane-normal deviation, median / P95 | {fmt(normal_median)} / {fmt(normal_p95)} deg |",
        f"| Mean angular-sweep period | {fmt(angular_period)} days |",
        f"| Linear-angle residual RMS | {fmt(angular_residual_rms)} deg |",
        f"| Dominant spectral periods | {period_text} |",
        f"| Recurrence error at dominant period | {fmt(primary_recurrence, 3)}% of mean radius |",
        f"| Recurrence error at angular-sweep period | {fmt(angular_recurrence, 3)}% of mean radius |",
        "",
        "## Interpretation",
        "",
        *(f"- {item}" for item in interpretation),
        "- A clean relative orbit would support an asymmetric primary-companion representation, but would not by itself establish a new physical classification.",
        "- The fitted plane and conic are diagnostics only; they are not corrections applied to TYCHOS.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Mars as an asymmetric companion relative to the Sun."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--relative-output", type=Path, default=DEFAULT_RELATIVE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    times, sun_world, mars_world, earth_world = load_export(source)
    report = analyze(
        source,
        times,
        sun_world,
        mars_world,
        earth_world,
        args.relative_output.resolve(),
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report.resolve()}")
    print(f"Wrote {args.relative_output.resolve()}")


if __name__ == "__main__":
    main()
