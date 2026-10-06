DROP TABLE IF EXISTS clean.journeys CASCADE;

CREATE TABLE clean.journeys AS
SELECT DISTINCT ON (rental_id::bigint)
    rental_id::bigint AS rental_id,
    start_time::timestamp AS start_time,
    end_time::timestamp AS end_time,
    start_station_id,
    REGEXP_REPLACE(TRIM(start_station_name), '\s+', ' ', 'g') AS start_station_name,
    end_station_id,
    REGEXP_REPLACE(TRIM(end_station_name), '\s+', ' ', 'g') AS end_station_name,
    bike_id,
    bike_model,
    duration_ms::bigint / 60000.0 AS duration_min
FROM raw.journeys
WHERE rental_id IS NOT NULL
  AND start_station_id IS NOT NULL
  AND end_station_id IS NOT NULL
  -- keep journeys between 1 minute and 3 hours
  AND duration_ms::bigint BETWEEN 60000 AND 10800000
ORDER BY rental_id::bigint;

ALTER TABLE clean.journeys ADD PRIMARY KEY (rental_id);