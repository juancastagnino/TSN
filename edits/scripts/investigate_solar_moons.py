"""Test a solar-satellite interpretation for Mercury and Venus.

The script is deliberately read-only.  It uses the saved comparison CSV files
and never changes celestial-settings.json.  A "fixed plane" here means that
the annual proxy/counter-rotation pair has no intervening tilt; the orbital
plane is then expressed on the planet object itself.  This is the simplest
test of a shared solar-equatorial plane without copying the Moon's 18.6-year
node motion.
"""

import argparse
import copy
from datetime import datetime

import numpy as np

from investigate_planet_tuning import (
    ROOT,
    load_comparison,
    metrics,
    model,
    number,
    setting_map,
)


BODIES = ("mercury", "venus")
PLANES = {"mercury": "Mercury Plane", "venus": "Venus Plane"}
DEFERENTS_B = {"mercury": "Mercury deferent B", "venus": "Venus deferent B"}


def score(settings, datasets, selection=None):
    values = {}
    for body in BODIES:
        dates, positions, reference, _ = datasets[body]
        if selection is None:
            selected = np.ones(len(dates), dtype=bool)
        else:
            selected = selection(dates)
        values[body] = metrics(
            model(settings, body, positions[selected]), reference[selected]
        )
    return values


def normalized_objective(results, baselines):
    return sum(
        results[body]["separation_rms"] / baselines[body]["separation_rms"]
        for body in BODIES
    ) / len(BODIES)


def fixed_plane(settings):
    candidate = copy.deepcopy(settings)
    for deferent in DEFERENTS_B.values():
        candidate[deferent]["orbitTilta"] = 0.0
        candidate[deferent]["orbitTiltb"] = 0.0
    return candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stride", type=int, default=24)
    parser.add_argument("--tilt-step", type=float, default=0.2)
    parser.add_argument("--node-step", type=float, default=0.2)
    args = parser.parse_args()

    settings = setting_map(ROOT / "src/settings/celestial-settings.json")
    datasets = {body: load_comparison(body, args.stride) for body in BODIES}
    train = lambda dates: dates < datetime(2020, 1, 1)
    test = lambda dates: dates >= datetime(2020, 1, 1)

    baseline_all = score(settings, datasets)
    baseline_train = score(settings, datasets, train)
    baseline_test = score(settings, datasets, test)
    print("baseline_all", baseline_all)
    print("baseline_train", baseline_train)
    print("baseline_test", baseline_test)

    fixed = fixed_plane(settings)
    print("remove_intervening_deferent_tilt", score(fixed, datasets))

    # First let each satellite choose its own fixed plane.  This establishes
    # whether the data favour the same orientation before imposing sharing.
    individual = {}
    for body in BODIES:
        plane = PLANES[body]
        best = None
        for tilt in np.arange(0.0, 8.0001, args.tilt_step):
            for node in np.arange(-3.0, 3.0001, args.node_step):
                candidate = copy.deepcopy(fixed)
                candidate[plane]["orbitTilta"] = float(tilt)
                candidate[plane]["orbitTiltb"] = float(node)
                result = score(candidate, datasets, train)[body]
                item = (result["separation_rms"], float(tilt), float(node), candidate)
                if best is None or item[0] < best[0]:
                    best = item
        _, tilt, node, candidate = best
        individual[body] = {
            "tilt": tilt,
            "node": node,
            "all": score(candidate, datasets)[body],
            "train": score(candidate, datasets, train)[body],
            "test": score(candidate, datasets, test)[body],
        }
    print("best_individual_fixed_planes", individual)

    # Impose one orientation on both bodies.  Equal relative weighting keeps
    # Mercury's larger absolute residual from drowning out Venus.
    best = None
    for tilt in np.arange(0.0, 8.0001, args.tilt_step):
        for node in np.arange(-3.0, 3.0001, args.node_step):
            candidate = copy.deepcopy(fixed)
            for plane in PLANES.values():
                candidate[plane]["orbitTilta"] = float(tilt)
                candidate[plane]["orbitTiltb"] = float(node)
            results = score(candidate, datasets, train)
            objective = normalized_objective(results, baseline_train)
            item = (objective, float(tilt), float(node), candidate)
            if best is None or item[0] < best[0]:
                best = item
    objective, tilt, node, candidate = best
    print(
        "best_shared_fixed_plane",
        {
            "tilt": tilt,
            "node": node,
            "normalized_train_objective": objective,
            "all": score(candidate, datasets),
            "train": score(candidate, datasets, train),
            "test": score(candidate, datasets, test),
        },
    )

    # Venus's annual residual is the largest longitude component.  Its small
    # counter-rotating deferent is the compact geometric term with the right
    # annual frequency, so screen its radius and phase together.
    venus_dates, venus_positions, venus_reference, _ = datasets["venus"]
    venus_train = venus_dates < datetime(2020, 1, 1)
    best = None
    for radius in np.arange(0.0, 2.0001, 0.05):
        for phase in np.arange(0.0, 360.0, 2.0):
            candidate = copy.deepcopy(settings)
            candidate["Venus deferent B"]["orbitRadius"] = float(radius)
            candidate["Venus deferent B"]["startPos"] = float(phase)
            result = metrics(
                model(candidate, "venus", venus_positions[venus_train]),
                venus_reference[venus_train],
            )
            item = (result["separation_rms"], float(radius), float(phase))
            if best is None or item[0] < best[0]:
                best = item
    _, coarse_radius, coarse_phase = best
    best = None
    for radius in np.arange(max(0.0, coarse_radius - 0.10), coarse_radius + 0.1001, 0.01):
        for phase in np.arange(coarse_phase - 4.0, coarse_phase + 4.001, 0.2):
            candidate = copy.deepcopy(settings)
            candidate["Venus deferent B"]["orbitRadius"] = float(radius)
            candidate["Venus deferent B"]["startPos"] = float(phase % 360.0)
            result = metrics(
                model(candidate, "venus", venus_positions[venus_train]),
                venus_reference[venus_train],
            )
            item = (result["separation_rms"], float(radius), float(phase % 360.0), candidate)
            if best is None or item[0] < best[0]:
                best = item
    _, radius, phase, candidate = best
    print(
        "venus_eccentric_deferent",
        {
            "radius": radius,
            "phase": phase,
            "all": score(candidate, datasets)["venus"],
            "train": score(candidate, datasets, train)["venus"],
            "test": score(candidate, datasets, test)["venus"],
        },
    )

    # Test one compact geometric explanation for the 49.98-day residual.  The
    # candidate speed is Mercury's natural second harmonic 2*M, not a fitted
    # period; this is the leading periodic term in an ellipse expansion.
    # CounterRotatedOrbit lets this displacement move without rotating the
    # planet's orbital plane or changing Mercury's own phase.
    mercury_dates, mercury_positions, mercury_reference, _ = datasets["mercury"]
    mercury_train = mercury_dates < datetime(2020, 1, 1)
    best = None
    eccentric_speed = 2.0 * number(settings["Mercury"], "speed")
    for mercury_radius in np.arange(0.0, 3.0001, 0.05):
        for mercury_phase in np.arange(0.0, 360.0, 2.0):
            candidate = copy.deepcopy(settings)
            candidate["Mercury Eccentric"]["speed"] = eccentric_speed
            candidate["Mercury Eccentric"]["orbitRadius"] = float(mercury_radius)
            candidate["Mercury Eccentric"]["startPos"] = float(mercury_phase)
            result = metrics(
                model(candidate, "mercury", mercury_positions[mercury_train]),
                mercury_reference[mercury_train],
            )
            item = (result["separation_rms"], float(mercury_radius), float(mercury_phase))
            if best is None or item[0] < best[0]:
                best = item
    _, coarse_radius, coarse_phase = best
    best = None
    for mercury_radius in np.arange(
        max(0.0, coarse_radius - 0.10), coarse_radius + 0.1001, 0.01
    ):
        for mercury_phase in np.arange(coarse_phase - 4.0, coarse_phase + 4.001, 0.2):
            candidate = copy.deepcopy(settings)
            candidate["Mercury Eccentric"]["speed"] = eccentric_speed
            candidate["Mercury Eccentric"]["orbitRadius"] = float(mercury_radius)
            candidate["Mercury Eccentric"]["startPos"] = float(mercury_phase % 360.0)
            result = metrics(
                model(candidate, "mercury", mercury_positions[mercury_train]),
                mercury_reference[mercury_train],
            )
            item = (
                result["separation_rms"],
                float(mercury_radius),
                float(mercury_phase % 360.0),
                candidate,
            )
            if best is None or item[0] < best[0]:
                best = item
    _, mercury_radius, mercury_phase, mercury_candidate = best
    print(
        "mercury_eccentric_deferent",
        {
            "radius": mercury_radius,
            "phase": mercury_phase,
            "speed": eccentric_speed,
            "all": score(mercury_candidate, datasets)["mercury"],
            "train": score(mercury_candidate, datasets, train)["mercury"],
            "test": score(mercury_candidate, datasets, test)["mercury"],
        },
    )

    # A compact candidate for simulator validation: remove Mercury's moving
    # intermediate tilt, retain separate fixed orbital planes, and strengthen
    # Venus's already-existing eccentric annual term.
    validation_candidate = fixed_plane(settings)
    validation_candidate["Mercury Plane"]["orbitTilta"] = 7.0
    validation_candidate["Mercury Plane"]["orbitTiltb"] = 0.6
    validation_candidate["Venus Plane"]["orbitTilta"] = 3.4
    validation_candidate["Venus Plane"]["orbitTiltb"] = -0.2
    validation_candidate["Venus deferent B"]["orbitRadius"] = radius
    validation_candidate["Venus deferent B"]["startPos"] = phase
    print(
        "validation_candidate",
        {
            "all": score(validation_candidate, datasets),
            "train": score(validation_candidate, datasets, train),
            "test": score(validation_candidate, datasets, test),
        },
    )

    print(
        "current_plane_parameters",
        {
            body: {
                "plane_tilt": number(settings[PLANES[body]], "orbitTilta"),
                "plane_node": number(settings[PLANES[body]], "orbitTiltb"),
                "deferent_b_tilt": number(settings[DEFERENTS_B[body]], "orbitTilta"),
                "deferent_b_node": number(settings[DEFERENTS_B[body]], "orbitTiltb"),
            }
            for body in BODIES
        },
    )


if __name__ == "__main__":
    main()
