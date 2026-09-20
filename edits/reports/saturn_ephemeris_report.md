# TYCHOS Saturn Ephemeris Audit

**Model:** TYCHOS saturn

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-20T14:57:03.619415+00:00
- Export configuration: new analysis with all planets but tweaks to the moon were done only
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.0939° | 0.6590° | 1.3500° | 1.7561° |
| Declination | -0.0351° | 0.1651° | 0.3498° | 0.5148° |
| Angular separation | 0.5358° | 0.6527° | 1.3353° | 1.6275° |
| Ecliptic longitude | 0.0992° | 0.6421° | 1.3340° | 1.6273° |
| Ecliptic latitude | -0.1105° | 0.1188° | 0.1588° | 0.1711° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 1.1420° | 0.0713° | 0.1922° | 1.1433° |
| 2001 | 1460 | 0.9322° | 0.0471° | 0.1058° | 0.9329° |
| 2002 | 1460 | 0.9448° | 0.0407° | 0.0573° | 0.9454° |
| 2003 | 1460 | 0.9175° | 0.0393° | 0.1151° | 0.9182° |
| 2004 | 1464 | 0.8515° | 0.0448° | 0.1884° | 0.8527° |
| 2005 | 1460 | 0.7575° | 0.0568° | 0.2342° | 0.7596° |
| 2006 | 1460 | 0.6519° | 0.0731° | 0.2463° | 0.6559° |
| 2007 | 1460 | 0.5590° | 0.0908° | 0.2331° | 0.5661° |
| 2008 | 1464 | 0.5021° | 0.1076° | 0.2079° | 0.5133° |
| 2009 | 1460 | 0.4923° | 0.1220° | 0.1819° | 0.5069° |
| 2010 | 1460 | 0.5191° | 0.1329° | 0.1627° | 0.5354° |
| 2011 | 1460 | 0.5570° | 0.1401° | 0.1472° | 0.5739° |
| 2012 | 1464 | 0.5851° | 0.1442° | 0.1285° | 0.6021° |
| 2013 | 1460 | 0.5932° | 0.1457° | 0.1031° | 0.6103° |
| 2014 | 1460 | 0.5730° | 0.1458° | 0.0771° | 0.5909° |
| 2015 | 1460 | 0.5255° | 0.1454° | 0.0725° | 0.5450° |
| 2016 | 1464 | 0.4536° | 0.1451° | 0.0982° | 0.4761° |
| 2017 | 1460 | 0.3670° | 0.1453° | 0.1299° | 0.3947° |
| 2018 | 1460 | 0.2826° | 0.1458° | 0.1495° | 0.3180° |
| 2019 | 1460 | 0.2402° | 0.1462° | 0.1493° | 0.2812° |
| 2020 | 1464 | 0.2821° | 0.1457° | 0.1306° | 0.3175° |
| 2021 | 1460 | 0.3869° | 0.1436° | 0.1080° | 0.4127° |
| 2022 | 1460 | 0.5112° | 0.1391° | 0.1133° | 0.5297° |
| 2023 | 1460 | 0.6349° | 0.1318° | 0.1564° | 0.6482° |
| 2024 | 1464 | 0.7508° | 0.1216° | 0.2134° | 0.7601° |
| 2025 | 1460 | 0.8606° | 0.1092° | 0.2675° | 0.8668° |
| 2026 | 685 | 0.8499° | 0.0612° | 0.2880° | 0.8515° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
