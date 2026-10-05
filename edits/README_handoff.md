# Developer / AI handoff

Read [README.md](README.md) for commands. This document records only the accepted
development baseline, interpretation constraints and next work. Generated reports
hold the detailed evidence for individual runs.

## Branch scope

This handoff describes **`development`**. It is the classic TYCHOS codebase used
for future controlled experiments. It currently includes:

- the accepted Moon Node/Plane implementation and lunar tuning;
- separate fixed Mercury and Venus planes that reproduce their original TYCHOS
  transforms;
- original Mercury, Venus and Pluto orbital settings otherwise;
- the classic Earth-level Mercury, Venus, Mars and Eros carrier chains; and
- the existing Sun-hosted outer planets and Halley.

The branch excludes Observer Trace, the native binary/declarative schema, moving
Mercury/Venus nodes and earlier eccentric or synodic refinement experiments.

## Current hierarchy

```text
SystemCenter                         (fixed PVP coordinate reference)
└─ Earth                             (moves on the PVP path)
   ├─ Moon Node / Plane
   │  └─ Moon deferent A -> Moon
   ├─ Sun deferent -> Sun
   │  ├─ Jupiter / Saturn / Uranus / Neptune / Pluto
   │  └─ Halley
   ├─ Venus deferent A / B -> Venus Plane -> Venus
   ├─ Mercury deferent A / B -> Mercury Plane -> Mercury
   ├─ Mars deferent E / S -> Mars -> Phobos / Deimos
   └─ Eros deferent A / B -> Eros
```

`SystemCenter` has no independent dynamics. It stores the coordinate reference
associated with the geometric centre of Earth's PVP orbit; it is not a celestial
body, physical barycentre or cause of motion. The centre is an attribute of the
PVP path even though the software evaluates the path from that reference.

The hierarchy remains intentionally classic on this branch. The later native
Sun-relative binary architecture belongs to another branch and must not be copied
here accidentally.

## Accepted Moon baseline

```text
Earth
└─ Moon Node -> Moon Plane -> node counter-rotation
   └─ Moon deferent A
      └─ Moon
```

`Moon deferent B` was an all-zero identity layer and remains removed. Node
precession is implemented by `MoonOrbitalPlane.jsx`.

| Entry | Retained values |
|---|---|
| Moon Node | `startPos=-296`, `speed=-0.33780566` |
| Moon Plane | centres `0.001, 0.002, 0`; tilts `0, -5.15` |
| Moon deferent A | `startPos=167.51`, `speed=0.71015440177343`, `radius=0.02786` |
| Moon | `startPos=318.0`, `speed=83.2851946`, `radius=0.25505129081458283` |

Accepted 2000-2026 three-hour JPL ICRF comparison:

| Metric | RMS |
|---|---:|
| RA coordinate | `1.098461°` |
| Declination | `0.391893°` |
| Angular separation | `1.115662°` |
| Ecliptic longitude | `1.094302°` |
| Ecliptic latitude | `0.228328°` |

Mean longitude error is `-0.002219°`. The paired phase/radius adjustment reduced
the fitted anomalistic-month residual from about `0.9947°` to `0.0059°`. The
remaining evection-frequency, variation-frequency and annual residuals are
diagnostics, not correction terms. Do not tune `Moon.speed` merely to cancel a
long-term fit before resolving the coordinate-frame question.

## Mercury and Venus plane baseline

The explicit planes are an architectural re-expression of the original geometry:

```text
Mercury deferent A -> Mercury deferent B -> Mercury Plane -> Mercury
Venus deferent A   -> Venus deferent B   -> Venus Plane   -> Venus
```

The former planet-level centres and tilts were moved into zero-speed, zero-radius
plane objects; the corresponding planet fields were reset. A 5,000-date in-memory
comparison found no coordinate change beyond floating-point noise, and the later
simulator export confirmed the baseline over 75,969 three-hour samples.

| Entry | Retained geometry |
|---|---|
| Mercury deferent B | `startPos=33`, `radius=0.6`, tilts `-1.3, 0.5` |
| Mercury Plane | centres `0, 3, -0.1`, tilts `3, 0.5` |
| Mercury | `startPos=-180.8`, `speed=26.08763045`, `radius=38.710225` |
| Venus deferent B | `startPos=16.6`, `radius=0.6`, `orbitCenterb=0.65` |
| Venus Plane | `orbitCenterb=-0.9`, tilts `3.2, -0.05` |
| Venus | `startPos=-23.6`, `speed=10.21331385`, `radius=72.327789` |

The confirmed angular-separation RMS values were `2.605186°` for Mercury and
`0.749226°` for Venus on the saved 2000-2026 baseline. Transit-relative RMS was
approximately `23.029 arcmin` for four Mercury transits and `12.934 arcmin` for
two Venus transits. These are baselines, not optimized results.

Do not add moving nodes, an eccentric layer or a shared plane silently. A
solar-equatorial experiment is new geometry and should compare planet-minus-Sun
offsets at transit epochs as its primary targeted diagnostic.

## Reference-frame contract

The native TYCHOS export is not established to be the same product as JPL
astrometric ICRF RA/Dec. Residuals may combine orbital and coordinate-convention
differences.

- Use a TYCHOS J2000 comparison export with `--reference icrf` when available.
- Use the classic/native export with `--reference apparent-of-date` only as an
  exploratory moving-frame comparison.
- JPL apparent-of-date also includes light-time, deflection, aberration, precession
  and nutation; coordinate agreement would not establish common mechanisms.
- Translation along the PVP path and rotation of coordinate axes are separate.
- Define origin, pole, zero-RA direction, epoch and time scale before tuning a
  planet to compensate for long-term drift.

## Research constraints

1. Never add fitted perturbations or empirical corrections to simulator output.
2. Preserve the settings, raw exports, configuration, reports and label for every
   retained baseline.
3. State one geometric hypothesis and change one layer at a time.
4. Keep bodies, timestamps, cadence and reference product identical in comparisons.
5. Inspect RA, declination, angular separation, longitude, latitude and relevant
   body-relative events.
6. Treat spectral and machine-learning fits as diagnostics only.
7. Validate retained parameter changes on an interval not used for selection.

## Next investigations

1. **Solar-equatorial hypothesis:** test shared versus separate Mercury/Venus plane
   orientations, prioritizing transit-relative offsets and using all-date metrics
   as guards.
2. **Lunar residual structure:** measure the evection and variation arguments in
   TYCHOS and JPL separately rather than fitting them as corrections.
3. **Reference-frame definition:** document the intended native axes and compare
   equivalent observables before tuning long-term trends.
4. **Out-of-sample validation:** verify accepted lunar and future planetary changes
   on a predeclared independent interval.

## Key files

| File | Responsibility |
|---|---|
| `src/settings/celestial-settings.json` | Accepted numerical settings |
| `src/settings/misc-settings.json` | Editor grouping and non-orbital controls |
| `src/components/SolarSystem.jsx` | Visible classic hierarchy |
| `src/components/PlotSolarSystem.jsx` | Plot/export classic hierarchy |
| `src/components/MoonOrbitalPlane.jsx` | Lunar node/plane transform |
| `src/components/Cobj.jsx` / `Pobj.jsx` | Live/export transform conventions |
| `src/utils/plotModelFunctions.js` | Export-model motion and coordinates |
| `edits/scripts/investigate_moon_tuning.py` | Read-only lunar screening |
| `edits/scripts/investigate_planet_tuning.py` | Read-only planetary screening |
| `edits/scripts/diagnose_solar_satellite_residuals.py` | Mercury/Venus residual attribution |
