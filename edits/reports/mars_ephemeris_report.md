# TYCHOS Mars Ephemeris Audit

**Model:** TYCHOS mars

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-17T01:47:29.223361+00:00
- Export configuration: Lunar node and orbital plane baseline
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.2902° | 0.5945° | 1.1678° | 2.1705° |
| Declination | -0.2885° | 0.4779° | 0.9631° | 1.5608° |
| Angular separation | 0.6377° | 0.7334° | 1.3432° | 2.3317° |
| Ecliptic longitude | 0.3559° | 0.6097° | 1.1640° | 2.2444° |
| Ecliptic latitude | -0.2788° | 0.4082° | 0.8086° | 1.0929° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.3224° | 0.4056° | 0.4196° | 0.5181° |
| 2001 | 1460 | 0.9041° | 0.3869° | 0.3562° | 0.9822° |
| 2002 | 1460 | 0.2007° | 0.3071° | 0.3110° | 0.3668° |
| 2003 | 1460 | 0.5667° | 0.2083° | 0.2220° | 0.6033° |
| 2004 | 1464 | 0.2143° | 0.3244° | 0.3225° | 0.3887° |
| 2005 | 1460 | 0.4797° | 0.3771° | 0.3511° | 0.6100° |
| 2006 | 1460 | 0.3619° | 0.3681° | 0.3625° | 0.5161° |
| 2007 | 1460 | 0.4765° | 0.4576° | 0.4761° | 0.6605° |
| 2008 | 1464 | 0.5787° | 0.4527° | 0.4921° | 0.7343° |
| 2009 | 1460 | 0.4353° | 0.4070° | 0.4628° | 0.5959° |
| 2010 | 1460 | 0.6929° | 0.5428° | 0.6937° | 0.8796° |
| 2011 | 1460 | 0.4359° | 0.3554° | 0.4233° | 0.5624° |
| 2012 | 1464 | 0.8202° | 0.6170° | 0.8110° | 1.0261° |
| 2013 | 1460 | 0.4261° | 0.3258° | 0.3987° | 0.5363° |
| 2014 | 1460 | 1.0797° | 0.6466° | 0.8794° | 1.2584° |
| 2015 | 1460 | 0.3938° | 0.3082° | 0.3766° | 0.5000° |
| 2016 | 1464 | 1.1461° | 0.4899° | 0.6078° | 1.2455° |
| 2017 | 1460 | 0.3667° | 0.3036° | 0.3628° | 0.4760° |
| 2018 | 1460 | 0.6020° | 0.2201° | 0.2416° | 0.6399° |
| 2019 | 1460 | 0.3819° | 0.3133° | 0.3640° | 0.4940° |
| 2020 | 1464 | 0.5162° | 0.3125° | 0.3149° | 0.6030° |
| 2021 | 1460 | 0.4842° | 0.3464° | 0.3854° | 0.5953° |
| 2022 | 1460 | 0.6020° | 0.4789° | 0.4714° | 0.7690° |
| 2023 | 1460 | 0.6769° | 0.4181° | 0.4616° | 0.7953° |
| 2024 | 1464 | 0.5991° | 0.4487° | 0.5280° | 0.7484° |
| 2025 | 1460 | 0.8459° | 0.5093° | 0.6724° | 0.9866° |
| 2026 | 685 | 0.3927° | 0.1593° | 0.2524° | 0.4237° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
