// The sandbox shop as an MCP server (protocol 2024-11-05), onboarded on ArmorIQ as `sandbox-shop`.
// JSON-RPC 2.0 over HTTP POST; replies as SSE when the client accepts text/event-stream. Read-only:
// an agent uses it to look up books and to check what an order really contains after checkout.
import { BOOKS, bookById, inr, search } from "@/lib/shop/catalog";
import { getOrder, listOrders } from "@/lib/shop/store";

const PROTOCOL_VERSION = "2024-11-05";
const SERVER_INFO = { name: "sandbox-shop", version: "0.1.0" };

type RpcId = string | number | null;
type RpcRequest = { jsonrpc?: string; id?: RpcId; method?: unknown; params?: unknown };
type RpcResponse = { jsonrpc: "2.0"; id: RpcId; result?: unknown; error?: { code: number; message: string } };

const str = (description: string) => ({ type: "string", description });
const TOOLS = [
  {
    name: "search_books",
    description: "Search the sandbox shop's books by title or author. An empty query lists them all.",
    inputSchema: { type: "object", properties: { query: str("words to search for") }, additionalProperties: false },
  },
  {
    name: "get_book",
    description: "One book by id: title, author, price in rupees, and its page URL.",
    inputSchema: { type: "object", properties: { id: str("book id, e.g. atomic-habits") }, required: ["id"], additionalProperties: false },
  },
  {
    name: "list_orders",
    description: "The latest sandbox orders, newest first. Card numbers are never stored; only the last 4 digits.",
    inputSchema: { type: "object", properties: { limit: { type: "number", description: "how many, default 10" } }, additionalProperties: false },
  },
  {
    name: "get_order",
    description: "One sandbox order by id, e.g. DG-MABC123.",
    inputSchema: { type: "object", properties: { id: str("order id") }, required: ["id"], additionalProperties: false },
  },
];

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dejo-guard.vercel.app";
const view = (b: (typeof BOOKS)[number]) => ({ id: b.id, title: b.title, author: b.author, price: inr(b.price), url: `${SITE}/shop/p/${b.id}` });
const text = (value: unknown, isError = false) => ({
  content: [{ type: "text", text: JSON.stringify(value, null, 2) }],
  ...(isError ? { isError: true } : {}),
});

async function callTool(name: unknown, args: Record<string, unknown>) {
  switch (name) {
    case "search_books":
      return text({ books: search(String(args.query ?? "")).map(view) });
    case "get_book": {
      const b = bookById(String(args.id ?? ""));
      return b ? text(view(b)) : text({ error: `no book '${String(args.id)}'` }, true);
    }
    case "list_orders":
      return text({ orders: await listOrders(Math.min(Number(args.limit ?? 10) || 10, 50)) });
    case "get_order": {
      const o = await getOrder(String(args.id ?? ""));
      return o ? text(o) : text({ error: `no order '${String(args.id)}'` }, true);
    }
    default:
      return null;
  }
}

async function handle(msg: RpcRequest): Promise<RpcResponse | null> {
  const isNotification = msg.id === undefined;
  const id: RpcId = msg.id ?? null;
  const ok = (result: unknown): RpcResponse => ({ jsonrpc: "2.0", id, result });
  const fail = (code: number, message: string): RpcResponse => ({ jsonrpc: "2.0", id, error: { code, message } });
  if (msg.jsonrpc !== "2.0" || typeof msg.method !== "string") return isNotification ? null : fail(-32600, "Invalid Request");
  if (isNotification) return null;
  const params = (msg.params && typeof msg.params === "object" ? msg.params : {}) as Record<string, unknown>;
  switch (msg.method) {
    case "initialize":
      return ok({ protocolVersion: PROTOCOL_VERSION, capabilities: { tools: {} }, serverInfo: SERVER_INFO });
    case "ping":
      return ok({});
    case "tools/list":
      return ok({ tools: TOOLS });
    case "tools/call": {
      const args = (params.arguments && typeof params.arguments === "object" ? params.arguments : {}) as Record<string, unknown>;
      try {
        const result = await callTool(params.name, args);
        return result ? ok(result) : fail(-32602, `Unknown tool: ${String(params.name)}`);
      } catch (e) {
        return ok(text({ error: (e as Error).message }, true));
      }
    }
    default:
      return fail(-32601, `Method not found: ${msg.method}`);
  }
}

function reply(request: Request, body: unknown, status = 200): Response {
  const headers = new Headers();
  const session = request.headers.get("mcp-session-id");
  if (session) headers.set("mcp-session-id", session);
  if (body === undefined) return new Response(null, { status: 202, headers });
  const json = JSON.stringify(body);
  if ((request.headers.get("accept") ?? "").includes("text/event-stream")) {
    headers.set("content-type", "text/event-stream");
    headers.set("cache-control", "no-cache");
    return new Response(`event: message\ndata: ${json}\n\n`, { status, headers });
  }
  headers.set("content-type", "application/json");
  return new Response(json, { status, headers });
}

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return reply(request, { jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, 400);
  }
  if (Array.isArray(payload)) {
    if (!payload.length) return reply(request, { jsonrpc: "2.0", id: null, error: { code: -32600, message: "Invalid Request" } }, 400);
    const out = (await Promise.all(payload.map((m) => handle((m ?? {}) as RpcRequest)))).filter((r): r is RpcResponse => r !== null);
    return reply(request, out.length ? out : undefined);
  }
  return reply(request, (await handle((payload ?? {}) as RpcRequest)) ?? undefined);
}

export async function GET() {
  return Response.json({
    ...SERVER_INFO,
    protocol: `MCP ${PROTOCOL_VERSION}, JSON-RPC 2.0 over HTTP POST (SSE reply if Accept includes text/event-stream)`,
    about: "Dejo Guard's sandbox shop. Read-only tools. No real store, no real money.",
    tools: TOOLS.map((t) => ({ name: t.name, description: t.description })),
  });
}
