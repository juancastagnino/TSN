#!/usr/bin/env python3
"""Generate a compact Markdown report from analyze_lunar_residuals.py outputs.

Example:
    py edits/scripts/generate_report.py \
        --summary edits/reports/lunar_summary.json \
        --components edits/reports/lunar_periodic_components.csv \
        --annual edits/reports/lunar_annual_stats.csv \
        --output edits/reports/lunar_ephemeris_report.md

Optionally provide --baseline-summary to add before/after improvement figures.
"""

import argparse
import csv
import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path):
    if not path:
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt(x, digits=4):
    if x is None or x == "":
        return "—"
    return f"{float(x):.{digits}f}"


def improvement(old, new):
    if not old:
        return None
    return 100.0 * (old - new) / old


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", required=True)
    p.add_argument("--components")
    p.add_argument("--annual")
    p.add_argument("--baseline-summary")
    p.add_argument("--model-label", default="Current TYCHOS lunar-plane branch")
    p.add_argument("--output", default="edits/reports/lunar_ephemeris_report.md")
    args = p.parse_args()

    s = load_json(args.summary)
    baseline = load_json(args.baseline_summary) if args.baseline_summary else None
    components = load_csv(args.components)
    annual = load_csv(args.annual)

    lines = []
    lines.append("# TYCHOS Lunar Ephemeris Audit")
    lines.append("")
    lines.append(f"**Model:** {args.model_label}")
    lines.append("")
    lines.append("## Dataset")
    lines.append("")
    lines.append(f"- Samples: **{s['n_samples']}**")
    lines.append(f"- Interval: **{s['start']} → {s['stop']}**")
    lines.append(f"- Median cadence: **{fmt(s.get('cadence_hours_median'), 3)} h**")
    lines.append(f"- Reference: **{s['reference']}**")
    lines.append(f"- Ecliptic residual analysis: {s['ecliptic_rotation']}")
    lines.append("")

    lines.append("## Current residuals")
    lines.append("")
    lines.append("| Metric | RMS | P95 abs. | Max abs. |")
    lines.append("|---|---:|---:|---:|")
    for label, key in [
        ("Declination", "declination_residual"),
        ("Angular separation", "angular_separation"),
        ("Ecliptic longitude", "ecliptic_longitude_residual"),
        ("Ecliptic latitude", "ecliptic_latitude_residual"),
    ]:
        d = s[key]
        lines.append(
            f"| {label} | {fmt(d['rms_deg'])}° | {fmt(d['p95_abs_deg'])}° | {fmt(d['max_abs_deg'])}° |"
        )
    lines.append("")

    if baseline:
        lines.append("## Baseline comparison")
        lines.append("")
        lines.append("| Metric | Baseline RMS | Current RMS | Improvement |")
        lines.append("|---|---:|---:|---:|")
        for label, key in [
            ("Declination", "declination_residual"),
            ("Angular separation", "angular_separation"),
            ("Ecliptic longitude", "ecliptic_longitude_residual"),
            ("Ecliptic latitude", "ecliptic_latitude_residual"),
        ]:
            old = baseline[key]["rms_deg"]
            new = s[key]["rms_deg"]
            imp = improvement(old, new)
            lines.append(f"| {label} | {fmt(old)}° | {fmt(new)}° | {fmt(imp, 2)}% |")
        lines.append("")

    pf = s.get("primary_period_fit", {})
    if pf:
        lines.append("## Longitudinal residual structure")
        lines.append("")
        lines.append(
            "A joint sinusoidal fit is used here as a diagnostic fingerprint of the residual, "
            "not as a claim about physical causation."
        )
        lines.append("")
        lines.append(f"- Longitude RMS before the four-period fit: **{fmt(pf.get('rms_before_deg'))}°**")
        lines.append(f"- Longitude RMS after the four-period fit: **{fmt(pf.get('rms_after_deg'))}°**")
        lines.append(f"- Variance explained: **{fmt(pf.get('variance_explained_percent'), 3)}%**")
        lines.append("")

    if components:
        lines.append("### Fitted periodic components")
        lines.append("")
        lines.append("| Component | Period (days) | Amplitude in primary fit | Amplitude in full diagnostic fit |")
        lines.append("|---|---:|---:|---:|")
        for r in components:
            lines.append(
                f"| {r['name']} | {fmt(r['period_days'], 6)} | "
                f"{fmt(r.get('primary_amplitude_deg'))}° | {fmt(r.get('full_fit_amplitude_deg'))}° |"
            )
        lines.append("")

    if annual:
        lines.append("## Annual stability")
        lines.append("")
        lines.append("| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |")
        lines.append("|---:|---:|---:|---:|---:|---:|")
        for r in annual:
            lines.append(
                f"| {r['year']} | {r['n']} | {fmt(r['rms_dlon_deg'])}° | "
                f"{fmt(r['rms_dlat_deg'])}° | {fmt(r['rms_ddec_deg'])}° | {fmt(r['rms_sep_deg'])}° |"
            )
        lines.append("")

    lines.append("## Interpretation notes")
    lines.append("")
    lines.append(
        "- The periodic labels above identify frequencies present in the TYCHOS-minus-JPL residual. "
        "They should not by themselves be interpreted as proof of a particular physical mechanism."
    )
    lines.append(
        "- The lunar-plane modification should be evaluated primarily by whether it reduces latitude/declination "
        "error without materially degrading the longitude already produced by the original TYCHOS geometry."
    )
    lines.append(
        "- Remaining longitudinal structure can then be investigated within the geometry proposed by TYCHOS "
        "before introducing any additional empirical correction terms."
    )
    lines.append("")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written to: {output}")


if __name__ == "__main__":
    main()
