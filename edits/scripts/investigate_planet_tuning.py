"""Screen Pluto and Mercury geometry against the saved ephemeris comparisons.

This is an analysis aid. It never edits celestial-settings.json. Simulator
exports remain the authoritative validation for any candidate parameter.
"""

import argparse
import copy
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
D2R = math.pi / 180.0
EPOCH = datetime(2000, 6, 21, 12)
YEAR_DAYS = 365.2425

CHAINS = {
    "pluto": ["Sun deferent", "Sun", "Pluto deferent", "Pluto"],
    "mercury": ["Mercury deferent A", "Mercury deferent B", "Mercury"],
}


def rx(angle):
    c, s = np.cos(angle), np.sin(angle)
    out = np.zeros((len(np.atleast_1d(angle)), 3, 3)) if np.ndim(angle) else np.empty((3, 3))
    if np.ndim(angle):
        out[:, 0, 0] = 1
        out[:, 1, 1] = c
        out[:, 1, 2] = -s
        out[:, 2, 1] = s
        out[:, 2, 2] = c
    else:
        out[:] = ((1, 0, 0), (0, c, -s), (0, s, c))
    return out


def ry(angle):
    c, s = np.cos(angle), np.sin(angle)
    out = np.zeros((len(np.atleast_1d(angle)), 3, 3)) if np.ndim(angle) else np.empty((3, 3))
    if np.ndim(angle):
        out[:, 0, 0] = c
        out[:, 0, 2] = s
        out[:, 1, 1] = 1
        out[:, 2, 0] = -s
        out[:, 2, 2] = c
    else:
        out[:] = ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return out


def rz(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)))


def apply(matrix, vectors):
    return np.einsum("nij,nj->ni", matrix, vectors) if matrix.ndim == 3 else vectors @ matrix.T


def number(setting, key):
    return float(setting.get(key, 0) or 0)


def setting_map(path):
    return {item["name"]: item for item in json.loads(path.read_text(encoding="utf-8"))}


def unit_vectors(ra, dec):
    return np.column_stack((np.sin(ra) * np.cos(dec), np.sin(dec), np.cos(ra) * np.cos(dec)))


def load_comparison(body, stride):
    path = ROOT / f"edits/data/derived/{body}_comparison.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))[::stride]
    dates = np.array([datetime.fromisoformat(row["date"]) for row in rows])
    positions = np.array([(date - EPOCH).total_seconds() / 86400.0 / YEAR_DAYS for date in dates])
    jpl = unit_vectors(
        np.deg2rad([float(row["jpl_ra_icrf_deg"]) for row in rows]),
        np.deg2rad([float(row["jpl_dec_icrf_deg"]) for row in rows]),
    )
    exported = unit_vectors(
        np.deg2rad([float(row["ty_ra_deg"]) for row in rows]),
        np.deg2rad([float(row["ty_dec_deg"]) for row in rows]),
    )
    return dates, positions, jpl, exported


def model(settings, body, positions):
    vectors = np.zeros((len(positions), 3))
    zeros = np.zeros(len(positions))
    for name in reversed(CHAINS[body]):
        setting = settings[name]
        angle = number(setting, "speed") * positions - number(setting, "startPos") * D2R
        radius = np.column_stack((np.full(len(positions), number(setting, "orbitRadius")), zeros, zeros))
        center = np.array(
            (
                number(setting, "orbitCentera"),
                number(setting, "orbitCenterc"),
                number(setting, "orbitCenterb"),
            )
        )
        tilt = rx(number(setting, "orbitTilta") * D2R) @ rz(number(setting, "orbitTiltb") * D2R)
        vectors = center + apply(tilt, apply(ry(angle), radius + vectors))

    earth = settings["Earth"]
    earth_frame = rx(number(earth, "tiltb") * D2R) @ rz(number(earth, "tilt") * D2R)
    vectors = apply(earth_frame.T, vectors)
    return vectors / np.linalg.norm(vectors, axis=1)[:, None]


def metrics(predicted, reference):
    dot = np.clip(np.sum(predicted * reference, axis=1), -1, 1)
    separation = np.rad2deg(np.arccos(dot))
    ra = np.unwrap(np.arctan2(predicted[:, 0], predicted[:, 2]))
    ref_ra = np.unwrap(np.arctan2(reference[:, 0], reference[:, 2]))
    dec = np.arcsin(predicted[:, 1])
    ref_dec = np.arcsin(reference[:, 1])
    obliquity = 23.439291111 * D2R
    def ecliptic(vectors):
        x = vectors[:, 2]
        y = vectors[:, 0] * np.cos(obliquity) + vectors[:, 1] * np.sin(obliquity)
        z = -vectors[:, 0] * np.sin(obliquity) + vectors[:, 1] * np.cos(obliquity)
        return np.unwrap(np.arctan2(y, x)), np.arcsin(z)
    lon, lat = ecliptic(predicted)
    ref_lon, ref_lat = ecliptic(reference)
    rms = lambda values: float(np.sqrt(np.mean(np.square(values))))
    return {
        "separation_rms": rms(separation),
        "ra_rms": rms(np.rad2deg(ra - ref_ra)),
        "dec_rms": rms(np.rad2deg(dec - ref_dec)),
        "longitude_rms": rms(np.rad2deg(lon - ref_lon)),
        "latitude_rms": rms(np.rad2deg(lat - ref_lat)),
        "separation_mean": float(np.mean(separation)),
    }


def candidate_dimensions(body):
    if body == "pluto":
        return [
            ("Pluto", "startPos", 2.0),
            ("Pluto", "speed", 0.001),
            ("Pluto", "orbitCentera", 100.0),
            ("Pluto", "orbitCenterb", 100.0),
            ("Pluto", "orbitCenterc", 100.0),
            ("Pluto", "orbitTilta", 2.0),
            ("Pluto", "orbitTiltb", 2.0),
            ("Pluto deferent", "startPos", 2.0),
        ]
    return [
        ("Mercury", "startPos", 1.0),
        ("Mercury", "speed", 0.002),
        ("Mercury", "orbitCenterb", 0.5),
        ("Mercury", "orbitCenterc", 0.2),
        ("Mercury", "orbitTilta", 0.5),
        ("Mercury", "orbitTiltb", 0.5),
        ("Mercury deferent B", "startPos", 1.0),
        ("Mercury deferent B", "orbitRadius", 0.2),
        ("Mercury deferent B", "orbitTilta", 0.5),
        ("Mercury deferent B", "orbitTiltb", 0.5),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("body", choices=sorted(CHAINS))
    parser.add_argument("--stride", type=int, default=8, help="Use every Nth three-hour sample")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--fix-speed", action="store_true", help="Exclude orbital speed from descent")
    args = parser.parse_args()

    dates, positions, reference, exported = load_comparison(args.body, args.stride)
    settings = setting_map(ROOT / "src/settings/celestial-settings.json")
    reconstructed = model(settings, args.body, positions)
    print("samples", len(positions), "stride", args.stride)
    print("reconstruction_vs_export", metrics(reconstructed, exported))
    print("baseline_vs_jpl", metrics(reconstructed, reference))

    train = dates < datetime(2020, 1, 1)
    test = ~train
    trial = copy.deepcopy(settings)
    dimensions = candidate_dimensions(args.body)
    if args.fix_speed:
        dimensions = [dimension for dimension in dimensions if dimension[1] != "speed"]
    print("baseline_train", metrics(reconstructed[train], reference[train]))
    print("baseline_test", metrics(reconstructed[test], reference[test]))

    print("single_parameter_screen")
    for name, key, initial_step in dimensions:
        current = number(settings[name], key)
        results = []
        for multiple in (-3, -2, -1, -0.5, 0, 0.5, 1, 2, 3):
            value = current + initial_step * multiple
            candidate = copy.deepcopy(settings)
            candidate[name][key] = value
            train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
            test_score = metrics(model(candidate, args.body, positions[test]), reference[test])
            results.append((train_score["separation_rms"], value, test_score["separation_rms"]))
        best = min(results, key=lambda item: item[0])
        print(f"{name}.{key}", {"value": best[1], "train_sep_rms": best[0], "test_sep_rms": best[2]})

    if args.body == "pluto":
        speed_results = []
        current_speed = number(settings["Pluto"], "speed")
        for value in np.linspace(current_speed - 0.004, current_speed + 0.008, 121):
            candidate = copy.deepcopy(settings)
            candidate["Pluto"]["speed"] = float(value)
            train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
            test_score = metrics(model(candidate, args.body, positions[test]), reference[test])
            speed_results.append((train_score["separation_rms"], float(value), test_score["separation_rms"]))
        print("fine_Pluto.speed", min(speed_results, key=lambda item: item[0]))
        center_results = []
        for value in np.linspace(950.0, 1150.0, 81):
            candidate = copy.deepcopy(settings)
            candidate["Pluto"]["orbitCentera"] = float(value)
            train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
            test_score = metrics(model(candidate, args.body, positions[test]), reference[test])
            center_results.append((train_score["separation_rms"], float(value), test_score["separation_rms"]))
        print("fine_Pluto.orbitCentera", min(center_results, key=lambda item: item[0]))
        print("Pluto.orbitCentera_tradeoff")
        for value in (950.0, 1000.0, 1050.0, 1100.0, 1110.0):
            candidate = copy.deepcopy(settings)
            candidate["Pluto"]["orbitCentera"] = value
            print(value, metrics(model(candidate, args.body, positions), reference))
        plane_results = []
        for center_a in np.linspace(950.0, 1200.0, 26):
            for tilt_a in np.linspace(10.0, 20.0, 41):
                candidate = copy.deepcopy(settings)
                candidate["Pluto"]["orbitCentera"] = float(center_a)
                candidate["Pluto"]["orbitTilta"] = float(tilt_a)
                train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
                plane_results.append((train_score["separation_rms"], float(center_a), float(tilt_a)))
        best_train, center_a, tilt_a = min(plane_results, key=lambda item: item[0])
        candidate = copy.deepcopy(settings)
        candidate["Pluto"]["orbitCentera"] = center_a
        candidate["Pluto"]["orbitTilta"] = tilt_a
        print(
            "fine_Pluto.center_tilt",
            {"center_a": center_a, "tilt_a": tilt_a, "train_sep_rms": best_train,
             "all": metrics(model(candidate, args.body, positions), reference),
             "test": metrics(model(candidate, args.body, positions[test]), reference[test])},
        )
    else:
        for key, low, high in (("orbitCenterb", -1.0, 4.0), ("orbitTilta", 2.0, 10.0)):
            results = []
            for value in np.linspace(low, high, 81):
                candidate = copy.deepcopy(settings)
                candidate["Mercury"][key] = float(value)
                train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
                test_score = metrics(model(candidate, args.body, positions[test]), reference[test])
                results.append((train_score["separation_rms"], float(value), test_score["separation_rms"]))
            print(f"fine_Mercury.{key}", min(results, key=lambda item: item[0]))
        radius_results = []
        for value in np.linspace(0.0, 0.8, 81):
            candidate = copy.deepcopy(settings)
            candidate["Mercury deferent B"]["orbitRadius"] = float(value)
            train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
            test_score = metrics(model(candidate, args.body, positions[test]), reference[test])
            radius_results.append((train_score["separation_rms"], float(value), test_score["separation_rms"]))
        _, radius, test_sep = min(radius_results, key=lambda item: item[0])
        candidate = copy.deepcopy(settings)
        candidate["Mercury deferent B"]["orbitRadius"] = radius
        print(
            "fine_Mercury.deferent_B_radius",
            {"radius": radius, "test_sep_rms": test_sep,
             "all": metrics(model(candidate, args.body, positions), reference)},
        )
        phase_results = []
        mercury_phase = number(settings["Mercury"], "startPos")
        deferent_phase = number(settings["Mercury deferent B"], "startPos")
        for planet_start in np.linspace(mercury_phase - 10.0, mercury_phase + 10.0, 41):
            for deferent_start in np.linspace(deferent_phase - 10.0, deferent_phase + 10.0, 41):
                candidate = copy.deepcopy(settings)
                candidate["Mercury"]["startPos"] = float(planet_start)
                candidate["Mercury deferent B"]["startPos"] = float(deferent_start)
                train_score = metrics(model(candidate, args.body, positions[train]), reference[train])
                phase_results.append((train_score["separation_rms"], float(planet_start), float(deferent_start)))
        train_sep, planet_start, deferent_start = min(phase_results, key=lambda item: item[0])
        candidate = copy.deepcopy(settings)
        candidate["Mercury"]["startPos"] = planet_start
        candidate["Mercury deferent B"]["startPos"] = deferent_start
        print(
            "fine_Mercury.phases",
            {"planet_start": planet_start, "deferent_start": deferent_start,
             "train_sep_rms": train_sep,
             "all": metrics(model(candidate, args.body, positions), reference),
             "test": metrics(model(candidate, args.body, positions[test]), reference[test])},
        )

    for round_number in range(args.rounds):
        for name, key, initial_step in dimensions:
            step = initial_step / (2**round_number)
            current = number(trial[name], key)
            choices = []
            for value in (current - step, current, current + step):
                candidate = copy.deepcopy(trial)
                candidate[name][key] = value
                prediction = model(candidate, args.body, positions[train])
                choices.append((metrics(prediction, reference[train])["separation_rms"], value, candidate))
            _, value, trial = min(choices, key=lambda item: item[0])
        train_metrics = metrics(model(trial, args.body, positions[train]), reference[train])
        test_metrics = metrics(model(trial, args.body, positions[test]), reference[test])
        values = {f"{name}.{key}": number(trial[name], key) for name, key, _ in dimensions}
        print("round", round_number + 1, "train", train_metrics, "test", test_metrics)
        print("values", json.dumps(values, sort_keys=True))


if __name__ == "__main__":
    main()
