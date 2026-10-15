// Carts and orders in Supabase. A cart is found by a cookie; an order keeps only the last 4 card digits.
import "server-only";
import { cookies } from "next/headers";
import { db } from "@/lib/db";
import { bookById } from "./catalog";

export type Line = { id: string; qty: number };
export type Order = { id: string; items: (Line & { title: string; price: number })[]; total_inr: number; name: string | null; city: string | null; card_last4: string | null; created_at: string };

const CART = "dg_cart";

export async function cartId(create = false): Promise<string | null> {
  const jar = await cookies();
  const have = jar.get(CART)?.value;
  if (have || !create) return have ?? null;
  const [row] = await db<{ id: string }[]>("carts", { method: "POST", body: JSON.stringify({ items: [] }) });
  jar.set(CART, row.id, { httpOnly: true, sameSite: "lax", path: "/", maxAge: 60 * 60 * 24 * 7 });
  return row.id;
}

export async function getCart(id: string | null): Promise<Line[]> {
  if (!id) return [];
  const rows = await db<{ items: Line[] }[]>(`carts?id=eq.${id}&select=items`);
  return rows[0]?.items ?? [];
}

export async function addToCart(bookId: string): Promise<Line[]> {
  if (!bookById(bookId)) throw new Error("no such book");
  const id = (await cartId(true))!;
  const items = await getCart(id);
  const line = items.find((l) => l.id === bookId);
  if (line) line.qty += 1;
  else items.push({ id: bookId, qty: 1 });
  await db(`carts?id=eq.${id}`, { method: "PATCH", body: JSON.stringify({ items, updated_at: new Date().toISOString() }) });
  return items;
}

export async function clearCart(id: string) {
  await db(`carts?id=eq.${id}`, { method: "PATCH", body: JSON.stringify({ items: [] }) });
}

export function priced(items: Line[]) {
  const lines = items.flatMap((l) => {
    const b = bookById(l.id);
    return b ? [{ ...l, title: b.title, price: b.price }] : [];
  });
  return { lines, total: lines.reduce((s, l) => s + l.price * l.qty, 0) };
}

export async function placeOrder(input: { cartId: string; name?: string; city?: string; last4: string }): Promise<Order> {
  const { lines, total } = priced(await getCart(input.cartId));
  if (!lines.length) throw new Error("the cart is empty");
  const id = `DG-${Date.now().toString(36).toUpperCase()}`;
  const [row] = await db<Order[]>("orders", {
    method: "POST",
    body: JSON.stringify({ id, cart_id: input.cartId, items: lines, total_inr: total, name: input.name ?? null, city: input.city ?? null, card_last4: input.last4 }),
  });
  await clearCart(input.cartId);
  return row;
}

export async function listOrders(limit = 20): Promise<Order[]> {
  return db<Order[]>(`orders?select=*&order=created_at.desc&limit=${limit}`);
}

export async function getOrder(id: string): Promise<Order | null> {
  const rows = await db<Order[]>(`orders?id=eq.${encodeURIComponent(id)}&select=*`);
  return rows[0] ?? null;
}
