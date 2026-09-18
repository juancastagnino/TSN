# TYCHOS Uranus Ephemeris Audit

**Model:** TYCHOS uranus

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-18T04:03:03.944741+00:00
- Export configuration: baseline analysis all planets 6hr 26 years
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -0.1336° | 0.2404° | 0.4479° | 0.5055° |
| Declination | 0.1102° | 0.1271° | 0.1994° | 0.2148° |
| Angular separation | 0.2539° | 0.2680° | 0.4392° | 0.4906° |
| Ecliptic longitude | -0.0854° | 0.2177° | 0.4101° | 0.4674° |
| Ecliptic latitude | 0.1558° | 0.1564° | 0.1731° | 0.1763° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.3378° | 0.1479° | 0.0456° | 0.3687° |
| 2001 | 1460 | 0.3733° | 0.1493° | 0.0374° | 0.4020° |
| 2002 | 1460 | 0.3591° | 0.1530° | 0.0406° | 0.3903° |
| 2003 | 1460 | 0.3410° | 0.1562° | 0.0448° | 0.3751° |
| 2004 | 1464 | 0.3198° | 0.1590° | 0.0503° | 0.3571° |
| 2005 | 1460 | 0.2980° | 0.1616° | 0.0564° | 0.3390° |
| 2006 | 1460 | 0.2755° | 0.1637° | 0.0633° | 0.3205° |
| 2007 | 1460 | 0.2539° | 0.1655° | 0.0705° | 0.3031° |
| 2008 | 1464 | 0.2333° | 0.1668° | 0.0779° | 0.2868° |
| 2009 | 1460 | 0.2144° | 0.1679° | 0.0849° | 0.2723° |
| 2010 | 1460 | 0.1961° | 0.1684° | 0.0920° | 0.2584° |
| 2011 | 1460 | 0.1777° | 0.1685° | 0.0993° | 0.2449° |
| 2012 | 1464 | 0.1577° | 0.1682° | 0.1074° | 0.2305° |
| 2013 | 1460 | 0.1362° | 0.1674° | 0.1161° | 0.2158° |
| 2014 | 1460 | 0.1133° | 0.1661° | 0.1260° | 0.2011° |
| 2015 | 1460 | 0.0914° | 0.1645° | 0.1364° | 0.1881° |
| 2016 | 1464 | 0.0751° | 0.1625° | 0.1472° | 0.1790° |
| 2017 | 1460 | 0.0706° | 0.1601° | 0.1573° | 0.1749° |
| 2018 | 1460 | 0.0805° | 0.1574° | 0.1664° | 0.1767° |
| 2019 | 1460 | 0.0991° | 0.1543° | 0.1738° | 0.1834° |
| 2020 | 1464 | 0.1209° | 0.1508° | 0.1792° | 0.1933° |
| 2021 | 1460 | 0.1412° | 0.1468° | 0.1819° | 0.2037° |
| 2022 | 1460 | 0.1594° | 0.1425° | 0.1820° | 0.2138° |
| 2023 | 1460 | 0.1752° | 0.1376° | 0.1798° | 0.2228° |
| 2024 | 1464 | 0.1897° | 0.1324° | 0.1756° | 0.2313° |
| 2025 | 1460 | 0.2041° | 0.1268° | 0.1698° | 0.2403° |
| 2026 | 685 | 0.2326° | 0.1222° | 0.1701° | 0.2628° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
