# TYCHOS Mercury Ephemeris Audit

**Model:** TYCHOS mercury

## Dataset

- Samples: **75969**
- Interval: **2000-06-21 00:00:00 → 2026-06-21 00:00:00**
- Median cadence: **3.000 h**
- Reference: **JPL ICRF astrometric RA/Dec**
- Ecliptic residual analysis: fixed J2000 obliquity 23.439291111 deg
- Analysis generated (UTC): 2026-09-27T14:27:14.360337+00:00
- Export configuration: Explicit Mercury/Venus with eccentricity
- Input hashes and any explicitly supplied export settings are recorded in the summary JSON.

## Current residuals

| Metric | Mean | RMS | P95 abs. | Max abs. |
|---|---:|---:|---:|---:|
| RA (coordinate) | 0.1118° | 0.7049° | 1.4924° | 2.1070° |
| Declination | 0.4955° | 0.6356° | 1.1947° | 1.9100° |
| Angular separation | 0.7949° | 0.9253° | 1.7393° | 2.5701° |
| Ecliptic longitude | 0.1658° | 0.7889° | 1.6079° | 2.4571° |
| Ecliptic latitude | 0.3683° | 0.4848° | 0.9226° | 1.3738° |

## Annual stability

| Year | N | RMS longitude | RMS latitude | RMS Dec | RMS separation |
|---:|---:|---:|---:|---:|---:|
| 2000 | 1552 | 0.7183° | 0.3040° | 0.3919° | 0.7791° |
| 2001 | 2920 | 0.7224° | 0.4788° | 0.5940° | 0.8661° |
| 2002 | 2920 | 0.7453° | 0.4937° | 0.6023° | 0.8935° |
| 2003 | 2920 | 0.7510° | 0.4888° | 0.5998° | 0.8955° |
| 2004 | 2928 | 0.7797° | 0.4878° | 0.6309° | 0.9190° |
| 2005 | 2920 | 0.8076° | 0.4865° | 0.6538° | 0.9419° |
| 2006 | 2920 | 0.7808° | 0.4772° | 0.6393° | 0.9142° |
| 2007 | 2920 | 0.7309° | 0.4753° | 0.6122° | 0.8712° |
| 2008 | 2928 | 0.7442° | 0.4848° | 0.6039° | 0.8876° |
| 2009 | 2920 | 0.7552° | 0.4952° | 0.6100° | 0.9026° |
| 2010 | 2920 | 0.7697° | 0.4861° | 0.6164° | 0.9097° |
| 2011 | 2920 | 0.8100° | 0.4892° | 0.6556° | 0.9454° |
| 2012 | 2928 | 0.8074° | 0.4823° | 0.6610° | 0.9396° |
| 2013 | 2920 | 0.7687° | 0.4756° | 0.6394° | 0.9031° |
| 2014 | 2920 | 0.7424° | 0.4777° | 0.6151° | 0.8822° |
| 2015 | 2920 | 0.7801° | 0.4920° | 0.6194° | 0.9219° |
| 2016 | 2928 | 0.7846° | 0.4913° | 0.6171° | 0.9252° |
| 2017 | 2920 | 0.7976° | 0.4876° | 0.6433° | 0.9342° |
| 2018 | 2920 | 0.8321° | 0.4880° | 0.6742° | 0.9638° |
| 2019 | 2920 | 0.8121° | 0.4789° | 0.6645° | 0.9419° |
| 2020 | 2928 | 0.7698° | 0.4751° | 0.6375° | 0.9039° |
| 2021 | 2920 | 0.7869° | 0.4829° | 0.6244° | 0.9227° |
| 2022 | 2920 | 0.8136° | 0.4964° | 0.6315° | 0.9526° |
| 2023 | 2920 | 0.8213° | 0.4872° | 0.6318° | 0.9544° |
| 2024 | 2928 | 0.8429° | 0.4893° | 0.6716° | 0.9739° |
| 2025 | 2920 | 0.8556° | 0.4844° | 0.6868° | 0.9824° |
| 2026 | 1369 | 1.0236° | 0.6079° | 0.8942° | 1.1895° |

## Interpretation notes

- No lunar periodic terms are fitted to this body.
- Compare shared-frame changes across bodies using the same epochs and declared export configuration.
- Ecliptic coordinates use a common fixed rotation; this does not establish the simulator's reference-frame accuracy.
