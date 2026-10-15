"""The decision feed: every ArmorIQ answer, written down the moment it arrives.

Local first — a SQLite file beside Dejo's own memory, read by `dejo-guard feed`. If the user
turns on the hosted feed (`DEJO_GUARD_FEED_URL` + `DEJO_GUARD_FEED_TOKEN`), each row is also
posted there so a page on the web can show it live. Posting is best effort: a feed that is
down never changes what ArmorIQ decided, and never blocks the browser.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from .config import feed_path, setting

SCHEMA = """
create table if not exists decisions (
  id text primary key,
  at real not null,
  task_id text,
  goal text,
  action text not null,       -- the Dejo action (click, fill, goto, run …)
  cls text not null,          -- the action class the page facts made
  because text,               -- which fact made it that class
  decision text not null,     -- allow | block | hold | approved | rejected
  reason text,                -- ArmorIQ's own reason, verbatim
  policy text,                -- ArmorIQ's matched policy
  delegation_id text,
  plan_id text,
  page_url text,
  words text,                 -- what the control says, for humans only
  ms integer,
  facts text                  -- the full page facts, JSON
);
create index if not exists decisions_at on decisions(at);
"""


class Feed:
    def __init__(self, path: Path | None = None):
        self.path = path or feed_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._db() as db:
            db.executescript(SCHEMA)
        self.remote = setting("DEJO_GUARD_FEED_URL")
        self.remote_token = setting("DEJO_GUARD_FEED_TOKEN")

    def _db(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5)

    def write(self, row: dict[str, Any]) -> dict[str, Any]:
        row = {"id": uuid.uuid4().hex, "at": time.time(), **row}
        if isinstance(row.get("facts"), dict):
            row["facts"] = json.dumps(row["facts"], ensure_ascii=False)
        cols = [c for c in row if c in _COLUMNS]
        with self._lock, self._db() as db:
            db.execute(
                f"insert into decisions ({', '.join(cols)}) values ({', '.join('?' * len(cols))})",
                [row[c] for c in cols],
            )
        if self.remote and self.remote_token:
            threading.Thread(target=self._post, args=(row,), daemon=True).start()
        return row

    def _post(self, row: dict[str, Any]) -> None:
        try:
            httpx.post(
                self.remote,
                json={k: row[k] for k in row if k in _COLUMNS},
                headers={"Authorization": f"Bearer {self.remote_token}"},
                timeout=5,
            )
        except httpx.HTTPError as problem:
            print(f"[dejo-guard] hosted feed unreachable: {problem}", file=sys.stderr, flush=True)

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._db() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("select * from decisions order by at desc limit ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


_COLUMNS = {
    "id", "at", "task_id", "goal", "action", "cls", "because", "decision", "reason", "policy",
    "delegation_id", "plan_id", "page_url", "words", "ms", "facts",
}
