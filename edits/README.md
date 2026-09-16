This directory is intended to make the experiment reproducible and to provide
enough technical context for either a human developer or an AI coding agent
to continue the investigation from the current branch.

# Experimental Lunar Orbit Adjustment

This folder documents an experimental adjustment to the lunar geometry
used by the Tychosium simulator.

The purpose of this work is not to replace the TYCHOS lunar model with a
conventional analytical lunar theory. The goal is to preserve the existing
compact geometrical model while improving the Moon's calculated ephemerides.

## Initial problem

A comparison between Tychosium and JPL Horizons showed that the original
lunar longitude was already reasonably reproduced, while the largest errors
occurred in declination and ecliptic latitude.

Over the 2000–2026 test interval, the original model produced approximately:

- RMS declination error: ~3.55°
- RMS angular separation: ~4.11°
- RMS ecliptic longitude error: ~1.81°

The original lunar geometry produced only about ±1° of ecliptic latitude,
while the observed Moon reaches approximately ±5.1°.

## Main modification

Instead of modifying the Moon's orbital speed or the existing deferents, an
independent precessing lunar orbital plane was introduced.

The transformation is conceptually:

    Ry(Ω) Rx(i) Ry(-Ω)

where:

- i ≈ 5.15° is the inclination of the lunar orbital plane
- Ω regresses with a period of approximately 18.6 years

This behaves like a tilted rigid disc whose orientation slowly rotates,
without adding the nodal rotation directly to the Moon's orbital longitude.

A small React/Three.js component named `MoonOrbitalPlane` implements this
coordinate transformation.

## Result

After calibrating the nodal phase, the modified model produced approximately:

- RMS declination error: ~0.68°
- maximum declination error: ~2.06°
- RMS angular separation: ~1.85°
- RMS ecliptic longitude error: ~1.80°

The important point is that the large improvement in declination was obtained
without materially changing the longitude already produced by the original
TYCHOS lunar model.

## Residual longitude

A higher-resolution comparison using six-hour samples revealed that most of
the remaining longitudinal error is highly periodic.

Strong components occur near:

- 27.55 days
- 31.81 days
- 14.77 days
- 1 year

The ~31.8-day component has an amplitude close to the classical lunar
evection (~1.274°).

This is particularly interesting in the context of the TYCHOS model, because
the TYCHOS book relates the Moon's evection and other apparent inequalities
to the geometry of the Earth-Moon system and Earth's slow PVP motion.

No attempt has yet been made here to add conventional perturbation terms.
The residual analysis is included so that these signals can instead be
investigated within the geometry proposed by the TYCHOS model.

## PVP ephemeris test

An additional A/B test was performed by generating otherwise identical lunar
ephemerides with Earth's PVP orbital speed enabled and disabled.

For the current geocentric ephemeris routine, the resulting lunar RA and Dec
were identical to numerical precision.

This suggests that the present ephemeris calculation removes the common Earth
transformation when converting the Moon back into the terrestrial reference
frame.

This does not necessarily mean that the PVP geometry is absent from the 3D
simulation. It means that its effect does not currently appear in this
particular geocentric ephemeris output.

## Files

- `scripts/compare_ephemerides.py`
  Parses and compares JPL Horizons and Tychosium ephemerides.

- `scripts/analyze_lunar_residuals.py`
  Computes error statistics and searches the longitude residual for periodic
  components.

- `scripts/pvp_ab_test.py`
  Compares PVP-enabled and PVP-disabled ephemerides.

- `reports/`
  Contains reproducible numerical summaries of the tests.

## Reference ephemeris

JPL Horizons:
- Target: Moon (301)
- Center: Earth (399), geocentric
- Reference frame: ICRF
- Ephemeris source: DE441
- High-resolution tests: 6-hour intervals

### Why a 6-hour sampling interval?

Early comparisons used a 7-day interval, which was sufficient for measuring
long-term positional accuracy and the lunar nodal behaviour.

For residual-frequency analysis, however, a much denser sampling interval was
needed. A 6-hour cadence resolves the major monthly and semi-monthly lunar
signals comfortably while keeping the 26-year dataset reasonably small.

The 6-hour dataset therefore became the reference dataset for the detailed
lunar residual analysis.

## Running the analysis scripts

The scripts were developed and tested on Windows from the root of the TSN repository.

python 3.11 or higher required
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r edits/scripts/requirements.txt

The examples below assume the repository has this structure:

TSN/
├── .venv/
├── edits/
│   ├── data/
│   │   ├── raw/
│   │   │   ├── tychos_moon_2000-2026_6h.txt
│   │   │   └── jpl_moon_de441_2000-2026_6h.txt
│   │   └── derived/
│   ├── reports/
│   └── scripts/
│       ├── compare_ephemerides.py
│       ├── analyze_lunar_residuals.py
│       ├── generate_report.py
│       └── requirements.txt

## IMPORTANT FOR TYCHOS AUTHORS

## Detailed interpretation of the 2000–2026 lunar ephemeris test

The high-resolution comparison contains 37,985 samples at a six-hour
cadence, spanning 21 June 2000 through 21 June 2026.

JPL Horizons DE441 geocentric ICRF astrometric coordinates were used as the
reference. Both datasets were transformed to ecliptic coordinates using a
fixed J2000 obliquity of 23.439291111°.

### 1. The orbital-plane correction solved most of the original declination problem

The modified lunar geometry produces:

- Declination RMS: **0.680°**
- Median absolute declination error: **0.468°**
- 95th percentile absolute declination error: **1.373°**
- Maximum absolute declination error: **2.187°**

This should be compared with the original Tychosium lunar model, whose
declination RMS over the same general epoch was approximately **3.55°**.

The improvement is therefore not a small calibration effect. Most of the
large original declination discrepancy was caused by the representation of
the lunar orbital plane.

Importantly, this improvement was obtained without materially changing the
original model's longitudinal behavior.

### 2. The remaining ecliptic-latitude error contains a substantial constant bias

The ecliptic-latitude residual is:

- Mean: **-0.396°**
- RMS: **0.466°**
- Median absolute error: **0.397°**
- 95th percentile: **0.808°**
- Maximum absolute error: **1.141°**

The fact that the mean residual (-0.396°) is close to the total RMS
(0.466°) is noteworthy.

Removing only the mean bias would reduce the centered latitude RMS to
approximately **0.245°**.

This suggests that a significant fraction of the remaining latitude error is
not random or strongly time-dependent, but resembles a persistent offset in
the lunar-plane geometry.

For that reason, further improvement of latitude may be possible without
introducing additional high-frequency lunar perturbations.

### 3. Longitude is now the dominant limitation of the model

The ecliptic-longitude residual is:

- Mean: **-0.280°**
- RMS: **1.796°**
- Median absolute error: **1.327°**
- 95th percentile: **3.291°**
- Maximum absolute error: **4.101°**

This is essentially the same longitudinal accuracy that existed before the
orbital-plane modification.

That result is important because it shows that the new nodal/inclination
geometry is largely decoupled from the original TYCHOS lunar longitude.

In other words, the modification improved the lunar orbital plane while
preserving the part of the original model that was already working.

### 4. Almost all of the longitudinal residual is deterministic

The most striking result of the high-resolution analysis is that the
longitudinal residual is highly periodic rather than noise-like.

A simultaneous least-squares fit using four periods:

- ~14.765 days
- ~27.555 days
- ~31.812 days
- ~365.256 days

reduces the longitude RMS from:

**1.7961° → 0.1034°**

This corresponds to approximately:

**99.66% of the longitudinal residual variance explained**

by only four periodic components plus an offset and a small linear trend.

The remaining RMS is therefore only about:

**0.103° ≈ 6.2 arcminutes**

after those dominant periodic structures are removed.

This is an important distinction.

The current ~1.8° longitudinal RMS does not represent an intrinsically
irregular or unpredictable failure of the geometrical model. Almost all of
it is concentrated in a very small number of coherent periodic signals.

### 5. The ~31.8-day component closely matches lunar evection

One of the strongest fitted residual components has:

- Period: approximately **31.812 days**
- Amplitude: approximately **1.274°**

This is extremely close to the conventional amplitude and period associated
with lunar evection.

Likewise, another residual component near 14.765 days has an amplitude close
to the classical lunar variation, while an annual component is also clearly
present.

These labels describe the observational periodicities only. No conventional
perturbation terms have been added to Tychosium in this experiment.

This distinction is intentional.

The TYCHOS book proposes geometrical explanations for several apparent lunar
inequalities, particularly evection, involving the Earth-Moon system and
Earth's slow PVP motion. The purpose of this analysis is therefore to
identify what remains in the ephemeris before deciding how those signals
should be represented in the TYCHOS geometry.

### 6. Additional periodic terms provide very little improvement

The four-component fit leaves an RMS residual of:

**0.10336°**

while the extended ("full") periodic fit reduces this only to:

**0.10012°**

The difference is very small.

This suggests that the first-order longitudinal problem is already captured
almost completely by the four dominant periods.

Adding progressively more periodic terms would therefore risk increasing
model complexity while producing relatively little additional accuracy.

For a model whose main strength is geometrical compactness, this is an
important result.

### 7. A small secular drift remains

The simultaneous fit also finds a linear longitude trend of approximately:

**3.77 × 10⁻⁵ degrees/day**

or approximately:

**0.0138°/year ≈ 49.6 arcseconds/year**

Across the full 26-year interval this amounts to roughly:

**0.36°**

This is small compared with the periodic longitude terms, but it is
systematic and should not be ignored.

At this stage it should not be assigned a physical interpretation.

Possible causes include:

- a very small difference in the lunar mean angular rate;
- a residual reference-frame convention difference;
- a long-period term approximating a linear slope over the tested interval;
- or another piece of the TYCHOS geometry that is not represented in the
  current ephemeris calculation.

If interpreted purely as a lunar mean-motion mismatch, the required
fractional change would be only a few parts per million, corresponding to a
difference of only several seconds in a ~27.3-day orbital period.

This makes the drift potentially useful as a diagnostic parameter rather
than a major failure of the model.

### 8. The six-hour sampling reveals extrema missed by the earlier weekly tests

Earlier seven-day comparisons produced slightly smaller maximum errors.

The denser six-hour dataset gives:

- Maximum declination error: **2.187°**
- Maximum angular separation: **4.098°**
- Maximum longitude error: **4.101°**

This does not indicate a degradation of the model.

The RMS values remain essentially consistent with the earlier analysis; the
higher maxima simply result from sampling the lunar cycle densely enough to
capture extrema that a seven-day cadence can miss.

For this reason the six-hour dataset should be considered the primary
reference dataset for future lunar accuracy tests.

### 9. The PVP ephemeris experiment should be interpreted separately

A separate diagnostic experiment was performed with Earth's PVP
motion enabled and disabled while leaving the lunar configuration unchanged.

Over the tested interval, the exported geocentric lunar RA and Dec values
were identical to numerical precision.

This demonstrates that Earth's PVP motion does not presently affect
the lunar coordinates produced by this particular geocentric ephemeris
calculation.

It does not necessarily imply that PVP is absent from the complete 3D
Tychosium geometry, particularly relative to the stellar background.

The distinction may be important because the TYCHOS book attributes several
apparent lunar inequalities to the motion of the Earth-Moon system along the
PVP orbit, whereas the current ephemeris tool appears to operate in a local
Earth-centered frame in which a common parent transformation can cancel.

This behavior has deliberately not been changed in the present branch.
Further investigation should determine whether it is intentional, specific
to the ephemeris tool, or relevant to the intended implementation of the
lunar geometry.

## Suggested verification and follow-up work

The present branch is intentionally being left at this stage rather than
continuing to tune the lunar model.

The current results are sufficiently stable to serve as a reproducible
baseline, while several useful follow-up tests remain available for future
work.

### 1. Out-of-sample validation of the residual fit

The four dominant longitudinal residual periods were identified using the
full 2000–2026 dataset.

A useful next test would be to fit the amplitudes and phases using only part
of the dataset, for example:

    Fit interval:
    2000-06-21 to 2013-06-21

    Validation interval:
    2013-06-21 to 2026-06-21

The fitted parameters should then be applied to the validation interval
without refitting them.

If the longitude RMS is reduced from approximately 1.8° to a value close to
the ~0.1° residual obtained in the full-dataset fit, this would confirm that
the identified components are stable missing periodic signals rather than
an artifact of fitting the complete dataset.

### 2. Stability of amplitude and phase through time

The same periodic components can be fitted independently in shorter windows
(for example one-year or two-year blocks).

Of particular interest is the approximately 31.8-day component whose
amplitude is very close to 1.274°, corresponding observationally to lunar
evection.

Recording amplitude and phase versus time would show whether this term is:

- approximately constant;
- annually modulated;
- modulated over the apsidal cycle;
- or affected by some other long-period geometry.

This may be especially useful when comparing the numerical residual with the
geometrical interpretation proposed in the TYCHOS model.

### 3. Investigate the small residual linear drift

The simultaneous fit found a longitude trend of approximately:

    3.77 × 10^-5 deg/day

equivalent to roughly:

    0.0138 deg/year
    ~49.6 arcsec/year

Across the full 26-year interval this corresponds to approximately 0.36°.

No interpretation is assigned to this trend in the present work.

Future investigation may test whether it results from:

- a small mismatch in lunar mean angular rate;
- a long-period residual approximating a linear trend over the tested span;
- coordinate/reference-frame conventions;
- or another unimplemented part of the lunar geometry.

The current branch deliberately does not alter `Moon.speed` to eliminate
this trend.

### 4. Revisit the remaining ecliptic-latitude bias

The mean ecliptic-latitude residual is approximately:

    -0.396°

while its RMS is approximately:

    0.466°

This indicates that a substantial fraction of the remaining latitude error
behaves like a systematic offset rather than a high-frequency perturbation.

A future geometric investigation may therefore be preferable to adding
additional periodic correction terms.

### 5. Investigate the role of PVP in stellar versus geocentric coordinates

A diagnostic A/B test was performed with Earth's PVP orbital speed enabled
and disabled.

The lunar RA and Dec produced by the geocentric ephemeris tool were identical
to numerical precision.

This suggests that the common Earth transformation cancels in the current
geocentric ephemeris calculation.

However, this test does not establish whether the same cancellation occurs
in the full Tychosium geometry relative to the stellar background.

A useful future investigation would therefore compare:

- the Moon relative to Earth;
- the Moon relative to fixed stars;
- and the coordinate path used by the ephemeris checker.

This may clarify whether the PVP-related lunar geometry described in the
TYCHOS book exists elsewhere in the simulator but is absent from the current
geocentric ephemeris output.

### 6. Avoid adding empirical lunar correction terms prematurely

The present residual analysis identifies known observational periodicities,
but the branch deliberately does not add analytical terms such as evection,
variation, or an annual equation directly to the Moon's longitude.

The aim of this work has been to preserve the compact geometrical character
of the TYCHOS model.

Before introducing empirical corrections, it would therefore be preferable
to determine whether the remaining periodicities can emerge naturally from
the geometry already proposed by the model.

## Developer / AI handoff

This branch has been organized so that the lunar investigation can be
continued without requiring the original development conversation.

A developer or coding agent approaching this work should begin by reading:

1. `edits/README.md`
2. the generated report in `edits/reports/`
3. the scripts in `edits/scripts/`
4. `MoonOrbitalPlane.jsx`
5. the lunar entries in `celestial-settings.json`
6. the Earth/Moon hierarchy in `PlotSolarSystem.jsx`
7. the coordinate and ephemeris functions in `plotModelFunctions.js`

### Current state of the model

The present branch should be treated as a baseline.

The main successful modification is the introduction of an independent
precessing lunar orbital plane using a conjugated rotation:

    Ry(Ω) Rx(i) Ry(-Ω)

This allows the lunar node to regress without directly adding the nodal
rotation to the Moon's orbital longitude.

Approximate parameters used in the current branch are:

    lunar inclination: ~5.151°
    nodal regression period: ~18.6 years
    nodal phase: calibrated near -26.5°

The existing TYCHOS lunar deferent speeds and longitudinal geometry were
otherwise preserved.

### Important constraints discovered during development

Several earlier experiments showed that simply assigning an additional
angular speed to a nested generic `Pobj` changes more than the intended
coordinate component.

In particular, attempts to represent nodal regression by adding another
ordinary rotating `Pobj` caused large longitude errors.

For this reason, future changes should preserve the distinction between:

- rotation of the lunar orbital plane;
- motion of the Moon within that plane;
- apsidal motion;
- and transformations inherited from Earth.

Do not assume that nested angular speeds can be algebraically added or
subtracted as scalar orbital rates.

### Reproducing the analysis

The scripts under `edits/scripts/` provide a reproducible path from raw
TYCHOS and JPL ephemerides to the numerical report.

The reference analysis uses:

    Start: 2000-06-21 00:00 UTC
    Stop:  2026-06-21 00:00 UTC
    Step:  6 hours

JPL reference:

    Target: Moon (301)
    Center: geocentric Earth
    Ephemeris: DE441
    Frame: ICRF
    Coordinates: astrometric RA / Dec

The Windows CMD commands documented above were the configuration actually
tested during development.

### Recommended working method

Before modifying the current lunar parameters:

1. reproduce the existing report;
2. confirm the baseline RMS values;
3. make only one geometrical change at a time;
4. regenerate the complete comparison;
5. compare both global accuracy and residual periodic structure.

This is important because some modifications can improve one coordinate
while silently degrading another.

The current branch intentionally prioritizes reproducibility over further
parameter tuning.