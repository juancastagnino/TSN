# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Moon

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 37985 samples.

Export configuration: Lunar node and orbital plane baseline

- Longitude: mean -0.279782 deg; RMS 1.796099 deg.
- Latitude: mean -0.395967 deg; RMS 0.465754 deg.
- Longitude trend conditional on the four-period fit: 49.585 arcsec/year (365.25 days/year).
- In-sample fitted longitude residual RMS: 0.103364 deg. This is not out-of-sample validation.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 27.525 days, approximately 1.8641 deg.
  - 31.760 days, approximately 1.0901 deg.
  - 14.769 days, approximately 0.6492 deg.
  - 365.240 days, approximately 0.1851 deg.

## Sun

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 37985 samples.

Export configuration: Lunar node and orbital plane baseline

- Longitude: mean 0.188137 deg; RMS 0.338777 deg.
- Latitude: mean -0.001484 deg; RMS 0.042584 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.240 days, approximately 0.3756 deg.
  - 379.850 days, approximately 0.1890 deg.
  - 351.713 days, approximately 0.1860 deg.
  - 29.491 days, approximately 0.0016 deg.

## Mars

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 37985 samples.

Export configuration: Lunar node and orbital plane baseline

- Longitude: mean 0.355890 deg; RMS 0.609664 deg.
- Latitude: mean -0.278761 deg; RMS 0.408211 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 365.240 days, approximately 0.2975 deg.
  - 351.713 days, approximately 0.2709 deg.
  - 249.901 days, approximately 0.2230 deg.
  - 379.850 days, approximately 0.1854 deg.

## Questions to investigate

- Test whether biases and fitted coefficients transfer to a separate time interval.
- Before interpreting a longitude drift as an orbital-speed error or precession, verify the reference frames and look for shared behavior across bodies. Similar numerical rates alone do not establish a cause.
- Compare global coordinate changes using the same epochs and export settings for Moon, Sun and Mars.
