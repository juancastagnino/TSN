# Moon parameter adjustment report

## Summary

We tested the Moon against the same JPL reference dataset from 2000-06-21 to 2026-06-21, using 75,969 samples at three-hour intervals. Only lunar parameters were changed; the Earth model and all other celestial settings remained fixed.

The retained adjustments are:

```text
Moon deferent A
  startPos:    177      -> 167.51
  orbitRadius: 0.0266   -> 0.02786

Moon
  startPos:    309      -> 318.0
```

The two starting positions were varied together while keeping their sum near `485.51 degrees`. This preserved the Moon's mean longitude alignment while changing the relative phase. The Deferent A radius was then refined independently.

## Main results

| Metric | Original | Adjusted | Improvement |
|---|---:|---:|---:|
| Longitude RMS | 1.390850 deg | 1.094302 deg | 21.3% |
| Angular-separation RMS | 1.407164 deg | 1.115662 deg | 20.7% |
| Right-ascension RMS | 1.410884 deg | 1.098461 deg | 22.1% |
| Declination RMS | 0.417194 deg | 0.391893 deg | 6.1% |
| Latitude RMS | 0.231405 deg | 0.228328 deg | 1.3% |
| Mean angular error | 1.226644 deg | 0.942490 deg | 23.2% |
| Median angular error | 1.176887 deg | 0.831498 deg | 29.3% |
| Angular-error P95 | 2.435662 deg | 2.093479 deg | 14.0% |
| Maximum angular error | 3.342275 deg | 2.995308 deg | 10.4% |

The mean longitude error was reduced from `-0.491413 degrees` to `-0.002219 degrees`, effectively removing the constant longitude bias.

The fitted anomalistic-month residual at approximately 27.55 days fell from `0.994726 degrees` to `0.005853 degrees`, a reduction of about 99.4%. This was the component most directly affected by the paired phase and Deferent A radius adjustments.

## Remaining error

The largest longitude residuals are now associated with periods near:

- 31.76 days: approximately 1.0873 degrees, associated with the evection diagnostic.
- 14.77 days: approximately 0.6502 degrees, associated with the variation diagnostic.
- 27.21 days: approximately 0.5023 degrees.
- One year: approximately 0.1851 degrees.

These components barely responded to the parameters adjusted here. Further changes to Deferent A are therefore unlikely to produce a substantial improvement. The next investigation should identify which part of the lunar geometry controls the evection and variation components, or whether an additional geometric term is required.

These are empirical comparisons with JPL astrometric coordinates, not proof of a physical interpretation. The adjusted configuration should be retained as a candidate baseline and tested on an independent time interval before being considered final.
