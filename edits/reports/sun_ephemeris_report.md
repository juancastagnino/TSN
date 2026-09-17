# TYCHOS Sun Ephemeris Audit

**Model:** TYCHOS sun

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-17T01:47:26.496761+00:00
- Export configuration: Lunar node and orbital plane baseline
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.1754° | 0.3235° | 0.5786° | 0.6483° |
| Declination | -0.0767° | 0.1356° | 0.2892° | 0.3451° |
| Angular separation | 0.2838° | 0.3414° | 0.6327° | 0.7299° |
| Ecliptic longitude | 0.1881° | 0.3388° | 0.6301° | 0.7274° |
| Ecliptic latitude | -0.0015° | 0.0426° | 0.0606° | 0.0626° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.2733° | 0.0425° | 0.1342° | 0.2766° |
| 2001 | 1460 | 0.2690° | 0.0425° | 0.1056° | 0.2723° |
| 2002 | 1460 | 0.2703° | 0.0425° | 0.1073° | 0.2736° |
| 2003 | 1460 | 0.2752° | 0.0425° | 0.1099° | 0.2785° |
| 2004 | 1464 | 0.2768° | 0.0424° | 0.1116° | 0.2801° |
| 2005 | 1460 | 0.2813° | 0.0425° | 0.1141° | 0.2845° |
| 2006 | 1460 | 0.2843° | 0.0425° | 0.1159° | 0.2874° |
| 2007 | 1460 | 0.2899° | 0.0425° | 0.1185° | 0.2930° |
| 2008 | 1464 | 0.2967° | 0.0425° | 0.1212° | 0.2997° |
| 2009 | 1460 | 0.2995° | 0.0426° | 0.1228° | 0.3026° |
| 2010 | 1460 | 0.3055° | 0.0426° | 0.1254° | 0.3085° |
| 2011 | 1460 | 0.3137° | 0.0426° | 0.1284° | 0.3166° |
| 2012 | 1464 | 0.3201° | 0.0425° | 0.1309° | 0.3229° |
| 2013 | 1460 | 0.3290° | 0.0425° | 0.1339° | 0.3317° |
| 2014 | 1460 | 0.3355° | 0.0426° | 0.1362° | 0.3382° |
| 2015 | 1460 | 0.3446° | 0.0426° | 0.1395° | 0.3472° |
| 2016 | 1464 | 0.3548° | 0.0426° | 0.1427° | 0.3574° |
| 2017 | 1460 | 0.3616° | 0.0427° | 0.1451° | 0.3641° |
| 2018 | 1460 | 0.3716° | 0.0427° | 0.1483° | 0.3741° |
| 2019 | 1460 | 0.3821° | 0.0426° | 0.1515° | 0.3845° |
| 2020 | 1464 | 0.3907° | 0.0425° | 0.1541° | 0.3930° |
| 2021 | 1460 | 0.4015° | 0.0426° | 0.1574° | 0.4037° |
| 2022 | 1460 | 0.4093° | 0.0427° | 0.1600° | 0.4116° |
| 2023 | 1460 | 0.4204° | 0.0427° | 0.1637° | 0.4226° |
| 2024 | 1464 | 0.4322° | 0.0427° | 0.1670° | 0.4343° |
| 2025 | 1460 | 0.4410° | 0.0428° | 0.1696° | 0.4430° |
| 2026 | 685 | 0.1525° | 0.0428° | 0.0590° | 0.1584° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
