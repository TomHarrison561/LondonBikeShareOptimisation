DROP TABLE IF EXISTS clean.station_locations CASCADE;

CREATE TABLE clean.station_locations AS
SELECT s.station_id,
       s.station_name,
       b.lat,
       b.lon,
       b.n_docks::int AS n_docks
FROM clean.stations s
JOIN raw.bikepoints b ON b.terminal_id = s.station_id
WHERE NOT s.is_old;

ALTER TABLE clean.station_locations ADD PRIMARY KEY (station_id);