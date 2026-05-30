PRAGMA user_version = 2;

CREATE TABLE IF NOT EXISTS agents(
  name      TEXT PRIMARY KEY,
  last_seen TEXT NOT NULL,
  last_tool TEXT,
  host      TEXT
);

CREATE TABLE IF NOT EXISTS messages(
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_id    TEXT NOT NULL,
  from_agent   TEXT NOT NULL,
  to_agent     TEXT NOT NULL,
  type         TEXT NOT NULL CHECK(type IN ('handoff','psa','question','answer','alert','note')),
  subject      TEXT NOT NULL,
  body         TEXT NOT NULL,
  priority     INTEGER DEFAULT 2 CHECK(priority BETWEEN 1 AND 3),
  created_at   TEXT NOT NULL,
  read_at      TEXT,
  acked_at     TEXT,
  mirrored_to_channel INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_inbox  ON messages(to_agent, acked_at, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_thread ON messages(thread_id, created_at);

CREATE TABLE IF NOT EXISTS acks(
  message_id INTEGER REFERENCES messages(id),
  agent      TEXT,
  acked_at   TEXT,
  PRIMARY KEY(message_id, agent)
);

CREATE TABLE IF NOT EXISTS resource_locks(
  resource    TEXT PRIMARY KEY,
  locked_by   TEXT NOT NULL,
  locked_at   TEXT NOT NULL,
  ttl_seconds INTEGER DEFAULT 300,
  reason      TEXT
);

CREATE INDEX IF NOT EXISTS idx_locks_agent ON resource_locks(locked_by);
