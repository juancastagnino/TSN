# TYCHOS Jupiter Ephemeris Audit

**Model:** TYCHOS jupiter

## Dataset

- Samples: **37985**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **6.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-20T14:57:07.293446+00:00
- Export configuration: new analysis with all planets but tweaks to the moon were done only
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.1014° | 0.3610° | 0.6834° | 0.8547° |
| Declination | -0.2771° | 0.3282° | 0.5797° | 0.7313° |
| Angular separation | 0.4365° | 0.4775° | 0.8204° | 1.0197° |
| Ecliptic longitude | 0.1342° | 0.3927° | 0.7535° | 0.9621° |
| Ecliptic latitude | -0.2411° | 0.2718° | 0.4356° | 0.4840° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 776 | 0.2702° | 0.2475° | 0.2587° | 0.3665° |
| 2001 | 1460 | 0.3177° | 0.2868° | 0.3118° | 0.4280° |
| 2002 | 1460 | 0.2017° | 0.3559° | 0.3152° | 0.4090° |
| 2003 | 1460 | 0.1677° | 0.3945° | 0.3628° | 0.4286° |
| 2004 | 1464 | 0.3193° | 0.3962° | 0.4459° | 0.5088° |
| 2005 | 1460 | 0.5026° | 0.3615° | 0.4949° | 0.6190° |
| 2006 | 1460 | 0.5698° | 0.2961° | 0.4299° | 0.6421° |
| 2007 | 1460 | 0.4467° | 0.2094° | 0.2525° | 0.4934° |
| 2008 | 1464 | 0.2007° | 0.1211° | 0.0972° | 0.2344° |
| 2009 | 1460 | 0.2896° | 0.0643° | 0.1214° | 0.2966° |
| 2010 | 1460 | 0.4357° | 0.0708° | 0.2131° | 0.4413° |
| 2011 | 1460 | 0.4250° | 0.1306° | 0.2262° | 0.4445° |
| 2012 | 1464 | 0.3624° | 0.2126° | 0.2628° | 0.4201° |
| 2013 | 1460 | 0.2233° | 0.2955° | 0.3116° | 0.3704° |
| 2014 | 1460 | 0.0857° | 0.3605° | 0.3436° | 0.3705° |
| 2015 | 1460 | 0.2379° | 0.3945° | 0.4231° | 0.4607° |
| 2016 | 1464 | 0.4718° | 0.3922° | 0.5203° | 0.6135° |
| 2017 | 1460 | 0.6634° | 0.3546° | 0.5555° | 0.7521° |
| 2018 | 1460 | 0.7092° | 0.2870° | 0.4540° | 0.7650° |
| 2019 | 1460 | 0.5564° | 0.1995° | 0.2393° | 0.5910° |
| 2020 | 1464 | 0.3009° | 0.1134° | 0.0709° | 0.3215° |
| 2021 | 1460 | 0.3123° | 0.0632° | 0.1180° | 0.3186° |
| 2022 | 1460 | 0.4062° | 0.0778° | 0.1903° | 0.4135° |
| 2023 | 1460 | 0.3981° | 0.1401° | 0.1805° | 0.4220° |
| 2024 | 1464 | 0.3448° | 0.2210° | 0.2310° | 0.4095° |
| 2025 | 1460 | 0.2105° | 0.3011° | 0.3208° | 0.3674° |
| 2026 | 685 | 0.2641° | 0.3650° | 0.3965° | 0.4505° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
