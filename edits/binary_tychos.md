# Binary TYCHOS implementation

## Status

The `native-binary-system` branch is the accepted native, versioned and
coordinate-preserving implementation of the current TYCHOS hierarchy.

The work converted relationships that were previously implicit in Earth-level
carrier chains into an explicit model topology. It did not fit a new orbit, impose
a conventional barycentre or change accepted celestial parameters. Fresh exports
proved equivalence to the saved predecessor.

## Accepted conceptual hierarchy

```text
SystemCenter                         (fixed PVP coordinate reference)
└─ Earth                             (moves on the PVP path)
   ├─ Moon Node / Plane
   │  └─ Moon deferent A
   │     └─ Moon
   └─ Sun-Mars Binary Frame
      └─ Sun Primary Branch
         └─ Sun deferent
            └─ Sun
               ├─ Mars Junior Companion
               │  └─ Mars
               │     ├─ Phobos
               │     └─ Deimos
               ├─ Venus Senior Solar Companion
               ├─ Mercury Junior Solar Companion
               ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
               ├─ Halley
               └─ Eros
```

This retains the central Tychonic relationship with the additional PVP motion:

1. Earth follows its slow PVP path.
2. The Sun system is positioned relative to Earth.
3. Mars is an asymmetric junior companion relative to the Sun.
4. Venus and Mercury are separate solar companions.
5. The outer planets, Halley and Eros belong to the Sun-hosted subsystem.
6. The Moon remains Earth-hosted; Phobos and Deimos inherit Mars.

## Meaning of `SystemCenter`

`SystemCenter` is an identity transform at model coordinate `(0,0,0)`. It has no
radius, speed, centre offset or tilt. It is not a body, physical barycentre or
cause of motion.

The PVP centre is a geometric attribute of Earth's PVP orbit. Conceptually the
path defines its centre; computationally the centre is used as the reference from
which the path is evaluated. That calculation order does not imply causality.

Earth and the Sun–Mars system therefore remain in a parent/descendant relationship.
They are not intended to become independently moving sibling systems beneath the
PVP reference. Such a reparenting would either be a coordinate-only rewrite with
no new physical meaning or a different astronomical model requiring new settings.

## Sun–Mars interpretation

The current geometry supports an asymmetric primary/companion description more
naturally than a conventional equal or barycentric binary:

- the Sun is the primary reference for the Mars relative path;
- Mars follows an approximately 687-day Sun-relative path;
- Phobos and Deimos inherit the completed Mars frame; and
- no mass ratio, forced opposition or interior barycentre is imposed.

The historical `7:1` observation refers to maximum versus minimum **Earth-to-Mars
distance**, measured here as approximately `7.209:1`. It is not the ratio of Sun
and Mars radii around a binary centre. A fixed-ratio centre screen found no
preferred finite interior centre, so the model deliberately retains the
asymmetric Sun-relative representation.

## Coordinate-preserving reconstruction

The old Mars, Mercury, Venus and Eros branches could not simply be moved beneath
the Sun: doing that would apply the Sun transforms a second time. Each branch now
reconstructs its exact legacy body-minus-Sun vector:

```text
body world position = Sun world position + exact legacy (body - Sun) vector
```

The relative builders preserve the original matrix order and expose meaningful
named stages.

### Mars

```text
Mars - Sun = centre difference
           + annual carrier mismatch
           + Mars deferent-S harmonic
           + main-orbit basis and Mars leaf
```

### Venus and Mercury

```text
planet - Sun = centre difference
             + annual carrier mismatch
             + deferent-B stage
             + fixed-plane stage
             + main-orbit basis and planet leaf
```

Mercury and Venus keep separate fixed planes. The accepted baseline reproduces
the original TYCHOS geometry; it does not yet force both numerical planes onto one
solar-equatorial orientation.

A zero orbital radius does not necessarily make a transform stage irrelevant.
Mercury deferent B still carries centre and orientation information and must remain
unless a complete equivalence test proves otherwise.

### Eros

```text
Eros - Sun = centre difference
           + annual carrier mismatch
           + deferent-B stage
           + main-orbit basis and Eros leaf
```

Eros's two radius-100 annual carriers do not cancel completely because their planes
differ. The non-cancelling vector is part of the accepted geometry.

## Native declarative model

[celestial-model.json](../src/settings/celestial-model.json) is the topology source
of truth. It declares stable node IDs, parent/child relationships, semantic roles,
live/plot modes, setting dependencies and Edit Settings groups.

[celestial-settings.json](../src/settings/celestial-settings.json) stores numerical
parameters by stable ID. Human-readable names remain labels and legacy aliases.
Old flat settings files are validated and imported; new saves use schema v2.

`DeclarativeCelestialModel.jsx` recursively constructs both the displayed model and
the hidden plot/export model. This prevents the two trees from drifting apart.
Calculated Sun-relative component nodes are not independent tuning parameters and
therefore do not appear as duplicate Edit Settings controls.

## Principal implementation files

| File | Responsibility |
|---|---|
| `src/settings/celestial-model.json` | Native topology and editor grouping |
| `src/settings/celestial-settings.json` | Stable-ID parameter registry |
| `src/utils/celestialSettingsSchema.js` | Validation, import and serialization |
| `src/components/DeclarativeCelestialModel.jsx` | Shared live/export tree builder |
| `src/components/SunMarsBinarySystem.jsx` | Sun–Mars semantic subtree |
| `src/components/SunMarsRelativeOrbit.jsx` | Exact Mars relative reconstruction |
| `src/components/VenusSunRelativeOrbit.jsx` | Exact Venus relative reconstruction |
| `src/components/MercurySunRelativeOrbit.jsx` | Exact Mercury relative reconstruction |
| `src/components/ErosSunRelativeOrbit.jsx` | Exact Eros relative reconstruction |
| `src/components/MoonOrbitalPlane.jsx` | Lunar node and plane transform |
| `src/utils/plotModelFunctions.js` | Plot/export model updates |

## Validation

The authoritative pre-migration baseline is preserved under
`00-backup/new-baseline`.

| Check | Result |
|---|---|
| Ten-body scientific summaries | Zero numerical deltas |
| Numeric analysis artifacts | 31 of 31 byte-identical |
| Sun–Mars diagnostic | 9,497 rows exactly unchanged |
| Direct Eros export | 75,969 rows identical in all displayed fields |
| Source suite | 57 tests across 11 suites passed |
| Production build | Passed |

These gates establish that the new topology reproduces the accepted predecessor.
They separate the software migration from later physical-geometry experiments.

## Editing the model

The familiar controls remain available, but each parameter now belongs to an
explicit geometric layer. Shared ancestors affect descendants; local planes and
leaves affect only their branches.

- Treat Sun settings as system-wide.
- Use a main body for primary phase, rate and scale questions.
- Use a fixed plane for latitude/declination and plane-orientation hypotheses.
- Use secondary deferents only when the residual structure points to that layer.
- Recheck descendants after changing an ancestor.
- For Mercury and Venus, include planet-minus-Sun transit diagnostics.
- Never edit calculated relative-component nodes as if they were free corrections.

The complete controlled workflow and parameter roles are in
[edit_settings_instructions.md](edit_settings_instructions.md).

## Scope of future work

The native hierarchy itself is accepted. Future experiments should modify one
explicit astronomical hypothesis at a time:

1. test whether Mercury and Venus should share a solar-equatorial orientation;
2. resolve the native coordinate-frame contract before using long-term JPL drift
   as a tuning target;
3. validate the accepted Moon settings and future planetary changes out of sample;
4. retain the current deferent components until a geometric derivation and export
   gate demonstrate that a component is redundant.

The PVP centre is not an outstanding hierarchy problem. It is already represented
appropriately as the coordinate reference belonging to Earth's PVP geometry.
