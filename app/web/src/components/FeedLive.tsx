"use client";

import { useEffect, useState } from "react";
import s from "./FeedLive.module.css";

type Row = {
  id: string;
  at: number;
  goal: string | null;
  action: string;
  cls: string;
  because: string | null;
  decision: string;
  reason: string | null;
  policy: string | null;
  delegation_id: string | null;
  plan_id: string | null;
  page_url: string | null;
  words: string | null;
  ms: number | null;
};

const KIND: Record<string, string> = {
  allow: "allow",
  approved: "allow",
  signed: "allow",
  hold: "hold",
  pending: "hold",
  block: "block",
  refused: "block",
  rejected: "block",
  expired: "block",
};

const path = (url: string | null) => {
  if (!url) return "";
  try {
    const u = new URL(url);
    return u.host + u.pathname;
  } catch {
    return url;
  }
};

// Polls the feed every 2 seconds. Newest decision on top. Every row is what ArmorIQ answered, verbatim.
export function FeedLive({ id, initial }: { id: string; initial: Row[] }) {
  const [rows, setRows] = useState<Row[]>(initial);
  const [live, setLive] = useState(true);

  useEffect(() => {
    let stop = false;
    const tick = async () => {
      try {
        const res = await fetch(`/api/feed?id=${encodeURIComponent(id)}`, { cache: "no-store" });
        const data = await res.json();
        if (!stop && data.ok) {
          setRows(data.rows);
          setLive(true);
        }
      } catch {
        if (!stop) setLive(false);
      }
    };
    const t = setInterval(tick, 2000);
    return () => {
      stop = true;
      clearInterval(t);
    };
  }, [id]);

  return (
    <div className={s.feed}>
      <div className={s.bar}>
        <span className={s.live} data-on={live || undefined}>
          <i /> {live ? "live" : "reconnecting"}
        </span>
        <span>
          {rows.length} decision{rows.length === 1 ? "" : "s"}
        </span>
      </div>
      {rows.length === 0 && <p className={s.empty}>Nothing yet. Decisions appear here the moment ArmorIQ answers.</p>}
      <ol className={s.list}>
        {rows.map((r) => (
          <li key={r.id} className={s.row}>
            <span className={s.time}>{new Date(r.at * 1000).toLocaleTimeString("en-IN", { hour12: false })}</span>
            <span className={s.badge} data-k={KIND[r.decision] ?? "hold"}>
              {r.decision}
            </span>
            <div className={s.body}>
              <div className={s.line}>
                <code>{r.action === "plan" ? "plan" : r.cls}</code>
                {r.words && <span className={s.words}>“{r.words}”</span>}
                <span className={s.page}>{path(r.page_url)}</span>
              </div>
              <div className={s.why}>
                {r.action === "plan" ? `task: ${r.goal ?? ""} · ${r.cls.split(",").join(" ")}` : r.because}
                {r.reason && <> · ArmorIQ: {r.reason}</>}
                {r.policy && <> · {r.policy}</>}
                {r.delegation_id && <> · hold {r.delegation_id.slice(0, 8)}</>}
                {r.ms ? <> · {r.ms} ms</> : null}
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
