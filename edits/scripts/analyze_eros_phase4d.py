"""Phase 4D: audit the exact current Eros geometry relative to the Sun.

The script is read-only. It expands the existing Earth-level Eros hierarchy into
Sun-relative components and validates the configured reconstruction against the
saved pre-change TYCHOS export. It does not edit settings or scene hierarchy.
"""

from __future__ import annotations

import argparse
import math
import re
from datetime import datetime
from pathlib import Path

import numpy as np

from analyze_solar_companion_phase4a import (
    D2R,
    EPOCH,
    YEAR_DAYS,
    angle_stats,
    apply,
    center,
    chain_position,
    compose,
    fmt,
    max_norm,
    normal_stability,
    number,
    radius_vectors,
    repeat,
    rms_norm,
    rx,
    rz,
    settings_map,
    stage_matrix,
    tilt,
    unit_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "00-backup/phase4c/eros_ephemerides_before.txt"
DEFAULT_SETTINGS = ROOT / "src/settings/celestial-settings.json"
DEFAULT_REPORT = ROOT / "edits/reports/eros_phase4d_report.md"
EROS_CHAIN = ["Eros deferent A", "Eros deferent B", "Eros"]
SUN_CHAIN = ["Sun deferent", "Sun"]

ROW = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s*\|\s*"
    r"(\d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(\d{2})h(\d{2})m(\d{2})s\s*\|\s*"
    r"(-?)(\d{2})°(\d{2})'(\d{2})\""
)


def load_eros_export(path: Path) -> tuple[list[datetime], np.ndarray, np.ndarray]:
    text = path.read_text(encoding="utf-8-sig")
    if text.count("PLANET: EROS") != 1:
        raise ValueError("Expected exactly one PLANET: EROS section")
    dates: list[datetime] = []
    ra_deg: list[float] = []
    dec_deg: list[float] = []
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        date, time, rah, ram, ras, sign, decd, decm, decs = match.groups()
        dates.append(datetime.fromisoformat(f"{date}T{time}"))
        ra_deg.append(15.0 * (int(rah) + int(ram) / 60.0 + int(ras) / 3600.0))
        declination = int(decd) + int(decm) / 60.0 + int(decs) / 3600.0
        dec_deg.append(-declination if sign == "-" else declination)
    if not dates:
        raise ValueError("No Eros ephemeris rows were parsed")
    positions = np.asarray(
        [(date - EPOCH).total_seconds() / 86400.0 / YEAR_DAYS for date in dates]
    )
    exported = unit_vectors(np.deg2rad(ra_deg), np.deg2rad(dec_deg))
    return dates, positions, exported


def expanded_components(settings, positions):
    count = len(positions)
    eros_a = settings[EROS_CHAIN[0]]
    eros_b = settings[EROS_CHAIN[1]]
    eros = settings[EROS_CHAIN[2]]
    sun_deferent = settings[SUN_CHAIN[0]]
    sun = settings[SUN_CHAIN[1]]

    qa = stage_matrix(eros_a, positions)
    qb = stage_matrix(eros_b, positions)
    qe = stage_matrix(eros, positions)
    qd = stage_matrix(sun_deferent, positions)
    qs = stage_matrix(sun, positions)
    qab = compose(qa, qb)

    fixed_centres = (
        repeat(center(eros_a) - center(sun_deferent), count)
        - apply(qd, repeat(center(sun), count))
    )
    annual_carriers = (
        apply(qa, radius_vectors(eros_a, count))
        - apply(qd, radius_vectors(sun_deferent, count))
        - apply(compose(qd, qs), radius_vectors(sun, count))
    )
    deferent_b = apply(
        qa,
        repeat(center(eros_b), count) + apply(qb, radius_vectors(eros_b, count)),
    )
    main_asteroid = apply(
        qab,
        repeat(center(eros), count) + apply(qe, radius_vectors(eros, count)),
    )
    components = {
        "fixed centre difference": fixed_centres,
        "annual carrier mismatch": annual_carriers,
        "deferent-B stage": deferent_b,
        "main asteroid stage": main_asteroid,
    }
    relative = sum(components.values(), np.zeros((count, 3)))
    orbit_basis = compose(qab, tilt(eros))
    normals = apply(orbit_basis, repeat(np.array((0.0, 1.0, 0.0)), count))
    return components, relative, normals


def fit_origin_plane(relative):
    second_moment = relative.T @ relative / len(relative)
    values, vectors = np.linalg.eigh(second_moment)
    normal = vectors[:, np.argmin(values)]
    if normal[1] < 0.0:
        normal = -normal
    height = relative @ normal
    return normal, height


def settings_rows(settings):
    lines = [
        "| Object | Radius | Start | Speed (rad/y) | Centre (a, b, c) | Tilts (a, b) |",
        "|---|---:|---:|---:|---|---|",
    ]
    for name in EROS_CHAIN:
        item = settings[name]
        centres = ", ".join(
            fmt(number(item, key), 6)
            for key in ("orbitCentera", "orbitCenterb", "orbitCenterc")
        )
        tilts = ", ".join(
            fmt(number(item, key), 6)
            for key in ("orbitTilta", "orbitTiltb")
        )
        lines.append(
            f"| {name} | {fmt(number(item, 'orbitRadius'), 6)} | "
            f"{fmt(number(item, 'startPos'), 6)} | {fmt(number(item, 'speed'), 9)} | "
            f"{centres} | {tilts} |"
        )
    return lines


def analyze(source: Path, settings_path: Path) -> str:
    dates, positions, exported = load_eros_export(source)
    settings = settings_map(settings_path)
    eros_absolute = chain_position(settings, EROS_CHAIN, positions)
    sun_absolute = chain_position(settings, SUN_CHAIN, positions)
    exact_relative = eros_absolute - sun_absolute
    components, expanded_relative, normals = expanded_components(settings, positions)

    earth = settings["Earth"]
    earth_frame = rx(number(earth, "tiltb") * D2R) @ rz(number(earth, "tilt") * D2R)
    reconstructed_export = apply(earth_frame.T, eros_absolute)
    export_rms, export_max = angle_stats(reconstructed_export, exported)

    distances = np.linalg.norm(exact_relative, axis=1)
    mean_distance = float(np.mean(distances))
    component_rows = []
    for name, values in components.items():
        omission_rms, omission_max = angle_stats(exact_relative, exact_relative - values)
        magnitude = rms_norm(values)
        component_rows.append(
            (name, magnitude, 100.0 * magnitude / mean_distance, omission_rms, omission_max)
        )

    eros_a = settings[EROS_CHAIN[0]]
    eros_b = settings[EROS_CHAIN[1]]
    eros = settings[EROS_CHAIN[2]]
    sun_deferent = settings[SUN_CHAIN[0]]
    sun = settings[SUN_CHAIN[1]]
    count = len(positions)
    qa = stage_matrix(eros_a, positions)
    qd = stage_matrix(sun_deferent, positions)
    qs = stage_matrix(sun, positions)
    eros_carrier = apply(qa, radius_vectors(eros_a, count))
    sun_carrier = apply(qd, radius_vectors(sun_deferent, count)) + apply(
        compose(qd, qs), radius_vectors(sun, count)
    )
    carrier_reference = math.sqrt(
        (rms_norm(eros_carrier) ** 2 + rms_norm(sun_carrier) ** 2) / 2.0
    )
    carrier_remainder = rms_norm(eros_carrier - sun_carrier)
    cancellation = 100.0 * (1.0 - carrier_remainder / carrier_reference)

    configured_normal, normal_rms, normal_max = normal_stability(normals)
    fitted_normal, height = fit_origin_plane(exact_relative)
    plane_rms = float(np.sqrt(np.mean(height * height)))
    plane_fraction = 100.0 * plane_rms / mean_distance
    plane_inclination = math.degrees(
        math.acos(float(np.clip(abs(fitted_normal[1]), 0.0, 1.0)))
    )

    ab_rate = number(eros_a, "speed") + number(eros_b, "speed")
    total_rate = ab_rate + number(eros, "speed")
    total_period = 2.0 * math.pi / abs(total_rate) * YEAR_DAYS
    b_period = 2.0 * math.pi / abs(ab_rate) * YEAR_DAYS

    lines = [
        "# Phase 4D: Eros Sun-relative geometry audit",
        "",
        f"Source: `{source.as_posix()}`  ",
        f"Interval: `{dates[0].isoformat(sep=' ')}` to `{dates[-1].isoformat(sep=' ')}`  ",
        f"Samples: `{len(dates)}` at three-hour cadence",
        "",
        "This is a read-only expansion of the current Earth-level Eros chain. No setting",
        "or hierarchy transform is changed.",
        "",
        "## Exact identity and export check",
        "",
        "```text",
        "Eros - Sun = fixed centre difference",
        "           + annual carrier mismatch",
        "           + Eros deferent-B stage",
        "           + main Eros stage",
        "```",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Algebra RMS | {rms_norm(expanded_relative - exact_relative):.3e} units |",
        f"| Algebra maximum | {max_norm(expanded_relative - exact_relative):.3e} units |",
        f"| Reconstructed direction vs saved export RMS | {fmt(export_rms, 6)} deg |",
        f"| Reconstructed direction vs saved export maximum | {fmt(export_max, 6)} deg |",
        "",
        "## Component importance",
        "",
        f"Mean Sun-relative distance: `{fmt(mean_distance, 6)}` model units; range "
        f"`{fmt(float(np.min(distances)), 6)}` to `{fmt(float(np.max(distances)), 6)}`.",
        "",
        "| Component | Vector RMS | Share of mean distance | Direction RMS if omitted | Maximum |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, magnitude, share, omission_rms, omission_max in component_rows:
        lines.append(
            f"| {name} | {fmt(magnitude, 6)} | {fmt(share, 3)}% | "
            f"{fmt(omission_rms, 6)} deg | {fmt(omission_max, 6)} deg |"
        )

    lines += [
        "",
        "## Rates, carrier and plane",
        "",
        "| Diagnostic | Result |",
        "|---|---:|",
        f"| A+B scalar rate | {fmt(ab_rate, 12)} rad/y |",
        f"| A+B nominal period | {fmt(b_period, 6)} days |",
        f"| A+B+Eros scalar rate | {fmt(total_rate, 12)} rad/y |",
        f"| Main nominal period | {fmt(total_period, 6)} days |",
        f"| Annual carrier remainder | {fmt(carrier_remainder, 6)} units |",
        f"| Annual carrier cancellation | {fmt(cancellation, 6)}% |",
        f"| Configured orbit-normal RMS / maximum spread | {fmt(normal_rms, 9)} / {fmt(normal_max, 9)} deg |",
        f"| Configured mean normal | ({fmt(configured_normal[0], 9)}, {fmt(configured_normal[1], 9)}, {fmt(configured_normal[2], 9)}) |",
        f"| Best Sun-relative origin-plane normal | ({fmt(fitted_normal[0], 9)}, {fmt(fitted_normal[1], 9)}, {fmt(fitted_normal[2], 9)}) |",
        f"| Sun-relative plane inclination to model XZ | {fmt(plane_inclination, 6)} deg |",
        f"| Sun-relative out-of-plane RMS | {fmt(plane_rms, 6)} units ({fmt(plane_fraction, 3)}%) |",
        "",
        "The configured Eros orbit basis has one fixed normal because the B and Eros",
        "tilts are zero; their Y rotations combine beneath the fixed tilt of deferent A.",
        "The complete Eros-minus-Sun path is less perfectly planar because the Sun and",
        "Eros annual radius-100 carriers occupy different tilted planes.",
        "",
        "## Current Eros settings",
        "",
        *settings_rows(settings),
        "",
        "## Phase 4D conclusion",
        "",
        "Eros admits an exact Sun-relative representation without changing a parameter.",
        "Unlike Mercury and Venus, it needs no separate fixed-plane object: the existing",
        "deferent-A tilt already defines its orbital basis. A lossless Sun-hosted hierarchy",
        "must nevertheless retain all four terms above. In particular, the annual carrier",
        "mismatch cannot be discarded simply because both carrier radii are 100; their",
        "plane orientations differ.",
        "",
        "Phase 4E may therefore replace the Earth-level A -> B -> Eros scene nesting with",
        "an explicit Sun-relative centre, carrier, B-stage and main-basis chain. The Eros",
        "leaf should remain unchanged. Acceptance requires a fresh Eros export matching",
        "the saved Phase 4C file at its formatted RA/Dec, distance and elongation precision,",
        "plus the ordinary all-body regression gate.",
        "",
    ]
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main():
    args = parse_args()
    report = analyze(args.input.resolve(), args.settings.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report.resolve()}")


if __name__ == "__main__":
    main()
