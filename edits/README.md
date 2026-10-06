# Ephemeris analysis

This directory contains the reproducible analysis workflow for TYCHOS hierarchy
experiments. Run commands from the repository root on Windows with Python 3.11
or newer.

## Quick start

```powershell
# First-time setup
py -m venv .venv
.venv\Scripts\activate
python.exe -m pip install -r edits/scripts/requirements.txt

# Configure bodies, dates, cadence and paths first.
# File: edits/scripts/analysis_config.json

# Download the matching JPL bundle.
python.exe -B edits/scripts/download_jpl.py

# Export the same bodies, dates and cadence from TYCHOS to:
# edits/data/raw/tychos_ephemerides.txt

# Fixed-frame comparison: use a TYCHOS J2000 export.
python.exe -B edits/scripts/run_analysis.py --all --reference icrf `
  --label "J2000 comparison"

# Moving-frame exploratory comparison: use the native TYCHOS export.
python.exe -B edits/scripts/run_analysis.py --all --reference apparent-of-date `
  --label "Full binary equivalence versus JPL apparent true-of-date"

# Produce both report sets from the same inputs for inspection.
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

The files, not the JSON alone, determine the samples analyzed. Use the same
selection and cadence in both exporters. [bodies.json](scripts/bodies.json) maps
supported names to Horizons target IDs.

Useful overrides:

```powershell
python.exe -B edits/scripts/download_jpl.py moon sun mars `
  --start "2000-06-21 00:00" --stop "2026-06-21 00:00" --step "6 h"

python.exe -B edits/scripts/run_analysis.py moon mercury
python.exe -B edits/scripts/run_analysis.py --all
python.exe -B edits/scripts/run_analysis.py --tychos path/to/tychos.txt `
  --jpl path/to/jpl.txt --label "declared export configuration"
```

`--all` analyzes registered bodies present in both files. An explicitly requested
body must exist in both.

## Reference modes

One Horizons download contains both supported products:

| `--reference` | JPL quantity | Appropriate TYCHOS input | Meaning |
|---|---|---|---|
| `icrf` | Astrometric RA/Dec in fixed ICRF | J2000 comparison export | Standard fixed-frame comparison; default |
| `apparent-of-date` | Airless apparent RA/Dec in the true equator/equinox of date | Native/PVP export | Exploratory moving-frame comparison |
| `both` | Both products | Either export, interpreted separately | Writes two clearly labelled result sets |

JPL apparent-of-date includes light-time, gravitational light deflection, stellar
aberration, precession and nutation. It is not assumed to be physically equivalent
to the native TYCHOS frame. That mode tests numerical proximity only.

True-of-date reports contain RA, declination and angular separation. They omit
ecliptic coordinates and lunar periodic fits because rotating them with a fixed
J2000 obliquity would mix frames.

## Full parent-relative hierarchy trial

The `full-binary-tychos` branch uses schema-v2
[celestial-model.json](../src/settings/celestial-model.json) and
[celestial-settings.json](../src/settings/celestial-settings.json). Its hierarchy
is:

```text
SystemCenter                         (PVP coordinate reference)
└─ Earth                             (PVP path)
   ├─ Moon node / plane / orbit
   └─ Sun-Mars Binary Frame
      └─ Sun Primary
         ├─ Mars Junior Companion -> Phobos / Deimos
         ├─ Venus Senior Solar Companion
         ├─ Mercury Junior Solar Companion
         ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
         ├─ Halley
         └─ Eros
```

`SystemCenter` is the fixed coordinate that stores the geometric-centre reference
of Earth's PVP orbit. It is not a body, barycentre or cause of motion. The Sun
system remains inside Earth's branch: Earth follows the PVP path, the Sun orbits
Earth, and the remaining solar bodies are organized beneath the Sun.

This branch completes the settings-level migration begun by
`native-binary-system`. Mars, Mercury, Venus and Eros now inherit the Sun's world
position and store only direct parent-relative centres, annual residuals and local
orbital stages. Their former duplicated radius-100 absolute carriers are gone.

The direct-settings derivation and fresh exports are equivalent to the saved
native baseline. The dense 200-model-year audit passes below `3e-14`, and all
759,756 non-metadata lines in the ten-body TYCHOS export are exactly identical.

Run the source-level migration and software gates with:

```powershell
node edits/scripts/derive_full_binary_settings.js
npm test -- --watchAll=false --runInBand
npm run build
```

Then export the same bodies, timestamps and cadence and compare them with the
saved pre-migration baseline under `00-backup/native-relative-baseline`.

```powershell
python.exe -B edits/scripts/compare_raw_tychos_exports.py
python.exe -B edits/scripts/compare_tychos_body_exports.py

# Optional report/artifact gate: regenerate reports with the same JPL product
# used by the saved baseline before running this comparison.
python.exe -B edits/scripts/run_analysis.py --all --reference apparent-of-date `
  --label "Full binary equivalence"
python.exe -B edits/scripts/compare_phase_equivalence.py
```

## Focused diagnostics

| Command | Purpose |
|---|---|
| `analyze_sun_mars_binary.py` | Compare Earth, SystemCenter and midpoint descriptions without changing the model |
| `analyze_sun_mars_asymmetric.py` | Measure the Sun-relative Mars path |
| `analyze_sun_mars_phase3d.py` | Audit the exact Sun/Mars component cancellation |
| `analyze_solar_companion_phase4a.py` | Audit Mercury/Venus Sun-relative components |
| `analyze_eros_phase4d.py` | Audit Eros Sun-relative components |
| `diagnose_solar_satellite_residuals.py` | Read-only Mercury/Venus residual attribution |

When using the binary diagnostics, enable **Sun-Mars binary CSV** in the TYCHOS
ephemeris panel and save it as `edits/data/raw/sun_mars_binary.csv`.

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

Generated reports are replaceable evidence, not permanent project history. For a
controlled trial, first preserve the complete reports, matching raw exports,
`analysis_config.json` and the settings used for the export. Input hashes and
`--label` record provenance but cannot prove which simulator settings produced a
file.

## Working rules

- Never add fitted perturbations or empirical corrections to TYCHOS output.
- Change geometry only through a stated hypothesis and retain guard metrics.
- Keep intervals, cadence, bodies and reference conventions identical in a
  before/after comparison.
- Separate structural equivalence from observational accuracy.
- Validate retained parameter changes on an independent interval.
- Establish the coordinate contract before interpreting JPL residuals as orbital
  errors.

## Maintained documents

- [README_handoff.md](README_handoff.md): concise accepted state, constraints and
  next work for developers and AI agents.
- [binary_tychos.md](binary_tychos.md): native hierarchy design and implementation.
- [edit_settings_instructions.md](edit_settings_instructions.md): controlled author
  workflow for parameter experiments.
- [data/docs/](data/docs/): TYCHOS source material.
