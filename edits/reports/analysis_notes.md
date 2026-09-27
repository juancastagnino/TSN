# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Sun

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: baseline planes for mercury and venus

- Longitude: mean 0.188138 deg; RMS 0.338777 deg.
- Latitude: mean -0.001484 deg; RMS 0.042585 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.3756 deg.
  - 379.845 days, approximately 0.1891 deg.
  - 351.708 days, approximately 0.1859 deg.
  - 29.491 days, approximately 0.0016 deg.

## Mercury

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: baseline planes for mercury and venus

- Longitude: mean 0.162524 deg; RMS 2.256057 deg.
- Latitude: mean 0.330030 deg; RMS 1.306036 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 49.980 days, approximately 2.1311 deg.
  - 365.236 days, approximately 1.7312 deg.
  - 379.845 days, approximately 0.8681 deg.
  - 351.708 days, approximately 0.8625 deg.

## Venus

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: baseline planes for mercury and venus

- Longitude: mean -0.193046 deg; RMS 0.708558 deg.
- Latitude: mean 0.030284 deg; RMS 0.250802 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.7873 deg.
  - 379.845 days, approximately 0.3980 deg.
  - 351.708 days, approximately 0.3919 deg.
  - 226.098 days, approximately 0.3307 deg.

## Pluto

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: baseline planes for mercury and venus

- Longitude: mean -0.160491 deg; RMS 0.505200 deg.
- Latitude: mean -0.013802 deg; RMS 0.265224 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.3267 deg.
  - 379.845 days, approximately 0.1952 deg.
  - 351.708 days, approximately 0.1409 deg.
  - 182.618 days, approximately 0.0252 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
