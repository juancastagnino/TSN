# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Working branch and repository scope

The main working branch is **`observer-trace`**. It intentionally contains both:

- the accepted Moon, Mercury and Pluto geometry/settings work described below; and
- the separate Observer Trace feature.

Do not remove Observer Trace changes from this branch when preparing routine work.
If an orbital-only contribution is needed for the upstream TYCHOS repository, make
that separation on a dedicated release branch rather than stripping this working
branch.

Observer Trace has its own menu controls for observer latitude/longitude, marker and
trace visibility, reference/seed markers, PVP-relative coordinates and displacement,
and Earth opacity. During Play, its line is sampled only when the continuously moving
model crosses the exact discrete step dates selected in the main time controls;
month/year sampling follows calendar steps. This avoids recording intermediate render
timestamps as spurious zigzags. Relevant files include
[ObserverTrace.jsx](../src/components/Observer/ObserverTrace.jsx),
[ObserverMarker.jsx](../src/components/Observer/ObserverMarker.jsx),
[ObserverReferenceMarker.jsx](../src/components/Observer/ObserverReferenceMarker.jsx),
[observerStore.js](../src/components/Observer/observerStore.js),
[menuConfigs.js](../src/components/Menus/menuConfigs.js) and
[Planet.jsx](../src/components/Planet.jsx). The Observer tests and production build
passed; the build retained only the pre-existing MediaPipe source-map warnings.

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

## Current Mercury and Pluto settings (2026-09-26)

The accepted Mercury/Pluto candidate was developed from the same 75,969 timestamps
at three-hour cadence, 2000-06-21 through 2026-06-21, against geocentric JPL ICRF
astrometric RA/Dec. Earth, Moon and both planets' orbital speeds remained fixed.
Only existing geometric parameters were changed; no perturbation or fitted residual
term was added.

The retained settings are:

| Entry | Retained changes from the original multi-body baseline |
|---|---|
| Mercury deferent B | `startPos: 33 -> 37`; `orbitRadius: 0.6 -> 0` |
| Mercury | `startPos: -180.8 -> -183`; `orbitCenterb: 3 -> 0.7`; `orbitTilta: 3 -> 6.9` |
| Pluto | `startPos: 200 -> 198`; `orbitCentera: 877 -> 1287.5`; `orbitCenterb: 667 -> 604.5`; `orbitCenterc: -333 -> -495.5`; `orbitTilta: 15 -> 14.75` |

All unlisted Mercury/Pluto parameters retain their previous values. In particular,
`Mercury.speed = 26.08763045` and `Pluto.speed = 0.0253303` were not tuned. Pluto's
mean speed was deliberately held fixed because a short-window speed fit implied an
implausible orbital period and was more likely to conceal a geometry problem.

### Controlled Mercury and Pluto results

The original reports and final reports use identical timestamps and JPL coordinates.
Original reports are preserved in `00-backup/`; the current generated reports are in
`edits/reports/`. The measured comparison is:

| Body / metric | Original | Current | Relative change |
|---|---:|---:|---:|
| Mercury RA RMS | 2.279213 deg | 1.788433 deg | -21.5% |
| Mercury declination RMS | 1.439953 deg | 0.889728 deg | -38.2% |
| Mercury separation RMS | 2.605186 deg | 1.931459 deg | -25.9% |
| Mercury longitude RMS | 2.256057 deg | 1.835098 deg | -18.7% |
| Mercury latitude RMS | 1.306036 deg | 0.608923 deg | -53.4% |
| Pluto RA RMS | 4.646249 deg | 0.547823 deg | -88.2% |
| Pluto declination RMS | 2.740124 deg | 0.246666 deg | -91.0% |
| Pluto separation RMS | 5.141106 deg | 0.568651 deg | -88.9% |
| Pluto longitude RMS | 4.027498 deg | 0.505200 deg | -87.5% |
| Pluto latitude RMS | 3.203408 deg | 0.265224 deg | -91.7% |

Pluto should be treated as ready and frozen pending an independent interval. Mercury
also improved materially, but its dominant longitude residual remains near 49.98 days
with an FFT amplitude of about `2.1360` degrees. That component barely responded to
the tested phase, centre, inclination and deferent-radius changes. Further blind
Mercury tuning is not recommended; identify which geometric mechanism could generate
that period before changing more settings.

[investigate_planet_tuning.py](scripts/investigate_planet_tuning.py) reconstructs the
Mercury and Pluto export hierarchy in memory and matches saved simulator exports to
about `0.0012` degrees before a settings change. It performs geometry-only sensitivity
screens and never writes `celestial-settings.json`. The script used pre-2020 and
2020-2026 chronological blocks to reject candidates that transferred poorly. Because
both blocks were inspected repeatedly during iteration, the latter is a robustness
diagnostic, **not** untouched out-of-sample validation. Test the retained configuration
unchanged on a genuinely independent interval before calling it final externally.

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

## Earth-frame audit: JPL compatibility remains unresolved

The current TYCHOS export is **not established to use the same frame as the JPL
ICRF reference**. Its residuals may include differences in coordinate conventions;
do not interpret them purely as orbital errors or declare the TYCHOS frame wrong.

In [plotModelFunctions.js](../src/utils/plotModelFunctions.js), `worldToLocal`
expresses target positions in Earth's `cSphereRef` at each sample date.
[Pobj.jsx](../src/components/Pobj.jsx) puts `tilt` and `tiltb` on that frame, while
child orbits sit outside the tilted group. The shared Earth orbital transform
cancels in local planetary coordinates. In contrast, `Stars.jsx` and `BSCStars.jsx`
anchor catalog orientation at J2000. Checks against Three.js found consistent
cardinal axes and origin subtraction; this does not establish celestial alignment.

`Earth.speed = -2*pi/25344` exactly encodes the book's PVP period and 51.13636
arcseconds per model year (365.2425 days). The online book's
[Chapter 11, section 11.4](https://book.tychos.space/chapters/11-earths-pvp-orbit),
[Chapter 12, section 12.1](https://book.tychos.space/chapters/12-sun-earth-rel-motion)
and [Chapter 19, sections 19.1-19.3](https://book.tychos.space/chapters/19-the-tychos-great-year)
provide the proposed distinction between equinoctial and stellar directions.
This may explain the intended frame convention; the book's physical explanation
and its implementation still need to be distinguished. Translation along PVP and
rotation of coordinate axes are separate operations.

An exploratory re-expression of the 2000-2026 baseline (`Earth.tiltb = 0.26`)
using Earth's J2000 orientation changed fitted Sun/Moon longitude trends from
+49.20/+49.59 to -1.94/-1.55 arcseconds per Julian year. Lunar separation RMS
nevertheless increased from 1.852 to 1.887 degrees. This shows sensitivity to the
frame, not a validated TYCHOS-to-ICRF conversion. That diagnostic is not part of
the reporting workflow; retain these figures only as exploratory context.

**Suggested TYCHOS work, pending verification:**

1. Define the exported axes with the authors: origin, pole, zero-RA direction,
   epoch, time scale and their evolution relative to the star catalog. Do not
   assume the current axes equal a standard astronomical equator/equinox of date.
2. Test known directions at J2000 and later dates, separating observer translation
   from orientation. A pure change of axes must preserve distances and pairwise
   angular separations. If fixed celestial axes are intended, prototype an explicit
   export convention using the established alignment, leaving orbital motions intact.
3. Compare equivalent observables. TYCHOS currently exports instantaneous geometric
   positions; JPL quantity 1 includes light-time. For a geometry audit, obtain JPL
   geocentric geometric vectors in the agreed frame. Selecting JPL apparent RA/Dec
   alone does not resolve this mismatch; see the
   [Horizons definitions](https://ssd.jpl.nasa.gov/horizons/manual.html#general-definitions).
4. Preserve numeric precision before formatting: `radToRa` rounds to a second of
   time (15 angular arcseconds), and `radToDec` to one arcsecond. Normalize any
   seconds-to-minutes carry. These export refinements require no perturbations.

Do not tune planetary speeds, remove PVP motion or apply a fitted drift correction
to force agreement. Establish the coordinate contract before changing the model.

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
Specialized deterministic evaluators now exist for the Moon and for Mercury/Pluto,
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
2. **Out-of-sample validation.** The accepted Moon, Mercury and Pluto parameters were
   selected with repeated inspection of the 2000-2026 interval. Obtain a separate
   interval, or predeclare chronological
   train/validation/test blocks before any more tuning. Preserve the time origin,
   exclude duplicated boundaries and apply chosen parameters unchanged to the held-
   out block. The current gains are strong in-sample evidence, not independent
   confirmation.
3. **Long-term drift and coordinate conventions.** The current lunar longitude fit
   still yields about 46-47 arcseconds/year and the early decades raise longitude
   RMS while latitude/declination remain comparatively stable. Establish the export
   axes and compare equivalent geometric observables before altering `Moon.speed`.
   Restore a matched multi-body export if testing whether the same drift remains in
   the Sun and other bodies.
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
7. **Mercury's 49.98-day residual.** Preserve the retained Mercury settings while
   investigating which nested geometric motion can generate this period. Its amplitude
   remained near `2.136` degrees while other Mercury metrics improved, so more blind
   changes to centres, phase or inclination are unlikely to remove it.

## Where to inspect the implementation

- [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx): node / counter-rotation.
- [celestial-settings.json](../src/settings/celestial-settings.json): retained node,
  plane, deferent-A and Moon parameters; deferent B is intentionally absent.
- [PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) and [Pobj.jsx](../src/components/Pobj.jsx): hierarchy, local axes, offsets and inherited transformations.
- [plotModelFunctions.js](../src/utils/plotModelFunctions.js): motion and conversion to exported coordinates.
- [analyze_ephemerides.py](scripts/analyze_ephemerides.py): reference rotation, fixed periods and diagnostic fits.
- [investigate_moon_tuning.py](scripts/investigate_moon_tuning.py): exploratory
  in-memory geometry screening. It reproduces saved exports to about `0.001` degree,
  but its fitted candidates are not accepted settings without simulator export and
  held-out validation.
- [investigate_planet_tuning.py](scripts/investigate_planet_tuning.py): analysis-only
  Mercury/Pluto hierarchy reconstruction, sensitivity screens and chronological
  transfer diagnostics. It does not edit simulator settings.

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
