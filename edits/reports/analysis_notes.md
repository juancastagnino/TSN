# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Moon

Interval: 1966-06-21 00:00:00 to 2026-06-21 00:00:00; 87661 samples.

Export configuration: Retained Simon lunar revision; deferent A radius 0.0266; identity deferent B removed

- Longitude: mean -0.713075 deg; RMS 1.497131 deg.
- Latitude: mean 0.009895 deg; RMS 0.235875 deg.
- Longitude trend conditional on the four-period fit: 46.423 arcsec/year (365.25 days/year).
- In-sample fitted longitude residual RMS: 0.380466 deg. This is not out-of-sample validation.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 31.807 days, approximately 1.2659 deg.
  - 27.566 days, approximately 0.9236 deg.
  - 14.768 days, approximately 0.6341 deg.
  - 27.224 days, approximately 0.4655 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
