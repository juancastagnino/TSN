# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Moon — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.243878 deg; RMS 1.118789 deg.
- Declination: mean -0.011961 deg; RMS 0.370266 deg.
- Angular separation: mean 0.949483 deg; RMS 1.127079 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Sun — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean 0.009528 deg; RMS 0.054706 deg.
- Declination: mean 0.003903 deg; RMS 0.014145 deg.
- Angular separation: mean 0.048500 deg; RMS 0.053584 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Mercury — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.070267 deg; RMS 2.582757 deg.
- Declination: mean 0.213288 deg; RMS 1.046590 deg.
- Angular separation: mean 2.157157 deg; RMS 2.677341 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Venus — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.034407 deg; RMS 0.423323 deg.
- Declination: mean 0.041715 deg; RMS 0.237351 deg.
- Angular separation: mean 0.387534 deg; RMS 0.461426 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Mars — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean 0.103560 deg; RMS 0.507825 deg.
- Declination: mean -0.285433 deg; RMS 0.442256 deg.
- Angular separation: mean 0.552903 deg; RMS 0.648968 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Jupiter — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.071695 deg; RMS 0.330077 deg.
- Declination: mean -0.264183 deg; RMS 0.289047 deg.
- Angular separation: mean 0.396866 deg; RMS 0.430288 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Saturn — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.081173 deg; RMS 0.681177 deg.
- Declination: mean -0.026352 deg; RMS 0.172020 deg.
- Angular separation: mean 0.572329 deg; RMS 0.673577 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Uranus — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -0.275236 deg; RMS 0.294406 deg.
- Declination: mean -0.007081 deg; RMS 0.045188 deg.
- Angular separation: mean 0.274629 deg; RMS 0.293417 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Neptune — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean 0.065835 deg; RMS 0.073729 deg.
- Declination: mean -0.135410 deg; RMS 0.149317 deg.
- Angular separation: mean 0.158620 deg; RMS 0.165642 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Pluto — true-of-date apparent

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Full binary equivalence versus JPL apparent true-of-date

- RA: mean -4.054771 deg; RMS 4.862810 deg.
- Declination: mean 2.688729 deg; RMS 2.709348 deg.
- Angular separation: mean 4.946189 deg; RMS 5.298340 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
