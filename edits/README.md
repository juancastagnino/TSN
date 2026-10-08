# Ephemeris analysis

This directory contains the maintained comparison workflow for the current
TYCHOS hierarchy. Run commands from the repository root with Python 3.11 or
newer.

## Quick start

```powershell
py -m venv .venv
.venv\Scripts\activate
python.exe -m pip install -r edits/scripts/requirements.txt

# Configure edits/scripts/analysis_config.json, then download JPL.
python.exe -B edits/scripts/download_jpl.py

# Export identical bodies/timestamps from TYCHOS to
# edits/data/raw/tychos_ephemerides.txt, then run:
python.exe -B edits/scripts/run_analysis.py --all `
  --reference apparent-of-date `
  --label "Description of the tested settings"
```

The principal outputs are
[`ephemeris_overview.md`](reports/ephemeris_overview.md) and
[`analysis_notes.md`](reports/analysis_notes.md). Existing matching JPL data may
be reused when only TYCHOS geometry changes.

## Configuration

Edit [`analysis_config.json`](scripts/analysis_config.json):

| Setting | Purpose |
|---|---|
| `bodies` | Default bodies to download and analyze |
| `start`, `stop`, `step` | Common UTC interval and cadence |
| `tychos` | Combined TYCHOS export path |
| `jpl` | Combined Horizons bundle path |

The exported files—not the JSON configuration alone—determine the samples that
are analyzed. TYCHOS and JPL must contain the same timestamps.

Useful overrides:

```powershell
python.exe -B edits/scripts/download_jpl.py moon sun mars `
  --start "2000-06-21 00:00" `
  --stop "2026-06-21 00:00" --step "6 h"

python.exe -B edits/scripts/run_analysis.py moon mercury `
  --reference apparent-of-date --label "Focused experiment"

python.exe -B edits/scripts/run_analysis.py --all `
  --tychos path/to/tychos.txt --jpl path/to/jpl.txt `
  --reference apparent-of-date --label "Declared export configuration"
```

`--all` processes registered bodies present in both combined inputs. An
explicitly requested body must exist in both files.

## Reference products

One Horizons download contains both supported coordinate products:

| Mode | JPL quantity | Intended use |
|---|---|---|
| `apparent-of-date` | Airless apparent RA/Dec in true equator/equinox of date | Normal comparison for the native TYCHOS export |
| `icrf` | Astrometric RA/Dec in fixed ICRF | Controlled fixed-frame investigations using a compatible TYCHOS export |
| `both` | Writes both report sets | Reference-frame research only |

Apparent true-of-date includes light-time, gravitational light deflection,
stellar aberration, precession and nutation. It is used here because it gives the
most useful numerical comparison with the native export; it is not assumed to be
physically identical to the TYCHOS frame.

True-of-date reports include RA, declination, angular separation, annual
statistics and FFT peaks of the signed RA residual. They intentionally avoid a
fixed-J2000 ecliptic rotation. ICRF reports may additionally use ecliptic
longitude and latitude diagnostics.

## Comparing with a saved baseline

Preserve a complete report set before changing parameters. After producing a
candidate run with the same reference mode, interval and cadence:

```powershell
python.exe -B edits/scripts/compare_summary_metrics.py `
  --baseline 00-backup/my-baseline `
  --candidate edits/reports
```

The comparison evaluates signed RA/declination means by absolute bias and
reports RMS and angular changes separately.

## Current hierarchy

```text
SystemCenter
└─ Earth
   ├─ Moon node / plane / orbit
   └─ Sun–Mars Binary Frame
      └─ Sun Primary
         ├─ Mars Junior Companion -> Phobos / Deimos
         ├─ Venus Senior Solar Companion
         ├─ Mercury Junior Solar Companion
         ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
         ├─ Halley
         └─ Eros
```

The schema-v3 source of truth is
[`src/settings/celestial-model.json`](../src/settings/celestial-model.json). Real
bodies own their node, plane, deferent and orbit components. Historical
phase-specific migration scripts are no longer part of the active workflow;
their results remain documented in [`binary_tychos.md`](binary_tychos.md), the
preserved baselines under `00-backup` and Git history.

## Maintained scripts

See [`scripts/README.md`](scripts/README.md) for the intentionally small script
inventory and each file's responsibility.

## Outputs and provenance

| Location | Contents |
|---|---|
| `data/derived/<body>_comparison.csv` | Timestamp-matched coordinates and differences |
| `reports/<body>_summary.json` | Metrics, dates, hashes and declared provenance |
| `reports/<body>_ephemeris_report.md` | Per-body report |
| `reports/<body>_annual_stats.csv` | Annual statistics |
| `reports/<body>_residuals.csv` | Per-sample residuals |
| `reports/<body>_fft_peaks.csv` | Finite-window spectral diagnostics |
| `reports/*_apparent_of_date_*` | Apparent true-of-date products |
| `reports/ephemeris_overview.md` | Input and output overview |
| `reports/analysis_notes.md` | Compact summary of the current run |

Generated files are replaceable evidence, not permanent history. A controlled
trial should preserve the raw exports, reports, analysis configuration and model
settings together. A `--label` records declared provenance but cannot prove which
simulator settings produced an already-existing export.

## Working rules

- Keep interval, cadence, bodies and reference product identical in every
  before/after comparison.
- Do not compare apparent true-of-date values directly with ICRF results.
- Separate structural refactors from astronomical parameter tuning.
- Treat FFT peaks as diagnostic fingerprints, not causal proof.
- Validate promising settings on an independent interval.
- Change model geometry only through a stated hypothesis and preserve a rollback
  baseline.

## Documentation

- [`README_handoff.md`](README_handoff.md): current developer/agent handoff.
- [`binary_tychos.md`](binary_tychos.md): hierarchy design and migration record.
- [`edit_settings_instructions.md`](edit_settings_instructions.md): controlled
  settings workflow.
- [`data/docs/`](data/docs/): TYCHOS source material.
