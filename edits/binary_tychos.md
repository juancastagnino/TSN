# Full binary TYCHOS implementation

## Purpose and status

`full-send-binary-tychos` is an experimental completion of the accepted
`native-binary-system` hierarchy. It makes the numerical settings parent-relative,
not only the visible tree.

The migration is intentionally equivalence preserving. It does not claim new
astronomical accuracy and does not retune an orbit. Its purpose is to establish a
clean native baseline from which later TYCHOS geometry can be investigated.

The active model now takes one explicit refinement beyond that equivalence
baseline: the common annual residual of Mars, Mercury and Venus is absent.
This decision improves several mean biases but modestly worsens their aggregate
RMS values. The exact equivalence-preserving values remain documented below and
in `00-backup/full-binary-baseline`.

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

The original residual was not an empirical correction fitted to JPL. It was the exact
algebraic remainder of the accepted predecessor. A later physical experiment may
try to explain or simplify it, but it must not be silently discarded during the
migration.

## Original common annual residual: historical restoration reference

The equivalence-preserving migration originally gave Mars, Mercury and Venus the
same annual definition. Schema v3 removes these parameters entirely; these
complete original blocks are retained here for deliberate restoration:

```json
{
"mercury-deferent-a": {
  "relativeAnnualStart": 0,
  "relativeAnnualSpeed": 6.283185307179586,
  "relativeAnnualCosX": 0,
  "relativeAnnualCosY": 0,
  "relativeAnnualCosZ": 0,
  "relativeAnnualSinX": 0,
  "relativeAnnualSinY": -0.4820580723705152,
  "relativeAnnualSinZ": -0.0011619066758328245
},
"venus-deferent-a": {
  "relativeAnnualStart": 0,
  "relativeAnnualSpeed": 6.283185307179586,
  "relativeAnnualCosX": 0,
  "relativeAnnualCosY": 0,
  "relativeAnnualCosZ": 0,
  "relativeAnnualSinX": 0,
  "relativeAnnualSinY": -0.4820580723705152,
  "relativeAnnualSinZ": -0.0011619066758328245
},
"mars-deferent-e": {
  "relativeAnnualStart": 0,
  "relativeAnnualSpeed": 6.283185307179586,
  "relativeAnnualCosX": 0,
  "relativeAnnualCosY": 0,
  "relativeAnnualCosZ": 0,
  "relativeAnnualSinX": 0,
  "relativeAnnualSinY": -0.4820580723705152,
  "relativeAnnualSinZ": -0.0011619066758328245
}
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

The common term may represent an inherited frame convention rather than three
independent physical motions. It has therefore been removed from the active
settings while its original values remain above as a reversible reference.

The zero-residual experiment found:

- Mercury absolute RA mean improved by `80.8%`, while angular RMS worsened by
  `0.42%`.
- Venus absolute RA mean improved by `32.0%` and angular mean by `3.2%`, while
  angular RMS worsened by `3.0%`.
- Mars absolute declination mean improved by `2.5%`, while angular RMS worsened by
  `3.9%`.
- Sun, Moon and all outer planets remained unchanged.

The active choice prioritizes the cleaner parent-relative geometry and improved
mean biases, while retaining the option to restore the former values or refine
local planes, centres and phases. Full results are in
[`zero_common_annual_residual_report.md`](reports/zero_common_annual_residual_report.md).

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

[celestial-model.json](../src/settings/celestial-model.json) is the schema-v3
single source of truth under ID `tychos-unified-binary-system`. It contains:

- the PVP reference frame;
- one record for each real celestial body and its `parentId`;
- every body's named `motion` components and numerical parameters;
- hierarchy-aware Edit Settings groups; and
- an internal `renderTree` that compiles the ordered transforms.

There is no separate `celestial-settings.json`. Nodes, planes and deferents are
motion terms owned by a body rather than entries in the astronomical body list.
The Edit Settings panel follows this same body/component structure, and its Save
action writes a complete reusable unified model.

Mercury, Venus and Mars have no `relativeAnnual*` properties. Eros retains those
fields because its distinct non-zero harmonic remains active and is exposed in
Edit Settings. Imports that try to restore any former radius-100 absolute carrier
are rejected. Stable component IDs and legacy-name imports remain supported.

## Verification

The final schema-v3 unification was exported and compared with the saved
zero-residual full-binary baseline. Moving hierarchy and settings into one file,
and nesting the 36 motion components inside 15 real body records, caused no
coordinate change.

The frozen source values in
`edits/scripts/derive_full_binary_settings.js` reproduce the accepted predecessor
over a dense -100 to +100 model-year grid.

| Gate | Result |
|---|---|
| Four direct carrier derivations | PASS |
| Maximum centre error | `2.3e-16` |
| Maximum annual error | `2.9e-14` |
| Source tests | 67 / 67 passed |
| Production build | PASS |
| Complete ten-body export | 759,756 non-metadata lines exactly identical |
| Direct Eros export | 75,969 displayed rows exactly identical |
| Sun–Mars diagnostic | All recorded numeric deltas exactly zero |
| Apparent true-of-date summaries | Zero numerical delta for all ten bodies |
| Residual/annual/FFT artifacts | 30 of 30 byte-identical |

The equivalence-baseline simulator export passes against
`00-backup/full-binary-baseline`. The only difference in that combined
ephemeris file is its generation timestamp. This completes the structural
migration without a scientific coordinate change. The active zero-residual
settings are a subsequent, intentional ephemeris refinement and are not expected
to pass this exact-equivalence gate.

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
