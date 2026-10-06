import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT/"sql"
RAW_DIR = ROOT/"data"/"raw"

class Database:
    def __init__(self, url=None):
        self.url = url or os.environ.get("BIKESHARE_DB_URL")
        if not self.url:
            raise RuntimeError("BIKESHARE_DB_URL not found")
        self.engine = create_engine(self.url)

    def run_sql_file(self, filename):
        sql = (SQL_DIR / filename).read_text()
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def query(self, sql):
        return pd.read_sql(text(sql), self.engine)


