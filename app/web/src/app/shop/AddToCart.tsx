"use client";

import { useState } from "react";
import s from "./shop.module.css";

// A plain <button> with no form: its click fires a fetch POST. Dejo Guard sees no link and no submit,
// so it watches the request instead and names it before it leaves the browser.
export function AddToCart({ id }: { id: string }) {
  const [state, setState] = useState<"idle" | "busy" | "added" | "failed">("idle");
  const [count, setCount] = useState(0);

  async function add() {
    setState("busy");
    try {
      const res = await fetch("/api/shop/cart", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id }) });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error);
      setCount(data.lines.reduce((n: number, l: { qty: number }) => n + l.qty, 0));
      setState("added");
    } catch {
      setState("failed");
    }
  }

  return (
    <>
      <div className={s.buy}>
        <button type="button" className="btn btnInk" onClick={add} disabled={state === "busy"}>
          Add to cart
        </button>
        <a className="btn btnLine" href="/shop/cart">
          Go to cart
        </a>
      </div>
      <p className={`${s.note} ${state === "added" ? s.ok : ""}`} role="status">
        {state === "added" && `Added. ${count} item${count === 1 ? "" : "s"} in your cart.`}
        {state === "failed" && "Could not add it. The request did not go through."}
      </p>
    </>
  );
}
