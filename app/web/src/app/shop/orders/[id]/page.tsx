import { notFound } from "next/navigation";
import { inr } from "@/lib/shop/catalog";
import { getOrder } from "@/lib/shop/store";
import s from "../../shop.module.css";

export const dynamic = "force-dynamic";

export default async function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const order = await getOrder(id);
  if (!order) notFound();
  return (
    <>
      <p className={`${s.note} ${s.ok}`}>Order placed · sandbox, no money moved</p>
      <h1 className={s.h1} style={{ marginTop: 6 }}>
        {order.id}
      </h1>
      <p className={s.lead}>
        {new Date(order.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
        {order.card_last4 && ` · test card ending ${order.card_last4}`}
      </p>
      <table className={s.table}>
        <tbody>
          {order.items.map((l) => (
            <tr key={l.id}>
              <td>{l.title}</td>
              <td className={s.right}>× {l.qty}</td>
              <td className={s.right}>{inr(l.price * l.qty)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className={s.total}>
        <span>Total {inr(order.total_inr)}</span>
        <a className="btn btnLine" href="/shop">
          Back to books
        </a>
      </div>
    </>
  );
}
