# Ephemeris Analysis Scripts — Reproduction Instructions

This document explains how to reproduce the lunar ephemeris comparison and residual analysis included in the experimental TYCHOS lunar-plane branch.

The workflow is intentionally reproducible from raw ephemerides:

```text
TYCHOS ephemeris export
        +
JPL Horizons reference ephemeris
        ↓
compare_ephemerides.py
        ↓
moon_comparison_2000-2026_6h.csv
        ↓
analyze_lunar_residuals.py
        ↓
numerical reports
        ↓
generate_report.py
        ↓
lunar_ephemeris_report.md
```

The reference high-resolution test covers:

```text
Start:   2000-06-21 00:00 UTC
Stop:    2026-06-21 00:00 UTC
Cadence: 6 hours
Samples: 37,985
```

The six-hour cadence was chosen because the earlier seven-day dataset was adequate for long-term positional comparisons but too sparse for a clean analysis of monthly and semi-monthly residual periodicities.

---

## 1. Expected directory structure

The examples below assume commands are run from the root of the TSN repository.

```text
TSN/
├── .venv/
├── edits/
│   ├── data/
│   │   ├── raw/
│   │   │   ├── tychos_moon_2000-2026_6h.txt
│   │   │   └── jpl_moon_de441_2000-2026_6h.txt
│   │   └── derived/
│   │       └── moon_comparison_2000-2026_6h.csv
│   ├── reports/
│   │   ├── lunar_summary.json
│   │   ├── lunar_periodic_components.csv
│   │   ├── lunar_fft_peaks.csv
│   │   ├── lunar_annual_stats.csv
│   │   ├── lunar_residuals.csv
│   │   └── lunar_ephemeris_report.md
│   └── scripts/
│       ├── compare_ephemerides.py
│       ├── analyze_lunar_residuals.py
│       ├── generate_report.py
│       └── requirements.txt
```

---

## 2. Python setup

Python 3.11 or newer is recommended.

The scripts were developed and tested on Windows using the standard Command Prompt (`cmd.exe`).

PowerShell is not required.

### Create a virtual environment

If `.venv` does not already exist and the Windows Python launcher is available:

```cmd
py -m venv .venv
```

### Install the required dependency

From the repository root:

```cmd
.venv\Scripts\python.exe -m pip install -r edits\scripts\requirements.txt
```

The current scripts require NumPy.

The virtual environment does **not** need to be activated. During development, calling its Python executable directly proved to be the most reliable approach on Windows:

```cmd
.venv\Scripts\python.exe
```

This avoids both PowerShell execution-policy issues and Windows Microsoft Store Python alias problems.

---

## 3. Generate the JPL Horizons reference ephemeris

The reference lunar ephemeris was obtained from the NASA/JPL Horizons API.

The comparison script expects the original Horizons plain-text response, including the header and the `$$SOE` / `$$EOE` markers. Do not manually remove the header.

### Reference request configuration

```text
Target:           Moon (301)
Center:           Earth geocenter (500@399)
Ephemeris type:   OBSERVER
Reference system: ICRF
Quantities:       astrometric and apparent RA/Dec
RA format:        HMS
Time scale:       UT
Start:            2000-06-21 00:00
Stop:             2026-06-21 00:00
Step:             6 hours
Output:           CSV-formatted plain text
Extra precision:  enabled
```

The Horizons response used for this project reported:

```text
Target body name: Moon (301)
Center body name: Earth (399)
Center-site name: GEOCENTRIC
Target source: DE441
Center source: DE441
```

The API request itself does not explicitly force the planetary ephemeris source. If Horizons uses a different source in the future, record the source reported in the returned header.

---

## 4. Using Thunder Client in VS Code

Thunder Client provides a convenient way to reproduce the JPL request.

### Create the request

1. Open Thunder Client in VS Code.
2. Create a new request.
3. Select `GET`.
4. Use the Horizons API endpoint:

```text
https://ssd.jpl.nasa.gov/api/horizons.api
```

5. Add the following query parameters:

```text
format        text
COMMAND       '301'
OBJ_DATA      'NO'
MAKE_EPHEM    'YES'
EPHEM_TYPE    'OBSERVER'
CENTER        '500@399'
START_TIME    '2000-06-21 00:00'
STOP_TIME     '2026-06-21 00:00'
STEP_SIZE     '6 h'
QUANTITIES    '1,2'
TIME_TYPE     'UT'
TIME_DIGITS   'SECONDS'
REF_SYSTEM    'ICRF'
ANG_FORMAT    'HMS'
EXTRA_PREC    'YES'
CSV_FORMAT    'YES'
```

6. Send the request.
7. Save the complete plain-text response as:

```text
edits/data/raw/jpl_moon_de441_2000-2026_6h.txt
```

### What the returned data should look like

The header should contain fields similar to:

```text
Target body name: Moon (301)
Center body name: Earth (399)
Center-site name: GEOCENTRIC
RA format       : HMS
Table format    : Comma Separated Values (spreadsheet)
```

The numerical ephemeris begins after:

```text
$$SOE
```

and ends before:

```text
$$EOE
```

The expected columns include:

```text
Date__(UT)__HR:MN:SS
R.A._____(ICRF)
DEC______(ICRF)
R.A.____(a-app)
DEC_____(a-app)
```

---

## 5. Example complete JPL Horizons URL request

The same request can be issued directly from a browser or any HTTP client.

```text
https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27301%27&OBJ_DATA=%27NO%27&MAKE_EPHEM=%27YES%27&EPHEM_TYPE=%27OBSERVER%27&CENTER=%27500%40399%27&START_TIME=%272000-06-21%2000%3A00%27&STOP_TIME=%272026-06-21%2000%3A00%27&STEP_SIZE=%276%20h%27&QUANTITIES=%271%2C2%27&TIME_TYPE=%27UT%27&TIME_DIGITS=%27SECONDS%27&REF_SYSTEM=%27ICRF%27&ANG_FORMAT=%27HMS%27&EXTRA_PREC=%27YES%27&CSV_FORMAT=%27YES%27
```

Some characters are URL-encoded in the complete form. For example:

```text
'      → %27
space  → %20
:      → %3A
@      → %40
,      → %2C
```

Thunder Client can normally handle the human-readable parameter values directly when they are entered in its Query parameters interface.

---

## 6. Generate the TYCHOS ephemeris

The TYCHOS ephemeris must cover the **same timestamps** as the JPL reference.

For the high-resolution reference test:

```text
Start:   2000-06-21 00:00:00
Stop:    2026-06-21 00:00:00
Step:    6 hours
```

The comparison script performs exact timestamp matching. Interpolation is not used.

Save the TYCHOS export as:

```text
edits/data/raw/tychos_moon_2000-2026_6h.txt
```

### Expected TYCHOS text format

The parser expects one position per line in this form:

```text
YYYY-MM-DD | HH:MM:SS | RA | Dec
```

For example:

```text
2000-06-21 | 00:00:00 | 21h08m20.6s | -18°16'33.9"
```

The expected coordinate notation is:

```text
RA:   21h08m20.6s
Dec: -18°16'33.9"
```

If the TYCHOS export format changes, `compare_ephemerides.py` may need to be updated accordingly.

---

## 7. Generate the TYCHOS/JPL comparison CSV

Required input files:

```text
edits\data\raw\tychos_moon_2000-2026_6h.txt
edits\data\raw\jpl_moon_de441_2000-2026_6h.txt
```

Run from the TSN repository root:

```cmd
.venv\Scripts\python.exe edits\scripts\compare_ephemerides.py edits\data\raw\tychos_moon_2000-2026_6h.txt edits\data\raw\jpl_moon_de441_2000-2026_6h.txt -o edits\data\derived\moon_comparison_2000-2026_6h.csv
```

The script:

- parses the TYCHOS export;
- parses the JPL Horizons `$$SOE` / `$$EOE` table;
- matches exact timestamps;
- converts RA and Dec to decimal degrees;
- calculates TYCHOS-minus-JPL residuals;
- calculates angular separation;
- stores both ICRF and apparent JPL comparisons.

Expected output:

```text
edits\data\derived\moon_comparison_2000-2026_6h.csv
```

The terminal should also report the number of parsed positions and exact timestamp matches.

For the reference dataset, the expected number of matches is:

```text
37,985
```

---

## 8. Analyze the lunar residuals

Run:

```cmd
.venv\Scripts\python.exe edits\scripts\analyze_lunar_residuals.py edits\data\derived\moon_comparison_2000-2026_6h.csv --out-dir edits\reports
```

The analysis uses JPL **ICRF astrometric RA/Dec** as the primary reference.

Both TYCHOS and JPL equatorial coordinates are rotated into a common ecliptic frame using the fixed J2000 mean obliquity:

```text
23.439291111°
```

The script calculates:

- declination residual statistics;
- angular-separation statistics;
- ecliptic longitude residuals;
- ecliptic latitude residuals;
- annual RMS statistics;
- diagnostic sinusoidal fits;
- FFT residual peaks;
- a machine-readable JSON summary.

### Diagnostic periods

The script currently checks these known periods:

```text
variation             14.765294 days
sidereal month        27.321661 days
anomalistic month     27.554551 days
synodic month         29.530589 days
evection              31.811938 days
annual                365.256363 days
apsidal precession    3232.6054 days
nodal regression      6798.3835 days
```

These labels are used as **diagnostic fingerprints** of periodicities present in the residual.

They are not, by themselves, claims about physical causation.

The compact four-component fit uses:

```text
variation
anomalistic month
evection
annual
```

### Generated files

The analysis normally creates:

```text
edits\reports\lunar_summary.json
edits\reports\lunar_periodic_components.csv
edits\reports\lunar_fft_peaks.csv
edits\reports\lunar_annual_stats.csv
edits\reports\lunar_residuals.csv
```

---

## 9. Generate the Markdown report

Run:

```cmd
.venv\Scripts\python.exe edits\scripts\generate_report.py --summary edits\reports\lunar_summary.json --components edits\reports\lunar_periodic_components.csv --annual edits\reports\lunar_annual_stats.csv --output edits\reports\lunar_ephemeris_report.md
```

Expected output:

```text
edits\reports\lunar_ephemeris_report.md
```

The generated report summarizes:

- dataset size and cadence;
- current RMS errors;
- longitudinal residual structure;
- fitted periodic components;
- annual stability;
- interpretation notes.

### Optional baseline comparison

`generate_report.py` also accepts an optional baseline summary:

```cmd
.venv\Scripts\python.exe edits\scripts\generate_report.py --summary edits\reports\lunar_summary.json --components edits\reports\lunar_periodic_components.csv --annual edits\reports\lunar_annual_stats.csv --baseline-summary PATH_TO_BASELINE_SUMMARY.json --output edits\reports\lunar_ephemeris_report.md
```

This adds a before/after RMS comparison when a compatible baseline JSON report is available.

---

## 10. Reference numerical results

A successful reproduction of the current branch using the committed 2000–2026 six-hour dataset should produce values close to:

```text
Samples:                         37,985
Median cadence:                  6.0 h

Declination RMS:                 0.67960°
Angular separation RMS:          1.85201°
Ecliptic longitude RMS:          1.79610°
Ecliptic latitude RMS:           0.46575°

Four-period longitude fit:
RMS before fit:                  1.79610°
RMS after fit:                   0.10336°
Variance explained:              99.6606%

Extended diagnostic fit:
RMS after fit:                   0.10012°
```

The fitted primary periodic amplitudes should also be close to:

```text
variation          14.765294 d    ~0.65845°
anomalistic month  27.554551 d    ~2.03543°
evection           31.811938 d    ~1.27381°
annual             365.256363 d   ~0.18492°
```

Small differences may occur if the raw ephemeris files, branch parameters, or external JPL output differ.

---

## 11. Common problems

### `python` opens the Microsoft Store or is not found

Use the virtual-environment executable directly:

```cmd
.venv\Scripts\python.exe
```

Do not rely on the `python` Windows alias.

### PowerShell refuses to activate `.venv`

Activation is not required.

Run commands directly with:

```cmd
.venv\Scripts\python.exe
```

The commands in this document were tested using `cmd.exe`.

### `No exact matching timestamps found`

Check that the TYCHOS and JPL files use exactly the same:

```text
start date
stop date
time of day
sampling interval
```

The comparison script intentionally uses exact timestamp matching.

### JPL positions are not being parsed

Check that the Horizons response:

- contains `$$SOE` and `$$EOE`;
- uses `CSV_FORMAT='YES'`;
- uses `ANG_FORMAT='HMS'`;
- includes `QUANTITIES='1,2'`;
- contains ICRF and apparent RA/Dec columns.

Do not save only the numerical rows unless the parser is modified accordingly.

### The number of JPL rows is different in a future run

Horizons is an external service and may change over time.

Check:

- the request start and stop times;
- `STEP_SIZE='6 h'`;
- the API response header;
- the reported JPL ephemeris source;
- whether the API output format has changed.

The committed raw JPL file can be used as a reference for the expected format.

### The generated report differs significantly from the committed report

Verify that:

1. the current lunar-plane branch is checked out;
2. the same TYCHOS ephemeris was exported;
3. the JPL file uses the same timestamps;
4. JPL ICRF coordinates are present;
5. the comparison CSV contains 37,985 matched samples;
6. the current scripts have not been modified.

---

## 12. Recommended workflow for future experiments

Before changing additional lunar parameters:

1. reproduce the current report;
2. confirm the reference RMS values;
3. make one geometrical change at a time;
4. regenerate the TYCHOS ephemeris;
5. regenerate the comparison CSV;
6. rerun the residual analysis;
7. compare both global error statistics and periodic residual structure.

This is important because a modification can improve one coordinate while silently degrading another.

The current branch is intended to serve as a reproducible baseline rather than as a final high-precision lunar theory.

---

## 13. For human developers and AI coding agents

A developer or AI agent continuing the work should not begin by tuning parameters blindly.

The recommended order is:

```text
read the main edits/README.md
        ↓
read this reproduction document
        ↓
reproduce the current report
        ↓
inspect the current lunar geometry
        ↓
make one controlled change
        ↓
regenerate the ephemeris
        ↓
rerun the complete comparison
```

Relevant implementation files include:

```text
src/components/MoonOrbitalPlane.jsx
src/components/PlotSolarSystem.jsx
src/settings/celestial-settings.json
src/utils/plotModelFunctions.js
```

The current branch deliberately preserves a separation between:

```text
lunar orbital-plane orientation
Moon motion within that plane
apsidal motion
Earth-inherited transformations
```

Earlier experiments showed that adding angular rates to ordinary nested `Pobj`
objects can alter unintended coordinate components.

Future work should therefore be validated numerically after every significant
geometrical change.

---

## 14. Reproducibility principle

The committed reports are provided for convenience, but they should not be
treated as the only evidence for the results.

The purpose of the scripts and raw reference files is to allow another
developer — human or AI — to regenerate the comparison independently and
verify the current branch from the underlying ephemerides.
