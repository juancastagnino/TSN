# Analysis notes

Diagnostics from the bodies processed in this run; hypotheses are not physical conclusions.

Read the [developer handoff](../README_handoff.md) for the retained baseline and geometric research approach. Update that document only when a supported conclusion or development priority changes.

## Mercury

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Mercury phases -183 and 37; Pluto startPos 198 centers 1287.5 604.5 -495.5 orbitTilta 14.75

- Longitude: mean 0.162084 deg; RMS 1.835098 deg.
- Latitude: mean 0.324952 deg; RMS 0.608923 deg.
- Largest longitude FFT peaks (finite-window estimates, not fitted orbital periods):
  - 49.980 days, approximately 2.1360 deg.
  - 34.912 days, approximately 0.7703 deg.
  - 365.236 days, approximately 0.7476 deg.
  - 115.806 days, approximately 0.4380 deg.

## Pluto

Interval: 2000-06-21 00:00:00 to 2026-06-21 00:00:00; 75969 samples.

Export configuration: Mercury phases -183 and 37; Pluto startPos 198 centers 1287.5 604.5 -495.5 orbitTilta 14.75

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
