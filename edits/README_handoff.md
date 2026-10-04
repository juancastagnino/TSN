# Developer / AI handoff

Read [README.md](README.md) to run an analysis. This document retains development
context and priorities, not the output of every trial. Update it when the accepted
baseline, a supported conclusion or the next priorities change; review it before
pushing changes to the branch. Generated reports are the evidence for individual runs.

## Branch scope

This handoff describes the **`binary-tychos`** branch, created from `development`.
It retains the accepted Moon Node/Plane baseline and explicit separate fixed planes
for Mercury and Venus. Mercury and Venus otherwise reproduce the original TYCHOS
geometry, and Pluto uses its original TYCHOS settings.

The branch develops a coordinate-preserving primary/companion architecture. Mars is
now an explicit asymmetric companion of the Sun, and Phase 4 moves the solar moons
into the same structural interpretation. Venus has passed its full simulator-export
equivalence gate, and Mercury has now passed the equivalent Phase 4C gate. No new
binary orbit, barycentric constraint or fitted parameter has been introduced.

This branch intentionally excludes Observer Trace. It also does not add moving
Mercury or Venus node objects: the current evidence supports separate fixed planes,
but does not yet establish measurable nodal precession for either solar satellite.

## Sun-Mars primary-companion architecture: phases 1 through 4C

The visual model and the hidden export/trace model now share
[`SunMarsBinarySystem.jsx`](../src/components/SunMarsBinarySystem.jsx). This removes
the formerly duplicated Sun, Mercury, Venus and Mars hierarchy from
[`SolarSystem.jsx`](../src/components/SolarSystem.jsx) and
[`PlotSolarSystem.jsx`](../src/components/PlotSolarSystem.jsx), reducing the risk
that later binary experiments alter only one of the two models.

The semantic hierarchy is now:

```text
Earth
└─ Sun-Mars Binary Frame                 (identity; no transform)
   ├─ Sun Primary Branch                 (identity)
   │  └─ existing Sun deferent / Sun chain
   │     ├─ existing outer-planet and Halley chains
   │     ├─ Sun-Relative Mars Frame
   │        └─ named centre / carrier / harmonic / main-basis stages
   │           └─ Mars Junior Companion Branch
   │              └─ Mars
   │                 ├─ Phobos
   │                 └─ Deimos
   │     ├─ Sun-Relative Venus Frame
   │        └─ named centre / carrier / B / plane / main-basis stages
   │           └─ Venus Senior Solar Companion Branch
   │              └─ Venus
   │     └─ Sun-Relative Mercury Frame
   │        └─ named centre / carrier / B / plane / main-basis stages
   │           └─ Mercury Junior Solar Companion Branch
   │              └─ Mercury
```

No celestial setting changes were needed for this hierarchy. Venus now uses an
exact expansion of its established compensating deferent chain beneath the moving
Sun object; Mercury now has the parallel Phase 4C candidate. The outer planets
remain under the Sun exactly as before. The Mars, Venus and Mercury stages are
active calculated transforms, not decorative identity labels. Mars has passed its
complete Phase 3E export gate, Venus has passed its Phase 4B gate, and Mercury is
accepted through its Phase 4C gate.

Phase 2 adds an explicit, shared binary state without changing the geometry. Its
initial reference centre is the moving Earth pivot already inherited by both legacy
chains; it is deliberately labelled `legacy-earth-pivot`, not asserted to be the
physical binary barycentre. At every live frame,
[`SunMarsBinaryTracker.jsx`](../src/components/SunMarsBinaryTracker.jsx)
re-expresses the current positions exactly as:

```text
Sun position  = common centre + Sun companion vector
Mars position = common centre + Mars companion vector
```

The state also records both centre radii, Sun-Mars separation, their radius ratio,
the angle between the companion vectors and its departure from exact opposition.
These are measurements of the current TYCHOS construction, not constraints. No
mass ratio, barycentric weighting, forced opposition or fitted orbit has been added.

The live state is exposed through `useStore().sunMarsBinaryStateRef`, using a
mutable ref so animation does not trigger React rerenders. The hidden ephemeris
model computes the identical decomposition through `getPlotSunMarsBinaryState` in
[`plotModelFunctions.js`](../src/utils/plotModelFunctions.js); `movePlotModel`
returns that state for callers that need it. Both paths share the pure vector logic
in [`sunMarsBinaryState.js`](../src/utils/sunMarsBinaryState.js).

Phase 2.5 adds a read-only diagnostic export to the existing Ephemerides panel.
Selecting **Sun-Mars binary CSV** samples three common-centre descriptions on the
same date range and cadence as the ordinary exporter:

1. the existing moving Earth pivot inherited by both transform chains;
2. the existing PVP/SystemCenter origin; and
3. the instantaneous geometric midpoint of Sun and Mars.

The separate CSV records world positions, both centre-relative vectors, their
radii and ratio, Sun-Mars separation, opposition angle and opposition error. It
does not alter the normal planetary TXT or any model transform. The midpoint is a
control only: equal radii and exact opposition follow from its definition, so they
cannot establish a physical barycentre. Use
[`analyze_sun_mars_binary.py`](scripts/analyze_sun_mars_binary.py) to generate the
maintained summary at `reports/sun_mars_binary_report.md` after an export.

Phase 3A screened fixed-ratio centres on the instantaneous Sun-Mars line using
9,497 daily samples from 2000-06-21 through 2026-06-21. For
`k = Mars radius / Sun radius`, each candidate was defined as
`C = (k*Sun + Mars)/(1+k)`. This construction guarantees constant ratio and exact
opposition, so only the resulting centre path relative to PVP was evaluated.

The screen found no preferred finite interior ratio. Both analytic objectives
(minimum RMS distance from PVP and minimum centre motion) collapsed to
`k -> infinity`, meaning the Sun endpoint. The finite-grid PVP-radius and
best-circle criteria also improved continuously toward the upper tested boundary
(`k = 20`). Representative best-circle residuals were `40.832%` at `k = 1`,
`31.638%` at `k = 2`, `17.442%` at `k = 5`, `9.750%` at `k = 10`, and `5.149%`
at `k = 20`; the Sun endpoint was `0.054%`.

The spectral decomposition explains the trend: finite interior centres combine a
strong annual Sun component with a roughly 678-day Mars component. As `k` grows,
the Mars component vanishes and the path becomes the existing nearly circular Sun
path. This is a useful negative result. The current exported geometry can always be
re-expressed around an arbitrary weighted centre, but compactness does not identify
an interior binary centre. Do not impose a ratio from this screen. See
`reports/sun_mars_phase3a_report.md` and
[`analyze_sun_mars_phase3a.py`](scripts/analyze_sun_mars_phase3a.py).

Phase 3B therefore tested the asymmetric interpretation directly, using
`Mars_world - Sun_world` rather than inventing another centre. Over the same 9,497
daily samples, the existing Mars-from-Sun path is strongly planar and is described
well by a focus-at-Sun ellipse:

| Relative-orbit diagnostic | Result |
|---|---:|
| Mean Sun-Mars distance | `154.055725` model units |
| Minimum / maximum distance | `138.664462 / 166.928431` |
| Maximum/minimum ratio | `1.203830 : 1` |
| Earth-Mars minimum / maximum distance | `37.222075 / 268.336972` |
| Earth-Mars maximum/minimum ratio | `7.209082 : 1` |
| Focus-ellipse eccentricity | `0.092325` |
| Focus-ellipse radial residual | `0.459675` units (`0.298%`) |
| Fixed-plane inclination to model XZ | `1.650977 deg` |
| Out-of-plane RMS | `0.686108` units (`0.445%`) |
| Mean angular-sweep period | `687.020633 days` |
| Recurrence error at that period | `0.163%` of mean radius |

This supports representing Mars as an asymmetric junior companion moving relative
to the Sun. It does not support a comparable-radius interior barycentre. The
author's approximate `7:1` statement concerns maximum versus minimum Earth-Mars
distance, not the Sun-relative ellipse; the measured TYCHOS ratio is `7.209082:1`
over this interval. This agreement is a geometric property to explain, but by
itself does not distinguish TYCHOS from another model that reproduces the same
Earth-Mars distances.

The identity groups are now named `Sun Primary Branch` and
`Mars Junior Companion Branch`. A separate read-only live state is exposed as
`useStore().sunMarsPrimaryCompanionStateRef`, and the hidden plot model provides
`getPlotSunMarsPrimaryCompanionState`. Both preserve the exact identity
`Mars_world = Sun_world + companionFromPrimary`; neither changes a transform.
See `reports/sun_mars_asymmetric_report.md`, the derived
`data/derived/sun_mars_relative.csv`, and
[`analyze_sun_mars_asymmetric.py`](scripts/analyze_sun_mars_asymmetric.py).

Phase 3C makes the semantic relationship structural while preserving the old
coordinates. `Mars Junior Companion Branch` is now a descendant of the Sun object.
[`SunPrimaryFrameAdapter.jsx`](../src/components/SunPrimaryFrameAdapter.jsx)
cancels the transform inherited between the common Sun-Mars frame and the Sun pivot:

```text
adapter local matrix = inverse(Sun-parent world matrix) * binary-frame world matrix
```

Consequently, the adapter's world frame equals the original binary frame and the
unchanged Mars deferent chain should produce its former world position exactly.
The live model updates this matrix each frame. The hidden plot/export model registers
the same adapter and updates it after every set of sampled orbital rotations. This
is an equivalence-preserving bridge, not yet a simplified Sun-relative Mars orbit.
Component tests verify arbitrary translated/rotated ancestors to numerical precision;
a fresh full simulator export subsequently confirmed end-to-end equivalence. Across
75,969 three-hour samples from 2000-06-21 through 2026-06-21, all reported metrics
for Moon, Sun, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune and Pluto were
numerically identical to Phase 2. The JSON differences were restricted to provenance
(analysis time, export hash and label). The separately regenerated Phase 2.5 binary
CSV was byte-for-byte identical with SHA-256
`5b42c843b7c3c5775106e4055a53adb91082e65c7b38c6f00043baa4a0886861`.
Phase 3C is therefore accepted as coordinate preserving at exported precision.

Phase 3D expands the accepted settings into an explicit algebraic identity rather
than fitting another orbit. In the Earth/PVP-carried model frame, the exact
Sun-relative vector is:

```text
Mars - Sun = centre difference
           + annual carrier mismatch
           + Mars deferent-S vector
           + main Mars vector
```

The Sun and `Mars deferent E` annual carriers have the same radius (`100`), speed
(`2*pi` per model year) and starting phase. They therefore cancel by `99.659145%`
RMS; the small remainder (`0.340855` units RMS) is principally due to the Sun's
`0.2762 deg` orbital tilt. What remains is dominated by a radius-`152.677` vector
whose nested local rate is
`2*pi + 0.3974599 - 3.33985 = 3.340795207 rad/year`, giving a nominal
`686.928161`-day period. The shared Earth/PVP frame rate changes its world-space
nominal period slightly to `686.979141` days. This is consistent with the directly
measured mean angular-sweep period of `687.020633` days; the latter also includes
the smaller components and nonuniform angular motion.

The radius-`7.44385` deferent-S vector runs at `6.680645207 rad/year`, or
`1.999717071` times the main local frequency. This supplies the near-second
harmonic expected in the first-order Fourier form of a focus-centred ellipse.
That form predicts `e ~= 2*7.44385/152.677 = 0.097511`, close to the independently
fitted `0.092325`. Its expected constant term is `3*7.44385 = 22.33155` units;
the configured centre-difference magnitude is `21.176473` units. The match is not
exact because orientations, small tilts, the residual annual carrier and a
`-0.000945207 rad/year` harmonic detuning remain in the full construction.

The reconstruction matches the exported world-space Sun-Mars vectors to about
`1e-12` RMS after applying the shared `SystemCenter -> Earth` orientation. This
last step is essential: common translations disappear when two positions are
subtracted, but a common rotation still rotates their relative vector. Omitting
only the annual carrier mismatch changes the export by `0.340855` units RMS
(`0.221254%` of mean Sun-Mars distance); retaining only the main vector loses
`14.528194%`. Therefore Phase 3E may name and re-express all four components, but
must not silently discard the centre or annual remainder. See
`reports/sun_mars_phase3d_report.md`,
`data/derived/sun_mars_phase3d_components.csv`, and
[`analyze_sun_mars_phase3d.py`](scripts/analyze_sun_mars_phase3d.py).

Phase 3E now makes that decomposition the active scene/export hierarchy. The old
`Mars deferent E -> Mars deferent S` object nesting has been removed from
`SunMarsBinarySystem`; their retained settings instead drive explicit named stages:

```text
Sun
└─ Sun-Relative Mars Frame
   └─ Sun-Mars Centre Difference
      └─ Sun-Mars Annual Carrier Mismatch
         └─ Mars Deferent-S Harmonic
            └─ Mars Main-Orbit Basis
               └─ Mars
                  ├─ Phobos
                  └─ Deimos
```

[`SunMarsRelativeOrbit.jsx`](../src/components/SunMarsRelativeOrbit.jsx) places the
root at the Sun while retaining the common binary-frame axes. It evaluates the
centre, annual and harmonic vectors directly from the existing settings, composes
the former E/S rotations into `Mars Main-Orbit Basis`, and lets the unchanged Mars
leaf supply its own centre, tilt, phase and radius. This preserves the final Mars
orientation inherited by Phobos and Deimos. The same updater is used by live and
hidden plot models; `movePlotModel` now passes the exact sampled position to
post-motion coordinate updaters.

Six test suites (`23` tests) pass. Component tests compare the new construction
with an independent Three.js reconstruction of the legacy hierarchy at five model
epochs to below `1e-10`, and the production build passes with only the pre-existing
MediaPipe source-map warnings.

The fresh full simulator gate has now passed, so Phase 3E is **accepted as
coordinate preserving**. Against the saved Phase 3C baseline:

- all scientific summary fields for Moon, Sun, Mercury, Venus, Mars, Jupiter,
  Saturn, Uranus, Neptune and Pluto have zero numerical difference;
- all 31 per-sample residual, annual-statistics and FFT/periodic CSV artifacts are
  byte-identical;
- all 9,497 binary-CSV timestamps match;
- the maximum Mars world-coordinate difference is about `1.85e-13` model units;
  and
- separation/radius differences remain at approximately `2.27e-13` or below.

The only visibly larger delta is `1.21e-6 deg` in the constructed midpoint's
opposition angle. That midpoint is defined from the Sun/Mars endpoints and is
therefore exactly opposed by construction; the delta is the expected sensitivity
of `acos` at 180 degrees, not a positional difference. See
`reports/phase3e_equivalence_report.md` and
[`compare_phase_equivalence.py`](scripts/compare_phase_equivalence.py).

### Phase 4A: solar-companion decomposition

Phase 4A has completed the equivalence-preserving solar-host audit for Mercury and
Venus. It makes no scene or settings change. The current absolute hierarchy for
each planet was independently reconstructed and its planet-minus-Sun vector was
expanded exactly as:

```text
planet - Sun = fixed centre difference
             + annual carrier mismatch
             + deferent-B stage
             + fixed-plane stage
             + main planet stage
```

Across 75,969 three-hour samples from 2000-06-21 through 2026-06-21, both expanded
vectors reproduce their full transform chains to machine precision: maximum vector
differences are about `5.75e-14` units for Mercury and `7.19e-14` for Venus. Their
independently reconstructed absolute directions match the formatted simulator
exports at `0.001159 deg` and `0.001154 deg` RMS respectively.

The annual radius-100 planet/Sun carriers cancel by `99.659129%`, leaving a
`0.340871`-unit RMS vector in both cases. That remainder must be retained. The
configured A and B scalar speeds sum exactly to zero, but their complete rotation
matrices do not: intervening tilts leave orbit-normal RMS variations of
`0.099831 deg` for Mercury and `0.049956 deg` for Venus. This confirms that a
scalar speed cancellation is not a lossless replacement for the existing chain.

Mercury deferent B is also not disposable merely because its radius is zero. Its
one-unit centre and tilted orientation affect all descendants; omitting the whole
stage would change the Sun-relative direction by `1.086348 deg` RMS. Venus deferent
B has a non-zero `0.6` radius and supplies both translation and orientation. The
two planets retain distinct orbit normals and must keep separate plane objects.

See `reports/solar_companion_phase4a_report.md` and
[`analyze_solar_companion_phase4a.py`](scripts/analyze_solar_companion_phase4a.py).

### Phase 4B: accepted Venus implementation

Venus has now been reparented structurally beneath the Sun. The legacy scene nesting
`Venus deferent A -> Venus deferent B -> Venus Plane -> Venus` was replaced by:

```text
Sun
└─ Sun-Relative Venus Frame
   └─ Sun-Venus Centre Difference
      └─ Sun-Venus Annual Carrier Mismatch
         └─ Venus Deferent-B Stage
            └─ Venus Fixed-Plane Stage
               └─ Venus Main-Orbit Basis
                  └─ Venus Senior Solar Companion Branch
                     └─ Venus
```

[`VenusSunRelativeOrbit.jsx`](../src/components/VenusSunRelativeOrbit.jsx) evaluates
the exact five-term Phase 4A identity from the current settings. The unchanged Venus
leaf supplies its own centre, tilt, phase and radius beneath the reconstructed main
basis. Both the visual model and hidden export model use this shared component.
Mercury and all celestial settings remain untouched.

The component reconstructs the independent legacy chain below `1e-10` model units
at selected epochs and across a dense 200-model-year grid. The full test suite now
passes (`31` tests), and the production build succeeds with only the pre-existing
MediaPipe source-map warnings.

The fresh full simulator gate has passed, so Phase 4B Venus is **accepted as
coordinate preserving**. Against the immediate saved Phase 4A baseline:

- all scientific summary fields for Moon, Sun, Mercury, Venus, Mars, Jupiter,
  Saturn, Uranus, Neptune and Pluto have zero numerical difference;
- all 31 per-sample residual, annual-statistics and FFT/periodic artifacts are
  byte-identical; and
- all 9,497 Sun-Mars binary timestamps and numeric fields are exactly identical.

The report is `reports/phase4b_venus_equivalence_report.md`. The comparison tool
now defaults to the complete `00-backup/phase4a` baseline and explicitly fails when
no summary JSON or numeric artifacts are present, preventing an empty baseline from
producing a false pass.

The separate Mercury step described above is now implemented as the Phase 4C
candidate below; it still requires its own export gate and remains isolated from
parameter tuning.

### Phase 4C: accepted Mercury implementation

Mercury has now been reparented structurally beneath the Sun using the same exact
five-term method, without changing the accepted Venus component or any celestial
setting:

```text
Sun
└─ Sun-Relative Mercury Frame
   └─ Sun-Mercury Centre Difference
      └─ Sun-Mercury Annual Carrier Mismatch
         └─ Mercury Deferent-B Stage
            └─ Mercury Fixed-Plane Stage
               └─ Mercury Main-Orbit Basis
                  └─ Mercury Junior Solar Companion Branch
                     └─ Mercury
```

[`MercurySunRelativeOrbit.jsx`](../src/components/MercurySunRelativeOrbit.jsx)
retains every Phase 4A term in its original matrix order. In particular, Mercury
deferent B remains active even though its orbital radius is zero: its non-zero
centre and orientation are explicitly reconstructed before the plane and main
orbit basis.

Independent component tests reproduce the legacy Mercury-from-Sun vector below
`1e-10` model units at selected epochs and over a dense 200-model-year grid. The
accepted Venus construction is unchanged. The complete Phase 4B reports and binary
CSV have been preserved under `00-backup/phase4b` as the immediate baseline.

The complete source test suite passes (`39` tests across `8` suites), and the
production build succeeds with only the pre-existing MediaPipe source-map warnings.

The fresh full simulator gate has passed, so Phase 4C Mercury is **accepted as
coordinate preserving**. Against the immediate saved Phase 4B baseline:

- all scientific summary fields for Moon, Sun, Mercury, Venus, Mars, Jupiter,
  Saturn, Uranus, Neptune and Pluto have zero numerical difference;
- all 31 per-sample residual, annual-statistics and FFT/periodic artifacts are
  byte-identical; and
- all 9,497 Sun-Mars binary timestamps and numeric fields are exactly identical.

The accepted report is `reports/phase4c_mercury_equivalence_report.md`. Mercury and
Venus are now both true structural descendants of the Sun while retaining the exact
ephemerides generated by their former carrier hierarchies. Their separate fixed
planes and all current settings remain intact.

### Phase 4D/4E: accepted Eros Sun-relative implementation

Phase 4D has completed the exact audit of the former Earth-level Eros chain. The
saved pre-change export contains 75,969 Eros rows at three-hour cadence from
2000-06-21 through 2026-06-21. The identity is:

```text
Eros - Sun = fixed centre difference
           + annual carrier mismatch
           + Eros deferent-B stage
           + main Eros stage
```

The component sum reproduces the legacy hierarchy with an algebraic RMS of
`2.654e-14` model units and maximum error of `8.988e-14`. Its direction agrees with
the formatted pre-change export to `0.001139 deg` RMS and `0.002087 deg` maximum.
The annual radius-100 carriers cancel by `89.654%`, not completely, because their
tilted planes differ. That `10.345532`-unit remainder is therefore real model
geometry and is retained. The configured Eros basis has a fixed normal, so no
additional Eros plane object is necessary. Full details are in
`reports/eros_phase4d_report.md`.

Phase 4E now places an exact `ErosSunRelativeOrbit` below the Sun and removes the
legacy Earth-level Eros A/B scene chain. It retains all four terms in matrix order
and leaves the Eros leaf and all celestial settings unchanged:

```text
Sun
└─ Sun-Relative Eros Frame
   └─ Sun-Eros Centre Difference
      └─ Sun-Eros Annual Carrier Mismatch
         └─ Eros Deferent-B Stage
            └─ Eros Main-Orbit Basis
               └─ Eros Solar Asteroid Branch
                  └─ Eros
```

Independent tests reproduce the legacy Eros-from-Sun vector below `1e-10` model
units at selected epochs and across a dense 200-model-year grid. The complete suite
passes (`47` tests across `9` suites), and the production build succeeds with only
the pre-existing MediaPipe source-map warnings.

Both independent export gates have now passed, so Phase 4E is **accepted as
coordinate preserving**:

- the fresh Eros-only export matches
  `00-backup/phase4c/eros_ephemerides_before.txt` at all 75,969 timestamps, with
  zero displayed RA, declination, distance and elongation mismatches;
- all scientific summary fields for the ten analyzed bodies have zero numerical
  difference from the complete Phase 4D baseline;
- all 31 per-sample, annual-statistics and spectral artifacts are byte-identical;
  and
- all 9,497 Sun-Mars binary rows and numeric fields are exactly identical.

The accepted reports are `reports/phase4e_eros_equivalence_report.md` and
`reports/phase4e_system_equivalence_report.md`. This closes the coordinate-
preserving hierarchy adaptation: Mars has an explicit Sun-relative companion
construction; Mercury, Venus and Eros are true Sun descendants; Phobos and Deimos
inherit from Mars; and the outer planets and Halley retain their existing Sun-hosted
placement. Any subsequent simplification or new physical hypothesis should begin as
a separate phase from this frozen structural baseline. The consolidated hierarchy,
implementation and author-facing tuning guidance are documented in
[`binary_tychos.md`](binary_tychos.md).

### Declarative hierarchy candidate

The first native-core migration is now implemented on the
`declarative-hierarchy` branch. `src/settings/celestial-model.json` declares the
complete Earth/Moon and Sun-primary/Mars-companion topology, semantic roles,
mode-specific nodes and relative-component settings dependencies. Both
`SolarSystem.jsx` and `PlotSolarSystem.jsx` now use one recursive
`DeclarativeCelestialModel` renderer instead of maintaining separate JSX trees.

No celestial setting or relative-orbit equation was changed. Schema and hierarchy
tests bring the complete suite to 52 passing tests across 10 suites. The production
build succeeds with only the pre-existing MediaPipe source-map warnings.

Both export gates pass, so the first declarative migration is **accepted as
coordinate preserving**:

- all ten scientific summary fields have zero deltas;
- all 31 numeric artifacts are byte-identical;
- all 9,497 Sun-Mars binary rows are exactly unchanged; and
- the direct Eros comparison has 75,969 matching timestamps with zero displayed
  RA, declination, distance or elongation mismatches.

The accepted reports are `reports/declarative_hierarchy_equivalence_report.md`
and `reports/declarative_hierarchy_eros_equivalence_report.md`. The very small
Eros direction RMS (`5.20e-7 deg`) is floating-point `acos` noise between identical
formatted coordinates. `celestial-model.json` may now be treated as the accepted
topological source of truth, while `celestial-settings.json` remains the accepted
numerical source of truth.

This remains an architectural re-expression, not parameter tuning.

Leave the outer planets and Halley in place because they are already Sun
descendants. Phobos and Deimos are already correctly inherited from Mars. Eros is
the final structural reparenting in this adaptation; only after its two export gates
pass should a redundant carrier be simplified or a new physical-geometry hypothesis
be tested.

Phase 1 was checked with 75,969 native-frame samples at three-hour cadence from
2000-06-21 through 2026-06-21. Mars remained exactly identical to the saved
old-TYCHOS export at every timestamp and at the export's RA/Dec precision. This
supports the expected identity of the new wrapper. The JPL residuals from that run
must not be treated as a clean orbital comparison because the export used the
moving native/PVP frame rather than fixed J2000/ICRF axes.

The next stages must remain controlled and reversible:

1. Export and summarize the Phase 2.5 diagnostics over a declared interval. This
   establishes what the existing TYCHOS hierarchy actually implies before a binary
   relationship is imposed.
2. Retain the Phase 3B asymmetric interpretation unless a later TYCHOS source gives
   a falsifiable interior-centre geometry. Do not select a ratio merely because
   every weighted decomposition gives exact opposition.
3. Phase 3C equivalence is confirmed. Preserve its export and reports as the
   structural baseline for the next experiment.
4. Phase 3D has reconstructed the measured Sun-relative Mars ellipse as four exact
   components. Phase 3E implements them as named Sun-relative transforms and its
   full export-equivalence gate has passed. Preserve this accepted export as the
   structural baseline for Phase 4.
5. Treat any fixed ratio, opposition or phase-lock constraint as a distinct TYCHOS
   hypothesis. Test one constraint at a time against both all-date ephemerides and
   event-centred diagnostics; do not hide discrepancies with fitted perturbations.

[`SunMarsBinarySystem.test.jsx`](../src/components/SunMarsBinarySystem.test.jsx)
guards the intended sibling relationship and the placement of the solar and Martian
moons. [`sunMarsBinaryState.test.js`](../src/utils/sunMarsBinaryState.test.js)
checks exact reconstruction, opposition diagnostics, zero-radius handling and the
hidden plot-model path. Numerical ephemeris equivalence is still verified with a
simulator export comparison.

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

## Current Mercury/Venus plane refactor (2026-09-27)

This branch now tests one narrow architectural question: can the original TYCHOS
Mercury and Venus geometry be expressed with explicit plane objects without changing
its ephemerides? It intentionally contains no Mercury eccentric, synodic or other
residual-fitted displacement layer.

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

The settings were restored from the `moon-orbital-plane` branch, which is the
source of truth for the original Mercury/Venus geometry used here. The complete
pre-orbit transform formerly stored on each planet was moved into its zero-speed,
zero-radius plane; the corresponding planet fields were reset to zero.

| Entry | Active settings |
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

The simulator export now confirms the restored baseline over 75,969 three-hour
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

### Transit-oriented baseline

Linear interpolation of the common three-hour Sun/planet export to the catalogued
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
7. **Freeze the explicit-plane baseline.** The source-level and simulator-export
   equivalence checks are complete. Keep this branch unchanged as the original
   TYCHOS Mercury/Venus geometry expressed through explicit plane objects.
8. **Solar-equator and transit experiment.** After equivalence is confirmed, test a
   separate controlled candidate in which both plane normals share the solar-equator
   orientation. Evaluate planet-to-Sun relative offsets at known transit epochs as
   the primary targeted diagnostic and retain all-date JPL RMS as a secondary guard.
   This experiment must not silently restore the removed eccentric/synodic layers.

## Where to inspect the implementation

- [MoonOrbitalPlane.jsx](../src/components/MoonOrbitalPlane.jsx): node / counter-rotation.
- [celestial-settings.json](../src/settings/celestial-settings.json): retained node,
  lunar parameters and equivalence-preserving Mercury/Venus planes; lunar deferent B
  is intentionally absent.
- [PlotSolarSystem.jsx](../src/components/PlotSolarSystem.jsx) and [Pobj.jsx](../src/components/Pobj.jsx): hierarchy, local axes, offsets and inherited transformations.
- [plotModelFunctions.js](../src/utils/plotModelFunctions.js): motion and conversion to exported coordinates.
- [analyze_ephemerides.py](scripts/analyze_ephemerides.py): reference rotation, fixed periods and diagnostic fits.
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
