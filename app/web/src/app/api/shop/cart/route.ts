// Add a book to the cart. Called by the shop's "Add to cart" button with fetch — a write request
// that Dejo Guard's network watch names `state_change` before it leaves the browser.
import { addToCart, cartId, getCart, priced } from "@/lib/shop/store";

export async function GET() {
  return Response.json(priced(await getCart(await cartId())));
}

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { id?: string };
  try {
    const items = await addToCart(String(body.id ?? ""));
    return Response.json({ ok: true, ...priced(items) });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 400 });
  }
}
