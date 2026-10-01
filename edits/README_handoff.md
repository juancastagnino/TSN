# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Branch scope

This handoff describes the **`venus-mercury-planes-frame`** branch. It retains the
accepted Moon Node/Plane baseline and explicit separate fixed planes for Mercury and
Venus, and adds an explicit ephemeris-output choice between the native moving-PVP
frame and a fixed J2000/ICRF-comparison frame. The frame conversion changes only how
coordinates are reported; it does not remove PVP motion or change the orbital model.

The active celestial settings are an author-supplied Sun/Mercury candidate and have
not yet been validated on this branch. The preceding equivalence-preserving plane
settings are saved in `00-backup/celestial-settings.json` for a controlled comparison.
Pluto remains at its original TYCHOS settings.

This branch intentionally excludes Observer Trace. It also does not add moving
Mercury or Venus node objects: the current evidence supports separate fixed planes,
but does not yet establish measurable nodal precession for either solar satellite.

## Current lunar geometry and settings (2026-09-25)

The accepted working model has one lunar deferent inside an independently
precessing node/plane transform:

```text
Earth
└─ MoonOrbitalPlane: node outer -> plane -> node counter-rotation
   └─ Moon deferent A
      └─ Moon
```

`Moon deferent B` was an all-zero identity layer. It has been removed from
[celestial-settings.json](../src/settings/celestial-settings.json),
[misc-settings.json](../src/settings/misc-settings.json), the visible hierarchy and
the export/trace hierarchy. This is a structural cleanup and must not change lunar
coordinates. Do not restore it merely to hold the node rate; node precession is
already implemented by [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx).

The accepted working settings are:

| Entry | Current orbital settings |
|---|---|
| Moon Node | `startPos = -296`, `speed = -0.33780566`; centres, radius and orbital tilts zero |
| Moon Plane | `orbitCentera = 0.001`, `orbitCenterb = 0.002`, `orbitCenterc = 0`, `orbitTilta = 0`, `orbitTiltb = -5.15`; radius, `startPos` and `speed` zero |
| Moon deferent A | `startPos = 167.51`, `speed = 0.71015440177343`, `orbitRadius = 0.02786`; centres and orbital tilts zero |
| Moon | `startPos = 318.0`, `speed = 83.2851946`, `orbitRadius = 0.25505129081458283`; centres and orbital tilts zero |

The final values came from controlled simulator exports. Deferent-A radius was
screened first, then `Moon deferent A.startPos` and `Moon.startPos` were moved in
opposite directions while keeping their sum near `485.51` degrees. This preserved
the longitude zero point while changing their relative phase. A final complex-vector
interpolation refined the radius to `0.02786`. The resulting 27.554551-day fitted
residual is about `0.0059` degrees; do not resume blind deferent tuning unless a new
dataset or geometric hypothesis justifies it. See
[moon_adjustment_report.md](reports/moon_adjustment_report.md).

The node speed is approximately `-2*pi/18.6`, a clockwise 18.6-model-year cycle.
The outer node rotation and matching counter-rotation precess the plane without
directly adding the node angle to lunar longitude. Numeric settings are stored as
strings and can contain whitespace; compare them numerically.

[PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) implements the
export/trace hierarchy. [SolarSystem.jsx](../src/components/SolarSystem.jsx) applies
the same hierarchy to both the enlarged displayed Moon and the hidden physical
`Actual Moon` used for coordinates. `MoonOrbitalPlane` live mode follows displayed
simulation time without registering duplicate export objects.

### Node/plane controls and implementation

`MoonOrbitalPlane.jsx` now applies both entries' centre offsets, radius, orbital
tilts, starting angle and speed. Each stage follows the existing `Cobj` convention:
**centre translation -> orbital tilt -> orbital rotation -> radius translation**;
the inner node counter-rotation remains after the plane stage.

- Node centre offsets are before the node rotation; plane centre offsets inherit
  that rotation. The retained nonzero plane centres therefore pivot with the node.
- `orbitCentera/b/c` map to scene axes `x/z/y`. Yellow guides show centre offsets,
  and white guides show orbital radius/circle while editing. They do not encode
  Earth's diameter automatically. `size` and `tilt` affect an editor axis marker;
  use `orbitTilta/b` for orbital geometry.
- Live display offsets use the same `39.2078` enlargement as the visible Moon;
  the hidden Actual Moon retains physical distances. Plot offsets follow `Pobj`'s
  size mode. Export stepping controls its own outer, plane and inner rotations.
- Edit Settings skips visibility controls for geometry entries without `visible`,
  preventing the former Leva `undefined.path` crash while retaining their controls.

Numerical component checks passed for zero-offset equivalence, all orbital controls,
the 18.6-year cycle, both size modes and live/export isolation. After deferent B was
removed, the Edit Settings tests passed and the production build passed with only
the pre-existing MediaPipe source-map warnings. The test now asserts that deferent B
does not reappear in the Edit Settings schema and derives reset expectations from
the loaded settings rather than obsolete hard-coded lunar values.

### Current Moon dataset and report

The accepted comparison is Moon-only: 75,969 samples at three-hour cadence from
2000-06-21 through 2026-06-21 against geocentric JPL ICRF astrometric RA/Dec. The
TYCHOS text export does not encode its settings, so provenance depends on preserving
the matching JSON and recording the run label. The accepted results are:

| Metric | Accepted result |
|---|---:|
| RA coordinate RMS | 1.098461 degrees |
| Declination RMS | 0.391893 degrees |
| Angular separation RMS | 1.115662 degrees |
| Ecliptic longitude RMS | 1.094302 degrees |
| Ecliptic latitude RMS | 0.228328 degrees |

The accepted result is summarized in
[moon_adjustment_report.md](reports/moon_adjustment_report.md). Generated files in
`reports/` are overwritten by every analysis. If they describe a later rejected
trial, rerun the accepted settings before treating them as the baseline evidence.

### Controlled improvement over the preceding lunar configuration

The preceding accepted configuration used the same 75,969 timestamps and JPL
coordinates, with `Moon deferent A.startPos = 177`, `orbitRadius = 0.0266` and
`Moon.startPos = 309`. The controlled comparison is:

| Metric | Previous | Current | Relative change |
|---|---:|---:|---:|
| RA coordinate RMS | 1.410884 | 1.098461 | -22.1% |
| Declination RMS | 0.417194 | 0.391893 | -6.1% |
| Angular separation RMS | 1.407164 | 1.115662 | -20.7% |
| Ecliptic longitude RMS | 1.390850 | 1.094302 | -21.3% |
| Ecliptic latitude RMS | 0.231405 | 0.228328 | -1.3% |

Mean angular error improved by 23.2%, median angular error by 29.3%, angular P95
by 14.0% and maximum angular error by 10.4%. Mean longitude residual changed from
`-0.491413` to `-0.002219` degrees, effectively removing the zero-point bias.

The anomalistic-month diagnostic amplitude fell from `0.994726` to `0.005853`
degrees, a 99.4% reduction. Variation (`~0.6574` degrees), the evection-frequency
component (`~1.2705` degrees) and the annual component (`~0.1849` degrees) were
nearly unchanged. The remaining 27.21-day FFT component is about `0.5023` degrees.
These are residual fingerprints, not correction terms or proof of physical cause.

A later combined plane trial changed `Moon Plane.orbitCentera` from `0.001` to
`-0.002`, `orbitTilta` from `0` to `-0.2` and `orbitTiltb` from `-5.15` to `-5.3`.
It was rejected: longitude RMS worsened 3.3%, angular RMS 3.9%, declination RMS
7.6%, latitude RMS 17.5% and the post-fit longitude remainder 23.2%. If the author's
plane hypothesis is revisited, test each parameter independently.

The accepted fit still has a longitude trend near 46-47 arcseconds/year. Do not
tune `Moon.speed` merely to cancel it before resolving the coordinate-frame and
observable-definition questions.

## Mercury/Venus plane hierarchy and current candidate (2026-09-30)

The explicit plane hierarchy remains intact. It contains no Mercury eccentric,
synodic or other residual-fitted displacement layer:

The active hierarchies are:

```text
Mercury deferent A
└─ Mercury deferent B
   └─ Mercury Plane
      └─ Mercury

Venus deferent A
└─ Venus deferent B
   └─ Venus Plane
      └─ Venus
```

The preceding saved baseline was an equivalence-preserving refactor of the original
TYCHOS hierarchy. The complete pre-orbit transform formerly stored on each planet
was moved into its zero-speed, zero-radius plane, and the corresponding planet fields
were reset to zero.

| Entry | Saved equivalence baseline |
|---|---|
| Mercury deferent B | Original: `startPos = 33`, `orbitRadius = 0.6`, `orbitTilta = -1.3`, `orbitTiltb = 0.5` |
| Mercury Plane | Original Mercury transform: `orbitCenterb = 3`, `orbitCenterc = -0.1`, `orbitTilta = 3`, `orbitTiltb = 0.5` |
| Mercury | Original `startPos = -180.8`, `speed = 26.08763045`, `orbitRadius = 38.710225`; centre and orbital-plane fields zero |
| Venus deferent B | Original: `startPos = 16.6`, `orbitRadius = 0.6`, `orbitCenterb = 0.65` |
| Venus Plane | Original Venus transform: `orbitCenterb = -0.9`, `orbitTilta = 3.2`, `orbitTiltb = -0.05` |
| Venus | Original `startPos = -23.6`, `speed = 10.21331385`, `orbitRadius = 72.327789`; centre and orbital-plane fields zero |

An in-memory comparison across 5,000 dates spanning 26 years found identical RA/Dec
and ecliptic longitude/latitude for the original hierarchy and the explicit-plane
hierarchy; the reported angular-separation difference was below `0.000001` degree
and arose only from floating-point `acos` noise.

`Mercury Eccentric`, `Mercury Synodic` and `CounterRotatedOrbit.jsx` are absent from
this branch. Their earlier numerical improvements belong to the refinement
experiments, not to this equivalence-preserving plane branch.

The previous simulator export confirmed that saved baseline over 75,969 three-hour
samples from 2000-06-21 through 2026-06-21. The offline hierarchy reconstruction
matches that export to about `0.0012` degree, consistent with export precision.

| Body / metric | Confirmed baseline |
|---|---:|
| Mercury RA RMS | `2.279213 deg` |
| Mercury declination RMS | `1.439953 deg` |
| Mercury separation RMS | `2.605186 deg` |
| Mercury longitude RMS | `2.256057 deg` |
| Mercury latitude RMS | `1.306036 deg` |
| Venus RA RMS | `0.727662 deg` |
| Venus declination RMS | `0.263360 deg` |
| Venus separation RMS | `0.749226 deg` |
| Venus longitude RMS | `0.708558 deg` |
| Venus latitude RMS | `0.250802 deg` |

The Mercury report in `00-backup` is not the original baseline: it already contains
an intermediate refinement (`1.931459` degrees separation RMS). The values above
match the original TYCHOS settings restored from `moon-orbital-plane`. Venus matches
its saved original report exactly. Sun also remains unchanged to report precision.

The confirming TYCHOS export hash is
`52de758f24504a6706e70d68373f3f1b097fbff9734f02e7a1e34d35bce65ad1`; the JPL
hash is `87ee271ab04c77bc78a24d34e7200651f07051be33052f5cbcc08eca5021d6b5`.
Its recorded label is `baseline planes for mercury and venus`.

### Author-supplied Sun/Mercury candidate

The active [celestial-settings.json](../src/settings/celestial-settings.json) now
contains a new author-supplied candidate. Relative to the saved equivalence baseline,
it changes the Sun deferent and Sun centre/tilt values, and substantially changes
Mercury deferents A/B, Mercury Plane and Mercury phase/centres. Orbital speeds are
unchanged. The main Mercury values now include:

| Entry | Active candidate values |
|---|---|
| Mercury deferent A | `orbitCentera = 2`, `orbitCenterb = 2`, `orbitCenterc = -0.5`; radius `100` |
| Mercury deferent B | `startPos = 195.5`, radius `0`, `orbitCentera = 1`, `orbitTiltb = -0.1` |
| Mercury Plane | centres `11, 4, 0`; tilts `-4, -3` |
| Mercury | `startPos = 16.7`, centres `-2, -4.9, 0`, `orbitTiltb = 0.5` |

Do not describe this candidate as an improvement until a same-grid J2000 export has
been compared with both JPL and the saved settings. One setting detail also needs
author confirmation: the active Venus object repeats `orbitCenterb = -0.9`,
`orbitTilta = 3.2` and `orbitTiltb = -0.05` even though the explicit Venus Plane
already contains those same values. In this hierarchy those transforms are applied
twice; they are no longer merely an equivalence-preserving relocation. Preserve the
file as received, but distinguish an intentional double transform from an accidental
carry-over before drawing conclusions about Venus.

### Transit-oriented baseline

These are historical values from the saved equivalence baseline, not results from
the active author candidate. Linear interpolation of the common three-hour Sun/planet export to the catalogued
greatest-transit times gives the following planet-to-Sun diagnostics. Relative error
compares the TYCHOS and JPL offsets of the planet from the Sun, so a shared absolute
Sun displacement does not dominate the result.

| Event | JPL Sun separation | TYCHOS Sun separation | Relative offset error |
|---|---:|---:|---:|
| Mercury 2003-05-07 | `11.805 arcmin` | `26.067 arcmin` | `28.151 arcmin` |
| Mercury 2006-11-08 | `7.048 arcmin` | `29.889 arcmin` | `28.447 arcmin` |
| Mercury 2016-05-09 | `5.309 arcmin` | `8.357 arcmin` | `7.301 arcmin` |
| Mercury 2019-11-11 | `1.266 arcmin` | `21.262 arcmin` | `21.594 arcmin` |
| Venus 2004-06-08 | `10.448 arcmin` | `18.437 arcmin` | `10.373 arcmin` |
| Venus 2012-06-06 | `9.240 arcmin` | `13.846 arcmin` | `15.065 arcmin` |

The RMS relative offset is `23.029 arcmin` for the four Mercury transits and
`12.934 arcmin` for the two Venus transits. These values are not yet optimized, but
they are substantially better transit anchors than the removed all-date refinements.
This supports keeping the original geometry as the exploratory plane baseline.

A later solar-equator experiment may constrain both plane normals to a common
orientation and evaluate planet-to-Sun offsets at transit epochs. That would be a new
geometry experiment, not an equivalence-preserving refactor, and should be recorded
as a separate controlled trial.

## Research approach

**Golden rule: never introduce perturbation terms or empirical corrections into
the TYCHOS model or its exported ephemerides.** Improvements must arise from the
compact geometry and its correct implementation. This rule applies regardless of
how much a fitted correction would reduce the numerical error.

Investigate how the hierarchy, translations, plane orientations and coordinate
conversion produce an observable. Sinusoidal fits may be used only in analysis
to characterize residuals; never apply them to the simulator or its exports.
If a residual has no established geometric explanation, retain it as an open
question rather than compensate for it with a perturbation.

Geometric effects may have an interpretation within the TYCHOS framework that is
not obvious from a residual plot or a local code fragment. Consult the
[TYCHOS book, second edition (2024)](<data/docs/TYCHOS book 2nd Edition Final_2024.pdf>)
when investigating claims such as lunar evection. Record the chapter/page and the
quantity being discussed. Distinguish the book's proposed explanation, a code-level
mechanism and a measured numerical result; do not assume they are equivalent.

Keep plane precession, motion within the plane, apsidal motion and Earth-inherited
transformations distinct. Earlier attempts using another ordinary rotating `Pobj`
produced large longitude errors. Nested angular speeds cannot generally be combined
as scalar orbital rates without examining the full transformation chain.

## Historical diagnostics to reproduce

The original plane-branch comparison used 37,985 six-hour samples, 2000-06-21 to
2026-06-21, against geocentric JPL ICRF astrometric coordinates (DE441 in that export).
These approximate figures are context from the earlier analysis, **not a fresh
certification of the current exports**:

| Quantity | Historical result |
|---|---:|
| Declination RMS, before / after plane change | 3.55 / 0.680 degrees |
| Angular separation RMS after plane change | 1.852 degrees |
| Longitude RMS | 1.796 degrees |
| Latitude mean / RMS | -0.396 / 0.466 degrees |
| Longitude RMS after four-period fit, offset and trend | 0.1034 degrees |

The fitted longitude components were approximately:

| Period | Amplitude | Diagnostic label |
|---|---:|---|
| 27.555 days | 2.035 degrees | Anomalistic-month component |
| 31.812 days | 1.274 degrees | Evection-frequency component |
| 14.765 days | 0.658 degrees | Variation-frequency component |
| 365.256 days | 0.185 degrees | Annual component |

These labels identify periodic structure, not its cause. The evection-like signal
is a useful prompt to inspect the proposed geometry and the book for a geometric
explanation. Extending the historical diagnostic fit only reduced RMS from about
0.1034 to 0.1001 degrees. Neither fit is a proposed correction to the model;
the prohibition on perturbation terms is independent of their numerical benefit.

The same fit reported a longitude trend near `3.77e-5 degrees/day`, or
**49.6 arcseconds/year** using 365.25 days/year. This is close to the general
precession in longitude, approximately **50.3 arcseconds/year** (JPL lists
5028.83 arcseconds per century in its [astrodynamic parameters](https://ssd.jpl.nasa.gov/astro_par.html)).
The numerical proximity makes a connection worth investigating, but does not
establish one. Compare the angular quantity, reference frame and sign before
assigning a cause. Do not tune `Moon.speed` merely to cancel this fitted slope.

## Historical multi-body review (before the latest lunar revision)

The earlier combined Moon/Sun/Mars run reproduced the historical lunar metrics above.
All three bodies have 37,985 matching six-hour samples over 2000-2026; input hashes
and coordinates were checked against the raw exports. Angular separation RMS is
1.8520 degrees for the Moon, 0.3414 for the Sun and 0.7334 for Mars.

An additional in-memory diagnostic fitted the Sun's longitude residual with a
365.256363-day sinusoid, constant and linear trend over the full interval. RMS fell
from 0.33878 to 0.00420 degrees, with a slope of 49.20 arcseconds/year, near the
Moon's 49.59 from its four-period fit. This solar fit is not part of the automatic
reports or out-of-sample validation. The similarity motivates a shared-frame or
geometry investigation; it does not identify the cause.

## Dual reference-frame export

The ephemerides UI now offers two explicit output conventions:

- **TYCHOS native (moving PVP):** preserves the historical coordinates expressed in
  Earth's moving local frame.
- **J2000 / ICRF comparison:** keeps the current modeled Earth as the observer origin
  but expresses every direction using Earth's orientation at J2000. This is a change
  of coordinate axes only; the bodies and Earth continue to follow the same TYCHOS
  geometry, including PVP motion.

Export headers and filenames identify the selected frame. The Ephemeris Checker uses
the same convention when evaluating stored rows. The Python comparison workflow
rejects native or legacy unlabelled exports by default, avoiding an accidental mixture
of moving and fixed axes. `--allow-native-frame` permits an explicitly labelled native
export only for a deliberate diagnostic comparison; generated notes carry a frame-
mismatch warning. TYCHOS output remains instantaneous geometric position; light-time
and aberration are still separate observable effects.

The implementation was validated first on the `reference-frame-audit` branch. Over
the 1800-2026 audit, switching from native to the fixed J2000 axes changed angular
separation RMS as follows. These values validate the frame method, not the current
author-supplied Mercury/Sun settings on this branch:

| Body | Native RMS | J2000 RMS |
|---|---:|---:|
| Sun | `1.503522 deg` | `0.287919 deg` |
| Moon | `1.899346 deg` | `1.122084 deg` |
| Mercury | `3.030546 deg` | `2.635184 deg` |
| Venus | `1.926218 deg` | `0.794751 deg` |
| Mars | `1.553249 deg` | `0.810591 deg` |
| Jupiter | `1.938540 deg` | `0.631422 deg` |
| Saturn | `1.142123 deg` | `0.923509 deg` |
| Uranus | `1.425828 deg` | `0.240804 deg` |
| Neptune | `1.806686 deg` | `0.447416 deg` |

The fitted common ecliptic-pole drift fell from `-45.162` to `+5.974`
arcseconds/year, an 86.8% reduction. Pairwise angular separations were unchanged,
as required for a pure coordinate rotation. Pluto worsened in that historical audit
and remains a separate geometric problem rather than evidence against the conversion.

An internal full-PVP-cycle test sampled nine sectors from model year 2000 through
27344. Native-versus-J2000 orientation differences progressed approximately
`0, 45, 90, 135, 180, 135, 90, 45, 0` degrees, while all exported distances and
elongations remained byte-identical across 228,105 rows. This confirms that the new
mode reports the existing model in fixed axes and returns after one PVP cycle; it is
not a fitted correction and does not establish which cosmology is physically correct.

This branch must now repeat the same-grid J2000 comparison with the explicit
Mercury/Venus planes and the new author settings. Do not reuse old report values as
if they measured this candidate.

## Multi-body machine-learning diagnostics (2026-09-21)

The laboratory under [machine_learning/](machine_learning/) now matches the current
three-hour, 2000-2026 ten-body export. The original held-out longitude regression is
retained, and [cross_body.py](machine_learning/cross_body.py) adds:

- body-specific predeclared physical periods;
- longitude, latitude and local east/north residuals;
- ordinary and ridge-regularized harmonic models, selected only on validation
  tangent-plane RMS;
- train-standardized SVD/PCA modes shared across bodies; and
- errors in angular separation for every body pair.

Generated `machine_learning/outputs/` remains ignored by Git. The current complete
run passed nine tests. Its advanced test results show good transfer for the Sun,
Venus, Uranus and Neptune, partial transfer for Mercury, Mars and Jupiter, and no
validated periodic benefit for Saturn (`zero` was selected). Annual eastward phases
vary substantially by body, so the present evidence does not support one universal
Earth correction. Common modes and pairwise errors are diagnostic evidence only;
they do not identify a physical cause or authorize applying fitted residuals.

The ML laboratory still cannot infer simulator parameter changes from a single export.
Specialized deterministic evaluators now exist for the Moon and for Mercury/Venus,
but there is no general hierarchy evaluator or Jacobian covering every body. Keep
geometric parameter screening separate from residual prediction and validate any
proposed geometry on an independent interval.

## Next investigations

1. **Resolve the evection/variation interpretation.** The largest residual terms
   are approximately `1.2705` degrees at 31.811938 days and `0.6574` degrees at
   14.765294 days. Their similarity to standard evection and variation coefficients
   is suggestive but not proof that TYCHOS omits them. The current script fits only
   fixed time periods to `TYCHOS - JPL`; it does not measure the term generated by
   either system. Export matching Sun data and fit TYCHOS and JPL separately against
   the physical arguments `2D-M` and `2D`, reporting amplitude and phase. Distinguish
   the book's geometric explanation, the implemented mechanism and measured output.
2. **Out-of-sample validation.** The accepted Moon parameters were selected with
   repeated inspection of the 2000-2026 interval. Obtain a separate interval, or
   predeclare chronological
   train/validation/test blocks before any more tuning. Preserve the time origin,
   exclude duplicated boundaries and apply chosen parameters unchanged to the held-
   out block. The current gains are strong in-sample evidence, not independent
   confirmation.
3. **Validate the author candidate in fixed axes.** Export Sun, Moon, Mercury, Venus
   and the remaining comparison bodies with `J2000 / ICRF comparison`, using exactly
   the same dates and cadence as JPL. Run the ordinary analysis and the reference-
   frame audit. Compare the result with a second export made from the saved settings;
   do not compare results produced in different output frames.
4. **Plane/centre robustness.** Keep the retained plane values unless a controlled
   one-parameter test improves latitude and declination without degrading longitude.
   The rejected three-parameter author trial is not evidence against each value
   individually. Confirm any candidate on withheld years. Do not reintroduce
   deferent B; it contributes no independent geometry.
5. **Amplitude/phase stability.** Compare shorter windows, particularly the
   nearly eliminated anomalistic component and the 31.8-day component, for stable
   amplitude and phase or slow modulation. Consult the book before assigning a
   TYCHOS interpretation.
6. **Improve spectral diagnostics.** Group neighboring FFT bins representing one
   broad peak rather than treating adjacent bins as independent periods. Extend the
   500-day FFT search only when a longer-period question requires it. These are
   analysis improvements, not model changes.
7. **Resolve the repeated Venus transform.** Confirm whether the author intended the
   same centre and two tilts on both `Venus Plane` and `Venus`. If not, move them to
   one layer only and verify equivalence before evaluating any Venus refinement.
8. **Mercury/Sun targeted validation.** Because the author describes this setting as
   a major Mercury/Sun improvement, evaluate both absolute J2000 errors and the
   Mercury-minus-Sun angular offset at known transit epochs. The relative transit
   diagnostic removes most shared frame error and is therefore the stronger targeted
   test. Retain all-date RMS as a secondary guard against overfitting a few events.

## Where to inspect the implementation

- [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx): node / counter-rotation.
- [celestial-settings.json](../src/settings/celestial-settings.json): retained node,
  lunar parameters, explicit Mercury/Venus planes and the unvalidated author-supplied
  Sun/Mercury candidate; lunar deferent B is intentionally absent.
- [PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) and [Pobj.jsx](../src/components/Pobj.jsx): hierarchy, local axes, offsets and inherited transformations.
- [plotModelFunctions.js](../src/utils/plotModelFunctions.js): model motion and the
  native/J2000 conversion used by export and checking.
- [Ephemerides.jsx](../src/components/Ephemerides/Ephemerides.jsx) and
  [EphemerisChecker.jsx](../src/components/EphemerisChecker/EphemerisChecker.jsx):
  frame selector, frame-labelled output and consistent checker evaluation.
- [analyze_ephemerides.py](scripts/analyze_ephemerides.py): reference rotation, fixed periods and diagnostic fits.
- [analyze_reference_frame.py](scripts/analyze_reference_frame.py): read-only common-
  rotation, transfer and rotation-invariant pairwise audit against JPL ICRF.
- [ephemeris_io.py](scripts/ephemeris_io.py): export-header parsing and frame-safety
  checks used by the analysis workflow.
- [investigate_moon_tuning.py](scripts/investigate_moon_tuning.py): exploratory
  in-memory geometry screening. It reproduces saved exports to about `0.001` degree,
  but its fitted candidates are not accepted settings without simulator export and
  held-out validation.
- [investigate_planet_tuning.py](scripts/investigate_planet_tuning.py): analysis-only
  planetary hierarchy reconstruction, sensitivity screens and chronological transfer
  diagnostics. It does not edit simulator settings.
- [diagnose_solar_satellite_residuals.py](scripts/diagnose_solar_satellite_residuals.py):
  read-only blockwise mean-motion fits, Sun-residual comparison and extended FFT; it
  writes the maintained Markdown/JSON residual-attribution report.

## Working and handoff discipline

Reproduce the baseline, change one geometric element, re-export, then compare all
coordinate metrics and residual structure over the same timestamps. A lower error
in one coordinate can coexist with a worse error in another. Treat the settings
label and input hashes as provenance, not automatic proof of the export settings.

When a trial needs a before/after comparison, optionally preserve the full current
`reports/` directory in `data/pretest/reports/` before overwriting results. Save
the matching inputs and known export settings as described in the
[pre-test backup workflow](README.md#optional-pre-test-backup) when reproducibility
is needed. This manual backup is not updated by the scripts and does not require
a new experiment document or a handoff update for every trial.

Keep only operational scripts, two maintained documents and regenerated outputs.
Before pushing, record the retained parameters, which comparisons support a change,
unresolved interpretations and the next concrete investigation.
Promote a result from generated notes to this handoff only when it changes the
working understanding; do not append a diary entry for each run.
