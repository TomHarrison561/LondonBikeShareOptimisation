CREATE OR REPLACE VIEW clean.hourly_pickups AS
SELECT start_station_id               AS station_id,
       date_trunc('hour', start_time) AS hour,
       COUNT(*)                       AS pickups
FROM clean.journeys
GROUP BY 1, 2;

CREATE OR REPLACE VIEW clean.morning_net_flow AS
WITH departures AS (
    SELECT start_station_id AS station_id, COUNT(*) AS n
    FROM clean.journeys
    WHERE EXTRACT(ISODOW FROM start_time) <= 5
      AND EXTRACT(HOUR FROM start_time) BETWEEN 7 AND 9
    GROUP BY 1
),
arrivals AS (
    SELECT end_station_id AS station_id, COUNT(*) AS n
    FROM clean.journeys
    WHERE EXTRACT(ISODOW FROM end_time) <= 5
      AND EXTRACT(HOUR FROM end_time) BETWEEN 7 AND 9
    GROUP BY 1
),
weekdays AS (
    SELECT COUNT(DISTINCT start_time::date) AS n_days
    FROM clean.journeys
    WHERE EXTRACT(ISODOW FROM start_time) <= 5
)
SELECT s.station_id,
       s.station_name,
       ROUND((COALESCE(a.n, 0) - COALESCE(d.n, 0))::numeric / w.n_days, 2)
           AS avg_net_inflow
FROM clean.stations s
LEFT JOIN departures d USING (station_id)
LEFT JOIN arrivals   a USING (station_id)
CROSS JOIN weekdays w
WHERE NOT s.is_old;