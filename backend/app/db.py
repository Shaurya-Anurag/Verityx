import os, sqlite3
from pathlib import Path
from contextlib import contextmanager
DB_PATH=Path(os.getenv("VERITYX_DB_PATH","./verityx.db"))
DB_PATH.parent.mkdir(parents=True,exist_ok=True)
@contextmanager
def connect():
 d=sqlite3.connect(DB_PATH); d.row_factory=sqlite3.Row
 try: yield d; d.commit()
 finally: d.close()
def init_db():
 with connect() as d:
  d.execute("""CREATE TABLE IF NOT EXISTS analyses(id TEXT PRIMARY KEY,claim TEXT NOT NULL,status TEXT NOT NULL,summary TEXT NOT NULL,freshness_score INTEGER,created_at TEXT NOT NULL,evidence_json TEXT NOT NULL,claims_json TEXT NOT NULL,method TEXT NOT NULL,rationale TEXT NOT NULL)""")
  d.execute("""CREATE TABLE IF NOT EXISTS monitors(id TEXT PRIMARY KEY,query TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,last_checked TEXT,last_analysis_id TEXT)""")
