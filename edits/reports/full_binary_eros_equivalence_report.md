# eros TYCHOS export-equivalence comparison

Status: **PASS**  
Baseline: `C:/Users/admin/OneDrive/Documentos/00-juan/tychos/TSN/00-backup/native-relative-baseline/eros_ephemerides_before.txt`  
Candidate: `C:/Users/admin/OneDrive/Documentos/00-juan/tychos/TSN/edits/data/raw/eros_ephemerides_after.txt`

This compares formatted TYCHOS output before and after a structural refactor.
It does not compare either export with JPL.

| Check | Result |
|---|---:|
| Baseline / candidate rows | 75969 / 75969 |
| Timestamp mismatches | 0 |
| RA text mismatches | 0 |
| Declination text mismatches | 0 |
| Distance text mismatches | 0 |
| Elongation text mismatches | 0 |
| Direction RMS / maximum | 5.1965780116e-07 / 1.7075472925e-06 deg |
| Maximum displayed-distance numeric delta | 0 |
| Maximum elongation delta | 0 deg |
| Distance units identical | yes |

A pass means every timestamp and every displayed RA, declination, distance and
elongation field is identical. It supports export equivalence at TYCHOS text
precision; it does not establish physical correctness.
