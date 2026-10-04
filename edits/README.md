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

python.exe -B edits/scripts/analyze_sun_mars_binary.py
# In TYCHOS, export the same bodies/dates/step to:
# edits/data/raw/tychos_ephemerides.txt

# Compare the exports and generate reports.
python.exe -B edits/scripts/run_analysis.py --label "binary tychos overhaul test phase 2. 2000-2026 3h"

# Read-only Mercury/Venus residual attribution after a matching Sun run.
python.exe -B edits/scripts/diagnose_solar_satellite_residuals.py

```

Open `edits/reports/ephemeris_overview.md` for results and
`edits/reports/analysis_notes.md` for diagnostic observations.
For an existing pair of exports, only `run_analysis.py` is needed.
No virtual-environment activation is required.

The residual-attribution command writes
`edits/reports/solar_satellite_residual_diagnostics.md` and `.json`. It fits
model-derived annual, orbital, synodic and second-harmonic periods in chronological
blocks, compares each planet with the simultaneous Sun residual, and searches FFT
periods through 1000 days. It never modifies simulator settings or ephemerides.

### Sun-Mars binary Phase 2.5 diagnostic

In the TYCHOS ephemeris panel, enable **Sun-Mars binary CSV** and use the normal
start date, end date and step controls. Planet selections are optional. When the
run finishes, **Save binary CSV** downloads a separate diagnostic file; the normal
planetary TXT format is unchanged.

Move or save that file as `edits/data/raw/sun_mars_binary.csv`, then run:

```powershell
python.exe -B edits/scripts/analyze_sun_mars_binary.py
```

Or pass its download location explicitly with `--input`. The report at
`edits/reports/sun_mars_binary_report.md` compares the existing Earth pivot, the
PVP/SystemCenter and the per-sample Sun-Mars midpoint. The midpoint is a mathematical
control: its equal radii and exact opposition are true by construction and do not
identify a physical barycentre.

The follow-up Phase 3A screen reuses the same CSV; no new simulator or JPL export
is required:

```powershell
python.exe -B edits/scripts/analyze_sun_mars_phase3a.py
```

It compares a family of fixed Sun-Mars radius ratios using separate PVP-distance,
path-size and best-fit-circle criteria. Its exact opposition is imposed by the
weighted-centre construction and must not be interpreted as an independent result.

Phase 3B analyzes the existing Mars trajectory directly from the Sun, testing the
asymmetric primary-companion interpretation without changing the model:

```powershell
python.exe -B edits/scripts/analyze_sun_mars_asymmetric.py
```

It reports the Sun-Mars distance range, focus-at-Sun conic fit, best fixed plane,
angular sweep, spectral periods and cycle recurrence. The derived relative-vector
CSV is written to `edits/data/derived/sun_mars_relative.csv`.

Phase 3D expands the configured Sun and Mars transform chains into their exact
Sun-relative components and quantifies the annual-carrier cancellation:

```powershell
python.exe -B edits/scripts/analyze_sun_mars_phase3d.py
```

It writes `edits/reports/sun_mars_phase3d_report.md` and the corresponding component
vectors to `edits/data/derived/sun_mars_phase3d_components.csv`. This is an algebraic
audit of existing settings, not a fitted orbit or simulator modification.

Phase 3E replaces the legacy Mars deferent scene nodes with the exact four-component
Sun-relative construction established by Phase 3D. Before Phase 4, make a fresh
TYCHOS export over the same interval and cadence as the saved Phase 3C baseline.
Enable **Sun-Mars binary CSV** as well. Then rerun the ordinary comparison and the
Phase 3B/3D diagnostics. Phase 3E is accepted only if the planetary ephemerides and
binary vectors remain unchanged at export precision.

The historical Phase 3E, Phase 4B and Phase 4C results are retained in the handoff
and saved reports. The current comparison command is configured for the final
Phase 4C-to-4E Eros system gate:

```powershell
python.exe -B edits/scripts/compare_phase_equivalence.py
```

By default it compares `00-backup/phase4d` with the current reports and binary
CSV, writing `edits/reports/phase4e_system_equivalence_report.md`. The command fails
if the baseline contains no summary JSON or numeric artifacts; an empty baseline
can no longer produce a vacuous pass.

Phase 4A audits the existing Mercury and Venus chains before either body is
reparented beneath the Sun:

```powershell
python.exe -B edits/scripts/analyze_solar_companion_phase4a.py
```

It expands each planet-minus-Sun vector into exact centre, annual-carrier,
deferent-B, fixed-plane and main-orbit components. The report at
`edits/reports/solar_companion_phase4a_report.md` also checks the expansion against
the full hierarchy and the current formatted TYCHOS export. This is a read-only
architectural audit; it does not tune settings or change the model.

Phase 4B makes Venus a structural descendant of the Sun using the exact five-term
Phase 4A construction. Mercury remains on its legacy carrier chain. Its fresh
ordinary and Sun-Mars binary exports over the same 2000-06-21 through 2026-06-21
three-hour grid passed the full gate. Reproduce it with:

```powershell
python.exe -B edits/scripts/compare_phase_equivalence.py --output edits/reports/phase4b_venus_equivalence_report.md
```

The saved Phase 4A reports are the immediate pre-Venus baseline. Phase 4B produced
zero scientific-summary differences for all ten bodies, 31 of 31 byte-identical
numeric artifacts and an exactly unchanged 9,497-row Sun-Mars binary CSV.

Phase 4C applies the same exact construction to Mercury while leaving the accepted
Venus component unchanged. The complete Phase 4B baseline has been preserved in
`00-backup/phase4b`. Fresh ordinary and Sun-Mars binary exports over the same
three-hour 2000-2026 grid passed the complete equivalence gate: all ten scientific
summaries have zero differences, all 31 numeric artifacts are byte-identical and
all 9,497 binary rows are exactly unchanged. The accepted report is
`edits/reports/phase4c_mercury_equivalence_report.md`.

Phase 4D audits the legacy Earth-level Eros chain before reparenting it:

```powershell
python.exe -B edits/scripts/analyze_eros_phase4d.py
```

The audit reconstructs `Eros - Sun` as four exact components: the fixed centre
difference, annual carrier mismatch, deferent-B stage and main Eros stage. Its
algebraic reconstruction error is below `9e-14` model units, while its reconstructed
direction agrees with the saved 75,969-row export to `0.001139 deg` RMS, consistent
with formatted export precision. The annual radius-100 carriers cancel by only
`89.65%` because their tilted planes differ, so that remainder must be retained.
No additional Eros plane object is required.

Phase 4E implements that exact construction beneath the Sun. It changes hierarchy,
not settings or intended coordinates. The accepted pre-change Eros export is
preserved as `00-backup/phase4c/eros_ephemerides_before.txt`; the complete Phase 4D
reports and binary CSV are preserved under `00-backup/phase4d`.

First export Eros alone over `2000-06-21 00:00` through `2026-06-21 00:00` at
three-hour cadence and save it as `edits/data/raw/eros_ephemerides_after.txt`.
Then run the direct formatted-export gate:

```powershell
python.exe -B edits/scripts/compare_tychos_body_exports.py
```

Next make the normal ten-body TYCHOS export over that same grid, enable and save the
Sun-Mars binary CSV, and run:

```powershell
python.exe -B edits/scripts/run_analysis.py --label "Phase 4E Eros Sun-relative hierarchy, 2000-2026 3h"
python.exe -B edits/scripts/compare_phase_equivalence.py
```

Both Phase 4E gates passed. The Eros export has zero timestamp, RA, declination,
distance and elongation mismatches across all 75,969 rows. The full system has zero
scientific-summary deltas for all ten analyzed bodies, all 31 numeric artifacts are
byte-identical, and all 9,497 Sun-Mars binary rows are exactly unchanged. Source
tests and the production build also pass. Phase 4E is therefore accepted as
coordinate preserving.

### Declarative hierarchy equivalence gate

The `declarative-hierarchy` branch moves the complete live and plot/export topology
into `src/settings/celestial-model.json`. Numerical settings and all accepted
relative-orbit components remain unchanged. The pre-migration reports, raw TYCHOS
export, binary CSV, Eros export, JPL source, settings and analysis configuration are
preserved together in `00-backup/new-baseline`.

After the code migration, export the normal ten bodies over the same
`2000-06-21 00:00` through `2026-06-21 00:00` three-hour grid, enable and save the
Sun-Mars binary CSV, and rerun:

```powershell
python.exe -B edits/scripts/run_analysis.py --label "Declarative hierarchy candidate, 2000-2026 3h"
python.exe -B edits/scripts/compare_phase_equivalence.py
```

Also export Eros alone over the same grid as
`edits/data/raw/eros_ephemerides_after.txt`, then run:

```powershell
python.exe -B edits/scripts/compare_tychos_body_exports.py
```

The migration is accepted only when both reports pass with no unintended output
change.

Both gates pass. The full ten-body and Sun-Mars binary comparison has zero summary
deltas, 31 of 31 byte-identical numeric artifacts and 9,497 exactly unchanged
binary rows. The direct Eros comparison has 75,969 matching timestamps and zero
displayed RA, declination, distance or elongation mismatches. The declarative
hierarchy is therefore accepted as coordinate preserving.

### Native binary-system schema gate

The `native-binary-system` branch promotes the accepted declarative topology and
flat parameter array into linked schema-v2 model/settings documents. Numerical
parameters and all relative-orbit formulas remain unchanged. Legacy flat-array
settings files remain importable; new saves use stable IDs.

Use one combined TYCHOS export containing the normal ten bodies **plus Eros** on
the same three-hour `2000-06-21 00:00` through `2026-06-21 00:00` grid, and save
the Sun-Mars binary CSV from the same unchanged model state. Then run:

```powershell
python.exe -B edits/scripts/run_analysis.py --label "Native binary system schema v2, 2000-2026 3h"
python.exe -B edits/scripts/compare_phase_equivalence.py --output edits/reports/native_binary_system_equivalence_report.md
```

```powershell
python.exe -B edits/scripts/compare_tychos_body_exports.py --candidate edits/data/raw/tychos_ephemerides.txt --output edits/reports/native_binary_system_eros_equivalence_report.md
```

Both native-schema gates pass. The ten-body summaries have zero numerical deltas,
all 31 numeric artifacts are byte-identical, and all 9,497 Sun-Mars binary rows
are exactly unchanged. The combined export also reproduces all 75,969 saved Eros
timestamps and displayed RA, declination, distance and elongation fields exactly.
The native schema is therefore accepted as coordinate preserving.

Before a comparison trial, optionally [save the current results](#optional-pre-test-backup)
in `edits/data/pretest/` before replacing exports or running the analysis again.

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
# Default: analyze against JPL ICRF astrometric RA/Dec.
python.exe -B edits/scripts/run_analysis.py moon
python.exe -B edits/scripts/run_analysis.py --all

# Analyze a TYCHOS native export against JPL apparent true-of-date RA/Dec.
python.exe -B edits/scripts/run_analysis.py --all --reference apparent-of-date `
  --label "TYCHOS native versus JPL true-of-date apparent"

# Generate separate ICRF and true-of-date report sets from the same inputs.
python.exe -B edits/scripts/run_analysis.py --all --reference both `
  --label "Reference-frame comparison"

# Override the JPL request without editing the defaults.
python.exe -B edits/scripts/download_jpl.py moon sun mars --start "2000-06-21 00:00" --stop "2026-06-21 00:00" --step "6 h"
```

Explicitly selected/default bodies must exist in both exports. `--all` uses the
intersection and reports registered bodies present in only one input.

### JPL reference modes

`run_analysis.py --reference` accepts:

| Value | JPL columns | Intended TYCHOS export | Interpretation |
|---|---|---|---|
| `icrf` | Astrometric RA/Dec in fixed ICRF | J2000 comparison export | Standard fixed-frame comparison; this remains the default. |
| `apparent-of-date` | Airless apparent RA/Dec in Earth's true equator and equinox of date | Native/PVP export | Exploratory comparison between moving frames. |
| `both` | Both products | Whichever TYCHOS export is supplied | Writes two separately labelled report sets for inspection; it does not make one TYCHOS export belong to both frames. |

JPL apparent-of-date includes light-time, gravitational light deflection, stellar
aberration, precession and nutation. The TYCHOS framework may interpret several
observed effects geometrically through the Man's Yearly Path, but this analysis
option tests numerical agreement only; it does not assume that the JPL and TYCHOS
mechanisms or moving frames are equivalent.

True-of-date reports contain RA, declination and angular-separation statistics.
They intentionally omit ecliptic longitude/latitude and lunar periodic fits:
rotating true-of-date RA/Dec with the pipeline's fixed J2000 obliquity would mix
reference frames and create invalid diagnostics.

## Inputs and provenance

TYCHOS already exports a single TXT with `PLANET: MOON`, `PLANET: SUN`, etc.
Save that file directly; do not split it or modify the simulator.
The JPL downloader requests bodies sequentially and combines complete responses,
including target headers, time tables, request URLs and download time. It replaces
the reference file only after all responses pass validation.

JPL requests use Earth geocenter (`500@399`), `OBSERVER`, quantities `1,2`, UT,
ICRF, HMS, seconds, extra precision and CSV-formatted text. Quantity 1 supplies
astrometric ICRF RA/Dec; for this Earth-centred observer, quantity 2 supplies
airless apparent RA/Dec in the true equator and equinox of date. One download
therefore supports all three analysis modes. The reference source is read from
Horizons headers, not inferred from the filename. Complete Thunder Client
responses can also be concatenated, with one response per target.

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
| `reports/<body>_apparent_of_date_*` | Separate true-of-date outputs created by `--reference apparent-of-date` or `both` |
| `reports/ephemeris_overview.md` | Latest results and input freshness by body |
| `reports/analysis_notes.md` | Observations and questions for bodies in this run |

The overview checks whole-file hashes, not simulator settings. Replacing one body
in a combined file conservatively marks other saved results stale. Refresh that
status without recalculating with `run_analysis.py --overview-only`.

Reports and derived CSVs can be regenerated. A clean `reports/` directory is valid.
Do not manually maintain scientific conclusions inside generated files: record
accepted conclusions in [README_handoff.md](README_handoff.md).

## Optional pre-test backup

Use `data/pretest/` when you want to compare a new trial with the previous run.
Copy the complete `reports/` directory to `data/pretest/reports/` before rerunning
the analysis. Include the JSON and CSV files, not just the Markdown summaries.
The overview identifies which bodies belong to the saved run; older outputs for
other bodies may also be present.

For a reproducible comparison, also preserve the two input TXT files under
`data/pretest/raw/`, plus `analysis_config.json`, `bodies.json` and the settings
snapshot actually used for that export. Save these before changing settings or
replacing the inputs. A copy of today's settings is evidence of the export
configuration only if you know that export used them. Derived comparison CSVs
are optional because they can be regenerated from the saved inputs.

This is a manual, optional backup of one comparison baseline. The scripts neither
read nor update `data/pretest/` automatically. Keep its contents together from
the same run; replace the backup deliberately when choosing a new baseline, or
archive it elsewhere if it must be retained. No separate trial document or backup
for every run is required. Compare the same bodies, timestamps and reference
conventions, and describe the changed parameter with `--label` in the new run.

## Purpose and interpretation

This workflow evaluates the compact TYCHOS geometry against reference ephemerides.
**Golden rule: never add perturbation terms or empirical corrections to the model
or its exported ephemerides.** Improvements must come from geometry and its correct
implementation; fitted periodic terms are for residual analysis only.

Before changing the model, read the [developer handoff](README_handoff.md) and
consult the source material in [data/docs/](data/docs/). A coherent residual can
point to a geometric or coordinate issue to investigate. Unexplained residuals
remain open questions, not candidates for compensating perturbation terms.

The default primary metrics compare against JPL ICRF astrometric RA/Dec. The
optional true-of-date mode uses JPL apparent coordinates and is explicitly
labelled as an exploratory moving-frame comparison. Ecliptic diagnostics are
available only for ICRF mode and use a common fixed J2000 obliquity. RA differences
are coordinate differences; angular separation measures total directional error.
Do not mix frames, intervals or export settings when comparing results.

The Moon's periodic fits are in-sample diagnostics, not simulator corrections or
proof of a physical mechanism. Other bodies do not receive lunar terms. FFT peaks
are finite-window estimates over 1-500 days, requiring regular cadence and enough
samples. Out-of-sample validation remains a separate pending investigation.

## Documents and scripts

- **This README:** setup, commands and output conventions; update when the workflow changes.
- **[README_handoff.md](README_handoff.md):** retained baseline, reasoning constraints and next investigations; review before pushing branch changes.
- **[binary_tychos.md](binary_tychos.md):** accepted binary hierarchy, implementation details, validation evidence and hierarchy-aware settings guidance.
- **[edit_settings_instructions.md](edit_settings_instructions.md):** practical author workflow for controlled settings experiments, including a Mercury-plane example.
- **[data/docs/](data/docs/):** the TYCHOS book and other source material; cite edition and chapter/page when using it.
- **`reports/`:** generated evidence for each run, not a development diary.
- **`data/pretest/` (optional):** manually saved results and inputs for a before/after comparison.

The operational scripts are `download_jpl.py`, `ephemeris_io.py`,
`compare_ephemerides.py`, `analyze_ephemerides.py`, `generate_report.py` and
`run_analysis.py`. NumPy is the only additional Python dependency.
Use either command-line entry point with `--help` for its options.

## Research tools

- [Machine learning](machine_learning/README.md): temporal residual diagnostics, configuration and generated experiment outputs.
- [Stellarium](stellarium/README.md): reference export and coordinate comparisons; datasets remain under `data/stellarium*`.
