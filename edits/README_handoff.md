# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Current lunar geometry and settings (2026-09-20)

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

The author's retained settings are:

| Entry | Current orbital settings |
|---|---|
| Moon Node | `startPos = -296`, `speed = -0.33780566`; centres, radius and orbital tilts zero |
| Moon Plane | `orbitCentera = 0.001`, `orbitCenterb = 0.002`, `orbitCenterc = 0`, `orbitTilta = 0`, `orbitTiltb = -5.15`; radius, `startPos` and `speed` zero |
| Moon deferent A | `startPos = 177`, `speed = 0.71015440177343`, `orbitRadius = 0.0266`; centres and orbital tilts zero |
| Moon | `startPos = 309`, `speed = 83.2851946`, `orbitRadius = 0.25505129081458283`; centres and orbital tilts zero |

The author independently converged on a deferent-A radius near `0.027`; the retained
value is `0.0266`. Numerical screening had separately identified approximately
`0.0270` as the strongest single-parameter candidate, but the current export also
changes plane offsets/orientation and lunar phases. Reported improvement therefore
belongs to the complete retained configuration, not to the radius alone.

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

The maintained run is Moon-only: 87,661 samples at six-hour cadence from
1966-06-21 through 2026-06-21 against geocentric JPL DE441 ICRF astrometric RA/Dec.
The current configuration is declared and embedded in
[moon_summary.json](reports/moon_summary.json); the TYCHOS text export itself does
not encode settings, so this provenance still depends on the user's declaration.
The current full-interval results are:

| Metric | 1966-2026 result |
|---|---:|
| RA coordinate RMS | 1.5248 degrees |
| Declination RMS | 0.4151 degrees |
| Angular separation RMS | 1.5126 degrees |
| Ecliptic longitude RMS | 1.4971 degrees |
| Ecliptic latitude RMS | 0.2359 degrees |

Only current Moon reports are retained. Deleted reports for other bodies were from a
different input bundle and must not be presented as current. Regenerate them with
matching TYCHOS and JPL inputs if a multi-body comparison is needed.

### Controlled improvement over the preceding lunar configuration

The local backup run covers only 2000-06-21 through 2026-06-21, so its headline
metrics must not be compared directly with the new 60-year headline metrics. A
controlled calculation over the 37,985 overlapping timestamps gives:

| Metric | Previous | Current | Relative change |
|---|---:|---:|---:|
| RA coordinate RMS | 1.4765 | 1.4109 | -4.4% |
| Declination RMS | 0.5425 | 0.4172 | -23.1% |
| Angular separation RMS | 1.5076 | 1.4072 | -6.7% |
| Ecliptic longitude RMS | 1.4801 | 1.3908 | -6.0% |
| Ecliptic latitude RMS | 0.3012 | 0.2314 | -23.2% |

Maximum separation also fell from `4.1366` to `3.3408` degrees. Across the 26
complete calendar years 2001-2026, declination improved in 24, latitude in 18,
separation in 17 and longitude in 16. This supports a real geometric improvement,
especially in lunar-plane accuracy, rather than a benefit confined to a few dates.

The anomalistic-month diagnostic amplitude fell from `1.3654` to `0.9947` degrees;
the sidereal-month amplitude fell from `0.1333` to `0.1142`. The four-period
remainder improved from `0.4332` to `0.3819` degrees and the full eight-period
remainder from `0.4218` to `0.3721`. Variation, evection and annual amplitudes are
nearly unchanged. These are in-sample residual fingerprints, not correction terms
or proof of a physical cause.

The main tradeoff is longitude zero-point alignment. Over the common interval the
mean longitude residual changed from `+0.1153` to `-0.4914` degrees and mean RA from
`+0.0520` to `-0.5452`. A future controlled phase test may recover part of that bias,
but it must preserve the latitude/declination gains. The current 60-year fit also
retains a longitude trend near 46-47 arcseconds/year; do not tune `Moon.speed` to
cancel it before the coordinate-frame question is resolved.

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

The laboratory still cannot infer simulator parameter changes from a single export.
That requires a general geometric evaluator and controlled finite differences or a
Jacobian across settings, extending the lunar screening approach. Keep that separate
from residual prediction and validate any proposed geometry on withheld years.

## Next investigations

1. **Phase/zero-point trial.** The retained geometry has better scatter but a mean
   2000-2026 longitude residual of `-0.4914` degrees. Change only one phase at a
   time, beginning with small `Moon.startPos` trials around `309.3-309.5` while
   holding radius, plane and speeds fixed. Then test deferent-A `startPos` only if
   needed. Judge raw separation, longitude bias, latitude/declination and annual
   stability together; do not accept a phase merely because it centres longitude.
2. **Out-of-sample validation.** The 1966-2026 export permits genuinely separated
   windows. Choose and record a training cutoff before fitting amplitudes, phases,
   offset or trend, then apply coefficients unchanged after the cutoff. Preserve the
   training time origin and trend centre, exclude a duplicated boundary timestamp,
   and compare variants with and without trend. Fixed periods were historically
   selected using other full-range data, so coefficient transfer is the claim being
   tested, not independent frequency discovery.
3. **Long-term drift and coordinate conventions.** The current lunar longitude fit
   still yields about 46-47 arcseconds/year and the early decades raise longitude
   RMS while latitude/declination remain comparatively stable. Establish the export
   axes and compare equivalent geometric observables before altering `Moon.speed`.
   Restore a matched multi-body export if testing whether the same drift remains in
   the Sun and other bodies.
4. **Plane/centre robustness.** Around the retained values, vary one of
   `Moon Plane.orbitCentera`, `orbitCenterb`, `orbitTiltb` or node `startPos` at a
   time. Confirm that the large latitude/declination gain transfers to withheld
   years. Do not reintroduce deferent B; it contributes no independent geometry.
5. **Amplitude/phase stability.** Compare shorter windows, particularly the
   anomalistic and 31.8-day components, for stable amplitude and phase or slow
   modulation. Consult the book before assigning a TYCHOS interpretation.
6. **Improve spectral diagnostics.** Group neighboring FFT bins representing one
   broad peak rather than treating adjacent bins as independent periods. Extend the
   500-day FFT search only when a longer-period question requires it. These are
   analysis improvements, not model changes.

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
