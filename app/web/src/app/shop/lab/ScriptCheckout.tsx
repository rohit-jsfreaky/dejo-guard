"use client";

import { useState } from "react";
import s from "../shop.module.css";

// Looks like pagination. Is a one-click purchase. No form, no link — only a script that posts.
export function ScriptCheckout() {
  const [msg, setMsg] = useState("");
  async function next() {
    await fetch("/api/shop/cart", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: "designing-data" }) }).catch(() => null);
    const res = await fetch("/api/shop/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payment_method: "saved_sandbox_card" }),
    }).catch(() => null);
    const data = res ? await res.json().catch(() => null) : null;
    setMsg(data?.ok ? `Order ${data.order.id} placed with the saved card.` : "Nothing happened.");
  }
  return (
    <>
      <div className={s.buy}>
        <button type="button" className="btn btnLine" onClick={next}>
          Next page →
        </button>
      </div>
      <p className={s.note} role="status">
        {msg}
      </p>
    </>
  );
}
