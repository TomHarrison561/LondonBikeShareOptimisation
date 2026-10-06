from db import Database
from load import load_journeys

def main():
    db = Database()

    db.run_sql_file("schemas.sql")
    load_journeys(db)
    db.run_sql_file("clean_data.sql")
    db.run_sql_file("stations.sql")
    db.run_sql_file("views.sql")

    print(db.query("""
        SELECT (SELECT COUNT(*) FROM raw.journeys)            AS raw_rows,
               (SELECT COUNT(*) FROM clean.journeys)          AS clean_rows,
               (SELECT COUNT(*) FROM clean.stations)          AS stations,
               (SELECT COUNT(*) FROM clean.stations
                WHERE is_old)                                AS old_stations
    """))

if __name__ == "__main__":
    main()