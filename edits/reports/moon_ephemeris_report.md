# TYCHOS Moon Ephemeris Audit

**Model:** TYCHOS moon

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-17T01:47:23.632593+00:00
- Export configuration: Lunar node and orbital plane baseline
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.3321° | 1.8116° | 3.3510° | 4.5447° |
| Declination | -0.3875° | 0.6796° | 1.3730° | 2.1867° |
| Angular separation | 1.5957° | 1.8520° | 3.3264° | 4.0984° |
| Ecliptic longitude | -0.2798° | 1.7961° | 3.2913° | 4.1008° |
| Ecliptic latitude | -0.3960° | 0.4658° | 0.8083° | 1.1414° |

## Longitudinal residual structure

A joint sinusoidal fit is used here as a diagnostic fingerprint of the residual, not as a claim about physical causation.

- Longitude RMS before the four-period fit: **1.7961°**
- Longitude RMS after the four-period fit: **0.1034°**
- Variance explained: **99.661%**

### Fitted periodic components

| Component | Period (days) | Amplitude in primary fit | Amplitude in full diagnostic fit |
|---|---:|---:|---:|
| variation | 14.765294 | 0.6585° | 0.6585° |
| sidereal_month | 27.321661 | —° | 0.0036° |
| anomalistic_month | 27.554551 | 2.0354° | 2.0356° |
| synodic_month | 29.530589 | —° | 0.0343° |
| evection | 31.811938 | 1.2738° | 1.2739° |
| annual | 365.256363 | 0.1849° | 0.1847° |
| apsidal_precession | 3232.605400 | —° | 0.0002° |
| nodal_regression | 6798.383500 | —° | 0.0117° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 1.7830° | 0.4707° | 0.3976° | 1.8398° |
| 2001 | 1460 | 1.8458° | 0.4093° | 0.4720° | 1.8875° |
| 2002 | 1460 | 1.9273° | 0.4088° | 0.6447° | 1.9671° |
| 2003 | 1460 | 1.8531° | 0.4442° | 0.8556° | 1.9009° |
| 2004 | 1464 | 1.6941° | 0.5039° | 0.9475° | 1.7645° |
| 2005 | 1460 | 1.7607° | 0.5201° | 0.9058° | 1.8332° |
| 2006 | 1460 | 1.8680° | 0.4520° | 0.7149° | 1.9175° |
| 2007 | 1460 | 1.8991° | 0.3874° | 0.5775° | 1.9350° |
| 2008 | 1464 | 1.7502° | 0.3907° | 0.5031° | 1.7903° |
| 2009 | 1460 | 1.7024° | 0.4514° | 0.4802° | 1.7565° |
| 2010 | 1460 | 1.8080° | 0.5277° | 0.5823° | 1.8799° |
| 2011 | 1460 | 1.8757° | 0.5400° | 0.7513° | 1.9486° |
| 2012 | 1464 | 1.7719° | 0.4875° | 0.8225° | 1.8332° |
| 2013 | 1460 | 1.7292° | 0.4307° | 0.8052° | 1.7790° |
| 2014 | 1460 | 1.7992° | 0.4252° | 0.6840° | 1.8459° |
| 2015 | 1460 | 1.8597° | 0.4920° | 0.5419° | 1.9191° |
| 2016 | 1464 | 1.8150° | 0.5464° | 0.4235° | 1.8922° |
| 2017 | 1460 | 1.7048° | 0.5401° | 0.3855° | 1.7856° |
| 2018 | 1460 | 1.6982° | 0.4983° | 0.3939° | 1.7657° |
| 2019 | 1460 | 1.8259° | 0.4097° | 0.5014° | 1.8682° |
| 2020 | 1464 | 1.8841° | 0.3965° | 0.6789° | 1.9223° |
| 2021 | 1460 | 1.7590° | 0.4644° | 0.8868° | 1.8150° |
| 2022 | 1460 | 1.6810° | 0.5100° | 0.9478° | 1.7537° |
| 2023 | 1460 | 1.7412° | 0.5143° | 0.8457° | 1.8128° |
| 2024 | 1464 | 1.8527° | 0.4642° | 0.6872° | 1.9055° |
| 2025 | 1460 | 1.8243° | 0.3908° | 0.5664° | 1.8626° |
| 2026 | 685 | 1.6720° | 0.3784° | 0.5237° | 1.7122° |

## Interpretation notes

- The periodic labels above identify frequencies present in the TYCHOS-minus-JPL residual. They should not by themselves be interpreted as proof of a particular physical mechanism.
- The lunar-plane modification should be evaluated primarily by whether it reduces latitude/declination error without materially degrading the longitude already produced by the original TYCHOS geometry.
- Remaining longitudinal structure can then be investigated within the geometry proposed by TYCHOS before introducing any additional empirical correction terms.

