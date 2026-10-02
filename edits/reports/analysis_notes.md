# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Sun

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: sun moon venus and mercury, J2000, 2000-2026 3h with tweaks to mercury
TYCHOS reference frame: `j2000-icrf`.

- Longitude: mean -0.003185 deg; RMS 0.051993 deg.
- Latitude: mean -0.001689 deg; RMS 0.011651 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.0717 deg.
  - 351.708 days, approximately 0.0361 deg.
  - 379.845 days, approximately 0.0356 deg.
  - 182.618 days, approximately 0.0126 deg.

## Moon

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: sun moon venus and mercury, J2000, 2000-2026 3h with tweaks to mercury
TYCHOS reference frame: `j2000-icrf`.

- Longitude: mean -0.193537 deg; RMS 1.106685 deg.
- Latitude: mean 0.010132 deg; RMS 0.228343 deg.
- Longitude trend conditional on the four-period fit: -4.340 arcsec/year (365.25 days/year).
- In-sample fitted longitude residual RMS: 0.382446 deg. This is not out-of-sample validation.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 31.760 days, approximately 1.0873 deg.
  - 14.768 days, approximately 0.6502 deg.
  - 27.210 days, approximately 0.5023 deg.
  - 365.236 days, approximately 0.1851 deg.

## Mercury

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: sun moon venus and mercury, J2000, 2000-2026 3h with tweaks to mercury
TYCHOS reference frame: `j2000-icrf`.

- Longitude: mean -0.025873 deg; RMS 2.639515 deg.
- Latitude: mean -0.001668 deg; RMS 0.744705 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 2.5373 deg.
  - 49.980 days, approximately 2.1282 deg.
  - 379.845 days, approximately 1.2727 deg.
  - 351.708 days, approximately 1.2640 deg.

## Venus

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: sun moon venus and mercury, J2000, 2000-2026 3h with tweaks to mercury
TYCHOS reference frame: `j2000-icrf`.

- Longitude: mean 0.011399 deg; RMS 0.406822 deg.
- Latitude: mean 0.017025 deg; RMS 0.218162 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 226.098 days, approximately 0.3302 deg.
  - 365.236 days, approximately 0.2433 deg.
  - 220.840 days, approximately 0.2394 deg.
  - 160.951 days, approximately 0.1236 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
