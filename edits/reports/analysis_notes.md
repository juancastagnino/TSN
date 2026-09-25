# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Moon

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: ia agents tests. Only moon analyzed

- Longitude: mean -0.011461 deg; RMS 1.130535 deg.
- Latitude: mean -0.021698 deg; RMS 0.268353 deg.
- Longitude trend conditional on the four-period fit: 46.651 arcsec/year (365.25 days/year).
- In-sample fitted longitude residual RMS: 0.471196 deg. This is not out-of-sample validation.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 31.760 days, approximately 1.0873 deg.
  - 14.768 days, approximately 0.6502 deg.
  - 27.210 days, approximately 0.6365 deg.
  - 365.236 days, approximately 0.1851 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
