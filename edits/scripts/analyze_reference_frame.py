#!/usr/bin/env python3
"""Test whether TYCHOS/JPL residuals contain one common rotating frame.

The script never modifies simulator settings.  It fits one proper 3-D rotation per
calendar year from selected anchor bodies, applies that rotation to independent
holdout bodies, and compares rotation-invariant pairwise angular separations.  A
linear rotation model fitted before ``--split-year`` is also projected into the
later interval so that a freely fitted annual rotation is not mistaken for proof of
a reference-frame difference.
"""

import argparse
import csv
from datetime import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

from compare_ephemerides import parse_jpl, parse_tychos
from ephemeris_io import (
    jpl_blocks,
    select_block,
    tychos_blocks,
    tychos_metadata,
    validate_jpl_header,
)


ROOT = Path(__file__).resolve().parents[2]
ARCSEC_PER_RADIAN = 180.0 * 3600.0 / math.pi
EPSILON_J2000_RAD = math.radians(23.439291111)
ECLIPTIC_NORTH = np.array(
    [0.0, -math.sin(EPSILON_J2000_RAD), math.cos(EPSILON_J2000_RAD)]
)
DEFAULT_ANCHORS = ("sun", "venus", "mars", "jupiter", "saturn", "uranus", "neptune")
DEFAULT_HOLDOUTS = ("moon", "mercury")
DEFAULT_PAIRWISE = DEFAULT_ANCHORS + DEFAULT_HOLDOUTS
BLOCKS = ((1800, 1849), (1850, 1899), (1900, 1949), (1950, 1999), (2000, 2026))


def comma_list(value):
    return tuple(item.strip().lower() for item in value.split(",") if item.strip())


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def radec_vectors(records, dates, ra_key, dec_key):
    ra = np.deg2rad(np.fromiter((records[date][ra_key] for date in dates), dtype=float))
    dec = np.deg2rad(np.fromiter((records[date][dec_key] for date in dates), dtype=float))
    cos_dec = np.cos(dec)
    return np.column_stack((cos_dec * np.cos(ra), cos_dec * np.sin(ra), np.sin(dec)))


def angular_errors(first, second):
    dots = np.einsum("ij,ij->i", first, second)
    return np.rad2deg(np.arccos(np.clip(dots, -1.0, 1.0)))


def rms(values):
    values = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(values * values)))


def proper_rotation(source, target):
    """Return R such that ``(R @ source.T).T`` best matches target."""
    covariance = source.T @ target
    left, _, right_t = np.linalg.svd(covariance)
    rotation = right_t.T @ left.T
    if np.linalg.det(rotation) < 0:
        right_t[-1, :] *= -1.0
        rotation = right_t.T @ left.T
    return rotation


def matrix_to_rotvec(rotation):
    cosine = np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0)
    angle = math.acos(float(cosine))
    if angle < 1e-12:
        return np.array(
            [rotation[2, 1] - rotation[1, 2],
             rotation[0, 2] - rotation[2, 0],
             rotation[1, 0] - rotation[0, 1]]
        ) / 2.0
    axis = np.array(
        [rotation[2, 1] - rotation[1, 2],
         rotation[0, 2] - rotation[2, 0],
         rotation[1, 0] - rotation[0, 1]]
    ) / (2.0 * math.sin(angle))
    return axis * angle


def rotvec_to_matrix(rotvec):
    angle = float(np.linalg.norm(rotvec))
    if angle < 1e-14:
        return np.eye(3)
    x, y, z = rotvec / angle
    cross = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + math.sin(angle) * cross + (1.0 - math.cos(angle)) * (cross @ cross)


def axis_rotate(vectors, axis, angles):
    """Rotate row vectors around one axis by a separate angle per row."""
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    angles = np.asarray(angles, dtype=float)
    cosine = np.cos(angles)[:, None]
    sine = np.sin(angles)[:, None]
    projection = (vectors @ axis)[:, None]
    return (
        vectors * cosine
        + np.cross(np.broadcast_to(axis, vectors.shape), vectors) * sine
        + projection * axis * (1.0 - cosine)
    )


def earth_frame_candidate(settings_path, dates, ty_vectors, jp_vectors, bodies):
    """Re-express exported vectors in the J2000 orientation used by star groups.

    Pobj puts Earth.cSphereRef below Earth's rotating orbit group, while all modeled
    targets are sibling children of cSphereRef.  worldToLocal therefore cancels the
    current Earth orbit rotation.  Stars.jsx and BSCStars.jsx instead freeze their
    group to Earth.cSphereRef at J2000.  This candidate restores that date-dependent
    orientation difference without modifying any orbit or exported input.
    """
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    earth = next(item for item in settings if item["name"] == "Earth")
    speed = float(earth["speed"])
    tilt = math.radians(float(earth.get("tilt", 0.0)))
    tiltb = math.radians(float(earth.get("tiltb", 0.0)))

    rx = np.array(
        [[1.0, 0.0, 0.0],
         [0.0, math.cos(tiltb), -math.sin(tiltb)],
         [0.0, math.sin(tiltb), math.cos(tiltb)]]
    )
    rz = np.array(
        [[math.cos(tilt), -math.sin(tilt), 0.0],
         [math.sin(tilt), math.cos(tilt), 0.0],
         [0.0, 0.0, 1.0]]
    )
    # Three.js local axes are (x, y, z)=(sin RA, sin Dec, cos RA).  Convert the
    # Earth-orbit +Y axis into cSphere local coordinates, then reorder to the
    # conventional equatorial vector axes used by this script.
    axis_three = (rx @ rz).T @ np.array([0.0, 1.0, 0.0])
    axis_equatorial = np.array([axis_three[2], axis_three[0], axis_three[1]])
    axis_equatorial /= np.linalg.norm(axis_equatorial)

    epoch = datetime(2000, 1, 1, 12, 0, 0)
    years_from_j2000 = np.fromiter(
        ((date - epoch).total_seconds() / (365.2425 * 86400.0) for date in dates),
        dtype=float,
    )
    angles = speed * years_from_j2000
    corrected = {
        body: axis_rotate(ty_vectors[body], axis_equatorial, angles) for body in bodies
    }
    body_results = {}
    for body in bodies:
        before = angular_errors(ty_vectors[body], jp_vectors[body])
        after = angular_errors(corrected[body], jp_vectors[body])
        body_results[body] = {
            "rms_before_deg": rms(before),
            "rms_after_code_frame_deg": rms(after),
            "variance_reduction_percent": float(
                100.0 * (1.0 - np.mean(after * after) / np.mean(before * before))
            ),
        }
    return {
        "settings_path": display_path(settings_path),
        "earth_speed_rad_per_model_year": speed,
        "earth_speed_arcsec_per_year": speed * ARCSEC_PER_RADIAN,
        "earth_tilt_deg": math.degrees(tilt),
        "earth_tiltb_deg": math.degrees(tiltb),
        "axis_equatorial_xyz": axis_equatorial.tolist(),
        "axis_dot_j2000_ecliptic_north": float(axis_equatorial @ ECLIPTIC_NORTH),
        "reference_epoch": epoch.isoformat(sep=" "),
        "body_results": body_results,
    }


def decimal_year(moment):
    start = datetime(moment.year, 1, 1)
    stop = datetime(moment.year + 1, 1, 1)
    return moment.year + (moment - start).total_seconds() / (stop - start).total_seconds()


def fit_linear_rotvec(years, rotvecs, reference_year=2000.0):
    centered = np.asarray(years, dtype=float) - reference_year
    design = np.column_stack((np.ones_like(centered), centered))
    coefficients, _, _, _ = np.linalg.lstsq(design, np.asarray(rotvecs), rcond=None)
    return coefficients[0], coefficients[1]


def concatenate_errors(bodies, first, second, mask=None):
    chunks = []
    for body in bodies:
        one = first[body] if mask is None else first[body][mask]
        two = second[body] if mask is None else second[body][mask]
        chunks.append(angular_errors(one, two))
    return np.concatenate(chunks)


def load_vectors(tychos_path, jpl_path, bodies, targets):
    ty_text = tychos_path.read_text(encoding="utf-8-sig")
    jp_text = jpl_path.read_text(encoding="utf-8-sig")
    ty_sections = tychos_blocks(ty_text)
    jp_sections = jpl_blocks(jp_text)
    ty_records = {}
    jp_records = {}
    common = None
    for body in bodies:
        target = targets[body]
        jp_block = select_block(jp_sections, target, "JPL")
        validate_jpl_header(jp_block)
        ty_records[body] = parse_tychos(
            select_block(ty_sections, body, "TYCHOS"), strict=True
        )
        jp_records[body] = parse_jpl(jp_block, strict=True)
        dates = set(ty_records[body]) & set(jp_records[body])
        if set(ty_records[body]) != set(jp_records[body]):
            raise ValueError(f"{body}: TYCHOS and JPL timestamps differ")
        common = dates if common is None else common & dates
    dates = sorted(common or ())
    if not dates:
        raise ValueError("No timestamps are common to all selected bodies")
    for body in bodies:
        if set(ty_records[body]) != set(dates):
            raise ValueError(f"{body}: timestamps differ from the common body grid")
    ty_vectors = {
        body: radec_vectors(ty_records[body], dates, "ra", "dec") for body in bodies
    }
    jp_vectors = {
        body: radec_vectors(jp_records[body], dates, "ra_icrf", "dec_icrf")
        for body in bodies
    }
    return dates, ty_vectors, jp_vectors


def evaluate_anchor_set(
    name,
    anchors,
    holdouts,
    dates,
    calendar_years,
    unique_years,
    annual_decimal_years,
    split_year,
    ty_vectors,
    jp_vectors,
):
    """Fit an anchor variant and summarize transfer to the same holdout bodies."""
    rotvecs = []
    annual_holdout_after = []
    for year in unique_years:
        mask = calendar_years == year
        source = np.concatenate([ty_vectors[body][mask] for body in anchors])
        target = np.concatenate([jp_vectors[body][mask] for body in anchors])
        rotation = proper_rotation(source, target)
        rotvecs.append(matrix_to_rotvec(rotation))
        for body in holdouts:
            rotated = ty_vectors[body][mask] @ rotation.T
            annual_holdout_after.append(angular_errors(rotated, jp_vectors[body][mask]))

    decimal_years = np.asarray(annual_decimal_years)
    rotvecs = np.asarray(rotvecs)
    train = decimal_years < split_year
    intercept, slope = fit_linear_rotvec(decimal_years[train], rotvecs[train])
    test_before = []
    test_after = []
    for year, mean_year in zip(unique_years, annual_decimal_years):
        if year < split_year:
            continue
        mask = calendar_years == year
        rotation = rotvec_to_matrix(intercept + slope * (mean_year - 2000.0))
        for body in holdouts:
            before = angular_errors(ty_vectors[body][mask], jp_vectors[body][mask])
            after = angular_errors(
                ty_vectors[body][mask] @ rotation.T, jp_vectors[body][mask]
            )
            test_before.append(before)
            test_after.append(after)

    holdout_before = concatenate_errors(holdouts, ty_vectors, jp_vectors)
    holdout_after = np.concatenate(annual_holdout_after)
    test_before = np.concatenate(test_before)
    test_after = np.concatenate(test_after)
    perpendicular = slope - (slope @ ECLIPTIC_NORTH) * ECLIPTIC_NORTH
    return {
        "name": name,
        "anchors": list(anchors),
        "ecliptic_pole_slope_arcsec_per_year": float(
            slope @ ECLIPTIC_NORTH * ARCSEC_PER_RADIAN
        ),
        "perpendicular_rate_arcsec_per_year": float(
            np.linalg.norm(perpendicular) * ARCSEC_PER_RADIAN
        ),
        "holdout_rms_before_deg": rms(holdout_before),
        "holdout_rms_after_annual_rotation_deg": rms(holdout_after),
        "holdout_annual_variance_reduction_percent": float(
            100.0
            * (1.0 - np.mean(holdout_after * holdout_after) / np.mean(holdout_before * holdout_before))
        ),
        "holdout_test_rms_before_deg": rms(test_before),
        "holdout_test_rms_after_predicted_rotation_deg": rms(test_after),
        "holdout_test_variance_reduction_percent": float(
            100.0
            * (1.0 - np.mean(test_after * test_after) / np.mean(test_before * test_before))
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tychos", type=Path,
        default=ROOT / "edits/data/raw/tychos_ephemerides.txt",
    )
    parser.add_argument(
        "--jpl", type=Path,
        default=ROOT / "edits/data/raw/jpl_ephemerides.txt",
    )
    parser.add_argument("--anchors", type=comma_list, default=DEFAULT_ANCHORS)
    parser.add_argument("--holdouts", type=comma_list, default=DEFAULT_HOLDOUTS)
    parser.add_argument("--pairwise", type=comma_list, default=DEFAULT_PAIRWISE)
    parser.add_argument("--split-year", type=int, default=1950)
    parser.add_argument(
        "--settings", type=Path,
        default=ROOT / "src/settings/celestial-settings.json",
        help="Settings used to derive the code-level Earth/J2000 orientation candidate",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "edits/reports/reference_frame_audit.md",
    )
    parser.add_argument(
        "--csv-output", type=Path,
        default=ROOT / "edits/reports/reference_frame_rotation.csv",
    )
    parser.add_argument(
        "--json-output", type=Path,
        default=ROOT / "edits/reports/reference_frame_audit.json",
    )
    args = parser.parse_args(argv)

    targets = {
        body: settings["target_id"]
        for body, settings in json.loads(
            (Path(__file__).with_name("bodies.json")).read_text(encoding="utf-8")
        ).items()
    }
    selected = tuple(dict.fromkeys(args.anchors + args.holdouts + args.pairwise))
    unknown = sorted(set(selected) - set(targets))
    if unknown:
        parser.error(f"Unknown bodies: {unknown}")
    overlap = sorted(set(args.anchors) & set(args.holdouts))
    if overlap:
        parser.error(f"Anchor and holdout bodies overlap: {overlap}")
    if len(args.anchors) < 2:
        parser.error("At least two non-collinear anchor bodies are required")

    tychos_path = args.tychos.resolve()
    jpl_path = args.jpl.resolve()
    export_metadata = tychos_metadata(
        tychos_path.read_text(encoding="utf-8-sig")
    )
    dates, ty_vectors, jp_vectors = load_vectors(
        tychos_path, jpl_path, selected, targets
    )
    calendar_years = np.fromiter((date.year for date in dates), dtype=int)
    unique_years = np.unique(calendar_years)
    if args.split_year <= unique_years.min() or args.split_year > unique_years.max():
        parser.error("--split-year must leave dates on both sides of the split")

    corrected = {body: np.empty_like(ty_vectors[body]) for body in selected}
    annual = []
    annual_rotvecs = []
    annual_decimal_years = []
    for year in unique_years:
        mask = calendar_years == year
        source = np.concatenate([ty_vectors[body][mask] for body in args.anchors])
        target = np.concatenate([jp_vectors[body][mask] for body in args.anchors])
        rotation = proper_rotation(source, target)
        rotvec = matrix_to_rotvec(rotation)
        for body in selected:
            corrected[body][mask] = ty_vectors[body][mask] @ rotation.T
        before = concatenate_errors(args.anchors, ty_vectors, jp_vectors, mask)
        after = concatenate_errors(args.anchors, corrected, jp_vectors, mask)
        holdout_before = concatenate_errors(args.holdouts, ty_vectors, jp_vectors, mask)
        holdout_after = concatenate_errors(args.holdouts, corrected, jp_vectors, mask)
        mean_year = float(np.mean([decimal_year(date) for date in np.asarray(dates)[mask]]))
        ecliptic_component = float(rotvec @ ECLIPTIC_NORTH)
        perpendicular = rotvec - ecliptic_component * ECLIPTIC_NORTH
        record = {
            "year": int(year),
            "decimal_year": mean_year,
            "n_dates": int(mask.sum()),
            "rot_x_arcsec": float(rotvec[0] * ARCSEC_PER_RADIAN),
            "rot_y_arcsec": float(rotvec[1] * ARCSEC_PER_RADIAN),
            "rot_z_arcsec": float(rotvec[2] * ARCSEC_PER_RADIAN),
            "ecliptic_pole_arcsec": float(ecliptic_component * ARCSEC_PER_RADIAN),
            "perpendicular_arcsec": float(np.linalg.norm(perpendicular) * ARCSEC_PER_RADIAN),
            "rotation_angle_arcsec": float(np.linalg.norm(rotvec) * ARCSEC_PER_RADIAN),
            "anchor_rms_before_deg": rms(before),
            "anchor_rms_after_deg": rms(after),
            "holdout_rms_before_deg": rms(holdout_before),
            "holdout_rms_after_deg": rms(holdout_after),
        }
        annual.append(record)
        annual_rotvecs.append(rotvec)
        annual_decimal_years.append(mean_year)

    train = np.asarray(annual_decimal_years) < args.split_year
    intercept, slope = fit_linear_rotvec(
        np.asarray(annual_decimal_years)[train], np.asarray(annual_rotvecs)[train]
    )
    predicted = {body: np.array(ty_vectors[body], copy=True) for body in selected}
    for year, mean_year in zip(unique_years, annual_decimal_years):
        if year < args.split_year:
            continue
        mask = calendar_years == year
        rotation = rotvec_to_matrix(intercept + slope * (mean_year - 2000.0))
        for body in selected:
            predicted[body][mask] = ty_vectors[body][mask] @ rotation.T

    test_mask = calendar_years >= args.split_year
    body_results = {}
    for body in selected:
        before = angular_errors(ty_vectors[body], jp_vectors[body])
        after = angular_errors(corrected[body], jp_vectors[body])
        test_before = before[test_mask]
        test_after = angular_errors(
            predicted[body][test_mask], jp_vectors[body][test_mask]
        )
        body_results[body] = {
            "role": (
                "anchor" if body in args.anchors
                else "holdout" if body in args.holdouts
                else "pairwise-only"
            ),
            "rms_before_deg": rms(before),
            "rms_after_annual_rotation_deg": rms(after),
            "annual_variance_reduction_percent": float(
                100.0 * (1.0 - np.mean(after * after) / np.mean(before * before))
            ),
            "test_start_year": args.split_year,
            "test_rms_before_deg": rms(test_before),
            "test_rms_after_predicted_rotation_deg": rms(test_after),
            "test_variance_reduction_percent": float(
                100.0
                * (1.0 - np.mean(test_after * test_after) / np.mean(test_before * test_before))
            ),
        }

    pair_results = []
    pair_errors = {}
    for first, second in itertools.combinations(args.pairwise, 2):
        ty_separation = angular_errors(ty_vectors[first], ty_vectors[second])
        jp_separation = angular_errors(jp_vectors[first], jp_vectors[second])
        difference = ty_separation - jp_separation
        key = f"{first}-{second}"
        pair_errors[key] = difference
        pair_results.append({"pair": key, "rms_deg": rms(difference)})
    pair_results.sort(key=lambda item: item["rms_deg"], reverse=True)

    pairwise_blocks = []
    for start, stop in BLOCKS:
        mask = (calendar_years >= start) & (calendar_years <= stop)
        if not np.any(mask):
            continue
        combined = np.concatenate([errors[mask] for errors in pair_errors.values()])
        pairwise_blocks.append(
            {
                "start_year": start,
                "stop_year": stop,
                "rms_deg": rms(combined),
                "n_pair_dates": int(combined.size),
            }
        )

    intercept_arcsec = intercept * ARCSEC_PER_RADIAN
    slope_arcsec = slope * ARCSEC_PER_RADIAN
    ecliptic_intercept = float(intercept @ ECLIPTIC_NORTH * ARCSEC_PER_RADIAN)
    ecliptic_slope = float(slope @ ECLIPTIC_NORTH * ARCSEC_PER_RADIAN)
    perpendicular_slope = slope - (slope @ ECLIPTIC_NORTH) * ECLIPTIC_NORTH
    trend = {
        "reference_year": 2000.0,
        "fit_stop_exclusive": args.split_year,
        "rot_x_at_reference_arcsec": float(intercept_arcsec[0]),
        "rot_y_at_reference_arcsec": float(intercept_arcsec[1]),
        "rot_z_at_reference_arcsec": float(intercept_arcsec[2]),
        "rot_x_slope_arcsec_per_year": float(slope_arcsec[0]),
        "rot_y_slope_arcsec_per_year": float(slope_arcsec[1]),
        "rot_z_slope_arcsec_per_year": float(slope_arcsec[2]),
        "ecliptic_pole_at_reference_arcsec": ecliptic_intercept,
        "ecliptic_pole_slope_arcsec_per_year": ecliptic_slope,
        "perpendicular_rate_arcsec_per_year": float(
            np.linalg.norm(perpendicular_slope) * ARCSEC_PER_RADIAN
        ),
    }

    sensitivity_specs = [("default", args.anchors)]
    without_sun = tuple(body for body in args.anchors if body != "sun")
    if len(without_sun) >= 2:
        sensitivity_specs.append(("without Sun", without_sun))
    outer = tuple(
        body for body in ("jupiter", "saturn", "uranus", "neptune")
        if body in selected
    )
    if len(outer) >= 2:
        sensitivity_specs.append(("outer planets", outer))
    anchor_sensitivity = []
    seen_anchor_sets = set()
    for name, anchors in sensitivity_specs:
        if anchors in seen_anchor_sets:
            continue
        seen_anchor_sets.add(anchors)
        anchor_sensitivity.append(
            evaluate_anchor_set(
                name,
                anchors,
                args.holdouts,
                dates,
                calendar_years,
                unique_years,
                annual_decimal_years,
                args.split_year,
                ty_vectors,
                jp_vectors,
            )
        )

    code_candidate = None
    if export_metadata["reference_frame"] != "j2000-icrf":
        code_candidate = earth_frame_candidate(
            args.settings.resolve(), dates, ty_vectors, jp_vectors, selected
        )

    report = {
        "method": "annual proper rotations fitted by the Kabsch/Wahba solution",
        "reference": "JPL ICRF astrometric RA/Dec",
        "anchors": list(args.anchors),
        "holdouts": list(args.holdouts),
        "pairwise_bodies": list(args.pairwise),
        "split_year": args.split_year,
        "n_dates": len(dates),
        "start": dates[0].isoformat(sep=" "),
        "stop": dates[-1].isoformat(sep=" "),
        "inputs": {
            "tychos": {
                "path": display_path(tychos_path),
                "sha256": fingerprint(tychos_path),
                **export_metadata,
            },
            "jpl": {
                "path": display_path(jpl_path),
                "sha256": fingerprint(jpl_path),
            },
        },
        "linear_rotation_trend": trend,
        "anchor_sensitivity": anchor_sensitivity,
        "code_derived_j2000_candidate": code_candidate,
        "body_results": body_results,
        "pairwise_blocks": pairwise_blocks,
        "largest_pairwise_errors": pair_results[:10],
        "annual_rotations": annual,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(annual[0]))
        writer.writeheader()
        writer.writerows(annual)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# TYCHOS/JPL reference-frame audit",
        "",
        f"Interval: `{report['start']}` to `{report['stop']}`; "
        f"`{report['n_dates']}` common timestamps.",
        "",
        "This is a diagnostic coordinate rotation, not a correction applied to TYCHOS.",
        "One proper 3-D rotation is fitted per year from the anchor bodies. Moon and",
        "Mercury are holdouts and do not influence those annual rotations. A linear",
        f"rotation model fitted before {args.split_year} is then projected into the",
        "later interval as a temporal-transfer test.",
        "",
        f"Anchors: `{', '.join(args.anchors)}`.",
        f"Holdouts: `{', '.join(args.holdouts)}`.",
        "",
        "## Linear rotation trend",
        "",
        f"Fit interval: dates before `{args.split_year}`; components use equatorial",
        "ICRF axes. The ecliptic-pole component is the projection onto the fixed J2000",
        "ecliptic north pole.",
        "",
        "| Component | At J2000 | Rate |",
        "|---|---:|---:|",
        f"| X | {trend['rot_x_at_reference_arcsec']:.2f} arcsec | "
        f"{trend['rot_x_slope_arcsec_per_year']:.3f} arcsec/year |",
        f"| Y | {trend['rot_y_at_reference_arcsec']:.2f} arcsec | "
        f"{trend['rot_y_slope_arcsec_per_year']:.3f} arcsec/year |",
        f"| Z | {trend['rot_z_at_reference_arcsec']:.2f} arcsec | "
        f"{trend['rot_z_slope_arcsec_per_year']:.3f} arcsec/year |",
        f"| J2000 ecliptic-pole projection | {ecliptic_intercept:.2f} arcsec | "
        f"{ecliptic_slope:.3f} arcsec/year |",
        f"| Rate perpendicular to ecliptic pole | — | "
        f"{trend['perpendicular_rate_arcsec_per_year']:.3f} arcsec/year |",
        "",
        "### Anchor-set sensitivity",
        "",
        "The same pre-split fit is repeated with different anchor sets. Stable rates",
        "argue against one body creating the inferred rotation. Holdout reductions combine",
        f"Moon and Mercury, neither of which participates in any fit.",
        "",
        "| Anchors | Ecliptic-pole rate | Perpendicular rate | Annual holdout reduction | "
        f"Transferred holdout reduction {args.split_year}+ |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in anchor_sensitivity:
        lines.append(
            f"| {item['name']} (`{', '.join(item['anchors'])}`) | "
            f"{item['ecliptic_pole_slope_arcsec_per_year']:.3f} arcsec/year | "
            f"{item['perpendicular_rate_arcsec_per_year']:.3f} arcsec/year | "
            f"{item['holdout_annual_variance_reduction_percent']:.1f}% | "
            f"{item['holdout_test_variance_reduction_percent']:.1f}% |"
        )
    lines.extend(["", "### Code-derived Earth/J2000 candidate", ""])
    if code_candidate:
        lines.extend([
            "The application freezes its star groups to `Earth.cSphereRef` at J2000, but",
            "the legacy planetary export uses `Earth.cSphereRef.worldToLocal` at each date.",
            "Because the modeled targets are children of Earth but siblings of cSphereRef,",
            "the current Earth-orbit rotation cancels from the legacy planetary vectors.",
            "The table below restores exactly the Earth-orbit orientation relative to the",
            "J2000 star orientation, using current settings and no fitted parameter.",
            "",
            f"Earth rotation rate: `{code_candidate['earth_speed_arcsec_per_year']:.6f}`",
            "arcsec/model-year. Axis alignment with fixed J2000 ecliptic north:",
            f"`{code_candidate['axis_dot_j2000_ecliptic_north']:.9f}`.",
            "",
            "| Body | Raw RMS | Code-derived J2000 RMS | Variance reduction |",
            "|---|---:|---:|---:|",
        ])
        for body in selected:
            values = code_candidate["body_results"][body]
            lines.append(
                f"| {body.title()} | {values['rms_before_deg']:.4f}° | "
                f"{values['rms_after_code_frame_deg']:.4f}° | "
                f"{values['variance_reduction_percent']:.1f}% |"
            )
        lines.extend([
            "",
            "This is a diagnostic re-expression of a native or unlabelled legacy export;",
            "it does not modify the saved input ephemerides.",
        ])
    else:
        lines.extend([
            "The TYCHOS input declares the `J2000 / ICRF comparison` frame. No additional",
            "Earth/PVP orientation is applied; doing so would double-rotate the export.",
        ])
    lines.extend([
        "",
        "## Absolute-direction residuals",
        "",
        "`Annual rotated` uses a separately fitted rotation each year. `Transferred`",
        f"uses only the linear rotation learned before {args.split_year} and evaluates",
        "the later interval. Reductions for anchor bodies are partly in-sample; reductions",
        "for Moon and Mercury are independent-body transfer evidence.",
        "",
        "| Body | Role | Raw RMS | Annual rotated RMS | Variance reduction | "
        f"Raw RMS {args.split_year}+ | Transferred RMS {args.split_year}+ | Test reduction |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for body, values in body_results.items():
        lines.append(
            f"| {body.title()} | {values['role']} | {values['rms_before_deg']:.4f}° | "
            f"{values['rms_after_annual_rotation_deg']:.4f}° | "
            f"{values['annual_variance_reduction_percent']:.1f}% | "
            f"{values['test_rms_before_deg']:.4f}° | "
            f"{values['test_rms_after_predicted_rotation_deg']:.4f}° | "
            f"{values['test_variance_reduction_percent']:.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Rotation-invariant pairwise separations",
            "",
            "A common rotation cannot change an angular separation between two bodies.",
            "The following RMS combines every selected body pair and timestamp in each",
            "block. Growth here must come from body geometry, timing/observable differences",
            "or another non-rotational effect.",
            "",
            "| Block | Pairwise-separation RMS |",
            "|---|---:|",
        ]
    )
    for block in pairwise_blocks:
        lines.append(
            f"| {block['start_year']}-{block['stop_year']} | {block['rms_deg']:.4f}° |"
        )
    lines.extend(
        [
            "",
            "Largest full-interval pairwise discrepancies:",
            "",
            "| Pair | RMS |",
            "|---|---:|",
        ]
    )
    for item in pair_results[:10]:
        lines.append(f"| {item['pair']} | {item['rms_deg']:.4f}° |")
    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- A successful common rotation is evidence for an orientation mismatch, not",
            "  proof of which physical or coordinate convention is correct.",
            "- Annual rotations can absorb the average of anchor-body orbital errors; the",
            "  holdout and post-split transfer columns are therefore essential.",
            "- Pairwise errors are frame-rotation invariant but may still include light-time,",
            "  aberration, timing and geometric-model differences.",
            "- No fitted rotation is applied to simulator output or celestial settings.",
            "",
        ]
    )
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    print(args.csv_output)
    print(args.json_output)


if __name__ == "__main__":
    main()
