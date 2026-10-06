# Developer / AI handoff

This handoff describes the experimental **`full-binary-tychos`** branch. See
[README.md](README.md) for analysis commands and [binary_tychos.md](binary_tychos.md)
for the design rationale.

## Current state

The accepted predecessor is `native-binary-system`. Its complete reports and raw
exports are preserved under `00-backup/native-relative-baseline`.

This branch completes the parent-relative settings migration without deliberately
changing any accepted orbit:

- Earth supplies the PVP motion.
- The Sun inherits Earth and supplies the solar-system position.
- Mars, Mercury, Venus and Eros inherit the Sun's world position.
- Their former absolute radius-100 A/E carriers have been replaced by direct
  parent-relative centres and explicit annual residual vectors.
- Their local S/B stages, fixed planes and body orbits retain the accepted values
  and matrix order.
- Jupiter, Saturn, Uranus, Neptune, Pluto and Halley were already Sun-hosted.
- The Moon remains Earth-hosted; Phobos and Deimos remain Mars-hosted.

After equivalence was proven, the common annual cosine/sine residual of Mars,
Mercury and Venus was intentionally set to zero. This is now the active setting.
The exact equivalence version and reports remain in
`00-backup/full-binary-baseline`, and its original residual values are preserved
in [binary_tychos.md](binary_tychos.md).

```text
SystemCenter
└─ Earth
   ├─ Moon Node / Plane -> Moon
   └─ Sun-Mars Binary Frame
      └─ Sun Primary -> Sun
         ├─ Mars Junior Companion -> Phobos / Deimos
         ├─ Venus Senior Solar Companion
         ├─ Mercury Junior Solar Companion
         ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
         ├─ Halley
         └─ Eros
```

`SystemCenter` is the fixed geometric reference of Earth's PVP path, not a body or
barycentre. The model remains Tychonic: Earth follows the PVP path, the Sun is
positioned relative to Earth, and the solar subsystem is organized beneath the
Sun.

## What is genuinely different

Previously the code evaluated each affected body from its old absolute chain and
subtracted the current Sun chain at runtime. Now the settings themselves contain
the already-derived parent-relative quantities:

```text
body world position
  = inherited Sun world position
  + direct relative centre
  + direct annual residual
  + local deferent / plane / body orbit
```

The migrated carrier IDs are:

- `mars-deferent-e`
- `mercury-deferent-a`
- `venus-deferent-a`
- `eros-deferent-a`

All four have `orbitRadius: 0`. Their annual remainder is stored in
`relativeAnnualCos*` and `relativeAnnualSin*` fields. The normal phase, speed and
tilt fields retain the local orientation basis required by descendant stages.

Old absolute-carrier files are rejected for these four entries rather than being
silently mixed with the new model. Other stable-ID and legacy-name imports remain
supported.

## Verification completed

| Gate | Result |
|---|---|
| Dense direct-settings audit, -100 to +100 model years | PASS for all four carriers |
| Maximum centre reconstruction error | `2.3e-16` |
| Maximum annual reconstruction error | `2.9e-14` |
| Source tests | 66 passed across 12 suites |
| Production build | PASS; only third-party MediaPipe source-map warnings |
| Complete ten-body TYCHOS export | PASS; 759,756 non-metadata lines identical |
| Direct Eros export | PASS; 75,969 displayed rows identical |
| Sun–Mars binary CSV | PASS within `1e-9`; differences are floating-point noise |
| Ten-body apparent true-of-date summaries | PASS; zero numerical delta |
| Residual, annual and FFT artifacts | PASS; 30 of 30 byte-identical |

Run the gates with:

```powershell
node edits/scripts/derive_full_binary_settings.js
npm test -- --watchAll=false --runInBand
npm run build
```

## End-to-end result

The fresh exports use the baseline bodies, interval, cadence and native frame.
They confirm complete displayed-coordinate equivalence with
`00-backup/native-relative-baseline`.

The combined files differ only in their `Generated on` timestamp. Eros is
identical in RA, declination, distance and elongation. The high-precision binary
CSV differs only around `1e-14`, plus `acos` endpoint sensitivity below
`1.21e-6°`; both are numerical roundoff.

After exporting and running the normal analysis:

```powershell
python.exe -B edits/scripts/compare_raw_tychos_exports.py
python.exe -B edits/scripts/compare_tychos_body_exports.py
```

Both saved and candidate report sets now use JPL apparent true-of-date, so the
scientific summary/artifact gate is valid and passes. Keep this reference product
identical in future before/after comparisons; do not compare these values directly
with an ICRF report set.

The structural migration is complete. The active zero-residual refinement improves
several mean biases but worsens angular RMS by `0.42%` for Mercury, `3.0%` for
Venus and `3.9%` for Mars. The decision currently prioritizes the cleaner geometry
and mean values; local refinement and independent-interval validation remain open.

## Key files

| File | Responsibility |
|---|---|
| `src/settings/celestial-model.json` | Full hierarchy and editor groups |
| `src/settings/celestial-settings.json` | Direct parent-relative parameters |
| `src/utils/nativeRelativeCarrier.js` | Direct centre/residual/orientation evaluator |
| `src/utils/celestialSettingsSchema.js` | Serialization and safe import rules |
| `src/components/*SunRelativeOrbit.jsx` | Local branch stages beneath the Sun |
| `edits/scripts/derive_full_binary_settings.js` | Frozen-baseline migration audit |

## Constraints

- Do not tune parameters until the fresh-export equivalence gate passes.
- Do not restore radius-100 carriers beneath the Sun.
- Do not treat a zero-radius stage as redundant if it retains centre/orientation.
- Keep reference-frame comparison separate from orbital tuning.
- Preserve the baseline settings, exports, configuration and reports together.
