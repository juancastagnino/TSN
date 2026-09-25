# TYCHOS Moon Ephemeris Audit

**Model:** TYCHOS moon

## Dataset

- Samples: **75969**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **3.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-25T14:22:16.239737+00:00
- Export configuration: ia agents tests. Only moon analyzed
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.0541° | 1.1369° | 2.1812° | 3.5233° |
| Declination | -0.0216° | 0.4216° | 0.8605° | 1.4571° |
| Angular separation | 0.9790° | 1.1597° | 2.1895° | 3.1194° |
| Ecliptic longitude | -0.0115° | 1.1305° | 2.1681° | 3.1266° |
| Ecliptic latitude | -0.0217° | 0.2684° | 0.5315° | 0.8349° |

## Longitudinal residual structure

A joint sinusoidal fit is used here as a diagnostic fingerprint of the residual, not as a claim about physical causation.

- Longitude RMS before the four-period fit: **1.1305°**
- Longitude RMS after the four-period fit: **0.4712°**
- Variance explained: **82.627%**

### Fitted periodic components

| Component | Period (days) | Amplitude in primary fit | Amplitude in full diagnostic fit |
|---|---:|---:|---:|
| variation | 14.765294 | 0.6582° | 0.6582° |
| sidereal_month | 27.321661 | —° | 0.1382° |
| anomalistic_month | 27.554551 | 0.0390° | 0.0409° |
| synodic_month | 29.530589 | —° | 0.0345° |
| evection | 31.811938 | 1.2732° | 1.2733° |
| annual | 365.256363 | 0.1849° | 0.1846° |
| apsidal_precession | 3232.605400 | —° | 0.0005° |
| nodal_regression | 6798.383500 | —° | 0.0126° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 1552 | 1.1169° | 0.2763° | 0.3835° | 1.1485° |
| 2001 | 2920 | 1.1463° | 0.2314° | 0.3862° | 1.1673° |
| 2002 | 2920 | 1.1648° | 0.1896° | 0.3855° | 1.1779° |
| 2003 | 2920 | 1.1552° | 0.1526° | 0.3944° | 1.1630° |
| 2004 | 2928 | 1.1290° | 0.1360° | 0.3883° | 1.1349° |
| 2005 | 2920 | 1.1161° | 0.1521° | 0.4067° | 1.1241° |
| 2006 | 2920 | 1.1342° | 0.1886° | 0.4516° | 1.1476° |
| 2007 | 2920 | 1.1271° | 0.2255° | 0.4536° | 1.1472° |
| 2008 | 2928 | 1.1127° | 0.2707° | 0.4384° | 1.1429° |
| 2009 | 2920 | 1.1071° | 0.3038° | 0.4529° | 1.1457° |
| 2010 | 2920 | 1.1285° | 0.3377° | 0.4723° | 1.1755° |
| 2011 | 2920 | 1.1111° | 0.3611° | 0.4549° | 1.1660° |
| 2012 | 2928 | 1.1081° | 0.3797° | 0.4243° | 1.1690° |
| 2013 | 2920 | 1.1304° | 0.3882° | 0.4421° | 1.1930° |
| 2014 | 2920 | 1.1386° | 0.3910° | 0.4363° | 1.2016° |
| 2015 | 2920 | 1.1317° | 0.3797° | 0.4324° | 1.1915° |
| 2016 | 2928 | 1.1319° | 0.3570° | 0.4065° | 1.1847° |
| 2017 | 2920 | 1.1334° | 0.3275° | 0.4215° | 1.1775° |
| 2018 | 2920 | 1.1283° | 0.2977° | 0.4179° | 1.1648° |
| 2019 | 2920 | 1.1389° | 0.2452° | 0.4022° | 1.1628° |
| 2020 | 2928 | 1.1449° | 0.2023° | 0.3840° | 1.1604° |
| 2021 | 2920 | 1.1486° | 0.1679° | 0.3903° | 1.1586° |
| 2022 | 2920 | 1.1317° | 0.1377° | 0.3850° | 1.1377° |
| 2023 | 2920 | 1.1211° | 0.1419° | 0.4031° | 1.1278° |
| 2024 | 2928 | 1.1131° | 0.1700° | 0.4350° | 1.1238° |
| 2025 | 2920 | 1.1426° | 0.2075° | 0.4581° | 1.1590° |
| 2026 | 1369 | 1.1155° | 0.2327° | 0.4512° | 1.1373° |

## Interpretation notes

- The periodic labels above identify frequencies present in the TYCHOS-minus-JPL residual. They should not by themselves be interpreted as proof of a particular physical mechanism.
- The lunar-plane modification should be evaluated primarily by whether it reduces latitude/declination error without materially degrading the longitude already produced by the original TYCHOS geometry.
- Remaining longitudinal structure can then be investigated within the geometry proposed by TYCHOS without introducing perturbations or empirical correction terms.

