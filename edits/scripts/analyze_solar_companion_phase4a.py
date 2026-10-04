"""Audit the exact Sun-relative Mercury and Venus geometry for Phase 4A.

This script is diagnostic only. It expands the current transform chains into
additive Sun-relative components, checks the algebra against an independent
full-chain reconstruction, and checks the reconstructed absolute directions
against the latest TYCHOS comparison CSVs. It never edits simulator settings.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
from settings_schema import settings_map


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS = ROOT / "src/settings/celestial-settings.json"
DEFAULT_REPORT = ROOT / "edits/reports/solar_companion_phase4a_report.md"
DERIVED = ROOT / "edits/data/derived"
EPOCH = datetime(2000, 6, 21, 12)
YEAR_DAYS = 365.2425
D2R = math.pi / 180.0

CHAINS = {
    "Mercury": [
        "Mercury deferent A",
        "Mercury deferent B",
        "Mercury Plane",
        "Mercury",
    ],
    "Venus": [
        "Venus deferent A",
        "Venus deferent B",
        "Venus Plane",
        "Venus",
    ],
}
SUN_CHAIN = ["Sun deferent", "Sun"]


def number(setting: dict, key: str) -> float:
    return float(setting.get(key, 0) or 0)


def rx(angle):
    c, s = np.cos(angle), np.sin(angle)
    if np.ndim(angle):
        out = np.zeros((len(angle), 3, 3))
        out[:, 0, 0] = 1
        out[:, 1, 1] = c
        out[:, 1, 2] = -s
        out[:, 2, 1] = s
        out[:, 2, 2] = c
        return out
    return np.array(((1, 0, 0), (0, c, -s), (0, s, c)), dtype=float)


def ry(angle):
    c, s = np.cos(angle), np.sin(angle)
    if np.ndim(angle):
        out = np.zeros((len(angle), 3, 3))
        out[:, 0, 0] = c
        out[:, 0, 2] = s
        out[:, 1, 1] = 1
        out[:, 2, 0] = -s
        out[:, 2, 2] = c
        return out
    return np.array(((c, 0, s), (0, 1, 0), (-s, 0, c)), dtype=float)


def rz(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)), dtype=float)


def apply(matrix: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    if matrix.ndim == 3:
        return np.einsum("nij,nj->ni", matrix, vectors)
    return vectors @ matrix.T


def compose(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.ndim == 2 and right.ndim == 2:
        return left @ right
    if left.ndim == 2:
        return np.einsum("ij,njk->nik", left, right)
    if right.ndim == 2:
        return np.einsum("nij,jk->nik", left, right)
    return np.einsum("nij,njk->nik", left, right)


def center(setting: dict) -> np.ndarray:
    # Three.js scene axes: settings b is scene Z and settings c is scene Y.
    return np.array(
        (
            number(setting, "orbitCentera"),
            number(setting, "orbitCenterc"),
            number(setting, "orbitCenterb"),
        )
    )


def tilt(setting: dict) -> np.ndarray:
    return rx(number(setting, "orbitTilta") * D2R) @ rz(
        number(setting, "orbitTiltb") * D2R
    )


def stage_matrix(setting: dict, positions: np.ndarray) -> np.ndarray:
    angles = number(setting, "speed") * positions - number(setting, "startPos") * D2R
    return compose(tilt(setting), ry(angles))


def radius_vectors(setting: dict, count: int) -> np.ndarray:
    out = np.zeros((count, 3))
    out[:, 0] = number(setting, "orbitRadius")
    return out


def repeat(vector: np.ndarray, count: int) -> np.ndarray:
    return np.repeat(vector[None, :], count, axis=0)


def chain_position(
    settings: dict[str, dict], chain: list[str], positions: np.ndarray
) -> np.ndarray:
    vectors = np.zeros((len(positions), 3))
    for name in reversed(chain):
        setting = settings[name]
        vectors = repeat(center(setting), len(positions)) + apply(
            stage_matrix(setting, positions), radius_vectors(setting, len(positions)) + vectors
        )
    return vectors


def unit_vectors(ra: np.ndarray, dec: np.ndarray) -> np.ndarray:
    return np.column_stack(
        (np.sin(ra) * np.cos(dec), np.sin(dec), np.cos(ra) * np.cos(dec))
    )


def load_comparison(body: str, stride: int) -> tuple[list[datetime], np.ndarray, np.ndarray]:
    path = DERIVED / f"{body.lower()}_comparison.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))[::stride]
    if not rows:
        raise ValueError(f"No rows found in {path}")
    dates = [datetime.fromisoformat(row["date"]) for row in rows]
    positions = np.array(
        [(date - EPOCH).total_seconds() / 86400.0 / YEAR_DAYS for date in dates]
    )
    exported = unit_vectors(
        np.deg2rad([float(row["ty_ra_deg"]) for row in rows]),
        np.deg2rad([float(row["ty_dec_deg"]) for row in rows]),
    )
    return dates, positions, exported


def rms_norm(vectors: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum(vectors * vectors, axis=1))))


def max_norm(vectors: np.ndarray) -> float:
    return float(np.max(np.linalg.norm(vectors, axis=1)))


def angular_separation(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    an = a / np.linalg.norm(a, axis=1)[:, None]
    bn = b / np.linalg.norm(b, axis=1)[:, None]
    return np.rad2deg(np.arccos(np.clip(np.sum(an * bn, axis=1), -1.0, 1.0)))


def angle_stats(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    angles = angular_separation(a, b)
    return float(np.sqrt(np.mean(angles * angles))), float(np.max(angles))


def expanded_components(
    settings: dict[str, dict], body: str, positions: np.ndarray
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    count = len(positions)
    a_name, b_name, plane_name, planet_name = CHAINS[body]
    a = settings[a_name]
    b = settings[b_name]
    plane = settings[plane_name]
    planet = settings[planet_name]
    sun_deferent = settings[SUN_CHAIN[0]]
    sun = settings[SUN_CHAIN[1]]

    qa = stage_matrix(a, positions)
    qb = stage_matrix(b, positions)
    qp = stage_matrix(plane, positions)
    qm = stage_matrix(planet, positions)
    qd = stage_matrix(sun_deferent, positions)
    qs = stage_matrix(sun, positions)

    qab = compose(qa, qb)
    qabp = compose(qab, qp)

    # Exact expansion of planet_absolute - sun_absolute. The Sun-deferent
    # terms are kept even though they are currently identities/zeros.
    fixed_centres = (
        repeat(center(a) - center(sun_deferent), count)
        - apply(qd, repeat(center(sun), count))
    )
    annual_carriers = (
        apply(qa, radius_vectors(a, count))
        - apply(qd, radius_vectors(sun_deferent, count))
        - apply(compose(qd, qs), radius_vectors(sun, count))
    )
    deferent_b = apply(
        qa,
        repeat(center(b), count) + apply(qb, radius_vectors(b, count)),
    )
    plane_stage = apply(
        qab,
        repeat(center(plane), count) + apply(qp, radius_vectors(plane, count)),
    )
    main_orbit = apply(
        qabp,
        repeat(center(planet), count) + apply(qm, radius_vectors(planet, count)),
    )
    components = {
        "fixed centre difference": fixed_centres,
        "annual carrier mismatch": annual_carriers,
        "deferent-B stage": deferent_b,
        "fixed-plane stage": plane_stage,
        "main planet stage": main_orbit,
    }
    relative = sum(components.values(), np.zeros((count, 3)))

    # The physical orbit normal includes any fixed tilt still retained by the
    # planet leaf. Its Ry orbital phase does not change the local Y normal.
    orbit_basis = compose(qabp, tilt(planet))
    normals = apply(orbit_basis, repeat(np.array((0.0, 1.0, 0.0)), count))
    return components, relative, normals


def normal_stability(normals: np.ndarray) -> tuple[np.ndarray, float, float]:
    normal = np.mean(normals / np.linalg.norm(normals, axis=1)[:, None], axis=0)
    normal /= np.linalg.norm(normal)
    aligned = repeat(normal, len(normals))
    angles = angular_separation(normals, aligned)
    return normal, float(np.sqrt(np.mean(angles * angles))), float(np.max(angles))


def fmt(value: float, digits: int = 9) -> str:
    return f"{value:.{digits}f}"


def analyze_body(
    settings: dict[str, dict], body: str, stride: int
) -> dict:
    dates, positions, exported = load_comparison(body, stride)
    planet_absolute = chain_position(settings, CHAINS[body], positions)
    sun_absolute = chain_position(settings, SUN_CHAIN, positions)
    exact_relative = planet_absolute - sun_absolute
    components, expanded_relative, normals = expanded_components(settings, body, positions)

    earth = settings["Earth"]
    earth_frame = rx(number(earth, "tiltb") * D2R) @ rz(number(earth, "tilt") * D2R)
    reconstructed_export = apply(earth_frame.T, planet_absolute)
    export_rms, export_max = angle_stats(reconstructed_export, exported)

    component_rows = []
    mean_distance = float(np.mean(np.linalg.norm(exact_relative, axis=1)))
    for name, values in components.items():
        omission_rms, omission_max = angle_stats(exact_relative, exact_relative - values)
        magnitude = rms_norm(values)
        component_rows.append(
            {
                "name": name,
                "magnitude_rms": magnitude,
                "distance_percent": 100.0 * magnitude / mean_distance,
                "omission_angle_rms": omission_rms,
                "omission_angle_max": omission_max,
            }
        )

    a = settings[CHAINS[body][0]]
    sun_deferent = settings[SUN_CHAIN[0]]
    sun = settings[SUN_CHAIN[1]]
    count = len(positions)
    qa = stage_matrix(a, positions)
    qd = stage_matrix(sun_deferent, positions)
    qs = stage_matrix(sun, positions)
    planet_carrier = apply(qa, radius_vectors(a, count))
    sun_carrier = apply(qd, radius_vectors(sun_deferent, count)) + apply(
        compose(qd, qs), radius_vectors(sun, count)
    )
    carrier_reference = math.sqrt(
        (rms_norm(planet_carrier) ** 2 + rms_norm(sun_carrier) ** 2) / 2.0
    )
    carrier_remainder = rms_norm(planet_carrier - sun_carrier)
    cancellation = 100.0 * (1.0 - carrier_remainder / carrier_reference)

    normal, normal_rms, normal_max = normal_stability(normals)
    b = settings[CHAINS[body][1]]
    planet = settings[CHAINS[body][3]]
    speed_sum = number(a, "speed") + number(b, "speed")
    period = 2.0 * math.pi / abs(number(planet, "speed")) * YEAR_DAYS

    return {
        "body": body,
        "dates": dates,
        "samples": len(positions),
        "mean_distance": mean_distance,
        "algebra_rms": rms_norm(expanded_relative - exact_relative),
        "algebra_max": max_norm(expanded_relative - exact_relative),
        "export_rms_deg": export_rms,
        "export_max_deg": export_max,
        "carrier_remainder": carrier_remainder,
        "carrier_cancellation": cancellation,
        "speed_sum": speed_sum,
        "nominal_period_days": period,
        "normal": normal,
        "normal_rms_deg": normal_rms,
        "normal_max_deg": normal_max,
        "components": component_rows,
    }


def settings_table(settings: dict[str, dict], body: str) -> list[str]:
    lines = [
        "| Object | Radius | Start | Speed (rad/y) | Centre (a, b, c) | Tilts (a, b) |",
        "|---|---:|---:|---:|---|---|",
    ]
    for name in CHAINS[body]:
        item = settings[name]
        centre_text = ", ".join(fmt(number(item, key), 6) for key in (
            "orbitCentera", "orbitCenterb", "orbitCenterc"
        ))
        tilt_text = ", ".join(fmt(number(item, key), 6) for key in (
            "orbitTilta", "orbitTiltb"
        ))
        lines.append(
            f"| {name} | {fmt(number(item, 'orbitRadius'), 6)} | "
            f"{fmt(number(item, 'startPos'), 6)} | {fmt(number(item, 'speed'), 9)} | "
            f"{centre_text} | {tilt_text} |"
        )
    return lines


def build_report(settings: dict[str, dict], results: list[dict], stride: int) -> str:
    first = results[0]["dates"][0].isoformat(sep=" ")
    last = results[0]["dates"][-1].isoformat(sep=" ")
    lines = [
        "# Phase 4A: Sun-relative Mercury and Venus audit",
        "",
        f"Interval: `{first}` to `{last}`; comparison stride `{stride}`; "
        f"`{results[0]['samples']}` samples per body.",
        "",
        "This is a diagnostic expansion of the current hierarchy. It does not change "
        "a parent, transform, celestial setting or exported coordinate.",
        "",
        "## Exact identity",
        "",
        "For each planet, the current absolute chain was expanded into:",
        "",
        "```text",
        "planet - Sun = fixed centre difference",
        "             + annual carrier mismatch",
        "             + deferent-B stage",
        "             + fixed-plane stage",
        "             + main planet stage",
        "```",
        "",
        "The expansion retains the full matrix order. Opposing scalar angular speeds "
        "are not treated as sufficient cancellation when a tilted transform lies between them.",
        "",
        "| Body | Algebra RMS | Algebra maximum | Reconstruction vs export RMS | Maximum |",
        "|---|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result['body']} | {result['algebra_rms']:.3e} units | "
            f"{result['algebra_max']:.3e} units | {fmt(result['export_rms_deg'], 6)} deg | "
            f"{fmt(result['export_max_deg'], 6)} deg |"
        )

    lines += [
        "",
        "The first two columns test the algebra against an independently evaluated full "
        "object chain. The export columns compare that reconstruction with the formatted "
        "TYCHOS RA/Dec in the current derived comparison files.",
        "",
        "## Component importance",
        "",
        "`Vector RMS` is the physical size of one additive term. `Share` divides it by "
        "the mean Sun-relative distance; shares do not sum to 100% because vectors cancel. "
        "`Direction error if omitted` measures how much the Sun-relative direction would "
        "change if that exact term were incorrectly discarded.",
    ]
    for result in results:
        lines += [
            "",
            f"### {result['body']}",
            "",
            f"Mean Sun-relative distance: `{fmt(result['mean_distance'], 6)}` model units.",
            "",
            "| Component | Vector RMS | Share of mean distance | Direction RMS if omitted | Maximum |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in result["components"]:
            lines.append(
                f"| {row['name']} | {fmt(row['magnitude_rms'], 6)} | "
                f"{fmt(row['distance_percent'], 3)}% | "
                f"{fmt(row['omission_angle_rms'], 6)} deg | "
                f"{fmt(row['omission_angle_max'], 6)} deg |"
            )

    lines += [
        "",
        "## Carrier cancellation and plane stability",
        "",
        "| Body | A+B scalar rate | Radius-100 carrier remainder | Carrier cancellation | "
        "Nominal local period | Orbit-normal RMS spread | Maximum spread |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result['body']} | {fmt(result['speed_sum'], 12)} rad/y | "
            f"{fmt(result['carrier_remainder'], 6)} units | "
            f"{fmt(result['carrier_cancellation'], 6)}% | "
            f"{fmt(result['nominal_period_days'], 6)} d | "
            f"{fmt(result['normal_rms_deg'], 6)} deg | "
            f"{fmt(result['normal_max_deg'], 6)} deg |"
        )
    lines += [
        "",
        "The A and B configured rates add to zero, but the full orientation is a product "
        "of rotation matrices. Non-zero B/plane tilts therefore leave a small time-dependent "
        "orientation that a simple `A speed + B speed = 0` rewrite would lose.",
        "",
        "Mean orbit normals in the current model axes:",
        "",
    ]
    for result in results:
        n = result["normal"]
        lines.append(
            f"- {result['body']}: `({fmt(n[0], 9)}, {fmt(n[1], 9)}, {fmt(n[2], 9)})`."
        )

    lines += [
        "",
        "## Current settings used by this audit",
    ]
    for body in CHAINS:
        lines += ["", f"### {body}", ""] + settings_table(settings, body)

    lines += [
        "",
        "## Phase 4A conclusion",
        "",
        "Both planets already admit an exact Sun-relative description, so explicit solar "
        "host parentage is geometrically viable without fitting new parameters. The safe "
        "implementation is not a single replacement ellipse: it must preserve the centre "
        "offset, annual-carrier remainder, deferent-B transform, distinct fixed plane and "
        "main planet transform in their present matrix order.",
        "",
        "Mercury deferent B must not be deleted merely because its orbit radius is zero. "
        "Its centre and orientation still affect all descendants. Venus deferent B also "
        "has a non-zero radius and therefore supplies both translation and orientation.",
        "",
        "The recommended Phase 4B experiment is to reparent **one body at a time**, starting "
        "with Venus because its non-zero B radius makes accidental term loss easier to detect. "
        "Create an explicit Sun-relative Venus frame driven by these five exact components, "
        "then require component tests and a fresh full-export equivalence gate before doing "
        "the same for Mercury. Keep the Mercury and Venus plane objects separate.",
        "",
        "No result here tests whether the present parameters are physically optimal or improve "
        "agreement with JPL. Phase 4A only establishes a lossless architectural route.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Use every Nth row from the current comparison CSVs (default: all rows)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.stride < 1:
        raise ValueError("--stride must be at least 1")
    settings = settings_map(args.settings)
    results = [analyze_body(settings, body, args.stride) for body in CHAINS]
    report = build_report(settings, results, args.stride)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report}")
    for result in results:
        print(
            result["body"],
            "algebra_max",
            f"{result['algebra_max']:.3e}",
            "export_rms_deg",
            f"{result['export_rms_deg']:.6f}",
            "normal_rms_deg",
            f"{result['normal_rms_deg']:.6f}",
        )


if __name__ == "__main__":
    main()
