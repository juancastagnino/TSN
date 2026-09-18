# TYCHOS Neptune Ephemeris Audit

**Model:** TYCHOS neptune

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-18T04:03:07.824912+00:00
- Export configuration: baseline analysis all planets 6hr 26 years
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.2068° | 0.2174° | 0.2850° | 0.2937° |
| Declination | -0.0086° | 0.0160° | 0.0351° | 0.0526° |
| Angular separation | 0.2040° | 0.2154° | 0.2852° | 0.2933° |
| Ecliptic longitude | 0.1860° | 0.1949° | 0.2548° | 0.2657° |
| Ecliptic latitude | -0.0818° | 0.0916° | 0.1404° | 0.1503° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.0514° | 0.0080° | 0.0053° | 0.0520° |
| 2001 | 1460 | 0.0644° | 0.0121° | 0.0058° | 0.0655° |
| 2002 | 1460 | 0.0828° | 0.0185° | 0.0055° | 0.0848° |
| 2003 | 1460 | 0.1013° | 0.0250° | 0.0055° | 0.1044° |
| 2004 | 1464 | 0.1189° | 0.0314° | 0.0057° | 0.1229° |
| 2005 | 1460 | 0.1345° | 0.0377° | 0.0058° | 0.1397° |
| 2006 | 1460 | 0.1479° | 0.0440° | 0.0057° | 0.1543° |
| 2007 | 1460 | 0.1584° | 0.0502° | 0.0053° | 0.1662° |
| 2008 | 1464 | 0.1664° | 0.0562° | 0.0050° | 0.1757° |
| 2009 | 1460 | 0.1726° | 0.0622° | 0.0051° | 0.1835° |
| 2010 | 1460 | 0.1777° | 0.0682° | 0.0061° | 0.1904° |
| 2011 | 1460 | 0.1830° | 0.0740° | 0.0076° | 0.1974° |
| 2012 | 1464 | 0.1897° | 0.0798° | 0.0089° | 0.2058° |
| 2013 | 1460 | 0.1978° | 0.0855° | 0.0097° | 0.2155° |
| 2014 | 1460 | 0.2075° | 0.0912° | 0.0100° | 0.2266° |
| 2015 | 1460 | 0.2175° | 0.0966° | 0.0101° | 0.2379° |
| 2016 | 1464 | 0.2271° | 0.1019° | 0.0102° | 0.2489° |
| 2017 | 1460 | 0.2355° | 0.1070° | 0.0106° | 0.2586° |
| 2018 | 1460 | 0.2419° | 0.1120° | 0.0117° | 0.2665° |
| 2019 | 1460 | 0.2455° | 0.1168° | 0.0136° | 0.2718° |
| 2020 | 1464 | 0.2465° | 0.1213° | 0.0165° | 0.2747° |
| 2021 | 1460 | 0.2449° | 0.1258° | 0.0204° | 0.2753° |
| 2022 | 1460 | 0.2418° | 0.1300° | 0.0249° | 0.2745° |
| 2023 | 1460 | 0.2381° | 0.1341° | 0.0296° | 0.2732° |
| 2024 | 1464 | 0.2352° | 0.1380° | 0.0341° | 0.2727° |
| 2025 | 1460 | 0.2341° | 0.1418° | 0.0379° | 0.2736° |
| 2026 | 685 | 0.2361° | 0.1397° | 0.0345° | 0.2743° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
