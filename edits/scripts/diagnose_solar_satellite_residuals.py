#!/usr/bin/env python3
"""Diagnose Mercury/Venus residuals without changing simulator settings.

The analysis uses the saved Sun, Mercury and Venus comparison CSVs to:

* compare planetary longitude residuals with the simultaneous Sun residual;
* fit annual, orbital, synodic and second-harmonic mean-motion arguments;
* repeat the fits in chronological blocks using one global phase origin; and
* extend the FFT search to 1000 days, covering Venus's ~584-day synodic cycle.

All fits are descriptive. They are not corrections applied to TYCHOS output.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
from settings_schema import settings_entries

from analyze_ephemerides import (
    equatorial_to_ecliptic,
    fft_peaks,
    fit_periods,
    read_comparison,
    rms,
    wrap_deg,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "edits" / "data" / "derived"
DEFAULT_REPORT_DIR = ROOT / "edits" / "reports"
MODEL_YEAR_DAYS = 365.2425
BODY_NAMES = ("mercury", "venus")


def load_body(path):
    rows = read_comparison(path)
    dates = [row["date"] for row in rows]
    epoch = dates[0]
    t_days = np.array([(date - epoch).total_seconds() / 86400.0 for date in dates])
    ty_lon, ty_lat = equatorial_to_ecliptic(
        [row["ty_ra_deg"] for row in rows],
        [row["ty_dec_deg"] for row in rows],
    )
    jpl_lon, jpl_lat = equatorial_to_ecliptic(
        [row["jpl_ra_deg"] for row in rows],
        [row["jpl_dec_deg"] for row in rows],
    )
    return {
        "dates": dates,
        "t_days": t_days,
        "dlon": wrap_deg(ty_lon - jpl_lon),
        "dlat": ty_lat - jpl_lat,
    }


def centered_rms(values):
    values = np.asarray(values, dtype=float)
    return rms(values - np.mean(values))


def period_from_speed(speed):
    return MODEL_YEAR_DAYS * 2.0 * math.pi / abs(speed)


def component_periods(settings, body):
    by_name = {item["name"]: item for item in settings}
    sun_speed = float(by_name["Sun"]["speed"])
    body_speed = float(by_name[body.capitalize()]["speed"])
    return [
        ("annual", period_from_speed(sun_speed)),
        ("orbital_mean_motion", period_from_speed(body_speed)),
        ("synodic_mean_motion", period_from_speed(body_speed - sun_speed)),
        ("second_orbital_harmonic", period_from_speed(2.0 * body_speed)),
    ]


def block_masks(dates):
    ranges = (
        (2000, 2004),
        (2005, 2009),
        (2010, 2014),
        (2015, 2019),
        (2020, 2026),
    )
    years = np.array([date.year for date in dates])
    return [
        (f"{start}-{stop}", (years >= start) & (years <= stop))
        for start, stop in ranges
    ]


def fit_components(t_days, residual, components, mask=None):
    if mask is None:
        mask = np.ones(len(t_days), dtype=bool)
    fitted, _, remainder, offset, trend = fit_periods(
        t_days[mask], residual[mask], components
    )
    return {
        "n": int(np.count_nonzero(mask)),
        "raw_centered_rms_deg": centered_rms(residual[mask]),
        "joint_remainder_rms_deg": rms(remainder),
        "offset_deg": offset,
        "trend_deg_per_day": trend,
        "components": fitted,
    }


def amplitude(result, name):
    return next(
        component["amplitude_deg"]
        for component in result["components"]
        if component["name"] == name
    )


def sun_relationship(planet, sun, components):
    if planet["dates"] != sun["dates"]:
        raise ValueError("Sun and planet comparison timestamps do not match")

    output = []
    masks = [("all", np.ones(len(planet["dates"]), dtype=bool))]
    masks.extend(block_masks(planet["dates"]))
    for label, mask in masks:
        x = np.asarray(sun["dlon"][mask], dtype=float)
        y = np.asarray(planet["dlon"][mask], dtype=float)
        x_centered = x - np.mean(x)
        y_centered = y - np.mean(y)
        denominator = float(np.dot(x_centered, x_centered))
        beta = float(np.dot(x_centered, y_centered) / denominator)
        correlation = float(np.corrcoef(x_centered, y_centered)[0, 1])
        adjusted = y_centered - beta * x_centered
        before = rms(y_centered)
        after = rms(adjusted)

        original_fit = fit_components(
            planet["t_days"], planet["dlon"], [components[0]], mask
        )
        adjusted_fit = fit_components(
            planet["t_days"][mask], adjusted, [components[0]]
        )
        output.append(
            {
                "block": label,
                "n": int(np.count_nonzero(mask)),
                "correlation": correlation,
                "ols_beta": beta,
                "centered_rms_before_deg": before,
                "centered_rms_after_sun_regression_deg": after,
                "rms_reduction_percent": 100.0 * (before - after) / before,
                "annual_amplitude_before_deg": amplitude(original_fit, "annual"),
                "annual_amplitude_after_sun_regression_deg": amplitude(
                    adjusted_fit, "annual"
                ),
            }
        )
    return output


def fmt(value, digits=4):
    return f"{value:.{digits}f}"


def markdown_report(result):
    lines = [
        "# Mercury/Venus residual attribution",
        "",
        "This is a read-only diagnostic of the current simulator export. Harmonic",
        "fits characterize residuals; they are not corrections applied to TYCHOS.",
        "Phases in every chronological block use the first dataset timestamp as the",
        "same zero point, so changes between blocks are directly comparable.",
        "",
        "## Dataset",
        "",
        f"- Interval: `{result['dataset']['start']}` to `{result['dataset']['stop']}`.",
        f"- Samples per body: `{result['dataset']['samples']}`.",
        f"- Median cadence: `{result['dataset']['cadence_hours']:.3f}` hours.",
        "- Ecliptic residuals use the fixed J2000-obliquity diagnostic rotation.",
        "",
    ]

    for body in BODY_NAMES:
        info = result[body]
        lines.extend(
            [
                f"## {body.capitalize()}",
                "",
                "### Model-derived periods",
                "",
                "| Argument | Period (days) |",
                "|---|---:|",
            ]
        )
        for name, period in info["periods"]:
            lines.append(f"| {name} | {period:.6f} |")

        lines.extend(
            [
                "",
                "### Joint full-interval fit",
                "",
                "| Argument | Amplitude (deg) | Phase at dataset epoch (deg) |",
                "|---|---:|---:|",
            ]
        )
        for component in info["full_fit"]["components"]:
            lines.append(
                f"| {component['name']} | {fmt(component['amplitude_deg'], 6)} | "
                f"{fmt(component['phase_deg_at_t0'], 3)} |"
            )
        lines.extend(
            [
                "",
                f"Centered longitude RMS before fit: `{fmt(info['full_fit']['raw_centered_rms_deg'], 6)}` deg.",
                f"Joint-fit remainder RMS: `{fmt(info['full_fit']['joint_remainder_rms_deg'], 6)}` deg.",
                "",
                "### Chronological amplitude and phase stability",
                "",
                "| Block | Argument | Amplitude (deg) | Phase (deg) |",
                "|---|---|---:|---:|",
            ]
        )
        for block in info["blocks"]:
            for component in block["fit"]["components"]:
                lines.append(
                    f"| {block['block']} | {component['name']} | "
                    f"{fmt(component['amplitude_deg'], 6)} | "
                    f"{fmt(component['phase_deg_at_t0'], 3)} |"
                )

        lines.extend(
            [
                "",
                "### Relationship to the Sun longitude residual",
                "",
                "| Block | Correlation | OLS beta | RMS before | RMS after | Reduction | Annual amp. before | Annual amp. after |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in info["sun_relationship"]:
            lines.append(
                f"| {row['block']} | {fmt(row['correlation'], 4)} | "
                f"{fmt(row['ols_beta'], 4)} | "
                f"{fmt(row['centered_rms_before_deg'], 4)} | "
                f"{fmt(row['centered_rms_after_sun_regression_deg'], 4)} | "
                f"{fmt(row['rms_reduction_percent'], 1)}% | "
                f"{fmt(row['annual_amplitude_before_deg'], 4)} | "
                f"{fmt(row['annual_amplitude_after_sun_regression_deg'], 4)} |"
            )

        lines.extend(
            [
                "",
                "### Extended FFT peaks (1-1000 days)",
                "",
                "| Rank | Period (days) | Amplitude (deg) |",
                "|---:|---:|---:|",
            ]
        )
        for rank, peak in enumerate(info["extended_fft"], 1):
            lines.append(
                f"| {rank} | {fmt(peak['period_days'], 3)} | "
                f"{fmt(peak['amplitude_deg'], 6)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Reading this report",
            "",
            "- Stable amplitude and phase across blocks support a repeatable geometric argument.",
            "- Systematic phase rotation suggests a mean-rate mismatch or modulation.",
            "- Strong Sun correlation suggests shared geometry or reference-frame structure; it does not prove the cause.",
            "- The Sun regression is diagnostic only and must not be applied as an ephemeris correction.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()

    settings_path = ROOT / "src" / "settings" / "celestial-settings.json"
    settings = settings_entries(settings_path)
    data = {
        body: load_body(args.data_dir / f"{body}_comparison.csv")
        for body in ("sun", *BODY_NAMES)
    }
    if not (data["sun"]["dates"] == data["mercury"]["dates"] == data["venus"]["dates"]):
        raise ValueError("Sun, Mercury and Venus comparison timestamps must match")

    dt = np.diff(data["sun"]["t_days"])
    result = {
        "dataset": {
            "start": data["sun"]["dates"][0].isoformat(sep=" "),
            "stop": data["sun"]["dates"][-1].isoformat(sep=" "),
            "samples": len(data["sun"]["dates"]),
            "cadence_hours": float(np.median(dt) * 24.0),
        }
    }

    for body in BODY_NAMES:
        periods = component_periods(settings, body)
        full_fit = fit_components(data[body]["t_days"], data[body]["dlon"], periods)
        blocks = []
        for label, mask in block_masks(data[body]["dates"]):
            blocks.append(
                {
                    "block": label,
                    "fit": fit_components(
                        data[body]["t_days"], data[body]["dlon"], periods, mask
                    ),
                }
            )
        result[body] = {
            "periods": periods,
            "full_fit": full_fit,
            "blocks": blocks,
            "sun_relationship": sun_relationship(data[body], data["sun"], periods),
            "extended_fft": fft_peaks(
                data[body]["t_days"],
                data[body]["dlon"],
                min_period=1.0,
                max_period=1000.0,
                n_peaks=20,
            ),
        }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "solar_satellite_residual_diagnostics.json"
    md_path = args.report_dir / "solar_satellite_residual_diagnostics.md"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown_report(result), encoding="utf-8")
    print(md_path.relative_to(ROOT))
    print(json_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
