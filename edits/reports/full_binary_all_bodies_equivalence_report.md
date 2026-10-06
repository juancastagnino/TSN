# Full binary all-body TYCHOS export equivalence

Status: **PASS**  
Baseline: `C:/Users/admin/OneDrive/Documentos/00-juan/tychos/TSN/00-backup/native-relative-baseline/tychos_ephemerides.txt`  
Candidate: `C:/Users/admin/OneDrive/Documentos/00-juan/tychos/TSN/edits/data/raw/tychos_ephemerides.txt`

Generation timestamps are excluded; every other exported line is compared exactly.

| Check | Result |
|---|---:|
| Baseline retained lines | 759756 |
| Candidate retained lines | 759756 |
| Ignored metadata lines | 1 / 1 |
| First-ten exact-line mismatches | 0 |

A pass establishes exact formatted export equivalence for every body in the
combined TYCHOS file. It is a structural migration gate, not a JPL accuracy test.
