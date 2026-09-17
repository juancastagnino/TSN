# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Retained baseline

The model adds an independent lunar node and orbital plane. The `Moon Node`
and `Moon Plane` entries in
[celestial-settings.json](../src/settings/celestial-settings.json) define their
parameters, and [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx)
implements the transformation:

```text
Ry(Omega) Rx(i) Ry(-Omega)
i = 5.151 degrees
Moon Node startPos = -26.5 degrees; speed = -0.3378 (simulator units)
```

The paired rotations let the plane precess without directly adding node rotation
to lunar longitude. Existing lunar deferents and orbital speeds are preserved.
[PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) places the lunar
deferents and Moon inside this orbital-plane component.

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

## Multi-body baseline review

The combined Moon/Sun/Mars run reproduces the historical lunar metrics above.
All three bodies have 37,985 matching six-hour samples over 2000-2026; input hashes
and coordinates were checked against the raw exports. Angular separation RMS is
1.8520 degrees for the Moon, 0.3414 for the Sun and 0.7334 for Mars.
The export label still contains the README example text rather than actual settings.

An additional in-memory diagnostic fitted the Sun's longitude residual with a
365.256363-day sinusoid, constant and linear trend over the full interval. RMS fell
from 0.33878 to 0.00420 degrees, with a slope of 49.20 arcseconds/year, near the
Moon's 49.59 from its four-period fit. This solar fit is not part of the automatic
reports or out-of-sample validation. The similarity motivates a shared-frame or
geometry investigation; it does not identify the cause.

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
4. **Latitude bias and remaining longitude structure.** Examine translations and
   orbital geometry one at a time. `Moon.orbitCenterc` is a candidate to revisit,
   not a settled correction. Leave the plane and rates fixed during that test.
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

Keep only operational scripts, two maintained documents and regenerated outputs.
Before pushing, record the retained parameters, which comparisons support a change,
unresolved interpretations and the next concrete investigation.
Promote a result from generated notes to this handoff only when it changes the
working understanding; do not append a diary entry for each run.
