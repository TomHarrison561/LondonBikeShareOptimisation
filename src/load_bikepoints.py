import pandas as pd
import requests
from db import Database

BIKEPOINT_URL = "https://api.tfl.gov.uk/BikePoint"

def load_bikepoints(db):
    response = requests.get(BIKEPOINT_URL, timeout=30)
    response.raise_for_status()
    rows = []
    for point in response.json():
        props = {p["key"]: p["value"] for p in point["additionalProperties"]}
        rows.append({
            "bikepoint_id": point["id"],
            "terminal_id": props.get("TerminalName"),
            "name": point["commonName"],
            "lat": point["lat"],
            "lon": point["lon"],
            "n_docks": props.get("NbDocks"),
        })

    df = pd.DataFrame(rows)
    df.to_sql("bikepoints", db.engine, schema="raw",
              if_exists="replace", index=False)

if __name__ == "__main__":
    load_bikepoints(Database())