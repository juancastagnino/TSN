# TYCHOS Venus Ephemeris Audit

**Model:** TYCHOS venus

## Dataset

- Samples: **75969**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **3.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-27T14:27:23.378143+00:00
- Export configuration: Explicit Mercury/Venus with eccentricity
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.2283° | 0.4844° | 0.9815° | 1.7211° |
| Declination | 0.0272° | 0.1650° | 0.3090° | 0.5617° |
| Angular separation | 0.4148° | 0.4840° | 0.9246° | 1.5267° |
| Ecliptic longitude | -0.1737° | 0.4447° | 0.9166° | 1.5279° |
| Ecliptic latitude | 0.0320° | 0.1929° | 0.3115° | 0.3706° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 1552 | 0.3505° | 0.1564° | 0.1195° | 0.3837° |
| 2001 | 2920 | 0.3893° | 0.2462° | 0.1671° | 0.4585° |
| 2002 | 2920 | 0.5831° | 0.1942° | 0.1667° | 0.6140° |
| 2003 | 2920 | 0.4204° | 0.1752° | 0.0897° | 0.4552° |
| 2004 | 2928 | 0.6208° | 0.1914° | 0.1503° | 0.6485° |
| 2005 | 2920 | 0.5267° | 0.1625° | 0.1118° | 0.5509° |
| 2006 | 2920 | 0.3737° | 0.2093° | 0.1305° | 0.4271° |
| 2007 | 2920 | 0.6059° | 0.1709° | 0.1475° | 0.6291° |
| 2008 | 2928 | 0.3956° | 0.1699° | 0.1157° | 0.4305° |
| 2009 | 2920 | 0.3323° | 0.2462° | 0.1950° | 0.4118° |
| 2010 | 2920 | 0.5141° | 0.1955° | 0.1827° | 0.5493° |
| 2011 | 2920 | 0.3431° | 0.1746° | 0.1144° | 0.3848° |
| 2012 | 2928 | 0.5623° | 0.1924° | 0.1738° | 0.5931° |
| 2013 | 2920 | 0.5124° | 0.1634° | 0.1317° | 0.5374° |
| 2014 | 2920 | 0.3048° | 0.2061° | 0.1552° | 0.3669° |
| 2015 | 2920 | 0.5356° | 0.1695° | 0.1603° | 0.5613° |
| 2016 | 2928 | 0.3567° | 0.1702° | 0.1424° | 0.3950° |
| 2017 | 2920 | 0.3004° | 0.2461° | 0.2267° | 0.3870° |
| 2018 | 2920 | 0.4574° | 0.1962° | 0.2039° | 0.4967° |
| 2019 | 2920 | 0.2912° | 0.1741° | 0.1407° | 0.3391° |
| 2020 | 2928 | 0.5258° | 0.1934° | 0.1987° | 0.5591° |
| 2021 | 2920 | 0.5224° | 0.1642° | 0.1530° | 0.5470° |
| 2022 | 2920 | 0.2635° | 0.2029° | 0.1795° | 0.3319° |
| 2023 | 2920 | 0.4850° | 0.1681° | 0.1789° | 0.5129° |
| 2024 | 2928 | 0.3532° | 0.1705° | 0.1705° | 0.3920° |
| 2025 | 2920 | 0.3092° | 0.2460° | 0.2600° | 0.3942° |
| 2026 | 1369 | 0.3069° | 0.1762° | 0.1524° | 0.3538° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
