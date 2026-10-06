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

## Why the common annual residual is retained

Mars, Mercury and Venus currently share this direct annual definition:

```json
{
  "relativeAnnualStart": 0,
  "relativeAnnualSpeed": 6.283185307179586,
  "relativeAnnualCosX": 0,
  "relativeAnnualCosY": 0,
  "relativeAnnualCosZ": 0,
  "relativeAnnualSinX": 0,
  "relativeAnnualSinY": -0.4820580723705152,
  "relativeAnnualSinZ": -0.0011619066758328245
}
```

It is evaluated as:

```text
R(t) = C cos(wt - phase) + S sin(wt - phase)
```

`relativeAnnualSpeed = 2π` gives one cycle per model year. The maximum
displacement is approximately `0.482` internal model units and lies almost
entirely along model Y.

In the preceding implementation, Mars, Mercury and Venus each contained an
untilted annual carrier of radius `100`. The Sun also had a radius-100 annual
motion, but with a small inclination of approximately `0.2762°`. Their
body-minus-Sun calculation therefore cancelled almost all of the two carriers,
but not this small component:

```text
100 × sin(0.2762°) ≈ 0.48206
```

The explicit residual fields were introduced solely to retain that component
after removing the duplicated absolute carriers. They were not fitted to JPL and
do not represent a newly proposed perturbation. Keeping them is what allowed the
full hierarchy migration to preserve every accepted ephemeris value.

Relative to the current local orbital radii, their approximate maximum scale is:

| Body | Relative displacement | Simplified maximum angular scale |
|---|---:|---:|
| Mercury | `1.25%` | about `0.71°` |
| Venus | `0.67%` | about `0.38°` |
| Mars | `0.32%` | about `0.18°` |

These angles are geometric scale estimates, not predicted constant offsets or
RMS changes. The observed effect is annual and depends on date, viewing direction
and all later transforms. Removing the residual would therefore not shift every
body by the same `0.4°`.

The common term may ultimately prove to be an inherited frame convention rather
than three independent physical motions. Conceptually, removing it or replacing
it with a clearer shared solar-frame geometry is worth investigating. It remains
in the present baseline so that this structural migration stays exactly
equivalent to its accepted predecessor.

A controlled future experiment should:

1. create a separate branch from this baseline;
2. set the `relativeAnnualCos*` and `relativeAnnualSin*` fields of Mars, Mercury
   and Venus to zero, changing nothing else initially;
3. regenerate identical-cadence exports;
4. inspect Mercury/Venus Sun-relative positions at conjunctions and transits,
   latitude, declination, full-period RA/Dec and angular separation; and
5. decide whether the term should remain, be removed, or be replaced by an
   explicitly defined shared geometry.

Eros must be investigated separately. Its larger and differently oriented
residual comes from its own former carrier plane and is not the same common term.

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
