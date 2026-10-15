// Make a new hosted feed. Called once by `dejo-guard share`; returns the feed id and its write token.
import { newFeed } from "@/lib/feed";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { label?: string };
  const { id, token } = await newFeed(typeof body.label === "string" ? body.label.slice(0, 60) : null);
  const site = new URL(request.url).origin;
  return Response.json({ ok: true, id, token, watch: `${site}/feed/${id}`, post: `${site}/api/feed` });
}
