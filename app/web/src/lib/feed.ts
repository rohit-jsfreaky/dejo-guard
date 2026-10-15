// Hosted decision feeds. A guard on someone's laptop streams its ArmorIQ decisions here under a feed id;
// anyone with the link can watch. The write token is stored only as a SHA-256 hash.
import "server-only";
import { createHash, randomBytes } from "node:crypto";
import { db } from "@/lib/db";

export type Row = {
  id: string;
  feed_id: string;
  at: number;
  task_id: string | null;
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

const hash = (token: string) => createHash("sha256").update(token).digest("hex");

export async function newFeed(label: string | null) {
  const id = randomBytes(6).toString("base64url");
  const token = randomBytes(24).toString("base64url");
  await db("feeds", { method: "POST", body: JSON.stringify({ id, token_hash: hash(token), label }) });
  return { id, token };
}

export async function feedForToken(token: string): Promise<string | null> {
  const rows = await db<{ id: string }[]>(`feeds?token_hash=eq.${hash(token)}&select=id`);
  return rows[0]?.id ?? null;
}

const COLS = ["id", "at", "task_id", "goal", "action", "cls", "because", "decision", "reason", "policy", "delegation_id", "plan_id", "page_url", "words", "ms", "facts"] as const;

export async function addRow(feedId: string, row: Record<string, unknown>) {
  const clean: Record<string, unknown> = { feed_id: feedId };
  for (const k of COLS) if (row[k] !== undefined) clean[k] = row[k];
  if (typeof clean.facts === "string") {
    try {
      clean.facts = JSON.parse(clean.facts);
    } catch {
      clean.facts = null;
    }
  }
  if (!clean.id || !clean.action || !clean.cls || !clean.decision || typeof clean.at !== "number") throw new Error("missing fields");
  await db("decisions", { method: "POST", body: JSON.stringify(clean), headers: { Prefer: "resolution=ignore-duplicates" } });
}

export async function rows(feedId: string, limit = 80): Promise<Row[]> {
  return db<Row[]>(
    `decisions?feed_id=eq.${encodeURIComponent(feedId)}&select=id,feed_id,at,task_id,goal,action,cls,because,decision,reason,policy,delegation_id,plan_id,page_url,words,ms&order=at.desc&limit=${limit}`,
  );
}

export const DEMO_FEED = process.env.DEMO_FEED_ID ?? "demo";
