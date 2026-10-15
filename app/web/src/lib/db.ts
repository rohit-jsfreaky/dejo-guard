// Supabase over plain REST, server side only. The secret key never reaches a browser.
import "server-only";

const BASE = process.env.SUPABASE_URL ?? "";
const KEY = process.env.SUPABASE_SECRET_KEY ?? "";

export async function db<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  if (!BASE || !KEY) throw new Error("Supabase is not configured (SUPABASE_URL / SUPABASE_SECRET_KEY)");
  const res = await fetch(`${BASE}/rest/v1/${path}`, {
    ...init,
    cache: "no-store",
    headers: { apikey: KEY, "Content-Type": "application/json", Prefer: "return=representation", ...(init.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`supabase ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}
