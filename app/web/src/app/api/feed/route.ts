// POST: a guard adds one decision to its feed (Authorization: Bearer <feed token>).
// GET ?id=<feed>: the latest decisions, newest first.
import { addRow, feedForToken, rows } from "@/lib/feed";

export async function POST(request: Request) {
  const token = (request.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!token) return Response.json({ ok: false, error: "no token" }, { status: 401 });
  const feedId = await feedForToken(token);
  if (!feedId) return Response.json({ ok: false, error: "unknown token" }, { status: 401 });
  try {
    await addRow(feedId, (await request.json()) as Record<string, unknown>);
    return Response.json({ ok: true });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 400 });
  }
}

export async function GET(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (!id) return Response.json({ ok: false, error: "which feed? ?id=" }, { status: 400 });
  return Response.json({ ok: true, rows: await rows(id) }, { headers: { "cache-control": "no-store" } });
}
