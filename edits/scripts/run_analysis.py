#!/usr/bin/env python3
"""Compare and report selected bodies, replacing fixed outputs on each run."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import analyze_ephemerides
import compare_ephemerides
import generate_report
from download_jpl import load_defaults
from ephemeris_io import tychos_blocks, jpl_blocks, validate_jpl_header, select_block

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "edits/reports"
DERIVED = ROOT / "edits/data/derived"


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_inputs(body, config, tychos_path, jpl_path, blocks=None):
    if blocks is None:
        blocks = (tychos_blocks(tychos_path.read_text(encoding="utf-8-sig")),
                  jpl_blocks(jpl_path.read_text(encoding="utf-8-sig")))
    ty_text = select_block(blocks[0], body, "TYCHOS")
    jp_text = select_block(blocks[1], config['target_id'], "JPL")
    validate_jpl_header(jp_text)
    ty = compare_ephemerides.parse_tychos(ty_text, strict=True)
    jp = compare_ephemerides.parse_jpl(jp_text, strict=True)
    if not ty or set(ty) != set(jp):
        raise ValueError(f"{body}: empty data or different timestamps; align the two exports")
    result = {}
    for key, path in (("tychos", tychos_path), ("jpl", jpl_path)):
        path = path.resolve()
        name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        result[key] = {"path": name, "sha256": fingerprint(path)}
    return result


def safe_cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def write_overview(configs):
    lines = ["# Ephemeris comparison by body", "",
             "Latest results per body. Different intervals or export configurations are not a controlled A/B comparison.", "",
             "Input status compares file hashes only; it does not verify which simulator settings produced an export.", "",
             "| Body | Input status | Samples | Interval | RMS Dec | RMS separation | RMS longitude | RMS latitude | Export configuration |",
             "|---|---|---:|---|---:|---:|---:|---:|---|"]
    for body, config in configs.items():
        path = REPORTS / f"{body}_summary.json"
        if not path.exists():
            lines.append(f"| {body} | No analysis | — | — | — | — | — | — | — |")
            continue
        s = json.loads(path.read_text(encoding="utf-8"))
        provenance = s.get("provenance", {})
        inputs = provenance.get("inputs", {})
        fresh = all(k in inputs and (ROOT/inputs[k]["path"]).exists()
                    and fingerprint(ROOT/inputs[k]["path"]) == inputs[k]["sha256"] for k in ("tychos", "jpl"))
        status = "Current" if fresh else "Stale or unverified"
        numbers = " | ".join(f"{s[k]['rms_deg']:.6f}°" for k in ("declination_residual", "angular_separation", "ecliptic_longitude_residual", "ecliptic_latitude_residual"))
        label = safe_cell(provenance.get("export_label", "Not recorded"))
        lines.append(f"| [{body}]({body}_ephemeris_report.md) | {status} | {s['n_samples']} | {s['start']} to {s['stop']} | {numbers} | {label} |")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS/"ephemeris_overview.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def write_notes(summaries):
    lines = ["# Analysis notes", "", "Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.", "",
             "Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.", ""]
    for body, s in summaries.items():
        lines += [f"## {body.title()}", "", f"Interval: {s['start']} to {s['stop']}; {s['n_samples']} samples.", "",
                  f"Export configuration: {s['provenance']['export_label']}", ""]
        for name, key in (("Longitude", "ecliptic_longitude_residual"), ("Latitude", "ecliptic_latitude_residual")):
            v = s[key]
            lines.append(f"- {name}: mean {v['mean_deg']:.6f} deg; RMS {v['rms_deg']:.6f} deg.")
        fit = s.get('primary_period_fit')
        if fit:
            drift = fit['linear_trend_deg_per_day']*365.25*3600
            lines += [f"- Longitude trend conditional on the four-period fit: {drift:.3f} arcsec/year (365.25 days/year).",
                      f"- In-sample fitted longitude residual RMS: {fit['rms_after_deg']:.6f} deg. This is not out-of-sample validation."]
        with (REPORTS/f"{body}_fft_peaks.csv").open(encoding='utf-8', newline='') as stream:
            peaks = list(csv.DictReader(stream))[:4]
        if peaks:
            lines += ["- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):"]
            lines += [f"  - {float(p['period_days']):.3f} days, approximately {float(p['amplitude_deg']):.4f} deg." for p in peaks]
        else:
            lines.append("- No FFT peaks available (insufficient samples or irregular cadence).")
        lines += [""]
    lines += ["## Questions to investigate", "",
              "- Test whether biases and fitted coefficients transfer to a separate time interval.",
              "- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.",
              "- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.", ""]
    (REPORTS/'analysis_notes.md').write_text('\n'.join(lines), encoding='utf-8')


def main(argv=None):
    defaults = load_defaults()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bodies", nargs="*", help="Body names from bodies.json, e.g. moon sun mars")
    parser.add_argument("--all", action="store_true", help="Process all registered bodies present in BOTH combined inputs")
    parser.add_argument("--tychos", type=Path, default=ROOT/defaults['tychos'])
    parser.add_argument("--jpl", type=Path, default=ROOT/defaults['jpl'])
    parser.add_argument("--label", help="User-declared export configuration, not inferred from current settings")
    parser.add_argument("--export-settings", type=Path, help="Optional JSON settings known to have been used for these exports")
    parser.add_argument("--overview-only", action="store_true", help="Refresh input freshness statuses without rerunning analyses")
    args = parser.parse_args(argv)
    configs = json.loads(Path(__file__).with_name("bodies.json").read_text(encoding="utf-8"))
    if args.overview_only:
        if args.bodies or args.all or args.label or args.export_settings:
            parser.error("--overview-only cannot be combined with analysis options")
        write_overview(configs)
        return
    if args.bodies and args.all:
        parser.error("Specify body names OR --all")
    tychos_path, jpl_path = args.tychos.resolve(), args.jpl.resolve()
    blocks = (tychos_blocks(tychos_path.read_text(encoding="utf-8-sig")),
              jpl_blocks(jpl_path.read_text(encoding="utf-8-sig")))
    bodies = list(dict.fromkeys(args.bodies or defaults['bodies']))
    if args.all:
        bodies = [b for b, c in configs.items() if b in blocks[0] and c['target_id'] in blocks[1]]
        for b, c in configs.items():
            if (b in blocks[0] or c['target_id'] in blocks[1]) and b not in bodies:
                print(f"Skipping {b}: present in only one input")
    if not bodies:
        parser.error("No registered bodies present in both inputs")
    unknown = set(bodies)-set(configs)
    if unknown:
        parser.error(f"Unknown bodies: {sorted(unknown)}")
    # Validate every requested body before replacing any output.
    inputs = {body: check_inputs(body, configs[body], tychos_path, jpl_path, blocks) for body in bodies}
    export_settings = json.loads(args.export_settings.read_text(encoding="utf-8")) if args.export_settings else None
    publications = []
    summaries = {}
    with tempfile.TemporaryDirectory(prefix="tychos-analysis-") as temporary:
        for body in bodies:
            config = configs[body]
            prefix = body
            stage = Path(temporary)/body
            stage.mkdir()
            comparison = stage/f"{body}_comparison.csv"
            final_comparison = DERIVED/comparison.name
            compare_ephemerides.main([str(tychos_path), str(jpl_path), '--body', body, '--target-id', config['target_id'], '-o', str(comparison), '--strict'])
            analyze_ephemerides.main([str(comparison), "--body", body, "--prefix", prefix, "--out-dir", str(stage)])
            summary_path = stage/f"{prefix}_summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            old_path = REPORTS/summary_path.name
            old = json.loads(old_path.read_text(encoding="utf-8")).get("provenance", {}) if old_path.exists() else {}
            same_export = old.get("inputs", {}).get("tychos", {}).get("sha256") == inputs[body]["tychos"]["sha256"]
            label = args.label or (old.get("export_label") if same_export else None) or "Not recorded; current settings do not establish export settings"
            settings = export_settings if args.export_settings else (old.get("declared_export_settings") if same_export and not args.label else None)
            summary["input_file"] = final_comparison.relative_to(ROOT).as_posix()
            summary["provenance"] = {"analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "inputs": inputs[body], "export_label": label,
                                     "declared_export_settings": settings,
                                     "settings_note": "User-declared, not embedded or verified by the TYCHOS export"}
            summaries[body] = summary
            summary_path.write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
            report_args = ["--summary", str(summary_path), "--annual", str(stage/f"{prefix}_annual_stats.csv"),
                           "--model-label", f"TYCHOS {body}", "--output", str(stage/f"{prefix}_ephemeris_report.md")]
            if body == "moon":
                report_args += ["--components", str(stage/f"{prefix}_periodic_components.csv")]
            generate_report.main(report_args)
            for path in stage.iterdir():
                publications.append((path, final_comparison if path == comparison else REPORTS/path.name))
        for body in bodies:
            for source in ("tychos", "jpl"):
                if fingerprint(ROOT/inputs[body][source]["path"]) != inputs[body][source]["sha256"]:
                    raise ValueError("Input changed during analysis; outputs were not replaced")
        for source, destination in publications:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    write_overview(configs)
    write_notes(summaries)
    print("Updated edits/reports/ephemeris_overview.md")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
