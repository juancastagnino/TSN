# Full binary TYCHOS implementation

## Purpose and status

`full-binary-tychos` is an experimental completion of the accepted
`native-binary-system` hierarchy. It makes the numerical settings parent-relative,
not only the visible tree.

The migration is intentionally equivalence preserving. It does not claim new
astronomical accuracy and does not retune an orbit. Its purpose is to establish a
clean native baseline from which later TYCHOS geometry can be investigated.

## Hierarchy

```text
SystemCenter                         (PVP geometric reference)
└─ Earth                             (PVP path)
   ├─ Moon Node / Plane -> Moon
   └─ Sun-Mars Binary Frame
      └─ Sun Primary Branch -> Sun
         ├─ Mars Junior Companion -> Phobos / Deimos
         ├─ Venus Senior Solar Companion
         ├─ Mercury Junior Solar Companion
         ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
         ├─ Halley
         └─ Eros
```

This is an asymmetric primary/companion description. No conventional mass
barycentre, forced opposition or equal binary radius is introduced. `SystemCenter`
is an identity coordinate reference associated with Earth's PVP geometry, not a
physical body or cause of motion.

## Why another migration was needed

The preceding native hierarchy placed Mars, Mercury, Venus and Eros beneath the
Sun, but preserved exact coordinates by calculating each old absolute chain and
subtracting the old Sun chain at runtime:

```text
relative vector = old absolute body chain - old absolute Sun chain
```

That was a valid and tested coordinate adapter, but the child carrier settings
still contained the former Earth-level radius-100 motion. The code hierarchy was
native while part of the parameter vocabulary remained absolute.

The full migration algebraically decomposes each affected carrier into:

1. a constant centre already expressed relative to the Sun;
2. a three-dimensional annual residual stored as cosine and sine basis vectors;
3. the unchanged local orientation basis required by later deferent, plane and
   main-orbit stages.

The resulting evaluation is:

```text
body world position
  = inherited Sun world position
  + direct relative centre
  + direct annual residual
  + local descendant geometry
```

The child no longer repeats the Sun's radius-100 movement. It receives the Sun's
world position from its parent and contributes only what is unique to its branch.

## Direct carrier settings

The migrated carriers are `mars-deferent-e`, `mercury-deferent-a`,
`venus-deferent-a` and `eros-deferent-a`. Their `orbitRadius` is now zero.

The direct annual residual uses:

```text
R(t) = C cos(wt - phase) + S sin(wt - phase)
```

where `C` is stored in `relativeAnnualCosX/Y/Z`, `S` in
`relativeAnnualSinX/Y/Z`, and the angle uses `relativeAnnualSpeed` and
`relativeAnnualStart`.

| Carrier | Direct centre in model XYZ | Annual residual character |
|---|---:|---|
| Mars E | `(6.8, 0, -20.055)` | small Sun-plane remainder |
| Mercury A | `(-1.3, -0.5, 2.645)` | same small remainder |
| Venus A | `(-3.3, 0, 0.645)` | same small remainder |
| Eros A | `(-43.3, -0.5, 32.145)` | larger 3-D remainder from differing planes |

The table uses model XYZ order. JSON centre fields map as
`X=orbitCentera`, `Y=orbitCenterc`, `Z=orbitCenterb`.

The residual is not an empirical correction fitted to JPL. It is the exact
algebraic remainder of the accepted predecessor. A later physical experiment may
try to explain or simplify it, but it must not be silently discarded during the
migration.

## Inheritance semantics

The relative-frame adapter inherits the Sun's world **position** while retaining
the binary frame's axes for the accepted local orbital orientation. Blindly
inheriting every Sun rotation would rotate the child orbital planes again and is
not equivalent to the established TYCHOS geometry.

The remaining local stages are still meaningful:

- Mars deferent S and the Mars leaf define the companion path.
- Mercury/Venus deferent B, fixed plane and leaf define their local paths.
- Eros deferent B and leaf define its local path.
- Mercury deferent B has zero radius but a non-zero centre/orientation and is not
  an identity transform.

## Settings and import contract

[celestial-model.json](../src/settings/celestial-model.json) declares the topology,
roles and Edit Settings groups. [celestial-settings.json](../src/settings/celestial-settings.json)
stores the numerical model under ID `tychos-full-binary-system`.

The new annual fields are serialized and exposed in Edit Settings. Imports that
try to replace one of the four direct carriers with the former absolute format are
rejected. This prevents an invalid hybrid of old radius-100 values and new residual
fields. Ordinary legacy-name imports for other settings remain supported.

## Verification

The frozen source values in
`edits/scripts/derive_full_binary_settings.js` reproduce the accepted predecessor
over a dense -100 to +100 model-year grid.

| Gate | Result |
|---|---|
| Four direct carrier derivations | PASS |
| Maximum centre error | `2.3e-16` |
| Maximum annual error | `2.9e-14` |
| Source tests | 66 / 66 passed |
| Production build | PASS |
| Complete ten-body export | 759,756 non-metadata lines exactly identical |
| Direct Eros export | 75,969 displayed rows exactly identical |
| Sun–Mars diagnostic | Within `1e-9`; only floating-point roundoff |
| Apparent true-of-date summaries | Zero numerical delta for all ten bodies |
| Residual/annual/FFT artifacts | 30 of 30 byte-identical |

The fresh simulator export also passes against
`00-backup/native-relative-baseline`. The only difference in the combined
ephemeris file is its generation timestamp. This completes the structural
migration without a scientific coordinate change.

## After equivalence is confirmed

The clean hierarchy makes later questions easier to isolate:

- whether Mercury and Venus should share a physically defined solar-equatorial
  plane;
- whether any direct annual residual has a simpler TYCHOS geometric explanation;
- whether a local deferent can be removed without losing accepted observables;
- how transit-relative Mercury/Venus observables behave; and
- which changes improve independent intervals rather than only fitted data.

Those are physical-model experiments and may legitimately change ephemerides.
They should begin only after this migration's end-to-end equivalence is recorded.
