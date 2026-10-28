import json
import sqlite3
import threading
from datetime import datetime, timezone


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, source TEXT, start TEXT,
                    data TEXT, first_seen TEXT, last_seen TEXT);
                CREATE TABLE IF NOT EXISTS interactions(event_id TEXT, action TEXT, ts TEXT,
                    PRIMARY KEY(event_id, action));
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
                CREATE TABLE IF NOT EXISTS source_status(id TEXT PRIMARY KEY, last_run TEXT, ok INTEGER,
                    count INTEGER, duration REAL, error TEXT);
                CREATE TABLE IF NOT EXISTS news(id TEXT PRIMARY KEY, source TEXT, published TEXT, data TEXT);
                CREATE TABLE IF NOT EXISTS images(url TEXT PRIMARY KEY, image TEXT, ts TEXT);
            """)
            self.conn.commit()

    def _q(self, sql, args=()):
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    # --- events ---
    def replace_source_events(self, source_ids: list[str], events: list[dict]):
        """Upsert this run's events; drop vanished ones unless the user interacted with them."""
        ts = now()
        with self.lock:
            c = self.conn
            for e in events:
                c.execute("""INSERT INTO events(id, source, start, data, first_seen, last_seen)
                             VALUES(?,?,?,?,?,?)
                             ON CONFLICT(id) DO UPDATE SET data=excluded.data, start=excluded.start,
                             last_seen=excluded.last_seen""",
                          (e["id"], e["source"], e["start"], json.dumps(e, ensure_ascii=False), ts, ts))
            marks = ",".join("?" * len(source_ids))
            c.execute(f"""DELETE FROM events WHERE source IN ({marks}) AND last_seen < ?
                          AND id NOT IN (SELECT event_id FROM interactions)""", (*source_ids, ts))
            c.commit()

    def all_events(self) -> list[dict]:
        out = []
        for data, first_seen in self._q("SELECT data, first_seen FROM events"):
            d = json.loads(data)
            d["first_seen"] = first_seen
            out.append(d)
        return out

    def cached_by_url(self, source) -> dict:
        return {d["url"]: d for d in (json.loads(r[0]) for r in
                                      self._q("SELECT data FROM events WHERE source=?", (source,)))}

    # --- interactions ---
    def interactions(self) -> list[tuple[str, str]]:
        return self._q("SELECT event_id, action FROM interactions")

    def set_interaction(self, event_id, action, on: bool):
        with self.lock:
            if on:
                self.conn.execute("INSERT OR REPLACE INTO interactions VALUES(?,?,?)", (event_id, action, now()))
            else:
                self.conn.execute("DELETE FROM interactions WHERE event_id=? AND action=?", (event_id, action))
            self.conn.commit()

    def clear_interactions(self, actions):
        with self.lock:
            self.conn.execute(f"DELETE FROM interactions WHERE action IN ({','.join('?' * len(actions))})",
                              actions)
            self.conn.commit()

    # --- settings ---
    def get_setting(self, key, default=None):
        rows = self._q("SELECT value FROM settings WHERE key=?", (key,))
        return json.loads(rows[0][0]) if rows else default

    def set_setting(self, key, value):
        with self.lock:
            self.conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, json.dumps(value, ensure_ascii=False)))
            self.conn.commit()

    # --- source status ---
    def set_status(self, sid, ok, count, duration, error=""):
        with self.lock:
            self.conn.execute("INSERT OR REPLACE INTO source_status VALUES(?,?,?,?,?,?)",
                              (sid, now(), int(ok), count, duration, error))
            self.conn.commit()

    def statuses(self) -> dict:
        return {r[0]: {"last_run": r[1], "ok": bool(r[2]), "count": r[3], "duration": r[4], "error": r[5]}
                for r in self._q("SELECT * FROM source_status")}

    # --- news ---
    def replace_news(self, items: list[dict]):
        with self.lock:
            for it in items:
                self.conn.execute("INSERT OR REPLACE INTO news VALUES(?,?,?,?)",
                                  (it["id"], it["source"], it["published"], json.dumps(it, ensure_ascii=False)))
            self.conn.execute("DELETE FROM news WHERE id NOT IN (SELECT id FROM news ORDER BY published DESC LIMIT 400)")
            self.conn.commit()

    def news(self, limit=200) -> list[dict]:
        return [json.loads(r[0]) for r in self._q("SELECT data FROM news ORDER BY published DESC LIMIT ?", (limit,))]

    # --- og:image cache ---
    def image_cache(self) -> dict:
        return {r[0]: (r[1], r[2]) for r in self._q("SELECT url, image, ts FROM images")}

    def put_images(self, found: dict):
        ts = now()
        with self.lock:
            self.conn.executemany("INSERT OR REPLACE INTO images VALUES(?,?,?)",
                                  [(u, img or "", ts) for u, img in found.items()])
            self.conn.commit()

    def delete_events_where(self, predicate):
        """Remove stored events matching predicate(event_dict) together with their interactions."""
        ids = [d["id"] for d in self.all_events() if predicate(d)]
        with self.lock:
            for i in ids:
                self.conn.execute("DELETE FROM events WHERE id=?", (i,))
                self.conn.execute("DELETE FROM interactions WHERE event_id=?", (i,))
            self.conn.commit()
        return len(ids)
