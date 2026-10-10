# Developer / AI handoff

This handoff describes the experimental **`full-send-binary-tychos`** branch. See
[README.md](README.md) for analysis commands and [binary_tychos.md](binary_tychos.md)
for the design rationale.

## Current state

The exact-equivalence predecessor reports and raw exports are preserved under
`00-backup/full-binary-baseline`.

This branch completes the parent-relative settings migration without deliberately
changing any accepted orbit:

- Earth supplies the PVP motion.
- The Sun inherits Earth and supplies the solar-system position.
- Mars, Mercury, Venus and Eros inherit the Sun's world position.
- Their former absolute radius-100 A/E carriers have been replaced by direct
  parent-relative centres and local motion terms.
- Their local S/B stages, fixed planes and body orbits retain the accepted values
  and matrix order.
- Jupiter, Saturn, Uranus, Neptune, Pluto and Halley were already Sun-hosted.
- The Moon remains Earth-hosted; Phobos and Deimos remain Mars-hosted.

After equivalence was proven, the common annual cosine/sine residual of Mars,
Mercury and Venus was intentionally set to zero. Schema v3 now removes those
parameters entirely rather than storing eight inactive zero fields.
The exact equivalence version and reports remain in
`00-backup/full-binary-baseline`, and its original residual values are preserved
in [binary_tychos.md](binary_tychos.md).

```text
SystemCenter
└─ Earth
   ├─ Moon Node / Plane -> Moon
   └─ Sun-Mars Binary Frame
      └─ Sun Primary -> Sun
         ├─ Mars Junior Companion -> Phobos / Deimos
         ├─ Venus Senior Solar Companion
         ├─ Mercury Junior Solar Companion
         ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
         ├─ Halley
         └─ Eros
```

`SystemCenter` is the fixed geometric reference of Earth's PVP path, not a body or
barycentre. The model remains Tychonic: Earth follows the PVP path, the Sun is
positioned relative to Earth, and the solar subsystem is organized beneath the
Sun.

## What is genuinely different

The complete astronomical source of truth is now the schema-v3
`src/settings/celestial-model.json`. It contains the reference frame, one record
per real body, parent relationships, every numerical motion component, editor
groups and the internal render tree. The separate `celestial-settings.json` has
been removed.

Node, plane and deferent terms remain available for geometric adjustment inside
their owning body's `motion` object, but they are no longer declared as celestial
bodies. Stable component IDs are retained for runtime and legacy import
compatibility.

Previously the code evaluated each affected body from its old absolute chain and
subtracted the current Sun chain at runtime. Now the settings themselves contain
the already-derived parent-relative quantities:

```text
body world position
  = inherited Sun world position
  + direct relative centre
  + optional parent-relative annual harmonic
  + local deferent / plane / body orbit
```

The migrated carrier IDs are:

- `mars-deferent-e`
- `mercury-deferent-a`
- `venus-deferent-a`
- `eros-deferent-a`

All four have `orbitRadius: 0`. Only Eros retains `relativeAnnualCos*` and
`relativeAnnualSin*`, because its distinct non-zero harmonic was not part of the
common-residual removal. The normal phase, speed and tilt fields retain the local
orientation basis required by descendant stages.

Old absolute-carrier files are rejected for these four entries rather than being
silently mixed with the new model. Other stable-ID and legacy-name imports remain
supported.

## Verification completed

The schema-v3 single-file migration was re-exported over the complete baseline
grid on 2026-10-06. It is numerically identical to the immediately preceding
zero-residual full-binary baseline; therefore reorganizing the data into body
records introduced no ephemeris change.

| Gate | Result |
|---|---|
| Dense direct-settings audit, -100 to +100 model years | PASS for all four carriers |
| Maximum centre reconstruction error | `2.3e-16` |
| Maximum annual reconstruction error | `2.9e-14` |
| Source tests | 67 passed across 12 suites |
| Production build | PASS; only third-party MediaPipe source-map warnings |
| Complete ten-body TYCHOS export | PASS; 759,756 non-metadata lines identical |
| Direct Eros export | PASS; 75,969 displayed rows identical |
| Sun–Mars binary CSV | PASS; all recorded numeric deltas exactly zero |
| Ten-body apparent true-of-date summaries | PASS; zero numerical delta |
| Residual, annual and FFT artifacts | PASS; 30 of 30 byte-identical |

Run the software gates with:

```powershell
npm test -- --watchAll=false --runInBand
npm run build
```

The phase-specific derivation scripts used during this migration have been
retired from the active script directory. Their results remain preserved in this
document, `binary_tychos.md`, the archived baselines and Git history.

## End-to-end result

The fresh exports use the baseline bodies, interval, cadence and native frame.
The archived exact-equivalence run confirms the parent-relative derivation against
`00-backup/full-binary-baseline`. The later common-residual removal is an
intentional scientific change and should not pass that particular raw-output gate.

The combined files differ only in their `Generated on` timestamp. Eros is
identical in RA, declination, distance and elongation. The high-precision binary
CSV differs only around `1e-14`, plus `acos` endpoint sensitivity below
`1.21e-6°`; both are numerical roundoff.

Both saved and candidate report sets now use JPL apparent true-of-date, so the
scientific comparison is valid. Keep this reference product identical in future
before/after comparisons; do not compare these values directly with an ICRF
report set. Use `compare_summary_metrics.py` for current report baselines.

The structural migration is complete. The active zero-residual refinement improves
several mean biases but worsens angular RMS by `0.42%` for Mercury, `3.0%` for
Venus and `3.9%` for Mars. The decision currently prioritizes the cleaner geometry
and mean values; local refinement and independent-interval validation remain open.

## Retained Pluto, Jupiter and Saturn refinements

These are empirical adjustments of existing TYCHOS parameters. They do not alter
the hierarchy, restore an absolute carrier, introduce a fitted correction term or
change the Sun. All quoted comparisons use JPL apparent true-of-date coordinates.

### Retained parameters

| Body / component | Parameter | Previous | Retained |
|---|---|---:|---:|
| Pluto orbit | `startPos` | `200` | `204.5` |
| Pluto orbit | `orbitCentera` | `877` | `1387.5` |
| Pluto orbit | `orbitCenterb` | `667` | `1110` |
| Pluto orbit | `orbitCenterc` | `-333` | `-525.5` |
| Jupiter orbit | `startPos` | `-34` | `-34.09` |
| Jupiter orbit | `speed` | `0.52994136` | `0.52989` |
| Jupiter orbit | `orbitCentera` | `-49` | `-49.95` |
| Jupiter orbit | `orbitCenterc` | `-1` | `1.1` |
| Jupiter orbit | `orbitTiltb` | `-1.2` | `-1.24` |
| Saturn orbit | `startPos` | `-123.8` | `-123.28` |
| Saturn deferent | `orbitRadius` | `89` | `98` |
| Saturn deferent | `orbitCenterc` | `0` | `1.68` |
| Saturn orbit | `orbitCenterb` | `40` | `35.87` |

Pluto's speed, radius and tilts were retained. Jupiter's other geometry was
retained. A Saturn speed change was tested and rejected, so its original
`0.21351984` remains active.

### Long-baseline results

The Pluto, Jupiter and Saturn long comparisons cover `1800-06-21` through
`2026-06-21` at one-day cadence.

| Body | Metric | Previous | Retained | Improvement |
|---|---|---:|---:|---:|
| Pluto | RA RMS | `10.051°` | `1.977°` | `80.3%` |
| Pluto | Dec RMS | `1.791°` | `1.324°` | `26.1%` |
| Pluto | Angular mean | `8.246°` | `2.188°` | `73.5%` |
| Pluto | Angular RMS | `9.687°` | `2.321°` | `76.0%` |
| Jupiter | RA RMS | `0.5380°` | `0.3893°` | `27.6%` |
| Jupiter | Dec RMS | `0.3234°` | `0.1575°` | `51.3%` |
| Jupiter | Angular mean | `0.5270°` | `0.3370°` | `36.0%` |
| Jupiter | Angular RMS | `0.6120°` | `0.4107°` | `32.9%` |
| Saturn | RA RMS | `0.9225°` | `0.6053°` | `34.4%` |
| Saturn | Dec RMS | `0.2277°` | `0.1763°` | `22.6%` |
| Saturn | Angular mean | `0.7209°` | `0.4997°` | `30.7%` |
| Saturn | Angular RMS | `0.9150°` | `0.6066°` | `33.7%` |

The fitted Jupiter and Saturn center values were confirmed by fresh exports:
Jupiter's predicted angular RMS was `0.41068°` and the measured value was
`0.41065°`; Saturn's predicted value was `0.60660°` and the measured value was
`0.60661°`.

### Independent validation status

Pluto was also tested over `2000-06-21` through `2026-06-21` at three-hour
cadence. Its angular mean improved from `5.509°` to `2.649°`, angular RMS from
`6.049°` to `2.690°`, RA RMS from `5.876°` to `1.862°`, and Dec RMS from
`2.554°` to `2.007°`. The modern Dec mean became worse, so the retained Pluto
setting is a global-fit choice rather than a claim that every metric improved.

Jupiter and Saturn still require the equivalent dense `2000-2026`, three-hour
validation before their refinements should be considered final. Their remaining
largest RA residuals are near `365.25` and `439.07` days for Jupiter, and
`378.65` days for Saturn. Those peaks are diagnostic fingerprints, not evidence
that another arbitrary parameter should be added.

## Key files

| File | Responsibility |
|---|---|
| `src/settings/celestial-model.json` | Single source: bodies, hierarchy, editor groups and all numerical motion parameters |
| `src/utils/nativeRelativeCarrier.js` | Direct centre/residual/orientation evaluator |
| `src/utils/celestialSettingsSchema.js` | Serialization and safe import rules |
| `src/components/*SunRelativeOrbit.jsx` | Local branch stages beneath the Sun |
| `edits/scripts/` | Maintained ephemeris workflow; see its local `README.md` |

## Constraints

- TYCHOS ephemerides must be generated by the astronomical geometry declared in
  `src/settings/celestial-model.json`.
- Never add fitted perturbations or empirical corrections to model output.
- Do not add Fourier residual terms, lookup tables, splines, date-dependent
  offsets, body-specific output patches or post-export corrections merely to
  improve agreement with JPL.
- Residual, annual and FFT analyses are diagnostic tools only. They may identify
  the period or geometric layer worth investigating, but their fitted values must
  not be injected into the ephemeris output.
- Refine existing geometric quantities—phase, speed, radius, centre, tilt, plane,
  node or an already-declared motion stage—through `celestial-model.json`.
- A genuinely new motion component is acceptable only when it expresses an
  explicit TYCHOS geometric hypothesis, is visible in the declarative model and
  editor, and is validated as geometry. It must not be a hidden error-cancellation
  layer.
- The analysis and export code must remain observers of the astronomical core;
  they must not silently modify body coordinates to improve comparison metrics.
- The retained Eros annual harmonic is a documented compatibility term inherited
  from the equivalence migration. It is not precedent for adding fitted harmonics
  to other bodies and should eventually be replaced only by demonstrated core
  geometry.
- Do not tune parameters until the fresh-export equivalence gate passes.
- Do not restore radius-100 carriers beneath the Sun.
- Do not treat a zero-radius stage as redundant if it retains centre/orientation.
- Keep reference-frame comparison separate from orbital tuning.
- Preserve the baseline settings, exports, configuration and reports together.
