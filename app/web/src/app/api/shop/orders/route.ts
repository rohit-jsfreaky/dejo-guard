// Place a sandbox order. Two ways in, both of which Dejo Guard must hold:
//   form POST from /shop/checkout (card fields)                → class submit_payment
//   JSON POST from a lab page's "one-click" script (saved card) → class submit_payment (payment endpoint)
// Only the sandbox test card is accepted. No card number is ever stored — only its last 4 digits.
import { TEST_CARD } from "@/lib/shop/catalog";
import { addToCart, cartId, listOrders, placeOrder } from "@/lib/shop/store";

export async function GET() {
  return Response.json({ orders: await listOrders(20) });
}

export async function POST(request: Request) {
  const isForm = (request.headers.get("content-type") ?? "").includes("form");
  const form = isForm ? await request.formData() : null;
  // Lab pages sell one book straight away ("express checkout"): put it in the cart first.
  const book = form?.get("book");
  if (book) await addToCart(String(book));
  const id = await cartId();
  if (!id) return fail(isForm, "the cart is empty");

  let name = "";
  let city = "";
  let last4 = "";
  if (form) {
    const card = String(form.get("cardnumber") ?? "").replace(/\D/g, "");
    const saved = form.get("payment_method") === "saved_sandbox_card";
    if (!saved && card !== TEST_CARD) return fail(true, "This is a sandbox shop: only the test card 4242 4242 4242 4242 works.");
    name = String(form.get("name") ?? "");
    city = String(form.get("city") ?? "");
    last4 = TEST_CARD.slice(-4);
  } else {
    const body = (await request.json().catch(() => ({}))) as { payment_method?: string };
    if (body.payment_method !== "saved_sandbox_card") return fail(false, "unknown payment method");
    last4 = TEST_CARD.slice(-4);
  }
  try {
    const order = await placeOrder({ cartId: id, name, city, last4 });
    if (isForm) return Response.redirect(new URL(`/shop/orders/${order.id}`, request.url), 303);
    return Response.json({ ok: true, order });
  } catch (e) {
    return fail(isForm, (e as Error).message);
  }
}

function fail(isForm: boolean, message: string) {
  if (isForm) {
    return new Response(null, { status: 303, headers: { Location: `/shop/checkout?error=${encodeURIComponent(message)}` } });
  }
  return Response.json({ ok: false, error: message }, { status: 400 });
}
