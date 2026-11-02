# NYC Mobility Analytics

A learning project building an analytics engineering platform from official NYC Yellow Taxi records. The business context is a fictional mobility company; the trip records are real.

**Status: Milestone 1 — source inspection and architecture only.** PostgreSQL, Docker, ingestion, dbt, CI, and the dashboard are not implemented. No production or cloud deployment is claimed.

The platform will explore observed trip demand, zone performance, fares, trip characteristics, payment methods, and recorded tipping patterns. January 2025 is the first batch; January–March 2025 is the initial expansion target. Annual seasonality requires longer coverage.

## Reproduce the inspection

Prerequisites: Python 3.9 or later with venv support, curl, and internet access. The initial inspection ran on macOS ARM64 with Python 3.9.6 and DuckDB 1.4.3. This does not establish full cross-platform compatibility.

Run from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-inspection.txt
mkdir -p data/raw
curl --fail --location --retry 3 --output data/raw/yellow_tripdata_2025-01.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet
curl --fail --location --retry 3 --output data/raw/taxi_zone_lookup.csv https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
.venv/bin/python scripts/inspect_sources.py
```

The script writes `reports/january-2025-profile.json`, including source URLs, SHA-256 hashes, byte sizes, observed schema, row counts, null counts, payment distribution, and zone coverage. It scans all rows in the local file without altering them. Its January boundary checks are intentionally specific to this milestone. DuckDB is used in memory for inspection; PostgreSQL remains the planned warehouse.

Raw files and the virtual environment are ignored by Git. The compact profile is intended for version control. If the publisher changes a file, its checksum and findings may change. Downloads here are manual inspection commands, not a validated production ingestion pipeline.

## Measured baseline

On November 2, 2026, the downloaded January source contained **3,475,226 records** and occupied **59,158,238 bytes**. The lookup contained **265 unique non-null zone IDs**. Every observed pickup and drop-off ID matched the lookup; this does not prove that all zones represent precise known locations.

See [inspection findings](docs/source-inspection.md) for anomalies and [architecture and contracts](docs/architecture.md) for design decisions.

## Milestones

1. Requirements, source inspection, architecture — current.
2. Docker and PostgreSQL.
3. Python ingestion and ingestion metadata.
4. dbt sources and staging.
5. Dimensional models and marts.
6. Incremental processing and data quality.
7. GitHub Actions and automated tests.
8. Business analysis and dashboard.
9. Optional BigQuery deployment, with separate approval for paid resources.
10. Documentation, technical review, and portfolio publication.

No CI badge, dashboard screenshots, or performance improvement claims are included before those deliverables exist. Runtime and warehouse storage benchmarks remain unmeasured.

## Sources

- [Official TLC datasets and lookup links](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [Yellow Taxi data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)

TLC cautions that the accuracy of provider-submitted data is not guaranteed. Analytical relationships will be described as associations, not causal effects.
