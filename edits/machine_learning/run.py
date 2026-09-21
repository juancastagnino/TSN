"""Temporal multi-body residual regression; never modifies simulator exports."""
import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'edits/scripts'))
from compare_ephemerides import read_tychos, read_jpl
from analyze_ephemerides import equatorial_to_ecliptic, wrap_deg
from ephemeris_io import tychos_blocks, jpl_blocks, validate_jpl_header
from cross_body import run_cross_body


def split_dates(dates, config):
    start, valid, test, stop = [datetime.fromisoformat(config[k]) for k in
                              ('start', 'validation_start', 'test_start', 'stop_exclusive')]
    if not start < valid < test < stop:
        raise ValueError('Split boundaries must be strictly increasing')
    return np.array(['train' if d < valid else 'validation' if d < test else 'test'
                     for d in dates])


def design(t, periods, trend, center):
    columns = [np.ones(len(t))]
    names = ['intercept']
    for period in periods:
        if not np.isfinite(period) or period <= 0:
            raise ValueError('Periods must be positive and finite')
        columns.extend([np.sin(2*np.pi*t/period), np.cos(2*np.pi*t/period)])
        names.extend([f'sin_{period}d', f'cos_{period}d'])
    if trend:
        columns.append((t-center)/365.25)
        names.append('years_from_train_center')
    return np.column_stack(columns), names


def metrics(error):
    return {'rmse_deg': float(np.sqrt(np.mean(error**2))),
            'mae_deg': float(np.mean(np.abs(error))),
            'bias_deg': float(np.mean(error)),
            'p95_abs_deg': float(np.percentile(np.abs(error), 95))}


def run(config, output):
    ty_path, jpl_path = [ROOT / config[k] for k in ('tychos', 'jpl')]
    body = config.get('body', 'moon')
    registry = json.loads((ROOT/'edits/scripts/bodies.json').read_text(encoding='utf-8'))
    ty = read_tychos(ty_path, strict=True, body=body)
    jpl = read_jpl(jpl_path, strict=True, target_id=registry[body]['target_id'])
    start = datetime.fromisoformat(config['start'])
    stop = datetime.fromisoformat(config['stop_exclusive'])
    cadence = float(config['cadence_hours'])
    if not np.isfinite(cadence) or cadence <= 0:
        raise ValueError('Cadence must be positive and finite')
    dates = sorted(d for d in ty if start <= d < stop)
    reference_dates = sorted(d for d in jpl if start <= d < stop)
    if dates != reference_dates or not dates:
        raise ValueError('TYCHOS and JPL must have identical nonempty timestamp grids')
    step = timedelta(hours=cadence)
    if dates[0] != start or dates[-1] + step != stop or any(
            b-a != step for a, b in zip(dates, dates[1:])):
        raise ValueError('Incomplete or irregular requested time grid')
    split = split_dates(dates, config)
    for label in ('train', 'validation', 'test'):
        if np.sum(split == label) < 30:
            raise ValueError(f'Insufficient samples in {label}')
    ty_lon, _ = equatorial_to_ecliptic([ty[d]['ra'] for d in dates], [ty[d]['dec'] for d in dates])
    jp_lon, _ = equatorial_to_ecliptic([jpl[d]['ra_icrf'] for d in dates], [jpl[d]['dec_icrf'] for d in dates])
    y = wrap_deg(ty_lon-jp_lon)
    if not np.all(np.isfinite(y)) or np.max(np.abs(y)) >= 90:
        raise ValueError('Target is invalid or too close to angular wrapping for linear regression')
    t = np.array([(d-start).total_seconds()/86400 for d in dates])
    train = split == 'train'
    center = float(t[train].mean())
    candidates = {}
    predictions = {}
    # Predeclared candidates. Selection only sees validation errors.
    for name, periods, trend in [('zero', [], False), ('mean', [], False),
                                 ('periodic', config['periods_days'], False),
                                 ('periodic_trend', config['periods_days'], True)]:
        x, names = design(t, periods, trend, center)
        if name == 'zero':
            coef = np.zeros(x.shape[1])
        else:
            coef, _, rank, _ = np.linalg.lstsq(x[train], y[train], rcond=None)
            if rank != x.shape[1] or train.sum() <= x.shape[1]:
                raise ValueError('Training design is not identifiable')
        predictions[name] = x @ coef
        candidates[name] = {'features': names, 'coefficients': coef.tolist(),
                            'train': metrics(y[train]-predictions[name][train]),
                            'validation': metrics((y-predictions[name])[split == 'validation'])}
    selected = min(candidates, key=lambda name: candidates[name]['validation']['rmse_deg'])
    # Frozen coefficients: no refit after validation, and no model choice on test.
    test = split == 'test'
    test_metrics = {name: metrics((y-predictions[name])[test]) for name in dict.fromkeys(['zero', 'mean', selected])}
    output.mkdir(parents=True, exist_ok=True)
    report = {'purpose': 'diagnostic residual prediction, not corrected ephemerides',
              'body': body, 'config': config, 'python': platform.python_version(), 'numpy': np.__version__,
              'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ty_path, jpl_path)},
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'export_settings': 'unknown; current settings are not proof of export configuration',
              'time_origin': start.isoformat(), 'train_center_days': center,
              'splits': {s: {'count': int(np.sum(split == s)),
                             'first': dates[np.flatnonzero(split == s)[0]].isoformat(),
                             'last': dates[np.flatnonzero(split == s)[-1]].isoformat()}
                         for s in ('train', 'validation', 'test')},
              'candidates': candidates, 'selected': selected, 'test': test_metrics,
              'limitations': ['Fixed diagnostic periods, not inferred physical mechanisms; lunar periods previously explored on 2000-2026.',
                              'TYCHOS frame compatibility and geometric versus astrometric conventions unresolved.',
                              'Samples are temporally correlated; counts are not independent observations.']}
    (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    x, feature_names = design(t, config['periods_days'], True, center)
    with (output/'dataset.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date_utc', 'body', 'split', 't_days', *feature_names,
                         'target_lon_tychos_minus_jpl_deg', 'predicted_residual_deg', 'unexplained_residual_deg'])
        for i, date in enumerate(dates):
            writer.writerow([date.isoformat(), body, split[i], t[i], *x[i], y[i],
                             predictions[selected][i], y[i]-predictions[selected][i]])
    with (output/'annual_metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['year', 'split', 'count', 'baseline_rmse_deg', 'selected_rmse_deg'])
        years = np.array([d.year for d in dates])
        for year in sorted(set(years)):
            for s in ('train', 'validation', 'test'):
                mask = (years == year) & (split == s)
                if mask.any():
                    writer.writerow([year, s, int(mask.sum()), metrics(y[mask])['rmse_deg'],
                                     metrics((y-predictions[selected])[mask])['rmse_deg']])
    lines = [f'# Resultado del experimento: {body}', '', f'Modelo seleccionado por validación: `{selected}`.', '',
             'RMSE del residuo de longitud que queda sin explicar (grados):', '',
             '| Modelo | Train | Validación | Test |', '|---|---:|---:|---:|']
    for name, item in candidates.items():
        test_value = f"{test_metrics[name]['rmse_deg']:.6f}" if name in test_metrics else 'no evaluado'
        lines.append(f"| {name} | {item['train']['rmse_deg']:.6f} | {item['validation']['rmse_deg']:.6f} | {test_value} |")
    lines.extend(['', 'No representa una mejora del simulador ni una identificación de causas físicas.',
                  'Fixed periods are diagnostic; historical lunar frequency exploration limits independence.',
                  'Consultar report.json para fechas, procedencia, coeficientes y limitaciones.'])
    (output/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))
    return report


def run_all(config, output, allow_missing=False):
    registry = json.loads((ROOT/'edits/scripts/bodies.json').read_text(encoding='utf-8'))
    bodies = config.get('bodies', ['moon'])
    if not bodies or len(set(bodies)) != len(bodies) or set(bodies)-set(registry):
        raise ValueError('Select unique registered bodies')
    ty = tychos_blocks((ROOT/config['tychos']).read_text(encoding='utf-8-sig'))
    jp = jpl_blocks((ROOT/config['jpl']).read_text(encoding='utf-8-sig'))
    missing = {b: [source for source, present in [('TYCHOS', b in ty),
                 ('JPL', registry[b]['target_id'] in jp)] if not present] for b in bodies}
    missing = {b: sources for b, sources in missing.items() if sources}
    if missing:
        message = 'Missing exports: '+json.dumps(missing)
        if not allow_missing:
            raise ValueError(message+'; export these bodies or use --available for an explicitly partial run')
        print('PARTIAL RUN. '+message)
    selected = [b for b in bodies if b not in missing]
    if not selected:
        raise ValueError('No selected bodies available in both inputs')
    for body in selected:
        validate_jpl_header(jp[registry[body]['target_id']])
    reports = {}
    for body in selected:
        local = dict(config, body=body)
        # No lunar frequencies are transferred to planets. Annual is a fixed diagnostic baseline.
        local['periods_days'] = config.get('periods_by_body', {}).get(
            body, config.get('periods_days', []) if body == 'moon' else [365.256363])
        reports[body] = run(local, output/body)
    advanced_config = dict(config, bodies=selected)
    advanced = run_cross_body(advanced_config, registry, output)
    summary = {'requested': bodies, 'completed': selected, 'missing': missing,
               'complete': not missing,
               'scope': 'Residual diagnostics plus cross-body common-mode and pairwise analysis; not geometric calibration',
               'results': {b: {'selected': r['selected'], 'test': r['test'], 'splits': r['splits']}
                           for b, r in reports.items()},
               'advanced_report': 'cross_body.json',
               'common_modes': advanced['common_modes']['modes']}
    output.mkdir(parents=True, exist_ok=True)
    (output/'overview.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    lines = ['# Diagnostico por cuerpo', '', 'Estado: '+('PARCIAL' if missing else 'completo'), '',
             '| Cuerpo | Modelo | RMSE original test (grados) | RMSE no explicado test (grados) |',
             '|---|---|---:|---:|']
    for b, r in reports.items():
        lines.append(f"| {b} | {r['selected']} | {r['test']['zero']['rmse_deg']:.6f} | {r['test'][r['selected']]['rmse_deg']:.6f} |")
    for b, sources in missing.items():
        lines.append(f"| {b} | faltan {' y '.join(sources)} | - | - |")
    lines += ['', 'Cada cuerpo tiene su dataset y reporte en su subcarpeta.',
              'El análisis conjunto de coordenadas, modos comunes y separaciones está en cross_body.md/json.',
              'No es una optimizacion global ni una mejora aplicada al simulador.',
              'Las subcarpetas de ejecuciones anteriores no incluidas aqui no pertenecen a esta ejecucion.']
    (output/'overview.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).with_name('config.json'))
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('outputs'))
    parser.add_argument('--bodies', nargs='+', help='Explicit subset of configured bodies')
    parser.add_argument('--available', action='store_true', help='Explicitly allow an incomplete body selection')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if args.bodies:
        config['bodies'] = args.bodies
    try:
        run_all(config, args.output, args.available)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error)+'\n')
