# Developer / AI handoff

Read [README.md](README.md) for commands. This file records only the accepted
baseline, its interpretation, constraints and next work. Generated reports contain
the detailed evidence for individual experiments.

## Current branch and status

This handoff describes **`native-binary-system`**, built from the accepted
declarative hierarchy baseline.

The current baseline is accepted as coordinate preserving. It includes:

- a native schema-v2 topology in `celestial-model.json`;
- stable-ID schema-v2 parameters in `celestial-settings.json`;
- the accepted Moon Node/Plane model and lunar tuning;
- an explicit asymmetric Sun–Mars primary/companion hierarchy;
- explicit Sun-relative Mercury, Venus and Eros branches;
- separate fixed Mercury and Venus plane objects reproducing their original
  TYCHOS geometry;
- Phobos and Deimos inheriting Mars; and
- the outer planets and Halley remaining beneath the Sun.

The branch excludes Observer Trace. It contains no Mercury/Venus eccentric or
synodic correction layers, no moving solar-companion nodes and no Pluto tuning.

## Accepted hierarchy

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
               │  └─ Mars -> Phobos / Deimos
               ├─ Venus Senior Solar Companion
               ├─ Mercury Junior Solar Companion
               ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
               ├─ Halley
               └─ Eros
```

### PVP interpretation

`SystemCenter` has zero radius, speed, centre offsets and tilts. It is a coordinate
reference, not a celestial body, physical barycentre or source of motion. The
centre is best understood as a geometric attribute of Earth's PVP orbit. Using it
to calculate the path does not assign it physical causality.

The accepted model therefore does **not** place Earth and the Sun–Mars system in
independently moving sibling branches. It retains the central Tychonic relationship:
Earth follows the PVP path, the Sun system is positioned relative to Earth, and the
solar bodies are organized beneath the Sun. Mars is an asymmetric Sun-relative
junior companion, not one member of a conventional equal or barycentric binary.

Do not elevate the PVP centre into an astronomical object. A compensated
reparenting would only be a coordinate-preserving software rewrite; an
uncompensated reparenting would be a different astronomical model.

## What changed

The former Earth-level Mars, Mercury, Venus and Eros chains were algebraically
rewritten beneath the Sun without changing their world coordinates:

```text
body world position = Sun world position + exact legacy (body - Sun) vector
```

The relative builders preserve every required centre, annual carrier, secondary
deferent, plane and main-orbit component in its original matrix order. Simply
reparenting the old nodes would add Sun transforms twice and is not equivalent.

The model and parameter documents are now genuinely native and declarative:

- `celestial-model.json` defines topology, roles, render modes, settings registry
  and Edit Settings groups.
- `celestial-settings.json` stores parameters by stable ID.
- `DeclarativeCelestialModel.jsx` builds both live and plot/export trees.
- legacy flat settings remain importable; new saves use schema v2.
- Edit Settings is generated from declared astronomical systems.

No numerical celestial parameter was changed merely to obtain this hierarchy.

## Equivalence evidence

The authoritative pre-migration baseline is in `00-backup/new-baseline`.

| Gate | Accepted result |
|---|---|
| Ten-body scientific summaries | Zero numerical deltas |
| Derived numeric artifacts | 31 of 31 byte-identical |
| Sun–Mars binary diagnostic | 9,497 rows exactly unchanged |
| Direct Eros export | 75,969 rows matching every displayed field |
| Source tests | 57 tests across 11 suites passed |
| Production build | Passed; only pre-existing MediaPipe source-map warnings |

This proves structural equivalence to the accepted predecessor. It does not by
itself prove a physical interpretation or improve agreement with JPL.

## Accepted astronomical settings

### Moon

```text
Earth
└─ Moon Node -> Moon Plane -> node counter-rotation
   └─ Moon deferent A
      └─ Moon
```

`Moon deferent B` was an all-zero identity layer and remains removed.

| Entry | Retained values |
|---|---|
| Moon Node | `startPos=-296`, `speed=-0.33780566` |
| Moon Plane | centres `0.001, 0.002, 0`; tilts `0, -5.15` |
| Moon deferent A | `startPos=167.51`, `speed=0.71015440177343`, `radius=0.02786` |
| Moon | `startPos=318.0`, `speed=83.2851946`, `radius=0.25505129081458283` |

On the accepted 2000-2026 three-hour JPL ICRF comparison, lunar angular-separation
RMS is `1.115662°`, longitude RMS `1.094302°`, latitude RMS `0.228328°`, RA RMS
`1.098461°` and declination RMS `0.391893°`. Mean longitude error is `-0.002219°`.
These values are in-sample and must be validated on another interval before further
tuning is accepted.

### Mercury and Venus

Each planet has its own fixed plane inside its Sun-relative branch. Those planes
are an equivalence-preserving expression of the original TYCHOS transforms; they
are not a claim that the two current numerical planes are identical. Their main
orbits, B stages and planes remain distinct.

Mercury deferent B has zero orbital radius but is not automatically an identity:
its centre and orientation affect descendants. Do not remove it without algebraic
and export equivalence evidence.

A shared solar-equatorial-plane experiment would be new physical geometry. Evaluate
it primarily with Mercury/Venus offsets relative to the Sun at transit epochs, with
all-date ephemerides as a guard. Keep it separate from this frozen baseline.

### Other bodies

- Mars retains the exact Sun-relative component reconstruction established during
  the binary audit; Phobos and Deimos inherit its final frame.
- Jupiter, Saturn, Uranus, Neptune, Pluto and Halley remain Sun-hosted.
- Pluto retains its original TYCHOS settings.
- Eros is Sun-hosted through an exact four-component reconstruction. Its two
  radius-100 annual carriers do not cancel completely because their planes differ.

## Reference-frame contract

The native TYCHOS export is not the same product as JPL astrometric ICRF RA/Dec.
Do not interpret their residuals solely as orbital errors.

- Use a TYCHOS J2000 comparison export with `--reference icrf`.
- Use the native/PVP export with `--reference apparent-of-date` only as an
  exploratory moving-frame comparison.
- JPL apparent-of-date also includes light-time, deflection, aberration, precession
  and nutation; matching coordinates would not establish matching mechanisms.
- Translation along the PVP path and rotation of coordinate axes are separate.
- Define origin, pole, zero-RA direction, epoch and time scale before changing
  orbital settings to address a long-term coordinate trend.

## Rules for future changes

1. Preserve a reproducible baseline: settings, raw exports, configuration, reports
   and label.
2. State one geometric hypothesis and identify the layer it affects.
3. Change one layer at a time and predict which descendants should move.
4. Compare identical bodies, timestamps, cadence and reference products.
5. Separate structural equivalence tests from accuracy experiments.
6. Check RA, declination, angular separation, longitude, latitude and relevant
   body-relative events.
7. Validate retained parameter changes on a withheld interval.
8. Never add fitted perturbations or empirical corrections to model output.

For author-facing parameter guidance, see
[edit_settings_instructions.md](edit_settings_instructions.md).

## Next investigations

1. **Solar-equatorial hypothesis:** test shared versus separate Mercury/Venus plane
   orientations, prioritizing transit-relative offsets.
2. **Lunar residual structure:** measure evection/variation arguments directly in
   TYCHOS and JPL rather than treating fitted periods as corrections.
3. **Reference-frame definition:** document the intended native axes and compare
   equivalent observables before tuning long-term drift.
4. **Out-of-sample validation:** verify accepted lunar and future planetary changes
   on an interval not used for selection.

## Key files

| File | Responsibility |
|---|---|
| `src/settings/celestial-model.json` | Native topology, roles and editor groups |
| `src/settings/celestial-settings.json` | Native stable-ID parameters |
| `src/utils/celestialSettingsSchema.js` | Validation and legacy import |
| `src/components/DeclarativeCelestialModel.jsx` | Live and plot model construction |
| `src/components/SunMarsRelativeOrbit.jsx` | Sun-relative Mars reconstruction |
| `src/components/VenusSunRelativeOrbit.jsx` | Sun-relative Venus reconstruction |
| `src/components/MercurySunRelativeOrbit.jsx` | Sun-relative Mercury reconstruction |
| `src/components/ErosSunRelativeOrbit.jsx` | Sun-relative Eros reconstruction |
| `src/components/MoonOrbitalPlane.jsx` | Lunar node/plane transform |
| `src/utils/plotModelFunctions.js` | Export-model updates and coordinates |
| `edits/binary_tychos.md` | Focused architecture explanation |
