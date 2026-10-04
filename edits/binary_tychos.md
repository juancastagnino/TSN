# Binary TYCHOS implementation

## Purpose and status

This branch expresses the accepted TYCHOS geometry through an explicit,
versioned asymmetric Sun–Mars primary/companion hierarchy. Mercury and Venus
are structurally hosted by the Sun as its junior and senior solar companions,
Eros is a Sun-hosted small body, and Phobos and Deimos remain children of Mars.

This is the first genuinely native/declarative implementation of that hierarchy
in the software, but it should not yet be described as the final or complete
book-native TYCHOS architecture. The distinction is important: the code now
states the intended astronomical roles explicitly, while some parentage and
relative-coordinate mathematics remain deliberately constrained by the old
model so that no accepted ephemeris is changed accidentally.

The change is deliberately **coordinate preserving**. It reorganizes the scene,
export hierarchy and settings schema without fitting new orbital parameters.
The numerical values in `celestial-settings.json` are unchanged. The resulting ephemerides are identical to the
pre-refactor model at export precision. This proves that the new hierarchy is a
lossless representation of the accepted geometry; it does not by itself prove a
physical binary interpretation or improve agreement with JPL.

The implementation and both live/plot paths are complete. The final validation
status is:

| Check | Result |
|---|---:|
| Source tests | 57 tests in 11 suites passed |
| Production build | Passed; only pre-existing MediaPipe source-map warnings |
| Scientific summaries | Zero deltas for all 10 analyzed bodies |
| Numeric analysis artifacts | 31 of 31 byte-identical |
| Sun–Mars diagnostic | 9,497 of 9,497 rows exactly unchanged |
| Eros export | 75,969 of 75,969 rows identical in RA, Dec, distance and elongation |

The accepted evidence is in:

- `reports/phase4e_system_equivalence_report.md`
- `reports/phase4e_eros_equivalence_report.md`
- `reports/eros_phase4d_report.md`
- `00-backup/phase4d/` for the immediate full-system baseline
- `00-backup/phase4c/eros_ephemerides_before.txt` for the pre-Eros export

## Present conceptual status

Three different claims must be kept separate:

1. **Native software representation:** achieved. The topology and settings are
   now versioned data, use stable IDs, drive both the visible and export models,
   and expose Sun, Mars, Mercury, Venus, Eros and the moons through explicit
   astronomical roles.
2. **Coordinate-preserving migration:** achieved. The new hierarchy reproduces
   the accepted pre-migration coordinates and exports without numerical changes.
3. **Complete literal implementation of every structural statement in the
   TYCHOS book and the author's October 2026 notes:** not yet achieved or fully
   specified.

The third claim cannot be made honestly until several remaining theoretical
choices are defined by the authors and then tested. This does not invalidate the
present implementation. It establishes a safe native baseline from which those
physical changes can be made without mixing them with software refactoring.

### What remains from the former model

The old hierarchy is no longer the active source of truth, but several kinds of
legacy information are intentionally retained:

- The accepted numerical orbital parameters are unchanged.
- Historical setting names remain as labels and import aliases so existing
  settings files still load.
- The deferent components that mathematically generate the accepted paths remain
  active where they have not been shown to be redundant.
- Sun-relative Mars, Mercury, Venus and Eros positions are reconstructed from
  exact differences between their former chains and the Sun chain. These are
  compatibility equations inside the new hierarchy, not post-export corrections.
- At the root level the Sun–Mars system is still structurally beneath Earth so
  that the accepted geocentric coordinates are preserved. `SystemCenter`
  identifies the PVP/secular context, but it is not yet an independently defined
  physical parent of both the Earth path and the Sun–Mars system.

Therefore, “legacy” here does not mean that a second hidden old model is still
running. It means that the new native tree deliberately preserves the proven
mathematics and values of the preceding implementation.

### Findings from the author's structure document

The October 2026 document is broadly compatible with the direction of this
refactor. It supports an asymmetric Sun–Mars relationship, treats Mercury and
Venus as solar companions, retains Phobos and Deimos under Mars, and places
Eros and Halley in the wider solar branch. It also adds requirements that are
not yet represented literally:

- the centre of the PVP orbit may serve as a secular system centre or secular
  barycentre, although the author describes that interpretation as debatable;
- Mercury and Venus should be coplanar with the Sun's equatorial plane, inclined
  by approximately 6–7 degrees;
- the 25,344-year Great Year, the 50,688-year Sun–Mars recurrence, the proposed
  1,000/2,000-year Mercury/Venus recurrences and their transit/retrograde
  relations should become explicit validation targets; and
- some Mars/deferent elements have not yet been classified by the author as
  fundamental geometry versus implementation devices.

The current Mercury and Venus branches retain two separate fixed planes because
that is what was required for exact equivalence with the accepted ephemerides.
They are not yet a single shared solar-equatorial plane. Likewise, the present
Sun–Mars hierarchy is semantically explicit but does not yet make the PVP centre
the literal common parent of a separately represented Earth path and Sun–Mars
system.

### Candidate fully book-native hierarchy

Once those definitions are settled, a stricter conceptual target could be:

```text
PVP / Secular Centre
├─ Earth PVP Path
└─ Sun–Mars System
   └─ Sun Primary
      ├─ Mars Junior Companion
      │  ├─ Phobos
      │  └─ Deimos
      ├─ Shared Solar Equatorial Plane
      │  ├─ Venus Senior Solar Companion
      │  └─ Mercury Junior Solar Companion
      ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
      ├─ Halley
      └─ Eros
```

That would be a physical-geometry revision, not another equivalence refactor.
It may legitimately change the ephemerides and therefore requires explicit
definitions, new settings and observational validation rather than being folded
silently into the accepted native baseline.

Before attempting it, the authors should ideally specify:

- whether the PVP centre is a true parent/origin or only a descriptive reference;
- the exact epoch, axes and orientation of the shared solar-equatorial plane;
- which current deferent components are fundamental and which may be replaced;
- what “return to the same place” means for the quoted long cycles: coordinate
  frame, observable, timestamp and numerical tolerance; and
- whether axial parallelism is a renderer constraint, an orbital rule or both.

## Development path and findings

| Phase | Purpose | Retained conclusion |
|---|---|---|
| 1–2.5 | Introduce a named Sun–Mars system and export diagnostic world vectors | The wrapper and diagnostics could be added without moving any body. A midpoint calculated from the endpoints is a mathematical control, not evidence for a physical barycentre. |
| 3A | Screen fixed weighted centres and radius ratios | Any weighted two-point centre produces exact opposition by construction. No mass or radius ratio should be selected from that identity alone. |
| 3B | Analyze Mars directly relative to the Sun | The existing output supports an asymmetric primary/companion description more naturally than an equal binary construction. |
| 3D | Expand the complete Mars-minus-Sun transform algebraically | Four existing components reproduce the Sun-relative Mars path exactly. |
| 3E | Replace the legacy Earth-level Mars prefix with those Sun-relative components | Accepted as coordinate preserving after complete export regression. |
| 4A | Audit the legacy Mercury and Venus chains relative to the Sun | Both chains admit exact Sun-relative representations while preserving their separate fixed planes. |
| 4B | Reparent Venus | Accepted with zero system-output differences. |
| 4C | Reparent Mercury | Accepted with zero system-output differences. |
| 4D | Audit Eros relative to the Sun | Four components are required; its tilted annual carriers do not cancel completely. |
| 4E | Reparent Eros and perform the final regression | Accepted with exact formatted Eros output and zero complete-system differences. |

The previously discussed `7:1` ratio refers to the approximate maximum versus
minimum **Earth-to-Mars distance**, not to Sun/Mars binary radii and not to an
inferred mass ratio. It should remain an observational/geometric feature to
explain, not a value imposed on a barycentric construction.

## Current coordinate-preserving hierarchy

The effective model tree is:

```text
SystemCenter
└─ Earth
   ├─ Moon orbital node/plane system
   │  └─ Moon deferent A
   │     └─ Moon
   │
   └─ Sun–Mars Binary Frame
      └─ Sun Primary Branch
         └─ Sun deferent
            └─ Sun
               ├─ Halley's deferent
               │  └─ Halley
               ├─ Jupiter deferent
               │  └─ Jupiter
               ├─ Saturn deferent
               │  └─ Saturn
               ├─ Uranus deferent
               │  └─ Uranus
               ├─ Neptune deferent
               │  └─ Neptune
               ├─ Pluto deferent
               │  └─ Pluto
               ├─ Sun-relative Mars components
               │  └─ Mars Junior Companion Branch
               │     └─ Mars
               │        ├─ Phobos
               │        └─ Deimos
               ├─ Sun-relative Venus frame
               │  └─ Venus Senior Solar Companion Branch
               │     └─ Venus
               ├─ Sun-relative Mercury frame
               │  └─ Mercury Junior Solar Companion Branch
               │     └─ Mercury
               └─ Sun-relative Eros frame
                  └─ Eros Solar Asteroid Branch
                     └─ Eros
```

The Moon remains Earth-hosted. The already Sun-hosted outer planets and Halley
did not require a relative-coordinate refactor. Phobos and Deimos automatically
inherit the final Mars frame.

## Why relative components are necessary

Simply moving a legacy Earth-level branch beneath the Sun would add the Sun's
translation and rotations a second time and change the ephemerides. Each new
component therefore reconstructs the old body-minus-Sun vector and places that
vector at the Sun while retaining the common binary-frame axes.

In simplified form:

```text
body world position = Sun world position + exact legacy (body - Sun) vector
```

`updateSunRelativeFrame()` performs the coordinate adaptation. The named
component vectors then rebuild every translation and orientation from the
existing settings in their original matrix order. Both the displayed model and
the hidden plot/export model use the same `SunMarsBinarySystem`, preventing the
two hierarchies from drifting apart.

### Mars

The exact Mars identity is:

```text
Mars - Sun = centre difference
           + annual carrier mismatch
           + Mars deferent-S harmonic
           + Mars main-orbit basis and unchanged Mars leaf
```

The new tree is:

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

This expresses Mars as an asymmetric companion of the Sun while preserving the
existing TYCHOS path. It does not impose an equal-mass barycentre, equal radii or
a conventional two-body dynamical solution. The approximately 687-day
Sun-relative path emerges from the retained geometry.

### Venus and Mercury

Each solar companion preserves five legacy stages:

```text
planet - Sun = centre difference
             + annual carrier mismatch
             + deferent-B stage
             + fixed-plane stage
             + main-orbit basis and unchanged planet leaf
```

Their fixed planes remain separate. The refactor does not force Mercury and
Venus onto one numerically identical plane.

Mercury deferent B deserves special attention: its current orbital radius is
zero, but its centre and orientation are not necessarily inert. The entire stage
must be retained unless an independent algebraic and export test proves that it
has become an identity.

### Eros

Eros preserves four stages:

```text
Eros - Sun = centre difference
           + annual carrier mismatch
           + Eros deferent-B stage
           + main-orbit basis and unchanged Eros leaf
```

The two annual carriers both have radius 100, but they cancel by only about
`89.654%` because their planes are tilted differently. The remaining
`10.345532` model units are part of the existing geometry and cannot be deleted
merely because the scalar radii match. Eros needs no additional fixed-plane
object: its deferent-A orientation already defines a fixed orbital basis.

## Main implementation files

| File | Responsibility |
|---|---|
| `src/components/SunMarsBinarySystem.jsx` | One shared semantic hierarchy for live and plot/export models |
| `src/components/SunMarsRelativeOrbit.jsx` | Exact Sun-relative Mars reconstruction and shared frame-placement helper |
| `src/components/VenusSunRelativeOrbit.jsx` | Exact Sun-relative Venus reconstruction |
| `src/components/MercurySunRelativeOrbit.jsx` | Exact Sun-relative Mercury reconstruction |
| `src/components/ErosSunRelativeOrbit.jsx` | Exact Sun-relative Eros reconstruction |
| `src/components/SolarSystem.jsx` | Live model entry point |
| `src/components/PlotSolarSystem.jsx` | Trace and ephemeris-export model entry point |
| `src/components/SunMarsBinaryTracker.jsx` | Optional diagnostic state collection and CSV export |
| `src/utils/sunMarsBinaryState.js` | Binary diagnostic calculations |
| `src/utils/plotModelFunctions.js` | Plot/export update ordering |
| `src/settings/celestial-model.json` | Versioned native topology, roles, stable setting registry and editor groups |
| `src/settings/celestial-settings.json` | Versioned native parameter document keyed by stable setting IDs |
| `src/utils/celestialSettingsSchema.js` | Validation, legacy import, serialization, indexing and editor-group resolution |

## Native, versioned hierarchy migration

The first migration made `src/settings/celestial-model.json` the single declarative source
for the complete topology. It records:

- stable node IDs and node types;
- parent/child relationships;
- astronomical roles;
- live-only versus plot/export nodes; and
- the accepted legacy settings on which every derived relative frame depends.

`DeclarativeCelestialModel.jsx` validates the schema and every referenced setting,
then recursively builds either the live `Cobj` model or the plot/export `Pobj`
model. `SolarSystem.jsx` and `PlotSolarSystem.jsx` no longer contain independent
hand-written celestial trees. `SunMarsBinarySystem.jsx` remains only as a
backward-compatible view of the corresponding declarative subtree.

The final native-core migration on `native-binary-system` links that topology to
schema-v2 celestial settings. Every setting now has a stable ID such as
`mercury-plane`; human-readable names are retained as labels and compatibility
aliases. Relative-orbit mathematics and object rendering resolve stable IDs,
while external scene names remain unchanged for cameras, labels and exports.

The Edit Settings menu is generated from the model's declared editor groups. It
now presents PVP/Earth, Earth-Moon, Sun primary, Mars companion, Venus companion,
Mercury companion, outer planets and small bodies as explicit systems rather
than guessing relationships from name substrings.

Loading remains backward compatible. Existing flat-array `TS_settings` files are
validated against the registry and converted to stable IDs in memory. New saves
use schema v2, retain `rotationStart`, and can be loaded atomically. Unknown,
duplicate or incomplete native defaults fail validation instead of silently
creating a partially broken model.

The schema tests verify unique IDs, known node types, valid render modes, valid
setting dependencies, legacy import and native round-trip, complete editor
coverage, accepted object order and exclusion of the physical
`Actual Moon` and live binary tracker from the plot/export model. The complete
source suite passes 57 tests across 11 suites, and the production build passes
with only the pre-existing MediaPipe source-map warnings.

The preceding declarative migration was fully accepted. Its fresh full-system gate has zero deltas in all
ten scientific summaries, all 31 numeric artifacts are byte-identical, and all
9,497 Sun-Mars binary rows are exactly unchanged. The direct Eros gate also passes:
all 75,969 timestamps and displayed RA, declination, distance and elongation fields
are identical to the restored pre-migration export. The tiny calculated direction
RMS (`5.20e-7 deg`) is floating-point `acos` noise between identical formatted
coordinates, not an exported-coordinate difference. The schema-v2 migration
changes no numerical setting and passes all code-level reconstruction tests. Its
fresh simulator gate now passes as well: the ten-body summaries have zero delta,
31 of 31 numeric artifacts are byte-identical, all 9,497 binary rows are exactly
unchanged, and all 75,969 Eros rows match in every displayed export field. The
native version is accepted as coordinate preserving.

The component tests compare each new relative reconstruction with its independent
legacy chain at selected epochs and across dense long-duration grids. The final
simulator exports remain the authoritative end-to-end check.

## Does editing work differently now?

### Short answer

The controls continue displaying the familiar setting names, and changes propagate
live through the new hierarchy. Internally the update is applied by stable ID.
The author does **not** need to edit the generated
Sun-relative component nodes directly.

The recommended working process is different, however. A parameter now has a
clear geometric role within a shared hierarchy. Editing a shared Sun setting can
move several descendants, while editing a leaf or local plane should affect only
one branch. Tuning should therefore follow dependencies and geometric layers
rather than treating every visible number as an independent correction knob.

### What the current Edit Settings menu does

The current menu follows the native declared systems. Mercury's A/B stages,
fixed plane and leaf are together under `Mercury Junior Solar Companion`; Venus
has its own corresponding group; Mars includes both deferents, the main body,
Phobos and Deimos. Generated entries such as `Sun-Mercury Annual Carrier
Mismatch` remain absent because they are calculated results, not independent
tunable parameters.

## Recommended tuning roles

| Setting layer | What it primarily controls | Recommended use |
|---|---|---|
| `Sun deferent` / `Sun` | Shared solar origin, annual carrier and orientation | Treat as global. Change only for a declared Sun/system hypothesis, then recheck every Sun descendant and the Moon/Sun observables. |
| `Mars deferent E` | Mars annual carrier, centre and outer orientation relative to the Sun | Use for annual/shared-frame geometry, not to correct a short-period Mars residual. |
| `Mars deferent S` | Secondary Mars component or harmonic | Change only when residual period/phase evidence points to this stage. |
| `Mars` | Main Mars phase, rate, radius, centre and plane | Use for the primary Sun-relative Mars path. Recheck Phobos and Deimos because they inherit this frame. |
| Mercury/Venus `deferent A` | Annual carrier relative to the Sun | Keep stable unless testing the solar-companion carrier itself. It is highly coupled to the Sun subtraction. |
| Mercury/Venus `deferent B` | Secondary centre/radius/orientation stage | Use for secondary geometry. Do not assume a zero radius makes the entire stage irrelevant. |
| `Mercury Plane` / `Venus Plane` | Fixed plane centre and orientation | Use for latitude/declination and explicit orbital-plane hypotheses. Tune each plane separately unless the theory specifically requires a common solar-equator plane. |
| `Mercury` / `Venus` | Main orbital phase, speed and radius | Use first for primary longitude/phase/scale questions. Transit-relative offsets should be a principal diagnostic. |
| `Eros deferent A` | Annual carrier and fixed Eros basis | Treat as structural; changing its tilt also changes the non-cancelling annual remainder. |
| `Eros deferent B` | Secondary Eros vector and rate | Use for a residual attributable to this stage, not as a generic correction. |
| `Eros` | Main Eros orbit | Use first for main phase, speed and radius experiments. |
| Outer-planet/Comet deferents and leaves | Their existing Sun-hosted geometry | Their editing process is unchanged. |
| Moon Node/Plane/deferent/leaf | Independent Earth-hosted lunar geometry | Keep lunar experiments separate from solar-companion tuning. |

`size`, `actualSize`, `tilt`, `tiltb`, `rotationStart` and `rotationSpeed` can
describe appearance or axial rotation rather than orbital position. They should
not be mixed into ephemeris tuning unless code inspection confirms that the
selected observable uses them. Orbital position is primarily controlled by
`startPos`, `speed`, `orbitRadius`, `orbitCenter*` and `orbitTilt*`.

## Recommended author workflow

1. **Freeze a reproducible baseline.** Save the settings file, TYCHOS export,
   reference export, analysis reports and run label together.
2. **State one geometric hypothesis.** Identify the body, hierarchy layer and
   expected observable before changing a value.
3. **Change one layer at a time.** Avoid changing a planet leaf, its plane and its
   deferent in the same trial. Otherwise the source of any improvement is unclear.
4. **Use the parameter matching the symptom.** Phase and radius tests belong at
   the main orbit first; latitude errors suggest plane orientation; a coherent
   secondary period may justify examining a deferent.
5. **Use body-relative events where appropriate.** For Mercury and Venus, compare
   planet-minus-Sun offsets at transits in addition to all-date RA/Dec. A shared
   absolute reference-frame offset should not dominate that diagnostic.
6. **Keep global and local tests separate.** A Sun edit is a system-wide test; a
   Mercury Plane edit is local. Never judge a global edit from Mercury alone.
7. **Test the same dates and cadence.** Do not compare RMS values from different
   intervals or sampling grids.
8. **Use chronological validation.** Select parameters on one interval and verify
   them unchanged on a withheld interval. Long-period bodies require longer test
   windows than Mercury or Venus.
9. **Separate equivalence from accuracy.** The Phase 4 scripts prove a refactor
   did not move anything. JPL/Stellarium comparisons evaluate observational
   agreement. A structural pass is not an accuracy improvement, and an RMS
   improvement is not proof of a physical interpretation.
10. **Retest descendants and the complete system.** A retained change must pass
    the target metric, guard metrics for other coordinates, event checks, and a
    whole-system regression appropriate to its dependency scope.

For ordinary parameter tuning, exact equivalence is neither expected nor the
goal—the output should change. The requirement is instead that the change be
intentional, localized as predicted, and validated out of sample. Exact
equivalence gates should be used again when code or hierarchy is refactored
without intending to alter the geometry.

## Edit Settings hierarchy and future refinements

The implemented top-level structure is:

```text
Appearance
Global / PVP frame
Earth and Moon
Sun–Mars system
├─ Shared Sun geometry
├─ Mars companion geometry
│  ├─ Annual carrier (Mars deferent E)
│  ├─ Secondary component (Mars deferent S)
│  ├─ Main Mars orbit
│  └─ Phobos / Deimos
├─ Solar companions
│  ├─ Mercury: carrier / B / plane / main orbit
│  └─ Venus: carrier / B / plane / main orbit
├─ Outer planets
└─ Small bodies
   ├─ Eros: carrier / B / main orbit
   └─ Halley
```

Within every object, controls should be divided into:

- **Phase and rate:** `startPos`, `speed`;
- **Orbital scale:** `orbitRadius`;
- **Orbit centre:** `orbitCentera`, `orbitCenterb`, `orbitCenterc`;
- **Orbital plane:** `orbitTilta`, `orbitTiltb`;
- **Body appearance and spin:** `size`, `actualSize`, `tilt`, `tiltb`, rotation
  controls.

Useful future refinements:

- Mark Sun and other shared settings with a **global/shared** warning.
- Display the generated relative-component names as read-only explanatory rows,
  not editable duplicate parameters.
- Show which descendants are affected before applying a shared change.
- Provide per-body reset, transaction-level undo and a before/after settings diff.
- Allow an experiment label and baseline snapshot to be saved with settings.
- Highlight zero-radius but non-identity stages such as Mercury deferent B.
- Add optional parameter descriptions and units directly in the menu.
- Add explicit units and numeric-range validation for orbital values.
- Avoid mutating the existing setting object before updating the store; create a
  validated immutable replacement instead.

Stable IDs now allow visible labels to evolve without changing astronomical
identity. Legacy names should nevertheless remain as import aliases until the
authors intentionally retire the old settings format.

## Acceptance discipline for future changes

For a hierarchy or code-only refactor:

- run component unit tests;
- build the application;
- export the affected body before and after over identical timestamps;
- run a formatted raw-export comparison where available;
- rerun the complete multi-body analysis and binary diagnostic; and
- require zero unintended differences.

For a parameter or physical-geometry experiment:

- preserve the baseline first;
- declare the changed parameters and intended effect;
- compare RA, declination, angular separation, longitude and latitude;
- inspect mean bias, RMS, percentiles and time-dependent residuals;
- check relevant relative events, especially Mercury/Venus transits;
- check non-target bodies implied by shared ancestors; and
- validate on an independent interval before accepting the setting.

The guiding rule remains: improvements should arise from a coherent geometric
interpretation and its correct implementation, not from adding fitted residual
corrections to the exported coordinates.

## Final interpretation

The completed refactor gives the TYCHOS proposal substantially greater
explanatory clarity in software: the code tree now visibly expresses Sun
primary, Mars companion, solar companions, inherited moons and Sun-hosted small
bodies instead of leaving those meanings implicit in Earth-level carrier
chains. The topology and parameter registry are genuinely native and
declarative; this is more than a display-only relabelling.

At the same time, exact equivalence was an intentional design constraint. The
current implementation should be presented as a **native, versioned,
coordinate-preserving TYCHOS hierarchy**, not yet as a definitive encoding of
every physical detail proposed in the book. Its remaining compatibility
mathematics preserve the accepted geometry while isolating the questions that
still require author definitions: the root role of the PVP centre, a possible
shared solar-equatorial plane for Mercury and Venus, and the theoretical status
of the retained deferent components.

Because the outputs are unchanged, all previous observational strengths and
weaknesses remain. That is precisely what makes this a reliable baseline. The
next book-native migration can now be evaluated as an explicit astronomical
hypothesis, with its coordinate changes measured against both this baseline and
independent observations, rather than being confused with a software rewrite.
