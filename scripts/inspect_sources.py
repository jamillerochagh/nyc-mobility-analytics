"""Profile local official TLC sources without modifying their records."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': digest.hexdigest()}


def profile(trips_path, zones_path):
    with duckdb.connect() as connection:
        connection.read_parquet(str(trips_path)).create_view('trips')
        connection.read_csv(str(zones_path), header=True).create_view('zones')

        def rows(sql):
            cursor = connection.execute(sql)
            names = [item[0] for item in cursor.description]
            return [dict(zip(names, row)) for row in cursor.fetchall()]

        schema = rows('DESCRIBE trips')
        nulls = {}
        for column in schema:
            name = column['column_name']
            quoted = '"' + name.replace('"', '""') + '"'
            nulls[name] = rows(
                f'SELECT count(*) FILTER (WHERE {quoted} IS NULL) AS n FROM trips'
            )[0]['n']
        summary = rows("""
            SELECT count(*) AS rows,
                min(tpep_pickup_datetime) AS earliest_pickup,
                max(tpep_pickup_datetime) AS latest_pickup,
                min(tpep_dropoff_datetime) AS earliest_dropoff,
                max(tpep_dropoff_datetime) AS latest_dropoff,
                count(*) FILTER (WHERE tpep_pickup_datetime < TIMESTAMP '2025-01-01'
                    OR tpep_pickup_datetime >= TIMESTAMP '2025-02-01') AS pickup_outside_january,
                count(*) FILTER (WHERE tpep_dropoff_datetime <= tpep_pickup_datetime)
                    AS nonpositive_duration,
                count(*) FILTER (WHERE trip_distance = 0) AS zero_distance,
                count(*) FILTER (WHERE trip_distance < 0) AS negative_distance,
                count(*) FILTER (WHERE fare_amount < 0) AS negative_fare,
                count(*) FILTER (WHERE total_amount < 0) AS negative_total,
                count(*) FILTER (WHERE passenger_count = 0) AS zero_passengers,
                count(*) FILTER (WHERE NOT EXISTS (
                    SELECT 1 FROM zones z WHERE z.LocationID = trips.PULocationID))
                    AS unmatched_pickup_zone,
                count(*) FILTER (WHERE NOT EXISTS (
                    SELECT 1 FROM zones z WHERE z.LocationID = trips.DOLocationID))
                    AS unmatched_dropoff_zone
            FROM trips
        """)[0]
        return {
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'January 2025; observations are flags, not exclusions',
            'sources': {
                'trips': {**fingerprint(trips_path), 'url':
                    'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet'},
                'zones': {**fingerprint(zones_path), 'url':
                    'https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv'},
            },
            'trip_schema': schema,
            'zone_schema': rows('DESCRIBE zones'),
            'summary': summary,
            'null_counts': nulls,
            'payment_types': rows('SELECT payment_type, count(*) AS rows FROM trips GROUP BY 1 ORDER BY 1'),
            'zone_summary': rows('SELECT count(*) AS rows, count(DISTINCT LocationID) AS distinct_ids, count(*) FILTER (WHERE LocationID IS NULL) AS null_ids FROM zones')[0],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trips', type=Path, default=Path('data/raw/yellow_tripdata_2025-01.parquet'))
    parser.add_argument('--zones', type=Path, default=Path('data/raw/taxi_zone_lookup.csv'))
    parser.add_argument('--output', type=Path, default=Path('reports/january-2025-profile.json'))
    args = parser.parse_args()
    report = profile(args.trips, args.zones)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], indent=2, default=str))
    print(f'Report: {args.output}')


if __name__ == '__main__':
    main()
