# TYCHOS Edit Settings guide

## Purpose

This guide explains how to adjust the native binary TYCHOS model without losing
track of what each setting controls. It is an operating manual for geometric
experiments, not a list of recommended corrections.

Before beginning, read [binary_tychos.md](binary_tychos.md). This branch is a
direct parent-relative migration whose algebraic and software gates pass. Complete
the fresh-export equivalence gate before accepting any physical retuning.

## The three layers of the model

Keep these layers separate when interpreting an edit:

1. `src/settings/celestial-model.json` declares the topology, astronomical roles,
   dependencies and Edit Settings groups.
2. `src/settings/celestial-settings.json` contains the numerical parameters,
   identified by stable IDs.
3. Native relative evaluators combine the direct parent-relative carrier fields
   with the local deferent, plane and body settings.

Use the Edit Settings panel for ordinary parameter experiments. Change the model
schema only when testing a different astronomical hierarchy.

## First rule: identify the geometric layer

Do not start by asking which number reduces RMS. Start by asking which geometric
part could produce the observed residual.

| Setting layer | Typical effect | Examples |
|---|---|---|
| Phase and rate | Along-orbit timing, accumulated longitude phase | `startPos`, `speed` |
| Orbital scale | Size of the local path | `orbitRadius` |
| Orbit centre | Constant or rotating displacement of a stage | `orbitCentera`, `orbitCenterb`, `orbitCenterc` |
| Orbital plane | Latitude/declination geometry and node orientation | `orbitTilta`, `orbitTiltb` |
| Direct annual residual | Parent-relative annual vector that did not cancel in migration | `relativeAnnualCos*`, `relativeAnnualSin*`, `relativeAnnualSpeed`, `relativeAnnualStart` |
| Appearance/spin | Rendering or axial rotation, usually not orbital position | `size`, `actualSize`, `tilt`, `tiltb`, `rotationStart`, `rotationSpeed` |

An Euler control such as `orbitTilta` is not automatically the physical
inclination printed in an astronomy reference. Its physical effect depends on
the parent axes, transform order and other rotations in the chain.

## Dependency rules

- A Sun or Sun-deferent change is global: recheck every Sun-hosted descendant.
- A Mars change also affects Phobos and Deimos because they inherit Mars's frame.
- Mercury and Venus each have a carrier, secondary stage, fixed plane and leaf
  orbit. Edit only the layer associated with the hypothesis being tested.
- The migrated Mars E, Mercury A, Venus A and Eros A carriers have zero orbital
  radius. Their annual remainder is stored explicitly in `relativeAnnual*`; their
  normal phase/speed/tilt fields still define the local orientation basis.
- Moon experiments are independent of solar-companion tuning and should be kept
  in a separate trial.
- A zero `orbitRadius` does not guarantee that a stage is irrelevant. Its centre
  and orientation may still alter descendant coordinates.
- Do not treat the `relativeAnnual*` vectors as generic correction knobs. They
  encode an exact predecessor component; changing them requires a stated
  geometric hypothesis and a full descendant regression.
- Former absolute carrier files cannot be merged into this model. Migrate the
  affected carrier fields explicitly instead of restoring radius-100 child paths.

## Safe experiment workflow

### 1. Freeze the baseline

Preserve together:

- the settings file used for the export;
- the TYCHOS and reference ephemerides;
- `analysis_config.json` and `bodies.json`;
- the complete generated reports; and
- the exact branch/commit and a short experiment label.

Do this before changing settings or replacing an export. A report without its
input files and settings snapshot is not a reproducible baseline.

### 2. Write one hypothesis

Record:

- the target body;
- the setting layer being tested;
- the observable expected to change;
- the metrics that must not become materially worse; and
- the training and withheld validation intervals.

Example: “Mercury's latitude residual may reflect an incorrect fixed-plane
orientation. Vary the Mercury Plane orientation only; do not change phase,
speed, radius, centres or deferents.”

### 3. Make the smallest interpretable trial

Change one parameter at a time initially. Use equal positive and negative probes
around the baseline. This reveals direction and sensitivity before attempting a
fine search. Do not change a plane, deferent and planet leaf in the same first
trial.

### 4. Regenerate the TYCHOS export

The analysis configuration does not regenerate or trim simulator output. Export
the same bodies, timestamps, cadence and reference-frame convention used by the
baseline.

When only settings change, the matching JPL file can normally be reused. When the
time grid, bodies or reference convention changes, regenerate the reference.

### 5. Analyze with an explicit label and snapshot

For a Mercury/Venus/Sun experiment:

```powershell
python.exe -B edits/scripts/run_analysis.py mercury venus sun `
  --reference apparent-of-date `
  --label "Mercury Plane orbitTilta +0.25 deg; all other settings unchanged" `
  --export-settings src/settings/celestial-settings.json
```

The example assumes the normal TYCHOS native/PVP export. Use `--reference icrf`
instead only when the TYCHOS file was explicitly exported in the J2000 comparison
frame. Use `--reference both` when auditing both JPL products, remembering that a
single TYCHOS export does not simultaneously belong to both frames.

The label and snapshot are declarations of what produced the export; the script
cannot verify them against a previously generated file. Save the settings before
exporting and do not edit them again until the export and analysis are complete.

### 6. Judge a group of metrics

At minimum inspect:

- RA mean and RMS;
- declination mean and RMS;
- longitude mean and RMS;
- latitude mean and RMS;
- total angular-separation mean, RMS, P95 and maximum;
- annual changes and residual periods; and
- any relevant event-relative observable.

Mean measures systematic bias; RMS measures typical scatter including that bias.
A lower mean with a worse RMS is not an unqualified improvement. For Mercury and
Venus, inspect planet-minus-Sun offsets at conjunctions and transits in addition
to all-date absolute coordinates.

### 7. Validate outside the tuning interval

Select a candidate on one interval and test the unchanged values on another.
Use identical sampling when comparing candidates. Do not compare metrics from a
three-hour 26-year run directly with a daily 226-year run.

### 8. Accept, reject or revert explicitly

Retain a change only when:

- it behaves in the predicted geometric direction;
- the target metrics improve consistently;
- guard metrics and dependent bodies remain acceptable;
- the improvement survives a withheld interval; and
- the change has a coherent TYCHOS interpretation.

An unexplained reduction in aggregate RMS is evidence for further investigation,
not sufficient reason to make a setting permanent.

## Worked example: investigating Mercury's plane

### Question

The present coordinate-preserving baseline has separate Mercury and Venus plane
objects. The author's structural notes propose that both solar companions are
coplanar with the Sun's equatorial plane, approximately 6–7 degrees relative to
the wider planetary reference.

The current plane controls are:

| Setting | `startPos` | Centre A/B/C | `orbitTilta` | `orbitTiltb` |
|---|---:|---:|---:|---:|
| Mercury Plane | 0.00° | 10.8 / 4.0 / 0.0 | -4.0° | -3.0° |
| Venus Plane | -0.25° | 1.8 / -0.4 / 0.0 | 3.4° | 0.3° |

These numbers must not be compared directly as physical inclinations. They act
inside different inherited transforms and include plane-centre offsets.

### Experiment A: local sensitivity

Keep every setting fixed except one Mercury Plane angle. Use small symmetric
probes, for example:

```text
Baseline: orbitTilta = -4.00°, orbitTiltb = -3.00°

Trial A1: orbitTilta = -4.25°
Trial A2: orbitTilta = -3.75°
Trial B1: orbitTiltb = -3.25°
Trial B2: orbitTiltb = -2.75°
```

Do not change the plane centre, Mercury leaf or either Mercury deferent during
this screen. For each trial compare Mercury latitude, declination and angular
separation, then verify that longitude/RA and transit-relative offsets have not
degraded unexpectedly.

The purpose is not to declare one of these four values correct. It is to learn:

- which control rotates the plane in the required direction;
- how sensitive the residual is to each axis;
- whether the error is approximately constant or time-dependent; and
- whether a plane edit helps only latitude or also total direction.

If neither sign produces a consistent response, the residual may not originate
in this plane layer, or the relevant direction may require a coupled two-axis
rotation.

### Experiment B: determine physical plane normals

Before imposing a common plane, calculate or display the actual world-space plane
normal for Mercury, Venus and the Sun's equator at a declared epoch. This removes
the ambiguity of comparing raw Euler controls. The experiment should record:

- reference epoch;
- coordinate frame;
- plane normal or inclination plus ascending-node direction; and
- angular separation between the three normals.

This diagnostic is preferable to copying Venus's raw `orbitTilt*` values into
Mercury, because identical local Euler values do not necessarily produce an
identical world-space plane under different parent transforms.

### Experiment C: explicit shared solar-equatorial plane

If the theoretical requirement is confirmed, implement a separate experimental
branch with one declared `Solar Equatorial Plane` parent shared by Mercury and
Venus. Define its epoch and orientation explicitly. Preserve any genuinely local
centre or phase terms below that parent rather than hiding them in the shared
plane.

This is a hierarchy/physical-geometry experiment, so exact equivalence is not
expected. Compare it against the frozen native baseline using:

- Mercury, Venus and Sun full-interval metrics;
- Mercury and Venus transit/conjunction offsets relative to the Sun;
- the proposed 1,000-year and 2,000-year recurrence observables;
- at least one withheld interval; and
- a full-system regression for unintended descendant changes.

The shared-plane model should be accepted because it satisfies a clearly defined
TYCHOS geometry and produces defensible observations—not simply because one RMS
number happens to fall.

## What not to do

- Do not tune directly against generated comparison CSV values by adding an
  empirical correction to exported RA/Dec.
- Do not mix native/PVP and J2000/ICRF exports in one comparison.
- Do not infer a physical plane angle from one raw Euler field.
- Do not change global Sun geometry to repair Mercury alone.
- Do not assume that the all-date JPL RMS is the only meaningful Mercury/Venus
  criterion; retain event-relative tests.
- Do not overwrite the only known-good settings file or report set.
- Do not interpret an equivalence test as an accuracy test, or an accuracy gain
  as proof of the proposed physical mechanism.

## Recommended experiment record

Use this short template for every retained trial:

```text
Experiment:
Branch/commit:
Baseline files:
Bodies, interval, cadence and coordinate frame:
Hypothesis:
Changed stable setting IDs and old/new values:
Expected effect:
Primary metrics:
Guard metrics and dependent bodies:
Event checks:
Training result:
Withheld-interval result:
Decision and reason:
```

This discipline allows another developer or author to reproduce the result and
understand why a setting was changed, rather than inheriting an unexplained set
of optimized numbers.
