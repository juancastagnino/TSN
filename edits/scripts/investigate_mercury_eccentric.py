"""Compare compact Mercury eccentric geometries without editing settings.

The explicit eccentric layer applies a rotating displacement and an equal
counter-rotation, leaving Mercury's plane and orbital phase independent.  This
script compares the previously tried 2M-S speed with the second harmonic 2M
that arises naturally in a first-order Fourier representation of an ellipse.
"""

import argparse
import copy
from datetime import datetime

import numpy as np

from investigate_planet_tuning import (
    D2R,
    ROOT,
    load_comparison,
    metrics,
    model,
    number,
    setting_map,
)


def longitude_residual(predicted, reference):
    obliquity = 23.439291111 * D2R

    def longitude(vectors):
        x = vectors[:, 2]
        y = vectors[:, 0] * np.cos(obliquity) + vectors[:, 1] * np.sin(obliquity)
        return np.unwrap(np.arctan2(y, x))

    return np.rad2deg(longitude(predicted) - longitude(reference))


def fft_amplitude(residual, cadence_days, target_period=49.98):
    centered = residual - np.mean(residual)
    spectrum = np.fft.rfft(centered)
    frequencies = np.fft.rfftfreq(len(centered), d=cadence_days)
    target_frequency = 1.0 / target_period
    index = int(np.argmin(np.abs(frequencies - target_frequency)))
    return {
        "period_days": float(1.0 / frequencies[index]),
        "amplitude_deg": float(2.0 * np.abs(spectrum[index]) / len(centered)),
    }


def evaluate(settings, positions, reference, selection, cadence_days):
    predicted = model(settings, "mercury", positions[selection])
    selected_reference = reference[selection]
    result = metrics(predicted, selected_reference)
    result["target_fft"] = fft_amplitude(
        longitude_residual(predicted, selected_reference), cadence_days
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stride", type=int, default=24)
    args = parser.parse_args()

    settings = setting_map(ROOT / "src/settings/celestial-settings.json")
    dates, positions, reference, _ = load_comparison("mercury", args.stride)
    train = dates < datetime(2020, 1, 1)
    test = ~train
    all_rows = np.ones(len(dates), dtype=bool)
    cadence_days = 0.125 * args.stride

    mercury_speed = number(settings["Mercury"], "speed")
    annual_speed = number(settings["Mercury deferent A"], "speed")
    variants = {
        "2M-S": 2.0 * mercury_speed - annual_speed,
        "2M": 2.0 * mercury_speed,
    }

    zero = copy.deepcopy(settings)
    zero["Mercury Eccentric"]["orbitRadius"] = 0.0
    print(
        "zero_radius_baseline",
        {
            "all": evaluate(zero, positions, reference, all_rows, cadence_days),
            "train": evaluate(zero, positions, reference, train, cadence_days),
            "test": evaluate(zero, positions, reference, test, cadence_days),
        },
    )

    for label, speed in variants.items():
        best = None
        for radius in np.arange(0.0, 4.0001, 0.05):
            for phase in np.arange(0.0, 360.0, 2.0):
                candidate = copy.deepcopy(settings)
                candidate["Mercury Eccentric"]["speed"] = float(speed)
                candidate["Mercury Eccentric"]["orbitRadius"] = float(radius)
                candidate["Mercury Eccentric"]["startPos"] = float(phase)
                result = metrics(
                    model(candidate, "mercury", positions[train]), reference[train]
                )
                item = (result["separation_rms"], float(radius), float(phase))
                if best is None or item[0] < best[0]:
                    best = item

        _, coarse_radius, coarse_phase = best
        best = None
        for radius in np.arange(
            max(0.0, coarse_radius - 0.10), coarse_radius + 0.1001, 0.01
        ):
            for phase in np.arange(coarse_phase - 4.0, coarse_phase + 4.001, 0.2):
                candidate = copy.deepcopy(settings)
                candidate["Mercury Eccentric"]["speed"] = float(speed)
                candidate["Mercury Eccentric"]["orbitRadius"] = float(radius)
                candidate["Mercury Eccentric"]["startPos"] = float(phase % 360.0)
                result = metrics(
                    model(candidate, "mercury", positions[train]), reference[train]
                )
                item = (
                    result["separation_rms"],
                    float(radius),
                    float(phase % 360.0),
                    candidate,
                )
                if best is None or item[0] < best[0]:
                    best = item

        _, radius, phase, candidate = best
        print(
            label,
            {
                "speed": speed,
                "radius": radius,
                "phase": phase,
                "all": evaluate(candidate, positions, reference, all_rows, cadence_days),
                "train": evaluate(candidate, positions, reference, train, cadence_days),
                "test": evaluate(candidate, positions, reference, test, cadence_days),
            },
        )


if __name__ == "__main__":
    main()
