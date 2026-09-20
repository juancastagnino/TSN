# TYCHOS Mercury Ephemeris Audit

**Model:** TYCHOS mercury

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-20T14:56:56.340837+00:00
- Export configuration: new analysis with all planets but tweaks to the moon were done only
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.1026° | 2.2792° | 4.4680° | 8.0653° |
| Declination | 0.3634° | 1.4399° | 2.5991° | 4.6382° |
| Angular separation | 2.1758° | 2.6052° | 4.7533° | 8.2929° |
| Ecliptic longitude | 0.1625° | 2.2560° | 4.2597° | 7.8118° |
| Ecliptic latitude | 0.3300° | 1.3060° | 2.5003° | 3.1492° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 2.6700° | 1.2199° | 1.4100° | 2.9324° |
| 2001 | 1460 | 2.3622° | 1.3145° | 1.3675° | 2.7016° |
| 2002 | 1460 | 2.2095° | 1.3012° | 1.3385° | 2.5628° |
| 2003 | 1460 | 2.1644° | 1.3166° | 1.4116° | 2.5320° |
| 2004 | 1464 | 2.2147° | 1.3052° | 1.4982° | 2.5691° |
| 2005 | 1460 | 2.2050° | 1.2868° | 1.5066° | 2.5511° |
| 2006 | 1460 | 2.2847° | 1.3028° | 1.4736° | 2.6280° |
| 2007 | 1460 | 2.3645° | 1.3143° | 1.4052° | 2.7033° |
| 2008 | 1464 | 2.3137° | 1.3104° | 1.3569° | 2.6575° |
| 2009 | 1460 | 2.1570° | 1.2982° | 1.3570° | 2.5162° |
| 2010 | 1460 | 2.2226° | 1.3273° | 1.4659° | 2.5873° |
| 2011 | 1460 | 2.1830° | 1.2897° | 1.5081° | 2.5338° |
| 2012 | 1464 | 2.2360° | 1.2916° | 1.5033° | 2.5803° |
| 2013 | 1460 | 2.3212° | 1.3094° | 1.4521° | 2.6631° |
| 2014 | 1460 | 2.3750° | 1.3155° | 1.3899° | 2.7133° |
| 2015 | 1460 | 2.2397° | 1.3048° | 1.3520° | 2.5907° |
| 2016 | 1464 | 2.1535° | 1.3108° | 1.3990° | 2.5198° |
| 2017 | 1460 | 2.2361° | 1.3129° | 1.4992° | 2.5916° |
| 2018 | 1460 | 2.1963° | 1.2863° | 1.5149° | 2.5435° |
| 2019 | 1460 | 2.2743° | 1.3004° | 1.4937° | 2.6178° |
| 2020 | 1464 | 2.3648° | 1.3131° | 1.4304° | 2.7031° |
| 2021 | 1460 | 2.3460° | 1.3132° | 1.3782° | 2.6870° |
| 2022 | 1460 | 2.1817° | 1.2983° | 1.3595° | 2.5375° |
| 2023 | 1460 | 2.2179° | 1.3261° | 1.4549° | 2.5827° |
| 2024 | 1464 | 2.2062° | 1.2937° | 1.5133° | 2.5560° |
| 2025 | 1460 | 2.2353° | 1.2912° | 1.5189° | 2.5796° |
| 2026 | 685 | 1.9558° | 1.4272° | 1.5075° | 2.4206° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
