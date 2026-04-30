-- Which geofences have the most daily visitors?
SELECT
  date(timestamp) AS visit_date,
  geofence_name,
  count(DISTINCT device_id) AS unique_visitors
FROM radar_pipeline.geofence_events
WHERE event_type = 'ENTER'
GROUP BY 1, 2
ORDER BY visit_date DESC, unique_visitors DESC;

-- What is the average dwell time per geofence?
SELECT
  geofence_name,
  avg(dwell_time_seconds) AS avg_dwell_seconds,
  approx_percentile(dwell_time_seconds, 0.5) AS median_dwell_seconds
FROM radar_pipeline.geofence_events
WHERE event_type = 'EXIT'
  AND dwell_time_seconds IS NOT NULL
GROUP BY 1
ORDER BY avg_dwell_seconds DESC;

-- Which devices visited multiple geofences in one day?
SELECT
  date(timestamp) AS visit_date,
  device_id,
  count(DISTINCT geofence_id) AS geofences_visited
FROM radar_pipeline.geofence_events
WHERE event_type = 'ENTER'
GROUP BY 1, 2
HAVING count(DISTINCT geofence_id) >= 2
ORDER BY visit_date DESC, geofences_visited DESC;

-- Peak entry times per geofence.
SELECT
  geofence_name,
  hour(timestamp) AS hour_of_day,
  count(*) AS entries
FROM radar_pipeline.geofence_events
WHERE event_type = 'ENTER'
GROUP BY 1, 2
ORDER BY geofence_name, entries DESC;
