# TYCHOS Venus Ephemeris Audit

**Model:** TYCHOS venus

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-18T04:02:52.785880+00:00
- Export configuration: baseline analysis all planets 6hr 26 years
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.2466° | 0.7277° | 1.4589° | 2.6045° |
| Declination | -0.0990° | 0.2634° | 0.4461° | 1.0742° |
| Angular separation | 0.6208° | 0.7492° | 1.5110° | 2.4658° |
| Ecliptic longitude | -0.1930° | 0.7086° | 1.5053° | 2.4293° |
| Ecliptic latitude | 0.0303° | 0.2508° | 0.3794° | 0.5341° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.1834° | 0.2564° | 0.2091° | 0.3153° |
| 2001 | 1460 | 0.9618° | 0.2418° | 0.4009° | 0.9868° |
| 2002 | 1460 | 0.8845° | 0.2774° | 0.1491° | 0.9242° |
| 2003 | 1460 | 0.6031° | 0.2341° | 0.1745° | 0.6468° |
| 2004 | 1464 | 0.6213° | 0.2407° | 0.2228° | 0.6655° |
| 2005 | 1460 | 0.5277° | 0.2805° | 0.2182° | 0.5975° |
| 2006 | 1460 | 0.7603° | 0.2259° | 0.2484° | 0.7911° |
| 2007 | 1460 | 0.9464° | 0.2449° | 0.2630° | 0.9729° |
| 2008 | 1464 | 0.5049° | 0.2484° | 0.1842° | 0.5626° |
| 2009 | 1460 | 0.9072° | 0.2428° | 0.3988° | 0.9343° |
| 2010 | 1460 | 0.9063° | 0.2779° | 0.1880° | 0.9447° |
| 2011 | 1460 | 0.5252° | 0.2347° | 0.1909° | 0.5750° |
| 2012 | 1464 | 0.5845° | 0.2420° | 0.2408° | 0.6318° |
| 2013 | 1460 | 0.4810° | 0.2833° | 0.2406° | 0.5580° |
| 2014 | 1460 | 0.6731° | 0.2256° | 0.2497° | 0.7082° |
| 2015 | 1460 | 0.9498° | 0.2456° | 0.2863° | 0.9762° |
| 2016 | 1464 | 0.4396° | 0.2498° | 0.2075° | 0.5056° |
| 2017 | 1460 | 0.8530° | 0.2439° | 0.3963° | 0.8825° |
| 2018 | 1460 | 0.9452° | 0.2786° | 0.2304° | 0.9815° |
| 2019 | 1460 | 0.4633° | 0.2352° | 0.2105° | 0.5195° |
| 2020 | 1464 | 0.5666° | 0.2432° | 0.2601° | 0.6158° |
| 2021 | 1460 | 0.4621° | 0.2860° | 0.2635° | 0.5431° |
| 2022 | 1460 | 0.6005° | 0.2255° | 0.2559° | 0.6401° |
| 2023 | 1460 | 0.9597° | 0.2464° | 0.3085° | 0.9859° |
| 2024 | 1464 | 0.3971° | 0.2514° | 0.2326° | 0.4699° |
| 2025 | 1460 | 0.8072° | 0.2450° | 0.3958° | 0.8391° |
| 2026 | 685 | 0.3920° | 0.2493° | 0.1309° | 0.4645° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
