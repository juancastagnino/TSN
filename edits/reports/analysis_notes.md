# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Moon — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean -0.150830 deg; RMS 1.107192 deg.
- Declination: mean 0.007144 deg; RMS 0.379622 deg.
- Angular separation: mean 0.950265 deg; RMS 1.122669 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Sun — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean 0.034910 deg; RMS 0.049646 deg.
- Declination: mean 0.000742 deg; RMS 0.012857 deg.
- Angular separation: mean 0.044690 deg; RMS 0.049187 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Mercury — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean -0.045277 deg; RMS 2.628988 deg.
- Declination: mean 0.199138 deg; RMS 1.036547 deg.
- Angular separation: mean 2.186521 deg; RMS 2.712446 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Venus — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean -0.018348 deg; RMS 0.416400 deg.
- Declination: mean 0.037338 deg; RMS 0.227395 deg.
- Angular separation: mean 0.386033 deg; RMS 0.450871 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Mars — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean 0.106922 deg; RMS 0.606933 deg.
- Declination: mean -0.333595 deg; RMS 0.531716 deg.
- Angular separation: mean 0.643944 deg; RMS 0.781403 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Jupiter — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean -0.314633 deg; RMS 0.514196 deg.
- Declination: mean -0.283276 deg; RMS 0.319245 deg.
- Angular separation: mean 0.509251 deg; RMS 0.590565 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Saturn — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean 0.476993 deg; RMS 0.899023 deg.
- Declination: mean -0.024003 deg; RMS 0.219219 deg.
- Angular separation: mean 0.698590 deg; RMS 0.889880 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Uranus — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean 0.010370 deg; RMS 0.194399 deg.
- Declination: mean 0.041423 deg; RMS 0.075975 deg.
- Angular separation: mean 0.178887 deg; RMS 0.203847 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Neptune — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean -0.298870 deg; RMS 0.453301 deg.
- Declination: mean 0.014025 deg; RMS 0.236832 deg.
- Angular separation: mean 0.397288 deg; RMS 0.493915 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Pluto — true-of-date apparent

Interval: 1826-06-21 00:00:00 to 2026-06-21 00:00:00; 73050 samples.

Export configuration: TYCHOS native versus JPL true-of-date apparent 1826-2026 1d interval

- RA: mean 7.538010 deg; RMS 10.540256 deg.
- Declination: mean -0.134145 deg; RMS 1.894528 deg.
- Angular separation: mean 8.726269 deg; RMS 10.161661 deg.
- J2000 ecliptic longitude/latitude diagnostics are omitted for true-of-date coordinates.
- No FFT peaks available (insufficient samples or irregular cadence).

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
