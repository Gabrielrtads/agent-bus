import os
import sqlite3
import datetime
import json

DB_PATH = os.environ.get(
    "AGENT_BUS_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentbus.db")
)
FALLBACK_PATH = os.path.join(os.path.dirname(DB_PATH), "agentbus.fallback.jsonl")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    try:
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
    finally:
        conn.close()

def touch_agent(name, tool, host=None):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO agents(name, last_seen, last_tool, host)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                last_seen = excluded.last_seen,
                last_tool = excluded.last_tool,
                host = COALESCE(excluded.host, host)
            """,
            (name, now, tool, host)
        )
        conn.commit()
    except sqlite3.Error as e:
        log_fallback("touch_agent_error", {"name": name, "tool": tool, "error": str(e)})
    finally:
        conn.close()

def log_fallback(event_type, payload):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {"timestamp": now, "event_type": event_type, "payload": payload}
    try:
        with open(FALLBACK_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass

try:
    init_db()
except Exception as e:
    log_fallback("init_db_error", {"error": str(e)})
