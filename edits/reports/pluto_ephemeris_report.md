# TYCHOS Pluto Ephemeris Audit

**Model:** TYCHOS pluto

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-18T04:03:11.643645+00:00
- Export configuration: baseline analysis all planets 6hr 26 years
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | -3.8697° | 4.6463° | 7.4853° | 7.9320° |
| Declination | 2.7183° | 2.7401° | 3.1280° | 3.1729° |
| Angular separation | 4.8100° | 5.1411° | 7.3818° | 7.7417° |
| Ecliptic longitude | -3.4410° | 4.0275° | 6.2805° | 6.6362° |
| Ecliptic latitude | 3.1404° | 3.2034° | 3.9294° | 4.0092° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.5366° | 1.8734° | 1.7902° | 1.9457° |
| 2001 | 1460 | 0.3442° | 1.9799° | 1.9364° | 2.0084° |
| 2002 | 1460 | 0.1867° | 2.0972° | 2.0965° | 2.1052° |
| 2003 | 1460 | 0.4897° | 2.2153° | 2.2459° | 2.2671° |
| 2004 | 1464 | 0.8466° | 2.3333° | 2.3841° | 2.4780° |
| 2005 | 1460 | 1.2038° | 2.4509° | 2.5106° | 2.7238° |
| 2006 | 1460 | 1.5544° | 2.5666° | 2.6243° | 2.9914° |
| 2007 | 1460 | 1.8973° | 2.6798° | 2.7250° | 3.2724° |
| 2008 | 1464 | 2.2313° | 2.7901° | 2.8123° | 3.5603° |
| 2009 | 1460 | 2.5552° | 2.8974° | 2.8868° | 3.8503° |
| 2010 | 1460 | 2.8670° | 3.0004° | 2.9478° | 4.1372° |
| 2011 | 1460 | 3.1666° | 3.0992° | 2.9958° | 4.4186° |
| 2012 | 1464 | 3.4543° | 3.1933° | 3.0311° | 4.6928° |
| 2013 | 1460 | 3.7311° | 3.2831° | 3.0545° | 4.9598° |
| 2014 | 1460 | 3.9970° | 3.3673° | 3.0656° | 5.2177° |
| 2015 | 1460 | 4.2539° | 3.4461° | 3.0649° | 5.4673° |
| 2016 | 1464 | 4.5025° | 3.5189° | 3.0521° | 5.7087° |
| 2017 | 1460 | 4.7438° | 3.5864° | 3.0285° | 5.9425° |
| 2018 | 1460 | 4.9767° | 3.6472° | 2.9937° | 6.1670° |
| 2019 | 1460 | 5.2017° | 3.7019° | 2.9484° | 6.3823° |
| 2020 | 1464 | 5.4182° | 3.7501° | 2.8929° | 6.5880° |
| 2021 | 1460 | 5.6263° | 3.7925° | 2.8286° | 6.7841° |
| 2022 | 1460 | 5.8234° | 3.8282° | 2.7559° | 6.9681° |
| 2023 | 1460 | 6.0097° | 3.8577° | 2.6756° | 7.1400° |
| 2024 | 1464 | 6.1846° | 3.8807° | 2.5884° | 7.2992° |
| 2025 | 1460 | 6.3497° | 3.8980° | 2.4951° | 7.4473° |
| 2026 | 685 | 6.3826° | 3.8707° | 2.3606° | 7.4601° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
