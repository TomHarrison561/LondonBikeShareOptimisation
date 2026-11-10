CREATE OR REPLACE VIEW clean.hourly_pickups AS
SELECT start_station_id               AS station_id,
       date_trunc('hour', start_time) AS hour,
       COUNT(*)                       AS pickups
FROM clean.journeys
GROUP BY 1, 2;

-- Average net bikes gained per working-day morning (7-10am).
-- 1 Jan (bank holiday) and 2 Jan (widely taken off) fall on weekdays but
-- don't have a commuter rush, so they're excluded, matching the forecast's
-- treatment of them as days off.
CREATE OR REPLACE VIEW clean.morning_net_flow AS
WITH working_days AS (
    SELECT DISTINCT start_time::date AS day
    FROM clean.journeys
    WHERE EXTRACT(ISODOW FROM start_time) <= 5
      AND start_time::date NOT IN (DATE '2026-01-01', DATE '2026-01-02')
),
departures AS (
    SELECT start_station_id AS station_id, COUNT(*) AS n
    FROM clean.journeys
    WHERE start_time::date IN (SELECT day FROM working_days)
      AND EXTRACT(HOUR FROM start_time) BETWEEN 7 AND 9
    GROUP BY 1
),
arrivals AS (
    SELECT end_station_id AS station_id, COUNT(*) AS n
    FROM clean.journeys
    WHERE end_time::date IN (SELECT day FROM working_days)
      AND EXTRACT(HOUR FROM end_time) BETWEEN 7 AND 9
    GROUP BY 1
)
SELECT s.station_id,
       s.station_name,
       ROUND((COALESCE(a.n, 0) - COALESCE(d.n, 0))::numeric
             / (SELECT COUNT(*) FROM working_days), 2)
           AS avg_net_inflow
FROM clean.stations s
LEFT JOIN departures d USING (station_id)
LEFT JOIN arrivals   a USING (station_id)
WHERE NOT s.is_old;
