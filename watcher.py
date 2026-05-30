"""
env-watcher - monitors changes in environment files and notifies the agent-bus.
Usage: python watcher.py [--daemon]
"""
import os, sys, time, sqlite3, datetime, uuid, argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set AGENT_BUS_DB environment variable to override the database path.
DB_PATH = os.environ.get(
    "AGENT_BUS_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentbus.db")
)

# Map filename patterns to human-readable descriptions
FILE_PATTERNS = [
    ("mcp_config.json",       "mcp_config.json (Antigravity IDE)"),
    (".claude/mcp.json",      "mcp.json (Claude Code CLI)"),
    (".claude.json",          ".claude.json (Claude Code global config)"),
    ("AGENTS.md",             "AGENTS.md (agent handoff)"),
    ("CLAUDE.md",             "CLAUDE.md (Claude rules)"),
    ("GEMINI.md",             "GEMINI.md (Gemini rules)"),
    (".agents/bus/server.py", "server.py (agent-bus core)"),
    (".agents/bus/tools.py",  "tools.py (agent-bus tools)"),
    ("settings.json",         "settings.json (IDE config)"),
]

# Directories to monitor recursively. Override with WATCH_DIRS env var (colon-separated).
DEFAULT_WATCH_DIRS = [
    os.path.expanduser("~/.gemini/config"),
    os.path.expanduser("~/.claude"),
    os.path.join(os.path.expanduser("~"), "Desktop", "IDE", ".agents"),
    os.path.join(os.path.expanduser("~"), "Desktop", "IDE", "Antigravity"),
    os.path.join(os.path.expanduser("~"), "Desktop", ".claude"),
]
WATCH_DIRS = os.environ.get("WATCH_DIRS", "").split(":") if os.environ.get("WATCH_DIRS") else DEFAULT_WATCH_DIRS

IGNORE = [
    "agentbus.db", ".db-wal", ".db-shm", "__pycache__", ".pyc",
    ".tmp", "~", "node_modules", ".git", ".obsidian",
    "watcher.py",
]


def bus_send(subject, body):
    """Write an alert directly to the SQLite bus database."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        thread_id = uuid.uuid4().hex[:12]
        conn.execute("""
            INSERT INTO messages
              (thread_id, from_agent, to_agent, type, subject, body, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (thread_id, "env-watcher", "*", "alert", subject, body, 2, now))
        conn.commit()
        conn.close()
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] BUS ALERT -> {subject}")
    except Exception as e:
        print(f"[watcher] Bus error: {e}", file=sys.stderr)


def classify(path):
    """Return a human-readable description if the path matches a known pattern."""
    norm = path.replace("\\", "/")
    for pattern, desc in FILE_PATTERNS:
        if pattern.lower() in norm.lower():
            return desc
    return None


class Handler(FileSystemEventHandler):
    def __init__(self):
        self._debounce = {}

    def _handle(self, path, action):
        for skip in IGNORE:
            if skip.lower() in path.lower():
                return
        desc = classify(path)
        if not desc:
            return
        now = time.time()
        key = os.path.normpath(path)
        if key in self._debounce and now - self._debounce[key] < 3:
            return
        self._debounce[key] = now
        filename = os.path.basename(path)
        subject = f"ENV changed: {filename}"
        body = (
            f"**File {action}:** `{path.replace(chr(92), '/')}`\n\n"
            f"**Type:** {desc}\n"
            f"**Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"> Automatic notification from env-watcher. Verify if this change is expected."
        )
        bus_send(subject, body)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path, "created")

    def on_moved(self, event):
        if not event.is_directory:
            self._handle(event.dest_path, "moved/renamed")


def main():
    parser = argparse.ArgumentParser(description="env-watcher for agent-bus")
    parser.add_argument("--daemon", action="store_true", help="Run silently in background")
    args = parser.parse_args()

    observer = Observer()
    handler = Handler()
    dirs_started = []
    for d in WATCH_DIRS:
        if os.path.exists(d):
            observer.schedule(handler, d, recursive=True)
            dirs_started.append(d)

    observer.start()
    if not args.daemon:
        print(f"[env-watcher] Monitoring {len(dirs_started)} directories. Ctrl+C to stop.")
        for d in dirs_started:
            print(f"  > {d}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
