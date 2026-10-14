from __future__ import annotations

import json
import sqlite3
import time


class Store:
    def __init__(self, path: str = "fortune.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, lang TEXT, state TEXT, data TEXT DEFAULT '{}',
          profile TEXT, daily_on INTEGER DEFAULT 0, daily_hour INTEGER DEFAULT 9,
          daily_last TEXT, referred_by INTEGER, created REAL);
        CREATE TABLE IF NOT EXISTS readings(user_id INTEGER, mode TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS payments(user_id INTEGER, payload TEXT, stars INTEGER, charge_id TEXT, ts REAL);
        """)
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(users)")}
        if "tz" not in cols:  # migration v3: user's current timezone (for "today")
            self.db.execute("ALTER TABLE users ADD COLUMN tz TEXT")
        self.db.commit()

    def get(self, uid: int):
        return self.db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

    def ensure(self, uid: int, lang: str) -> bool:
        """Create the user if missing; returns True when newly created."""
        if self.get(uid):
            return False
        self.db.execute("INSERT INTO users(id, lang, created) VALUES(?,?,?)", (uid, lang, time.time()))
        self.db.commit()
        return True

    COLUMNS = {"lang", "state", "data", "profile", "daily_on", "daily_hour", "daily_last", "referred_by", "tz"}

    def set(self, uid: int, **kw):
        if not kw or not set(kw) <= self.COLUMNS:
            raise ValueError(f"bad columns: {set(kw) - self.COLUMNS}")
        for k in ("data", "profile"):
            if k in kw and not isinstance(kw[k], (str, type(None))):
                kw[k] = json.dumps(kw[k], ensure_ascii=False)
        cols = ", ".join(f"{k}=?" for k in kw)
        self.db.execute(f"UPDATE users SET {cols} WHERE id=?", (*kw.values(), uid))
        self.db.commit()

    def data(self, uid):
        r = self.get(uid)
        return json.loads(r["data"] or "{}") if r else {}

    def profile(self, uid):
        r = self.get(uid)
        return json.loads(r["profile"]) if r and r["profile"] else None

    def log_reading(self, uid, mode):
        self.db.execute("INSERT INTO readings VALUES(?,?,?)", (uid, mode, time.time()))
        self.db.commit()

    def log_payment(self, uid, payload, stars, charge_id):
        self.db.execute("INSERT INTO payments VALUES(?,?,?,?,?)", (uid, payload, stars, charge_id, time.time()))
        self.db.commit()

    def stats(self):
        q = lambda s: self.db.execute(s).fetchone()[0]  # noqa: E731
        modes = dict(self.db.execute("SELECT mode, COUNT(*) FROM readings GROUP BY mode").fetchall())
        return {"users": q("SELECT COUNT(*) FROM users"),
                "refs": q("SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL"),
                "daily": q("SELECT COUNT(*) FROM users WHERE daily_on=1"), "modes": modes}

    def daily_users(self):
        return self.db.execute("SELECT * FROM users WHERE daily_on=1 AND profile IS NOT NULL").fetchall()
