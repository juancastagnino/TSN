# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Current lunar geometry and settings (2026-09-20)

The model adds an independent lunar node and orbital plane. The `Moon Node`
and `Moon Plane` entries in
[celestial-settings.json](../src/settings/celestial-settings.json) define their
parameters, and [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx)
implements the following transformation at the current zero node/plane offsets,
zero node/plane radii and zero plane starting angle/speed:

```text
Ry(Omega) Rx(i) Ry(-Omega)
i = 5.151 degrees
Moon Node startPos = -25 degrees; speed = -0.33780566 (simulator units)
```

The paired rotations let the plane precess without directly adding node rotation
to lunar longitude. The node speed is approximately `-2*pi/18.6`: a clockwise
18.6-model-year cycle. Do not also put this speed on `Moon deferent B`; that would
add another rotation rather than configure the existing node.

The author's latest settings replace the earlier deferent geometry:

| Entry | Current orbital settings |
|---|---|
| Moon Node | `startPos = -25`, `speed = -0.33780566`; centres, radius and orbital tilts zero |
| Moon Plane | `orbitTilta = 5.151`; centres, radius, `orbitTiltb`, `startPos` and `speed` zero |
| Moon deferent A | `startPos = 141`, `speed = 0.71015440177343`, `orbitRadius = 0.00469117647`, `orbitCentera = -0.001`; other centres and orbital tilts zero |
| Moon deferent B | Identity transformation: centres, radius, starting angle, speed and orbital tilts zero; `size = 0` |
| Moon | `startPos = 345`, `orbitCentera = 0.012`, `orbitCenterb = 0.012`, `orbitCenterc = 0`; unchanged `speed = 83.28521`, `orbitRadius = 0.25505129081458283` |

This is a geometric revision, not just an algebraic merger of the former deferents.
The saved JSON contains numeric strings, sometimes with trailing whitespace;
normalize numerically when comparing settings. It also omits `rotationStart`:
the Moon's former `3.14159` now defaults to zero, affecting its surface orientation
separately from its orbital coordinates.

[PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) places the lunar
deferents and Moon inside this orbital-plane component.
[SolarSystem.jsx](../src/components/SolarSystem.jsx) applies the same plane to
the displayed Moon and the hidden physical Moon used by the coordinate pin.
Its `live` mode follows simulation time without registering in the export/trace
model, so generating ephemerides cannot advance the graphical lunar node.

### Node/plane controls and implementation

`MoonOrbitalPlane.jsx` now applies both entries' centre offsets, radius, orbital
tilts, starting angle and speed. Each stage follows the existing `Cobj` convention:
**centre translation -> orbital tilt -> orbital rotation -> radius translation**;
the inner node counter-rotation remains after the plane stage.

- Node centre offsets are before the node rotation; plane centre offsets inherit
  that rotation. To explore an offset pivoting with the node, use the plane's
  centres with plane speed zero. This experiment has not been applied to the settings.
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
the 18.6-year cycle, both size modes and live/export isolation. The production build
passed with existing MediaPipe source-map warnings. Interactive browser verification
of the new controls remains pending; no new ephemerides were generated for nonzero
node/plane offsets.

### Latest report findings

The 2026-09-20 run uses the same 37,985 timestamps and JPL input as the previous
Moon run in local `00-backup/`. Declination RMS improved `0.6796 -> 0.5266` degrees,
latitude RMS `0.4658 -> 0.2473`, longitude RMS `1.7961 -> 1.7487`, and angular
separation RMS `1.8520 -> 1.7626`. Other bodies' numerical summaries were unchanged
from the preceding committed run. See [moon_summary.json](reports/moon_summary.json).

Most latitude improvement is removal of its mean bias (`-0.3960 -> +0.0034` degrees);
the scatter about the mean is nearly unchanged. The anomalistic-month longitude
amplitude fell `2.0356 -> 1.8545` degrees, but the sidereal-month amplitude rose
`0.0036 -> 0.2293`. Consequently, the four-period fit remainder increased
`0.1034 -> 0.1925` degrees, while the eight-period remainder stayed near `0.1005`.
The four-period fitted drift remains approximately `49.64` arcseconds/year.
These are in-sample diagnostics, not corrections or out-of-sample validation.

An in-memory reconstruction matching current exports within their rounding precision
tested only `Moon deferent A.orbitCentera = 0` instead of `-0.001`. It reduced the
sidereal-month amplitude to about `0.0046` degrees and predicted separation RMS
`1.7530` degrees, with latitude RMS still near `0.247`. **This is a candidate for a
controlled simulator export, not an applied or accepted setting change.** Existing
reports describe the author's configuration before the controls extension; numerical
checks establish equivalence at its zero node/plane offsets, not validation of new
offset geometries.

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

## Next investigations

1. **Improve spectral diagnostics.** Group neighboring FFT bins representing one
   broad peak: the Sun's reported 351.7, 365.2 and 379.9-day values occupy adjacent
   frequency bins and should not be treated as three independent periods. Extend
   the current 500-day search limit when studying longer-period structure in Mars.
   These are analysis improvements, not model changes.
2. **Out-of-sample validation - to do.** Fit the four fixed periods, amplitudes,
   phases, offset and optionally trend on 2000-06-21 through 2013-06-21. Apply the
   coefficients unchanged to later samples through 2026-06-21; exclude the shared
   boundary timestamp and preserve the training time origin and trend center.
   Compare versions with/without trend, and annual validation errors. Since periods
   were examined on the full historical dataset, this tests coefficient transfer,
   not a completely independent discovery of frequencies.
3. **Amplitude/phase stability.** Compare shorter windows, particularly the
   31.8-day component, for stable behavior or longer-period modulation. Consult
   the book before assigning a TYCHOS interpretation.
4. **Lunar centre geometry.** Confirm the isolated deferent-A offset test described
   above with a fresh simulator export. Separately investigate the author's proposed
   node-driven pivot using the now-active node/plane controls. Change one element
   at a time; preserve the latitude improvement and check raw angular separation,
   annual statistics and periodic structure. Do not combine these trials or infer
   that a lower fitted remainder alone improves the model.
5. **Drift and coordinate conventions.** Check whether similar trends appear in
   other bodies and whether frame conventions or longer-period structure can
   explain the fitted slope before changing the mean orbital rate.

## Where to inspect the implementation

- [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx): node / counter-rotation.
- [celestial-settings.json](../src/settings/celestial-settings.json): `Moon Node` and `Moon Plane` definitions and model parameters.
- [PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) and [Pobj.jsx](../src/components/Pobj.jsx): hierarchy, local axes, offsets and inherited transformations.
- [plotModelFunctions.js](../src/utils/plotModelFunctions.js): motion and conversion to exported coordinates.
- [analyze_ephemerides.py](scripts/analyze_ephemerides.py): reference rotation, fixed periods and diagnostic fits.

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
