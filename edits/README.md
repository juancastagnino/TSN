# Ephemeris analysis

Run from the repository root on Windows with Python 3.11 or newer.

```powershell
# First-time setup only
py -m venv .venv
.venv\Scripts\activate
python.exe -m pip install -r edits/scripts/requirements.txt

# Edit edits/scripts/analysis_config.json: bodies, UTC dates, step, input paths.
# Download JPL once for that selection and time grid.
python.exe -B edits/scripts/download_jpl.py

# In TYCHOS, export the same bodies/dates/step to:
# edits/data/raw/tychos_ephemerides.txt

# Compare the exports and generate reports.
python.exe -B edits/scripts/run_analysis.py --label "Describe the settings used for this export"
```

Open `edits/reports/ephemeris_overview.md` for results and
`edits/reports/analysis_notes.md` for diagnostic observations.
For an existing pair of exports, only the last command is needed.
No virtual-environment activation is required.

## Configure an analysis

Edit [scripts/analysis_config.json](scripts/analysis_config.json):

| Setting | Default | Purpose |
|---|---|---|
| `bodies` | `moon`, `sun`, `mars` | Bodies downloaded and analyzed by default |
| `start`, `stop` | 2000-06-21 to 2026-06-21, 00:00 UTC | JPL request interval |
| `step` | `6 h` | JPL request cadence; integer `m`, `h` or `d` |
| `tychos` | `edits/data/raw/tychos_ephemerides.txt` | Combined simulator export |
| `jpl` | `edits/data/raw/jpl_ephemerides.txt` | Combined reference file |

Set the same interval and cadence manually in the TYCHOS exporter. The analyzer
uses the dates actually present in the files; changing the JSON does not update,
trim or regenerate an existing export.

[scripts/bodies.json](scripts/bodies.json) maps body names to Horizons target IDs.
Other registered bodies can be selected without changing the scripts.

```powershell
# Analyze only the Moon, or all registered bodies present in both files.
python.exe -B edits/scripts/run_analysis.py moon
python.exe -B edits/scripts/run_analysis.py --all

# Override the JPL request without editing the defaults.
python.exe -B edits/scripts/download_jpl.py moon sun mars --start "2000-06-21 00:00" --stop "2026-06-21 00:00" --step "6 h"
```

Explicitly selected/default bodies must exist in both exports. `--all` uses the
intersection and reports registered bodies present in only one input.

## Inputs and provenance

TYCHOS already exports a single TXT with `PLANET: MOON`, `PLANET: SUN`, etc.
Save that file directly; do not split it or modify the simulator.
The JPL downloader requests bodies sequentially and combines complete responses,
including target headers, time tables, request URLs and download time. It replaces
the reference file only after all responses pass validation.

JPL requests use Earth geocenter (`500@399`), `OBSERVER`, quantities `1,2`, UT,
ICRF, HMS, seconds, extra precision and CSV-formatted text. The reference source
is read from Horizons headers, not inferred from the filename. Complete Thunder
Client responses can also be concatenated, with one response per target.

Reuse JPL when changing only the simulator geometry. Download again when the
required bodies or time grid change; a download replaces the bundle with exactly
the requested selection. The analyzer checks body identities, matching timestamps,
malformed rows and duplicates. It does not interpolate.

`--label` describes the settings used **at export time**, not the current settings
file. Without a label, configuration is unknown unless the identical TYCHOS file
already has a recorded label. `--export-settings path/to/settings.json` optionally
records a snapshot that you declare was used for the export. Neither declaration
is automatically verified against the simulator.

Use `--tychos path/to/export.txt` and `--jpl path/to/reference.txt` to override
analysis inputs, or `--output path/to/reference.txt` to override a download.

## Generated outputs

Each run replaces fixed outputs for its selected bodies; no per-experiment folders
are needed. Other bodies' previous outputs remain until recomputed or removed.

| Location | Contents |
|---|---|
| `data/derived/<body>_comparison.csv` | Matched coordinates and differences |
| `reports/<body>_summary.json` | Metrics, dates, hashes and declared export settings |
| `reports/<body>_ephemeris_report.md` | Per-body summary |
| `reports/<body>_annual_stats.csv`, `<body>_residuals.csv` | Annual and per-sample diagnostics |
| `reports/<body>_fft_peaks.csv` | Exploratory longitude spectral peaks |
| `reports/moon_periodic_components.csv` | Moon-only fitted periodic components |
| `reports/ephemeris_overview.md` | Latest results and input freshness by body |
| `reports/analysis_notes.md` | Observations and questions for bodies in this run |

The overview checks whole-file hashes, not simulator settings. Replacing one body
in a combined file conservatively marks other saved results stale. Refresh that
status without recalculating with `run_analysis.py --overview-only`.

Reports and derived CSVs can be regenerated. A clean `reports/` directory is valid.
Do not manually maintain scientific conclusions inside generated files: record
accepted conclusions in [README_handoff.md](README_handoff.md).

## Purpose and interpretation

This workflow evaluates the compact TYCHOS geometry against reference ephemerides.
**Golden rule: never add perturbation terms or empirical corrections to the model
or its exported ephemerides.** Improvements must come from geometry and its correct
implementation; fitted periodic terms are for residual analysis only.

Before changing the model, read the [developer handoff](README_handoff.md) and
consult the source material in [data/docs/](data/docs/). A coherent residual can
point to a geometric or coordinate issue to investigate. Unexplained residuals
remain open questions, not candidates for compensating perturbation terms.

Primary metrics compare against JPL ICRF astrometric RA/Dec; the CSV also retains
apparent-coordinate comparisons. Ecliptic diagnostics use a common fixed J2000
obliquity. RA differences are coordinate differences; angular separation measures
total directional error. Do not mix frames, intervals or export settings when
comparing results.

The Moon's periodic fits are in-sample diagnostics, not simulator corrections or
proof of a physical mechanism. Other bodies do not receive lunar terms. FFT peaks
are finite-window estimates over 1-500 days, requiring regular cadence and enough
samples. Out-of-sample validation remains a separate pending investigation.

## Documents and scripts

- **This README:** setup, commands and output conventions; update when the workflow changes.
- **[README_handoff.md](README_handoff.md):** retained baseline, reasoning constraints and next investigations; review before pushing branch changes.
- **[data/docs/](data/docs/):** the TYCHOS book and other source material; cite edition and chapter/page when using it.
- **`reports/`:** generated evidence for each run, not a development diary.

The operational scripts are `download_jpl.py`, `ephemeris_io.py`,
`compare_ephemerides.py`, `analyze_ephemerides.py`, `generate_report.py` and
`run_analysis.py`. NumPy is the only additional Python dependency.
Use either command-line entry point with `--help` for its options.
