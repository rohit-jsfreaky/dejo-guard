"""Recording mode: film the guard's browser the way a demo video needs it. Off unless DEJO_GUARD_RECORD is set.

With DEJO_GUARD_RECORD=<folder>, every page action is shown before it happens: a drawn cursor glides to the element
the agent picked, a box marks it, and the box takes ArmorIQ's answer (allowed / held / blocked, with the class).
Chrome's own screencast saves the frames, and events.jsonl says when each answer appeared. Nothing about the
decision changes: this only draws on the page and waits a moment so a viewer can follow.
"""

from __future__ import annotations

import base64
import contextlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any

PAGE_HELPERS = r"""(() => {
  if (window.__dg) return;
  const css = `
    #__dg_cursor { position: fixed; left: 0; top: 0; z-index: 2147483647; pointer-events: none; will-change: transform; }
    #__dg_ripple { position: fixed; z-index: 2147483646; pointer-events: none; width: 44px; height: 44px;
      margin: -22px 0 0 -22px; border-radius: 50%; border: 3px solid #0d1116; opacity: 0; }
    #__dg_spot { position: fixed; z-index: 2147483645; pointer-events: none; border: 3px solid #5b5fc7;
      border-radius: 10px; background: rgba(91, 95, 199, 0.07); opacity: 0; }
    #__dg_tag { position: fixed; z-index: 2147483647; pointer-events: none; opacity: 0; white-space: nowrap;
      font: 600 15px/1 "Hanken Grotesk", system-ui, sans-serif; color: #fff; padding: 9px 12px 9px 11px;
      border-radius: 9px; box-shadow: 0 6px 18px rgba(13,17,22,.18); display: flex; gap: 8px; align-items: center; }
    #__dg_tag code { font: 500 13px/1 ui-monospace, "JetBrains Mono", monospace; opacity: .85; }
    #__dg_tick { position: fixed; right: 0; bottom: 0; width: 2px; height: 2px; z-index: 2147483640; pointer-events: none;
      animation: __dg_tick .5s linear infinite; }
    @keyframes __dg_tick { 0% { opacity: .01 } 50% { opacity: .02 } 100% { opacity: .01 } }`;
  const mount = () => {
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    const c = document.createElement('div'); c.id = '__dg_cursor';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M4 2.5 L4 21 L9 16.6 L12.4 24.2 L15.6 22.8 L12.3 15.4 L19.2 15.4 Z" fill="#0d1116" stroke="#ffffff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    const r = document.createElement('div'); r.id = '__dg_ripple';
    const s = document.createElement('div'); s.id = '__dg_spot';
    const g = document.createElement('div'); g.id = '__dg_tag';
    const t = document.createElement('div'); t.id = '__dg_tick';
    document.body.append(s, g, r, c, t);
    const p = window.__dg.pos; c.style.transform = 'translate(' + p.x + 'px,' + p.y + 'px)';
  };
  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const anim = (ms, step) => new Promise((done) => {
    const t0 = performance.now();
    const f = (now) => { const k = Math.min(1, (now - t0) / ms); step(ease(k)); k < 1 ? requestAnimationFrame(f) : done(); };
    requestAnimationFrame(f);
  });
  const COLORS = { look: ['#5b5fc7', 'rgba(91,95,199,.07)'], allow: ['#1f7a4d', 'rgba(31,122,77,.08)'],
                   hold: ['#b26a00', 'rgba(178,106,0,.10)'], block: ['#46525d', 'rgba(70,82,93,.10)'] };
  window.__dg = {
    pos: { x: innerWidth * 0.62, y: innerHeight * 0.55 },
    place(x, y) { this.pos = { x, y }; const c = document.getElementById('__dg_cursor');
      if (c) c.style.transform = 'translate(' + x + 'px,' + y + 'px)'; },
    move(x, y, ms) { const a = { ...this.pos }; const c = document.getElementById('__dg_cursor');
      return anim(ms, (k) => { const px = a.x + (x - a.x) * k, py = a.y + (y - a.y) * k; this.pos = { x: px, y: py };
        c.style.transform = 'translate(' + px + 'px,' + py + 'px)'; }); },
    ripple() { const r = document.getElementById('__dg_ripple'); r.style.left = this.pos.x + 'px'; r.style.top = this.pos.y + 'px';
      return anim(420, (k) => { r.style.opacity = String(0.9 * (1 - k)); r.style.transform = 'scale(' + (0.4 + 0.9 * k) + ')'; }); },
    spot(rect, kind) { const s = document.getElementById('__dg_spot'); const [line, fill] = COLORS[kind] || COLORS.look;
      Object.assign(s.style, { left: (rect.x - 7) + 'px', top: (rect.y - 7) + 'px', width: (rect.width + 14) + 'px',
        height: (rect.height + 14) + 'px', borderColor: line, background: fill });
      const o = parseFloat(s.style.opacity || '0'); return anim(220, (k) => { s.style.opacity = String(o + (1 - o) * k); }); },
    tag(rect, kind, text, detail) { const g = document.getElementById('__dg_tag'); const [line] = COLORS[kind] || COLORS.look;
      g.style.background = line;
      g.innerHTML = '<span>' + text + '</span>' + (detail ? '<code>' + detail + '</code>' : '');
      if (kind === 'block') g.querySelector('span').style.textDecoration = 'line-through';
      const below = rect.y + rect.height + 14, h = 36;
      g.style.left = Math.max(8, Math.min(innerWidth - 8 - g.offsetWidth, rect.x - 7)) + 'px';
      g.style.top = (below + h < innerHeight ? below : Math.max(8, rect.y - 14 - h)) + 'px';
      return anim(200, (k) => { g.style.opacity = String(k); }); },
    clear() { const s = document.getElementById('__dg_spot'), g = document.getElementById('__dg_tag');
      const a = parseFloat(s.style.opacity || '0'), b = parseFloat(g.style.opacity || '0');
      return anim(220, (k) => { s.style.opacity = String(a * (1 - k)); g.style.opacity = String(b * (1 - k)); }); },
  };
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();"""

WORDS = {"allow": "ArmorIQ: allowed", "hold": "ArmorIQ: held for your approval", "block": "ArmorIQ: blocked"}


class Stage:
    """One per guard. Does nothing at all unless DEJO_GUARD_RECORD names a folder."""

    def __init__(self) -> None:
        folder = os.environ.get("DEJO_GUARD_RECORD")
        self.on = bool(folder)
        self.dir = Path(folder) if folder else None
        self._pages: set[int] = set()
        self._contexts: set[int] = set()
        self._n = 0
        self._lock = threading.Lock()
        self._box: dict | None = None
        if self.dir:
            (self.dir / "frames").mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- capture

    def attach(self, page: Any) -> None:
        if not self.on or page is None or id(page) in self._pages:
            return
        self._pages.add(id(page))
        context = page.context
        if id(context) not in self._contexts:
            self._contexts.add(id(context))
            context.add_init_script(PAGE_HELPERS)
        with contextlib.suppress(Exception):  # an about:blank page takes it on its next load
            page.evaluate(PAGE_HELPERS)
        cdp = context.new_cdp_session(page)
        cdp.on("Page.screencastFrame", lambda frame: self._frame(cdp, frame))
        cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 90, "maxWidth": 1920, "maxHeight": 1080,
                                          "everyNthFrame": 1})
        self.event("attach", url=page.url)

    def _frame(self, cdp: Any, frame: dict) -> None:
        with self._lock:
            self._n += 1
            name = f"f{self._n:07d}.jpg"
        (self.dir / "frames" / name).write_bytes(base64.b64decode(frame["data"]))
        with open(self.dir / "frames.jsonl", "a", encoding="utf-8") as out:
            out.write(json.dumps({"t": frame["metadata"]["timestamp"], "file": name}) + "\n")
        with contextlib.suppress(Exception):
            cdp.send("Page.screencastFrameAck", {"sessionId": frame["sessionId"]})

    def event(self, kind: str, **fields: Any) -> None:
        if not self.on:
            return
        with open(self.dir / "events.jsonl", "a", encoding="utf-8") as out:
            out.write(json.dumps({"t": time.time(), "kind": kind, **fields}, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------- showing

    def _js(self, page: Any, script: str, arg: Any = None, wait_ms: int = 0) -> None:
        with contextlib.suppress(Exception):  # drawing must never break the action
            page.evaluate(f"(a) => window.__dg && {script}", arg)
            if wait_ms:
                page.wait_for_timeout(wait_ms)

    def before(self, page: Any, target: Any) -> None:
        """The cursor goes to the element the agent picked, and marks it."""
        if not self.on:
            return
        self.attach(page)
        self._box = None
        if target is None:
            return
        try:
            target.scroll_into_view_if_needed(timeout=2000)
            self._box = target.bounding_box()
        except Exception:  # noqa: BLE001
            self._box = None
        if not self._box:
            return
        b = self._box
        self._js(page, "window.__dg.move(a.x, a.y, 700)", {"x": b["x"] + b["width"] / 2, "y": b["y"] + b["height"] / 2},
                 wait_ms=750)
        self._js(page, "window.__dg.spot(a, 'look')", b, wait_ms=350)

    def decided(self, page: Any, decision: Any, cls: str, words: str | None) -> None:
        """ArmorIQ's answer, on the element, for long enough to read."""
        if not self.on:
            return
        self.event("decision", decision=decision.action, cls=cls, reason=decision.reason, words=words,
                   url=getattr(page, "url", None))
        if not self._box:
            return
        detail = cls
        if str(decision.reason or "").startswith("tool-not-in-plan"):
            detail = f"{cls} · not in the plan"  # ArmorIQ's own reason: intent drift
        self._js(page, "window.__dg.spot(a.b, a.k)", {"b": self._box, "k": decision.action})
        self._js(page, "window.__dg.tag(a.b, a.k, a.t, a.d)",
                 {"b": self._box, "k": decision.action, "t": WORDS.get(decision.action, decision.action), "d": detail},
                 wait_ms=1600 if decision.action == "allow" else 2600)
        if decision.action == "allow":
            self._js(page, "window.__dg.ripple()", wait_ms=250)

    def after(self, page: Any) -> None:
        if not self.on:
            return
        self._js(page, "window.__dg.clear()", wait_ms=250)
        self._box = None


_STAGE: Stage | None = None


def stage() -> Stage:
    global _STAGE
    if _STAGE is None:
        _STAGE = Stage()
    return _STAGE
