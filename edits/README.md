# Ephemeris analysis

This directory contains the reproducible comparison workflow for the classic
TYCHOS development branch. Run commands from the repository root on Windows with
Python 3.11 or newer.

## Quick start

```powershell
# First-time setup
py -m venv .venv
.venv\Scripts\activate
python.exe -m pip install -r edits/scripts/requirements.txt

# Configure bodies, UTC dates, cadence and paths in:
# edits/scripts/analysis_config.json

# Download the matching JPL bundle.
python.exe -B edits/scripts/download_jpl.py

# Export the same bodies, dates and cadence from TYCHOS to:
# edits/data/raw/tychos_ephemerides.txt

# Default fixed-frame comparison.
python.exe -B edits/scripts/run_analysis.py --all --reference icrf `
  --label "Development baseline"

# Exploratory comparison of the native export with JPL apparent true-of-date.
python.exe -B edits/scripts/run_analysis.py --all --reference apparent-of-date `
  --label "TYCHOS native versus JPL apparent true-of-date"

# Produce both separately labelled report sets.
python.exe -B edits/scripts/run_analysis.py --all --reference both `
  --label "Reference-frame comparison"
```

The principal outputs are
[ephemeris_overview.md](reports/ephemeris_overview.md) and
[analysis_notes.md](reports/analysis_notes.md). Existing matching JPL data may be
reused when only TYCHOS geometry changes.

## Configuration

Edit [analysis_config.json](scripts/analysis_config.json):

| Setting | Purpose |
|---|---|
| `bodies` | Default bodies to download and analyze |
| `start`, `stop`, `step` | Common UTC interval and cadence |
| `tychos` | Combined TYCHOS export path |
| `jpl` | Combined Horizons bundle path |

The files, not the JSON alone, determine the samples analyzed. Set the same bodies,
interval and cadence in both exporters. [bodies.json](scripts/bodies.json) maps
supported names to Horizons target IDs.

Useful overrides:

```powershell
python.exe -B edits/scripts/download_jpl.py moon sun mars `
  --start "2000-06-21 00:00" --stop "2026-06-21 00:00" --step "6 h"

python.exe -B edits/scripts/run_analysis.py moon mercury
python.exe -B edits/scripts/run_analysis.py --tychos path/to/tychos.txt `
  --jpl path/to/jpl.txt --label "declared export configuration"
```

`--all` analyzes registered bodies present in both files. An explicitly requested
body must exist in both.

## Reference modes

One Horizons download contains both supported products:

| `--reference` | JPL quantity | Appropriate TYCHOS input | Meaning |
|---|---|---|---|
| `icrf` | Astrometric RA/Dec in fixed ICRF | J2000 export when available | Fixed-frame comparison; default |
| `apparent-of-date` | Airless apparent RA/Dec in the true equator/equinox of date | Classic/native PVP export | Exploratory moving-frame comparison |
| `both` | Both products | Either export, interpreted separately | Writes two labelled result sets |

JPL apparent-of-date includes light-time, gravitational light deflection, stellar
aberration, precession and nutation. It is not assumed to be physically equivalent
to the native TYCHOS frame. That mode tests numerical proximity only.

True-of-date reports contain RA, declination and angular separation. They omit
ecliptic coordinates and lunar periodic fits because a fixed J2000 obliquity would
mix reference frames.

## Current development baseline

This branch retains the classic hand-written hierarchy with the accepted Moon
Node/Plane model and explicit fixed planes for Mercury and Venus:

```text
SystemCenter                         (PVP coordinate reference)
└─ Earth                             (PVP path)
   ├─ Moon Node / Plane -> Moon deferent A -> Moon
   ├─ Sun -> outer planets and Halley
   ├─ Venus deferent A / B -> Venus Plane -> Venus
   ├─ Mercury deferent A / B -> Mercury Plane -> Mercury
   ├─ Mars deferent E / S -> Mars -> Phobos / Deimos
   └─ Eros deferent A / B -> Eros
```

`SystemCenter` is a coordinate reference for the geometric centre of Earth's PVP
path, not a body, barycentre or cause of motion. The Mercury/Venus plane objects
re-express their original TYCHOS transforms without changing their intended
ephemerides. Pluto retains its original settings. Observer Trace is not included.

See [README_handoff.md](README_handoff.md) for retained parameters, evidence and
the next controlled experiments.

## Focused diagnostics

```powershell
# Read-only Mercury/Venus residual attribution after a matching Sun run.
python.exe -B edits/scripts/diagnose_solar_satellite_residuals.py

# Exploratory in-memory geometry screens; neither edits settings.
python.exe -B edits/scripts/investigate_moon_tuning.py
python.exe -B edits/scripts/investigate_planet_tuning.py
```

These tools characterize residuals and sensitivity. Their fitted terms or candidate
parameters are not accepted model changes without a simulator export and controlled
validation.

## Outputs and provenance

| Location | Contents |
|---|---|
| `data/derived/<body>_comparison.csv` | Matched samples and coordinate differences |
| `reports/<body>_summary.json` | Metrics, dates, hashes and declared settings provenance |
| `reports/<body>_ephemeris_report.md` | Per-body report |
| `reports/<body>_annual_stats.csv` | Annual statistics |
| `reports/<body>_residuals.csv` | Per-sample diagnostics |
| `reports/<body>_fft_peaks.csv` | Exploratory finite-window spectral peaks |
| `reports/*_apparent_of_date_*` | Separate true-of-date products |
| `reports/ephemeris_overview.md` | Combined current overview |
| `reports/analysis_notes.md` | Generated observations for the current run |

Generated reports are replaceable evidence. Before a controlled trial, preserve
the complete reports, matching raw exports, configuration and settings used for
the export. Input hashes and `--label` record provenance but cannot prove which
simulator settings produced a file.

## Working rules

- Never add fitted perturbations or empirical corrections to TYCHOS output.
- Change geometry only through a stated hypothesis and retain guard metrics.
- Keep bodies, timestamps, cadence and reference convention identical in a
  before/after comparison.
- Separate structural equivalence from observational accuracy.
- Validate retained parameter changes on an independent interval.
- Establish the coordinate contract before interpreting JPL residuals as orbital
  errors.

## Maintained material

- [README_handoff.md](README_handoff.md): concise accepted state, constraints and
  next work for developers and AI agents.
- [data/docs/](data/docs/): TYCHOS source material.
- [machine_learning/README.md](machine_learning/README.md): residual diagnostics.
- [stellarium/README.md](stellarium/README.md): independent coordinate comparisons.
