DROP TABLE IF EXISTS clean.stations CASCADE;

CREATE TABLE clean.stations AS
WITH names AS (
    SELECT start_station_id AS station_id, start_station_name AS station_name
    FROM clean.journeys
    UNION ALL
    SELECT end_station_id, end_station_name
    FROM clean.journeys
),
counts AS (
    SELECT station_id, station_name, COUNT(*) AS n
    FROM names
    GROUP BY station_id, station_name
)
SELECT DISTINCT ON (station_id)
       station_id,
       station_name,
       station_name ~ '_OLD$' AS is_old
FROM counts
ORDER BY station_id, n DESC;

ALTER TABLE clean.stations ADD PRIMARY KEY (station_id);