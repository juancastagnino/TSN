"""Interpretable multi-coordinate and cross-body residual diagnostics.

This module never changes simulator settings or exports. It uses temporal
train/validation/test splits to characterize residual structure and common modes.
"""

import csv
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "edits/scripts"))

from analyze_ephemerides import equatorial_to_ecliptic, wrap_deg
from compare_ephemerides import read_jpl, read_tychos


TARGETS = ("longitude", "latitude", "east", "north")


def metrics(values):
    values = np.asarray(values, dtype=float)
    return {
        "rmse_deg": float(np.sqrt(np.mean(values * values))),
        "mae_deg": float(np.mean(np.abs(values))),
        "bias_deg": float(np.mean(values)),
        "p95_abs_deg": float(np.percentile(np.abs(values), 95)),
    }


def unit_vectors(ra_deg, dec_deg):
    ra = np.radians(ra_deg)
    dec = np.radians(dec_deg)
    return np.column_stack((np.cos(dec) * np.cos(ra),
                            np.cos(dec) * np.sin(ra), np.sin(dec)))


def angular_separation(a, b):
    return np.degrees(np.arccos(np.clip(np.sum(a * b, axis=1), -1.0, 1.0)))


def design(t_days, periods, trend, center_days):
    columns = [np.ones(len(t_days))]
    names = ["intercept"]
    for period in periods:
        phase = 2 * np.pi * t_days / period
        columns.extend((np.sin(phase), np.cos(phase)))
        names.extend((f"sin_{period}d", f"cos_{period}d"))
    if trend:
        columns.append((t_days - center_days) / 365.25)
        names.append("years_from_train_center")
    return np.column_stack(columns), names


def ridge_fit(x, y, alpha):
    penalty = np.eye(x.shape[1]) * alpha
    penalty[0, 0] = 0.0
    return np.linalg.solve(x.T @ x + penalty, x.T @ y)


def combined_tangent_rmse(error):
    tangent = error[:, -2:]
    return float(np.sqrt(np.mean(tangent[:, 0] ** 2 + tangent[:, 1] ** 2)))


def load_body(config, registry, body):
    ty = read_tychos(ROOT / config["tychos"], strict=True, body=body)
    jp = read_jpl(ROOT / config["jpl"], strict=True,
                  target_id=registry[body]["target_id"])
    start = datetime.fromisoformat(config["start"])
    stop = datetime.fromisoformat(config["stop_exclusive"])
    dates = sorted(d for d in ty if start <= d < stop)
    reference_dates = sorted(d for d in jp if start <= d < stop)
    if not dates or dates != reference_dates:
        raise ValueError(f"{body}: TYCHOS/JPL timestamp grids differ")
    step = timedelta(hours=float(config["cadence_hours"]))
    if dates[0] != start or dates[-1] + step != stop or any(
            b - a != step for a, b in zip(dates, dates[1:])):
        raise ValueError(f"{body}: incomplete or irregular configured grid")

    ty_ra = np.array([ty[d]["ra"] for d in dates])
    ty_dec = np.array([ty[d]["dec"] for d in dates])
    jp_ra = np.array([jp[d]["ra_icrf"] for d in dates])
    jp_dec = np.array([jp[d]["dec_icrf"] for d in dates])
    ty_lon, ty_lat = equatorial_to_ecliptic(ty_ra, ty_dec)
    jp_lon, jp_lat = equatorial_to_ecliptic(jp_ra, jp_dec)
    residuals = np.column_stack((
        wrap_deg(ty_lon - jp_lon), ty_lat - jp_lat,
        wrap_deg(ty_ra - jp_ra) * np.cos(np.radians(jp_dec)),
        ty_dec - jp_dec,
    ))
    return {
        "dates": dates,
        "residuals": residuals,
        "ty_vec": unit_vectors(ty_ra, ty_dec),
        "jpl_vec": unit_vectors(jp_ra, jp_dec),
    }


def fit_body(config, body, dates, residuals, split):
    start = datetime.fromisoformat(config["start"])
    t = np.array([(d - start).total_seconds() / 86400 for d in dates])
    train = split == "train"
    validation = split == "validation"
    test = split == "test"
    center = float(t[train].mean())
    periods = config["periods_by_body"][body]
    candidates = {}
    predictions = {}

    zero = np.zeros_like(residuals)
    mean = np.broadcast_to(residuals[train].mean(axis=0), residuals.shape)
    for name, prediction in (("zero", zero), ("mean", mean)):
        predictions[name] = prediction
        candidates[name] = {
            "features": [] if name == "zero" else ["intercept"],
            "alpha": None,
            "trend": False,
            "validation_tangent_rmse_deg": combined_tangent_rmse(
                (residuals - prediction)[validation]),
        }

    for trend in (False, True):
        x, names = design(t, periods, trend, center)
        for alpha in config.get("ridge_alphas", [0.0]):
            coef = ridge_fit(x[train], residuals[train], float(alpha))
            prediction = x @ coef
            name = ("periodic_trend" if trend else "periodic") + f"_ridge_{alpha:g}"
            predictions[name] = prediction
            candidates[name] = {
                "features": names,
                "alpha": float(alpha),
                "trend": trend,
                "validation_tangent_rmse_deg": combined_tangent_rmse(
                    (residuals - prediction)[validation]),
                "coefficients_by_target": {
                    target: coef[:, i].tolist() for i, target in enumerate(TARGETS)
                },
            }

    selected = min(candidates,
                   key=lambda name: candidates[name]["validation_tangent_rmse_deg"])
    prediction = predictions[selected]
    result = {
        "periods_days": periods,
        "selected": selected,
        "candidates": candidates,
        "splits": {},
    }
    for label, mask in (("train", train), ("validation", validation), ("test", test)):
        error = residuals[mask] - prediction[mask]
        result["splits"][label] = {
            "baseline": {target: metrics(residuals[mask, i])
                         for i, target in enumerate(TARGETS)},
            "unexplained": {target: metrics(error[:, i])
                            for i, target in enumerate(TARGETS)},
            "baseline_tangent_rmse_deg": combined_tangent_rmse(residuals[mask]),
            "unexplained_tangent_rmse_deg": combined_tangent_rmse(error),
        }
    return result, prediction


def common_modes(config, bodies, body_data, split):
    train = split == "train"
    # Equalize each coordinate so Mercury or Pluto cannot dominate merely by scale.
    columns = []
    names = []
    scales = {}
    for body in bodies:
        for index, direction in ((2, "east"), (3, "north")):
            values = body_data[body]["residuals"][:, index]
            center = float(values[train].mean())
            scale = float(values[train].std())
            scale = max(scale, 1e-9)
            columns.append((values - center) / scale)
            names.append(f"{body}_{direction}")
            scales[names[-1]] = {"train_mean_deg": center, "train_std_deg": scale}
    matrix = np.column_stack(columns)
    _, singular, vt = np.linalg.svd(matrix[train], full_matrices=False)
    variance = singular * singular
    ratios = variance / variance.sum()
    modes = []
    for i in range(min(3, len(ratios))):
        loadings = {names[j]: float(vt[i, j]) for j in range(len(names))}
        strongest = sorted(loadings.items(), key=lambda item: abs(item[1]), reverse=True)[:8]
        modes.append({"mode": i + 1, "train_variance_percent": float(100 * ratios[i]),
                      "strongest_loadings": dict(strongest), "all_loadings": loadings})
    reconstruction = {}
    scores = matrix @ vt[:3].T
    for count in (1, 2, 3):
        restored = scores[:, :count] @ vt[:count]
        error = matrix - restored
        reconstruction[str(count)] = {
            label: float(np.sqrt(np.mean(error[split == label] ** 2)))
            for label in ("train", "validation", "test")
        }
    return {"standardization": scales, "modes": modes,
            "standardized_reconstruction_rmse": reconstruction}


def pairwise_diagnostics(bodies, body_data, split):
    pairs = {}
    for i, first in enumerate(bodies):
        for second in bodies[i + 1:]:
            ty_sep = angular_separation(body_data[first]["ty_vec"],
                                        body_data[second]["ty_vec"])
            jp_sep = angular_separation(body_data[first]["jpl_vec"],
                                        body_data[second]["jpl_vec"])
            error = ty_sep - jp_sep
            pairs[f"{first}-{second}"] = {
                label: metrics(error[split == label])
                for label in ("train", "validation", "test")
            }
    return pairs


def annual_diagnostics(config, bodies, body_data, split):
    start = datetime.fromisoformat(config["start"])
    dates = body_data[bodies[0]]["dates"]
    t = np.array([(d - start).total_seconds() / 86400 for d in dates])
    train = split == "train"
    test = split == "test"
    center = float(t[train].mean())
    x, _ = design(t, [365.256363], True, center)
    result = {}
    for body in bodies:
        tangent = body_data[body]["residuals"][:, 2:4]
        coef = ridge_fit(x[train], tangent[train], 0.0)
        prediction = x @ coef
        periodic = {}
        for index, direction in enumerate(("east", "north")):
            sin_coef, cos_coef = coef[1, index], coef[2, index]
            periodic[direction] = {
                "amplitude_deg": float(np.hypot(sin_coef, cos_coef)),
                "phase_deg_at_start": float(np.degrees(np.arctan2(cos_coef, sin_coef))),
            }
        result[body] = {
            "periodic": periodic,
            "trend_deg_per_year": {"east": float(coef[3, 0]),
                                   "north": float(coef[3, 1])},
            "test_tangent_rmse_before_deg": combined_tangent_rmse(tangent[test]),
            "test_tangent_rmse_after_deg": combined_tangent_rmse(
                (tangent - prediction)[test]),
        }
    return result


def run_cross_body(config, registry, output):
    bodies = config["bodies"]
    body_data = {body: load_body(config, registry, body) for body in bodies}
    dates = body_data[bodies[0]]["dates"]
    if any(body_data[b]["dates"] != dates for b in bodies[1:]):
        raise ValueError("Cross-body diagnostics require the same dates for all bodies")
    valid = datetime.fromisoformat(config["validation_start"])
    test = datetime.fromisoformat(config["test_start"])
    split = np.array(["train" if d < valid else "validation" if d < test else "test"
                      for d in dates])
    body_results = {}
    predictions = {}
    for body in bodies:
        body_results[body], predictions[body] = fit_body(
            config, body, dates, body_data[body]["residuals"], split)

    result = {
        "purpose": "diagnostic only; never apply fitted residuals to TYCHOS",
        "targets": list(TARGETS),
        "selection_metric": "validation tangent-plane RMSE (east/north)",
        "bodies": body_results,
        "annual_diagnostics": annual_diagnostics(config, bodies, body_data, split),
        "common_modes": common_modes(config, bodies, body_data, split),
        "pairwise_separation": pairwise_diagnostics(bodies, body_data, split),
        "limitations": [
            "Common modes indicate shared temporal structure, not physical cause.",
            "Tangent-plane east/north errors are local small-angle diagnostics.",
            "Pairwise angular separation removes pure global rotations but not observer translation.",
            "Periods are predeclared physical hypotheses; fitted terms are not simulator corrections.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "cross_body.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    lines = ["# Diagnóstico avanzado entre cuerpos", "",
             "Los modelos son diagnósticos; no corrigen las efemérides.", "",
             "| Cuerpo | Modelo elegido | RMS tangente test original | RMS sin explicar |",
             "|---|---|---:|---:|"]
    for body in bodies:
        item = body_results[body]
        test_item = item["splits"]["test"]
        lines.append(f"| {body} | `{item['selected']}` | "
                     f"{test_item['baseline_tangent_rmse_deg']:.6f} | "
                     f"{test_item['unexplained_tangent_rmse_deg']:.6f} |")
    lines += ["", "## Componente anual común a todos los ajustes", "",
              "Ajuste diagnóstico train: constante + tendencia + 365.256363 días.", "",
              "| Cuerpo | Amp. este | Fase este | Amp. norte | RMS test antes | RMS test después |",
              "|---|---:|---:|---:|---:|---:|"]
    for body in bodies:
        item = result["annual_diagnostics"][body]
        east = item["periodic"]["east"]
        north = item["periodic"]["north"]
        lines.append(f"| {body} | {east['amplitude_deg']:.4f} | "
                     f"{east['phase_deg_at_start']:.1f}° | {north['amplitude_deg']:.4f} | "
                     f"{item['test_tangent_rmse_before_deg']:.4f} | "
                     f"{item['test_tangent_rmse_after_deg']:.4f} |")
    lines += ["", "## Modos comunes", ""]
    for mode in result["common_modes"]["modes"]:
        strongest = ", ".join(f"{k}={v:+.3f}" for k, v in
                              mode["strongest_loadings"].items())
        lines.append(f"- Modo {mode['mode']}: {mode['train_variance_percent']:.2f}% "
                     f"de varianza train; cargas principales: {strongest}.")
    lines += ["", "Las separaciones de todos los pares están en `cross_body.json`.",
              "Una rotación global pura preserva esas separaciones; una traslación del observador no."]
    (output / "cross_body.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
