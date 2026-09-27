# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Sun

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Explicit Mercury/Venus with eccentricity

- Longitude: mean 0.188138 deg; RMS 0.338777 deg.
- Latitude: mean -0.001484 deg; RMS 0.042585 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.3756 deg.
  - 379.845 days, approximately 0.1891 deg.
  - 351.708 days, approximately 0.1859 deg.
  - 29.491 days, approximately 0.0016 deg.

## Mercury

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Explicit Mercury/Venus with eccentricity

- Longitude: mean 0.165775 deg; RMS 0.788866 deg.
- Latitude: mean 0.368318 deg; RMS 0.484796 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.7357 deg.
  - 115.806 days, approximately 0.4397 deg.
  - 169.574 days, approximately 0.3840 deg.
  - 379.845 days, approximately 0.3725 deg.

## Venus

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Explicit Mercury/Venus with eccentricity

- Longitude: mean -0.173665 deg; RMS 0.444675 deg.
- Latitude: mean 0.031958 deg; RMS 0.192897 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.236 days, approximately 0.3307 deg.
  - 226.098 days, approximately 0.3303 deg.
  - 220.840 days, approximately 0.2394 deg.
  - 379.845 days, approximately 0.1645 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for all bodies in this run.
