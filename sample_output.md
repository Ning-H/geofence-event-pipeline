# Sample Output: Real-Time Geofence Event Pipeline

Generated from a local Phase 1 run using LocalStack on April 30, 2026.

## Run Summary

The simulator published synthetic NYC device pings into a LocalStack-backed Kinesis stream. The Python consumer read the stream, detected geofence state changes with Shapely, wrote raw pings and geofence events to S3 Parquet, and updated latest device state in DynamoDB.

Observed local outputs:

- Raw ping Parquet files written under `s3://radar-pipeline-local/raw-pings/`
- Geofence event Parquet files written under `s3://radar-pipeline-local/geofence-events/`
- DynamoDB `device_state` rows updated for simulated devices
- Geofence events include both `ENTER` and `EXIT`
- Exit events include `dwell_time_seconds`

## S3 Parquet Outputs

Command:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://radar-pipeline-local/raw-pings/ --recursive
aws --endpoint-url=http://localhost:4566 s3 ls s3://radar-pipeline-local/geofence-events/ --recursive
```

Sample raw ping files:

```text
2026-04-29 23:52:01       4750 raw-pings/year=2026/month=04/day=30/hour=03/pings-00a6261c-c0f8-43c9-aba2-a337dc977e75.parquet
2026-04-29 23:51:54       4736 raw-pings/year=2026/month=04/day=30/hour=03/pings-053ab5b2-083d-417c-b058-3ce6c743223e.parquet
2026-04-29 23:52:20       4748 raw-pings/year=2026/month=04/day=30/hour=03/pings-055b5538-9815-48ec-9291-c429a227a7e0.parquet
...
```

Sample geofence event files:

```text
2026-04-29 23:52:00       8056 geofence-events/year=2026/month=04/day=30/events-5ad373d6-5fbd-4d4c-9967-e8f3ee93dfe9.parquet
2026-04-29 23:51:48       7879 geofence-events/year=2026/month=04/day=30/events-7e4360ff-5e96-482b-93a8-9179cbc46183.parquet
2026-04-29 23:52:28       7976 geofence-events/year=2026/month=04/day=30/events-ac45255d-f10d-4514-8c8f-8fd3489f78dc.parquet
```

## Raw Ping Preview

Command:

```bash
python scripts/preview_parquet_outputs.py
```

Latest raw ping file:

```text
s3://radar-pipeline-local/raw-pings/
latest file: raw-pings/year=2026/month=04/day=30/hour=03/pings-79b0763c-6857-40f0-980f-b0cb1a1f555b.parquet
```

Sample rows:

```text
device_id                                   lat       lng        timestamp                     speed
device_dd35b084-79e3-4476-9cde-bde6482c0206 40.763001 -73.983041 2026-04-30T03:52:12.286451Z   6.65
device_a17e6305-46e8-4808-8aad-8a09bdeee1d8 40.657422 -73.810851 2026-04-30T03:52:12.286931Z  13.43
device_ed6282bb-c799-4795-bda7-3b4f9509cf38 40.776368 -73.974658 2026-04-30T03:52:12.287403Z   4.24
device_e570bdb3-26c2-4bf9-8c55-0b33b3253785 40.747551 -73.985008 2026-04-30T03:52:12.287786Z   9.57
device_e95981ce-ca5b-4b2d-a188-568b0217332e 40.736125 -73.944979 2026-04-30T03:52:12.288217Z   8.10
```

## Geofence Event Preview

Latest geofence event file:

```text
s3://radar-pipeline-local/geofence-events/
latest file: geofence-events/year=2026/month=04/day=30/events-ac45255d-f10d-4514-8c8f-8fd3489f78dc.parquet
```

Sample rows:

```text
event_id                             device_id                                   geofence_id      geofence_name          event_type lat       lng        timestamp                    dwell_time_seconds
b16a6bc5-9e59-4b54-82e9-0f38771a5f01 device_f0e05864-5c29-41a5-9726-fb17cc317494 brooklyn_bridge  Brooklyn Bridge        ENTER      40.705483 -73.992848 2026-04-30T03:51:50.350182Z NaN
94a41f10-a6f4-4d9a-9cfb-f9497338afb8 device_e95981ce-ca5b-4b2d-a188-568b0217332e grand_central    Grand Central Terminal ENTER      40.752549 -73.974884 2026-04-30T03:51:53.453253Z NaN
b7436001-b733-4af6-9b9d-cb4d3e911e5d device_72dc290c-db5d-41f0-8711-ac9986692e90 brooklyn_bridge  Brooklyn Bridge        EXIT       40.713699 -73.994400 2026-04-30T03:51:54.991386Z 9.298278
1e2be85d-529e-4289-b422-5a596c327bda device_2d81e3b0-5297-4108-8552-dfb64a419f24 brooklyn_bridge  Brooklyn Bridge        ENTER      40.705296 -74.002582 2026-04-30T03:51:56.576164Z NaN
6c16045f-801e-4e8c-9aa0-b2f393ddd247 device_dd35b084-79e3-4476-9cde-bde6482c0206 times_square     Times Square           EXIT       40.761003 -73.984568 2026-04-30T03:51:58.252385Z 14.104116
```

## DynamoDB Hot State

Command:

```bash
python scripts/inspect_localstack.py --dynamodb
```

Sample rows from `device_state`:

```text
device_421916f2-dddf-4c64-91f9-27829df285ca  geofence=outside             last_seen=2026-04-30T03:52:12.280413+00:00
device_5a890723-3e7e-484a-b033-6fbde1ac2db7  geofence=Central Park South  last_seen=2026-04-30T03:52:09.171567+00:00
device_a17e6305-46e8-4808-8aad-8a09bdeee1d8  geofence=JFK Airport         last_seen=2026-04-30T03:52:12.286931+00:00
device_2b42ef34-d63b-401d-889b-b3593733da69  geofence=Central Park South  last_seen=2026-04-30T03:52:12.279746+00:00
device_d7f4a656-732b-4a32-a4bd-245b458c116a  geofence=JFK Airport         last_seen=2026-04-30T03:52:10.718417+00:00
```

## Interpretation

This output proves the pipeline works end to end:

- Kinesis ingestion accepted simulated location pings.
- The consumer processed streaming events.
- Geofence detection emitted `ENTER` and `EXIT` events.
- Dwell time was calculated for exit events.
- Raw and derived events were persisted as partitioned Parquet files.
- DynamoDB maintained current per-device geofence state for real-time lookup.
