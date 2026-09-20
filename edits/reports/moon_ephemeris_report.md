# TYCHOS Moon Ephemeris Audit

**Model:** TYCHOS moon

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-20T14:56:45.520661+00:00
- Export configuration: new analysis with all planets but tweaks to the moon were done only
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.5363° | 1.7681° | 3.2522° | 4.3683° |
| Declination | -0.0508° | 0.5266° | 1.1276° | 1.8918° |
| Angular separation | 1.4862° | 1.7626° | 3.2019° | 4.0044° |
| Ecliptic longitude | -0.4796° | 1.7487° | 3.1915° | 4.0078° |
| Ecliptic latitude | 0.0034° | 0.2473° | 0.4675° | 0.7292° |

## Longitudinal residual structure

A joint sinusoidal fit is used here as a diagnostic fingerprint of the residual, not as a claim about physical causation.

- Longitude RMS before the four-period fit: **1.7487°**
- Longitude RMS after the four-period fit: **0.1925°**
- Variance explained: **98.690%**

### Fitted periodic components

| Component | Period (days) | Amplitude in primary fit | Amplitude in full diagnostic fit |
|---|---:|---:|---:|
| variation | 14.765294 | 0.6581° | 0.6584° |
| sidereal_month | 27.321661 | —° | 0.2293° |
| anomalistic_month | 27.554551 | 1.8589° | 1.8545° |
| synodic_month | 29.530589 | —° | 0.0347° |
| evection | 31.811938 | 1.2733° | 1.2737° |
| annual | 365.256363 | 0.1848° | 0.1847° |
| apsidal_precession | 3232.605400 | —° | 0.0002° |
| nodal_regression | 6798.383500 | —° | 0.0116° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 1.6867° | 0.2335° | 0.4351° | 1.6991° |
| 2001 | 1460 | 1.7978° | 0.2458° | 0.4437° | 1.8117° |
| 2002 | 1460 | 1.9195° | 0.2482° | 0.5254° | 1.9317° |
| 2003 | 1460 | 1.8955° | 0.2461° | 0.6444° | 1.9068° |
| 2004 | 1464 | 1.7914° | 0.2557° | 0.6566° | 1.8070° |
| 2005 | 1460 | 1.8140° | 0.2654° | 0.6101° | 1.8301° |
| 2006 | 1460 | 1.8180° | 0.2547° | 0.5526° | 1.8314° |
| 2007 | 1460 | 1.7331° | 0.2602° | 0.5994° | 1.7497° |
| 2008 | 1464 | 1.5614° | 0.2505° | 0.5626° | 1.5781° |
| 2009 | 1460 | 1.5828° | 0.2458° | 0.4836° | 1.5977° |
| 2010 | 1460 | 1.7875° | 0.2540° | 0.4787° | 1.8025° |
| 2011 | 1460 | 1.9002° | 0.2456° | 0.5394° | 1.9119° |
| 2012 | 1464 | 1.8179° | 0.2320° | 0.5304° | 1.8277° |
| 2013 | 1460 | 1.7718° | 0.2358° | 0.4582° | 1.7846° |
| 2014 | 1460 | 1.7996° | 0.2310° | 0.3674° | 1.8111° |
| 2015 | 1460 | 1.7770° | 0.2181° | 0.3382° | 1.7859° |
| 2016 | 1464 | 1.6623° | 0.2214° | 0.3717° | 1.6743° |
| 2017 | 1460 | 1.5295° | 0.2139° | 0.4112° | 1.5415° |
| 2018 | 1460 | 1.5836° | 0.2253° | 0.3893° | 1.5957° |
| 2019 | 1460 | 1.7791° | 0.2389° | 0.4249° | 1.7924° |
| 2020 | 1464 | 1.8613° | 0.2461° | 0.5262° | 1.8738° |
| 2021 | 1460 | 1.7862° | 0.2566° | 0.6466° | 1.8002° |
| 2022 | 1460 | 1.7430° | 0.2634° | 0.6418° | 1.7601° |
| 2023 | 1460 | 1.7534° | 0.2680° | 0.5743° | 1.7707° |
| 2024 | 1464 | 1.7363° | 0.2702° | 0.5713° | 1.7531° |
| 2025 | 1460 | 1.6068° | 0.2749° | 0.6161° | 1.6275° |
| 2026 | 685 | 1.4222° | 0.2685° | 0.5855° | 1.4451° |

## Interpretation notes

- The periodic labels above identify frequencies present in the TYCHOS-minus-JPL residual. They should not by themselves be interpreted as proof of a particular physical mechanism.
- The lunar-plane modification should be evaluated primarily by whether it reduces latitude/declination error without materially degrading the longitude already produced by the original TYCHOS geometry.
- Remaining longitudinal structure can then be investigated within the geometry proposed by TYCHOS without introducing perturbations or empirical correction terms.

