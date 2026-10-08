# Maintained analysis scripts

This directory intentionally contains only the current reusable ephemeris
workflow and its tests. Historical phase-specific experiments were removed after
their conclusions and evidence were incorporated into the maintained documents
and `00-backup`; they remain available through Git history.

## Normal workflow

| File | Responsibility |
|---|---|
| `analysis_config.json` | Default bodies, interval, cadence and input paths |
| `bodies.json` | TYCHOS body names and JPL Horizons target IDs |
| `download_jpl.py` | Download one Horizons bundle containing ICRF and apparent true-of-date coordinates |
| `run_analysis.py` | Validate inputs and orchestrate comparison, analysis and report generation |
| `compare_ephemerides.py` | Match TYCHOS and JPL samples for one body |
| `analyze_ephemerides.py` | Calculate RA/Dec/angular metrics, annual statistics and FFT diagnostics |
| `generate_report.py` | Render a per-body Markdown report |
| `ephemeris_io.py` | Shared strict parsers for TYCHOS and Horizons exports |
| `compare_summary_metrics.py` | Compare generated summary JSON files with any preserved baseline directory |
| `requirements.txt` | Python dependencies |

`run_analysis.py` is the normal entry point. The lower-level scripts are kept
separate so they remain testable and reusable, but ordinarily should not be run
by hand.

## Tests

`test_reference_modes.py` exercises ICRF and apparent true-of-date processing,
including separate output names and apparent-mode RA residual diagnostics.

```powershell
python.exe -B -m unittest edits/scripts/test_reference_modes.py
```

## Research convention

Current comparisons normally use `--reference apparent-of-date`. ICRF support is
retained for controlled fixed-frame investigations, but the two products must
not be mixed in a before/after comparison.

Generated reports are replaceable evidence. Preserve the reports, raw exports,
`analysis_config.json` and the exact celestial model together before starting a
new parameter experiment.
