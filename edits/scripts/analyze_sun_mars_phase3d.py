#!/usr/bin/env python3
"""Phase 3D: algebraically decompose the existing Sun-relative Mars geometry."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "edits" / "data" / "raw" / "sun_mars_binary.csv"
DEFAULT_SETTINGS = ROOT / "src" / "settings" / "celestial-settings.json"
DEFAULT_REPORT = ROOT / "edits" / "reports" / "sun_mars_phase3d_report.md"
DEFAULT_COMPONENTS = ROOT / "edits" / "data" / "derived" / "sun_mars_phase3d_components.csv"
EPOCH = datetime(2000, 6, 21, 12)
YEAR_DAYS = 365.2425
D2R = math.pi / 180.0


def number(setting: dict, key: str) -> float:
    return float(setting.get(key, 0) or 0)


def settings_map(path: Path) -> dict[str, dict]:
    return {
        item["name"]: item
        for item in json.loads(path.read_text(encoding="utf-8"))
    }


def rx(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.asarray(
        ((1.0, 0.0, 0.0), (0.0, cosine, -sine), (0.0, sine, cosine))
    )


def rz(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.asarray(
        ((cosine, -sine, 0.0), (sine, cosine, 0.0), (0.0, 0.0, 1.0))
    )


def ry(angles: np.ndarray) -> np.ndarray:
    cosine, sine = np.cos(angles), np.sin(angles)
    matrices = np.zeros((len(angles), 3, 3))
    matrices[:, 0, 0] = cosine
    matrices[:, 0, 2] = sine
    matrices[:, 1, 1] = 1.0
    matrices[:, 2, 0] = -sine
    matrices[:, 2, 2] = cosine
    return matrices


def apply(matrix: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    if matrix.ndim == 3:
        return np.einsum("nij,nj->ni", matrix, vectors)
    return vectors @ matrix.T


def center(setting: dict) -> np.ndarray:
    return np.asarray(
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


def angles(setting: dict, positions: np.ndarray) -> np.ndarray:
    return (
        number(setting, "speed") * positions
        - number(setting, "startPos") * D2R
    )


def radius_vectors(setting: dict, count: int) -> np.ndarray:
    vectors = np.zeros((count, 3))
    vectors[:, 0] = number(setting, "orbitRadius")
    return vectors


def chain_position(
    settings: dict[str, dict], names: list[str], positions: np.ndarray
) -> np.ndarray:
    vectors = np.zeros((len(positions), 3))
    for name in reversed(names):
        setting = settings[name]
        vectors = center(setting) + apply(
            tilt(setting),
            apply(
                ry(angles(setting, positions)),
                radius_vectors(setting, len(positions)) + vectors,
            ),
        )
    return vectors


def orient_through_chain(
    settings: dict[str, dict], names: list[str], positions: np.ndarray, vectors: np.ndarray
) -> np.ndarray:
    """Apply only the linear (rotation) part of a shared parent chain."""
    oriented = vectors
    for name in reversed(names):
        setting = settings[name]
        oriented = apply(
            tilt(setting), apply(ry(angles(setting, positions)), oriented)
        )
    return oriented


def load_export(
    path: Path,
) -> tuple[list[datetime], np.ndarray, np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("The Phase 2.5 CSV contains no samples")

    times = [
        datetime.fromisoformat(f"{row['date']}T{row['time']}") for row in rows
    ]

    def vectors(prefix: str) -> np.ndarray:
        return np.asarray(
            [[float(row[f"{prefix}_{axis}"]) for axis in "xyz"] for row in rows]
        )

    return times, vectors("sun_world"), vectors("mars_world"), vectors("earth_center")


def rms_norm(vectors: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum(vectors * vectors, axis=1))))


def max_norm(vectors: np.ndarray) -> float:
    return float(np.max(np.linalg.norm(vectors, axis=1)))


def fmt(value: float, digits: int = 9) -> str:
    return "n/a" if not math.isfinite(value) else f"{value:.{digits}f}"


def write_components(
    path: Path,
    times: list[datetime],
    exported: np.ndarray,
    reconstructed: np.ndarray,
    constant_component: np.ndarray,
    carrier_mismatch: np.ndarray,
    secondary: np.ndarray,
    main: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        header = ["date", "time"]
        for prefix in (
            "exported",
            "reconstructed",
            "constant",
            "carrier_mismatch",
            "secondary",
            "main",
        ):
            header.extend(f"{prefix}_{axis}" for axis in "xyz")
        writer.writerow(header)
        for index, timestamp in enumerate(times):
            writer.writerow(
                [
                    timestamp.date().isoformat(),
                    timestamp.time().isoformat(),
                    *exported[index],
                    *reconstructed[index],
                    *constant_component[index],
                    *carrier_mismatch[index],
                    *secondary[index],
                    *main[index],
                ]
            )


def analyze(
    source: Path,
    settings_path: Path,
    output_components: Path,
    times: list[datetime],
    sun_world: np.ndarray,
    mars_world: np.ndarray,
    earth_world: np.ndarray,
    settings: dict[str, dict],
) -> str:
    positions = np.asarray(
        [(timestamp - EPOCH).total_seconds() / 86400.0 / YEAR_DAYS for timestamp in times]
    )
    count = len(positions)
    exported_relative = mars_world - sun_world

    sun = settings["Sun"]
    mars_e = settings["Mars deferent E"]
    mars_s = settings["Mars deferent S"]
    mars = settings["Mars"]

    reconstructed_sun = chain_position(
        settings, ["Sun deferent", "Sun"], positions
    )
    reconstructed_mars = chain_position(
        settings,
        ["Mars deferent E", "Mars deferent S", "Mars"],
        positions,
    )
    local_reconstructed_relative = reconstructed_mars - reconstructed_sun

    # Both branches inherit the SystemCenter and Earth rotations. Their
    # translations disappear under subtraction, but their rotations do not.
    # Applying that shared orientation is required to compare the algebraic
    # Earth-local vector with the world-space diagnostic export.
    common_parent_names = ["SystemCenter", "Earth"]
    reconstructed_relative = orient_through_chain(
        settings,
        common_parent_names,
        positions,
        local_reconstructed_relative,
    )
    reconstruction_error = reconstructed_relative - exported_relative

    e_tilt = tilt(mars_e)
    s_tilt = tilt(mars_s)
    mars_tilt = tilt(mars)
    sun_tilt = tilt(sun)
    e_rotation = ry(angles(mars_e, positions))
    s_rotation = ry(angles(mars_s, positions))
    mars_rotation = ry(angles(mars, positions))
    sun_rotation = ry(angles(sun, positions))

    constant_single = center(mars_e) - center(sun)
    constant_component = np.repeat(constant_single[None, :], count, axis=0)

    mars_annual = apply(
        e_tilt, apply(e_rotation, radius_vectors(mars_e, count))
    )
    sun_annual = apply(
        sun_tilt, apply(sun_rotation, radius_vectors(sun, count))
    )
    carrier_mismatch = mars_annual - sun_annual

    s_center_local = np.repeat(center(mars_s)[None, :], count, axis=0)
    secondary_local = s_center_local + apply(
        s_tilt, apply(s_rotation, radius_vectors(mars_s, count))
    )
    secondary = apply(e_tilt, apply(e_rotation, secondary_local))

    mars_center_local = np.repeat(center(mars)[None, :], count, axis=0)
    main_inside_s = mars_center_local + apply(
        mars_tilt, apply(mars_rotation, radius_vectors(mars, count))
    )
    main = apply(
        e_tilt,
        apply(e_rotation, apply(s_tilt, apply(s_rotation, main_inside_s))),
    )

    local_decomposed = constant_component + carrier_mismatch + secondary + main
    decomposition_error = local_decomposed - local_reconstructed_relative

    constant_component = orient_through_chain(
        settings, common_parent_names, positions, constant_component
    )
    carrier_mismatch = orient_through_chain(
        settings, common_parent_names, positions, carrier_mismatch
    )
    secondary = orient_through_chain(
        settings, common_parent_names, positions, secondary
    )
    main = orient_through_chain(settings, common_parent_names, positions, main)
    decomposed = constant_component + carrier_mismatch + secondary + main

    shared_radius = number(sun, "orbitRadius") == number(mars_e, "orbitRadius")
    shared_speed = number(sun, "speed") == number(mars_e, "speed")
    shared_phase = number(sun, "startPos") == number(mars_e, "startPos")
    carrier_cancellation = 100.0 * (
        1.0 - rms_norm(carrier_mismatch) / max(number(sun, "orbitRadius"), 1e-15)
    )

    main_speed = number(mars_e, "speed") + number(mars_s, "speed") + number(mars, "speed")
    secondary_speed = number(mars_e, "speed") + number(mars_s, "speed")
    inherited_frame_speed = sum(
        number(settings[name], "speed") for name in common_parent_names
    )
    world_main_speed = inherited_frame_speed + main_speed
    world_secondary_speed = inherited_frame_speed + secondary_speed
    main_period_days = 2.0 * math.pi / abs(main_speed) * YEAR_DAYS
    secondary_period_days = 2.0 * math.pi / abs(secondary_speed) * YEAR_DAYS
    world_main_period_days = 2.0 * math.pi / abs(world_main_speed) * YEAR_DAYS
    world_secondary_period_days = (
        2.0 * math.pi / abs(world_secondary_speed) * YEAR_DAYS
    )
    harmonic_ratio = secondary_speed / main_speed
    harmonic_detuning = secondary_speed - 2.0 * main_speed
    detuning_deg_per_year = math.degrees(harmonic_detuning)
    detuning_cycle_years = (
        2.0 * math.pi / abs(harmonic_detuning)
        if abs(harmonic_detuning) > 0.0
        else math.inf
    )
    amplitude_ratio = number(mars_s, "orbitRadius") / number(mars, "orbitRadius")
    twice_amplitude_ratio = 2.0 * amplitude_ratio
    first_order_constant = 3.0 * number(mars_s, "orbitRadius")
    constant_difference_pct = 100.0 * (
        rms_norm(constant_component) - first_order_constant
    ) / first_order_constant

    simplified_without_mismatch = constant_component + secondary + main
    mismatch_omission_error = simplified_without_mismatch - exported_relative
    main_only_error = main - exported_relative

    write_components(
        output_components,
        times,
        exported_relative,
        decomposed,
        constant_component,
        carrier_mismatch,
        secondary,
        main,
    )

    earth_mars = np.linalg.norm(mars_world - earth_world, axis=1)
    earth_ratio = float(np.max(earth_mars) / np.min(earth_mars))

    lines = [
        "# Sun-Mars Phase 3D algebraic decomposition",
        "",
        f"Source export: `{source.as_posix()}`  ",
        f"Settings: `{settings_path.as_posix()}`  ",
        f"Interval: `{times[0].isoformat(sep=' ')}` to `{times[-1].isoformat(sep=' ')}`  ",
        f"Samples: `{count}`",
        "",
        "This analysis expands the existing transform chain; it does not fit a new",
        "orbit or alter the simulator.",
        "Component identities are formed in the Earth/PVP-carried model frame; the",
        "shared `SystemCenter -> Earth` rotation is then applied for exact comparison",
        "with the exported world-space vectors.",
        "",
        "## Exact relative-vector identity",
        "",
        "```text",
        "Mars - Sun = constant centre difference",
        "           + annual carrier mismatch",
        "           + Mars deferent-S vector",
        "           + main Mars vector",
        "```",
        "",
        "| Reconstruction check | RMS vector error | Maximum vector error |",
        "|---|---:|---:|",
        f"| Settings chain versus exported Sun-Mars vector | {fmt(rms_norm(reconstruction_error), 12)} | {fmt(max_norm(reconstruction_error), 12)} |",
        f"| Sum of four explicit components versus settings chain | {fmt(rms_norm(decomposition_error), 12)} | {fmt(max_norm(decomposition_error), 12)} |",
        "",
        "## Annual carrier cancellation",
        "",
        "| Property | Sun | Mars deferent E |",
        "|---|---:|---:|",
        f"| Radius | {fmt(number(sun, 'orbitRadius'), 6)} | {fmt(number(mars_e, 'orbitRadius'), 6)} |",
        f"| Speed | {fmt(number(sun, 'speed'), 12)} | {fmt(number(mars_e, 'speed'), 12)} |",
        f"| Start phase | {fmt(number(sun, 'startPos'), 6)} deg | {fmt(number(mars_e, 'startPos'), 6)} deg |",
        f"| Orbital tilt A | {fmt(number(sun, 'orbitTilta'), 6)} deg | {fmt(number(mars_e, 'orbitTilta'), 6)} deg |",
        "",
        f"Equal radius: `{shared_radius}`; equal speed: `{shared_speed}`; equal phase: `{shared_phase}`.  ",
        f"The radius-100 annual vectors cancel by `{fmt(carrier_cancellation, 6)}%` RMS.",
        "The remaining mismatch comes principally from the Sun's small orbital tilt.",
        "",
        "## Remaining geometric components",
        "",
        "| Component | RMS magnitude | Nominal radius | Effective angular speed | Period |",
        "|---|---:|---:|---:|---:|",
        f"| Constant centre difference | {fmt(rms_norm(constant_component), 6)} | — | 0 | — |",
        f"| Annual carrier mismatch | {fmt(rms_norm(carrier_mismatch), 6)} | two cancelling 100-unit vectors | annual | 365.2425 d |",
        f"| Mars deferent-S vector | {fmt(rms_norm(secondary), 6)} | {fmt(number(mars_s, 'orbitRadius'), 6)} | {fmt(secondary_speed, 9)} rad/y | {fmt(secondary_period_days, 6)} d |",
        f"| Main Mars vector | {fmt(rms_norm(main), 6)} | {fmt(number(mars, 'orbitRadius'), 6)} | {fmt(main_speed, 9)} rad/y | {fmt(main_period_days, 6)} d |",
        "",
        "The main period is produced by the sum of the nested angular rates:",
        "",
        "```text",
        f"{fmt(number(mars_e, 'speed'), 9)} + {fmt(number(mars_s, 'speed'), 9)} + ({fmt(number(mars, 'speed'), 9)})",
        f"= {fmt(main_speed, 9)} rad/model-year",
        f"=> {fmt(main_period_days, 6)} days",
        "```",
        "",
        "The shared Earth/PVP frame rotates at",
        f"`{fmt(inherited_frame_speed, 12)} rad/model-year`. In exported world",
        "coordinates this changes the main component's nominal period to",
        f"`{fmt(world_main_period_days, 6)} days` and the secondary component's",
        f"to `{fmt(world_secondary_period_days, 6)} days`; it does not change their",
        "instantaneous lengths or the carrier cancellation.",
        "",
        "## Why the remainder is ellipse-like",
        "",
        f"The deferent-S frequency is `{fmt(harmonic_ratio, 9)}` times the main frequency; exact second harmonic would be `2.0`.  ",
        f"Its radius/main-radius ratio is `{fmt(amplitude_ratio, 9)}`; twice that is `{fmt(twice_amplitude_ratio, 9)}`.  ",
        "The independently measured focus-ellipse eccentricity was `0.092325`.",
        "In the first-order Fourier form of a focus-centred Kepler ellipse, the",
        "second harmonic has radius approximately `a*e/2`; this geometry therefore",
        "predicts `e ≈ 2*7.44385/152.677 = 0.097511`, close to the measured value.",
        f"That same expansion has a constant term of magnitude `3*a*e/2`, or three",
        f"times the secondary radius: `{fmt(first_order_constant, 6)}` here. The actual",
        f"centre-difference magnitude is `{fmt(rms_norm(constant_component), 6)}`",
        f"(`{fmt(constant_difference_pct, 3)}%` relative difference). The orientations,",
        "small tilts, annual remainder and slight frequency detuning account for why",
        "the construction is ellipse-like rather than an exact two-term ellipse.",
        "",
        f"Second-harmonic detuning: `{fmt(harmonic_detuning, 12)} rad/year` (`{fmt(detuning_deg_per_year, 9)} deg/year`).  ",
        f"Corresponding full relative-phase cycle: approximately `{fmt(detuning_cycle_years, 3)} model years`.",
        "",
        "## Simplification checks",
        "",
        "| Approximation | RMS error versus exported Sun-Mars vector | Percent of mean Sun-Mars distance |",
        "|---|---:|---:|",
        f"| Drop only annual carrier mismatch | {fmt(rms_norm(mismatch_omission_error), 6)} | {fmt(100.0 * rms_norm(mismatch_omission_error) / np.mean(np.linalg.norm(exported_relative, axis=1)), 6)}% |",
        f"| Keep only main Mars vector | {fmt(rms_norm(main_only_error), 6)} | {fmt(100.0 * rms_norm(main_only_error) / np.mean(np.linalg.norm(exported_relative, axis=1)), 6)}% |",
        "",
        "## Interpretation",
        "",
        "- The near-687-day Sun-relative period is a direct consequence of the nested configured speeds, not a fitted correction.",
        "- The clean relative ellipse emerges because the two large annual radius-100 carrier vectors nearly cancel, exposing one main vector and one near-second-harmonic vector.",
        "- The small carrier mismatch and constant centre difference remain part of the accepted geometry and must not be silently discarded.",
        f"- The Earth-Mars maximum/minimum distance ratio remains `{fmt(earth_ratio, 6)}:1`; it is a separate observer-relative result.",
        "- Phase 3E may re-express these exact components as named Sun-relative transforms, but should preserve all four components before testing any simplification.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Algebraically decompose the existing Sun-relative Mars chain."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    settings_path = args.settings.resolve()
    times, sun_world, mars_world, earth_world = load_export(source)
    settings = settings_map(settings_path)
    report = analyze(
        source,
        settings_path,
        args.components.resolve(),
        times,
        sun_world,
        mars_world,
        earth_world,
        settings,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report.resolve()}")
    print(f"Wrote {args.components.resolve()}")


if __name__ == "__main__":
    main()
