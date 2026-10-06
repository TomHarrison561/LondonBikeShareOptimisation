import pandas as pd
from db import Database, RAW_DIR

COLUMN_MAP = {
    "Number": "rental_id",
    "Start date": "start_time",
    "Start station number": "start_station_id",
    "Start station": "start_station_name",
    "End date": "end_time",
    "End station number": "end_station_id",
    "End station": "end_station_name",
    "Bike number": "bike_id",
    "Bike model": "bike_model",
    "Total duration (ms)": "duration_ms",
}
COLUMNS = list(COLUMN_MAP.values())

def load_journeys(db):
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No CSV files found")

    for i, path in enumerate(files):
        df = pd.read_csv(path, dtype=str)   # create pandas data frame
        df = df.rename(columns=COLUMN_MAP).reindex(columns=COLUMNS)
        # reindex removes columns not in COLUMN_MAP, adds missing columns
        # with empty values, and makes each file have same column order

        df["source_file"] = path.name

        df.to_sql(
            "journeys", db.engine, schema="raw",
            if_exists="replace" if i == 0 else "append",
            index=False, chunksize=10_000, method="multi"
        )


if __name__ == "__main__":
    db = Database()
    db.run_sql_file("schemas.sql")
    load_journeys(db)

