# Phase export-equivalence comparison

Status: **PASS**  
Coordinate/numeric tolerance: `1.000e-09`  
Constructed midpoint endpoint-angle tolerance: `2.000e-06 deg`

## Scientific summary fields

Provenance fields are intentionally excluded.

| Body | Maximum numeric delta | Other differences |
|---|---:|---|
| jupiter_apparent_of_date | 0 | none |
| mars_apparent_of_date | 0 | none |
| mercury_apparent_of_date | 0 | none |
| moon_apparent_of_date | 0 | none |
| neptune_apparent_of_date | 0 | none |
| pluto_apparent_of_date | 0 | none |
| saturn_apparent_of_date | 0 | none |
| sun_apparent_of_date | 0 | none |
| uranus_apparent_of_date | 0 | none |
| venus_apparent_of_date | 0 | none |

## Per-sample and spectral artifacts

Byte-identical files: `30` of `30`.

Non-identical files: none

## Sun-Mars binary CSV

Rows: `9497`; timestamp mismatches: `0`.

| Field | Maximum absolute delta | RMS delta |
|---|---:|---:|
| midpoint_opposition_angle_deg | 1.20741827914e-06 | 1.64727569253e-07 |
| midpoint_opposition_error_deg | 1.20741827914e-06 | 1.64727569253e-07 |
| earth_opposition_error_deg | 1.13686837722e-12 | 2.08583425347e-14 |
| earth_opposition_angle_deg | 1.13131726209e-12 | 2.07257183026e-14 |
| pvp_opposition_error_deg | 5.40012479178e-13 | 1.74397618371e-14 |
| pvp_opposition_angle_deg | 5.20694598549e-13 | 1.69852063427e-14 |
| earth_mars_radius | 1.13686837722e-13 | 9.18657979681e-15 |
| sun_mars_separation | 8.52651282912e-14 | 1.00141450734e-14 |
| mars_world_z | 5.68434188608e-14 | 9.67523426779e-15 |
| earth_mars_dz | 5.68434188608e-14 | 9.67523426779e-15 |
| pvp_mars_dz | 5.68434188608e-14 | 9.67523426779e-15 |
| pvp_mars_radius | 5.68434188608e-14 | 9.44330907037e-15 |
| midpoint_center_z | 5.68434188608e-14 | 5.90087749775e-15 |
| midpoint_sun_dz | 5.68434188608e-14 | 6.19592944991e-15 |
| midpoint_mars_dz | 5.68434188608e-14 | 6.25838278728e-15 |

## Interpretation

- This gate compares TYCHOS outputs before and after a structural refactor; it does not measure agreement with JPL.
- Different export hashes or decimal strings are acceptable only when timestamp-aligned numeric values remain within tolerance.
- The midpoint is defined from the two endpoints, so its opposition is exactly 180 degrees by construction. Its relaxed angle tolerance covers only floating-point sensitivity of `acos` at that endpoint; it does not relax any position field.
- A pass supports coordinate equivalence at the declared tolerance; it does not prove physical correctness.
