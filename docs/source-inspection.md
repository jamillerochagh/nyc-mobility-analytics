# January 2025 source inspection

Measured November 2, 2026. Reproduce with the README commands. Full schema, checksums, source URLs, null counts, and payment distribution are recorded in `reports/january-2025-profile.json`.

## Findings

| Observation | Measured result |
|---|---:|
| Trip records | 3,475,226 |
| Parquet bytes | 59,158,238 |
| Trip columns | 20 |
| Lookup rows / distinct IDs | 265 / 265 |
| Null lookup IDs | 0 |
| Unmatched pickup / drop-off IDs | 0 / 0 |
| Pickups outside January 2025 | 22 |
| Nonpositive duration | 2,051 |
| Zero / negative distance | 90,893 / 0 |
| Negative fare | 144,118 |
| Negative total amount | 63,037 |
| Missing passenger count | 540,149 |
| Zero passenger count | 24,656 |

Flag counts overlap and must not be added to estimate excluded records. No records were removed. Counts do not establish causes for anomalies.

Pickup timestamps range from `2024-12-31 20:47:55` to `2025-02-01 00:00:44`. Drop-off timestamps range from `2024-12-18 07:52:40` to `2025-02-01 23:44:11`. File month is therefore not a reliable event-date constraint.

## Schema implications

DuckDB observed `INTEGER` vendor/location IDs, `BIGINT` passenger count/rate code/payment type, timezone-naive `TIMESTAMP` pickup/drop-off fields, `VARCHAR` store-and-forward flag, and `DOUBLE` distance and amount columns. These are reader-exposed SQL types, not a claim about every month's Parquet physical/logical encoding.

The file spells the airport column **`Airport_fee`**, while the published dictionary uses `airport_fee`. Staging needs explicit name normalization. `cbd_congestion_fee` is present.

Passenger count, rate code, store-and-forward flag, congestion surcharge, and airport fee each have 540,149 null values. Payment type 0 also appears 540,149 times. Matching counts do not establish that these are the same records; a row-level cross-tab is needed to verify overlap. All other columns have zero observed nulls.

Observed payment codes are 0–5. The dictionary includes code 6 even though it was not observed here; accepted-value rules should follow the documented domain rather than only this sample.

## Validation and boundaries

The full-file profiling run succeeded. A second run produced identical results after excluding the generation timestamp. Payment-category counts reconcile to the source row count. The lookup has unique non-null identifiers and both zone joins cover every observed record. The report includes SHA-256 digests to identify exactly which inputs were profiled. CLI help and Python compilation passed. Raw downloads and the virtual environment were confirmed ignored by Git. Git's tracked-diff whitespace check passed; all new artifacts remain untracked pending a first commit.

There is no ingestion pipeline, database, dbt project, or automated test suite at this milestone. February and March are not downloaded. Exclusion rules, duplicate analysis, monetary reconciliation, and detailed outlier investigation remain open. No execution benchmark is claimed.
