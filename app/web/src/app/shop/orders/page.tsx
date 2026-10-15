import { inr } from "@/lib/shop/catalog";
import { listOrders } from "@/lib/shop/store";
import s from "../shop.module.css";

export const dynamic = "force-dynamic";

export default async function Orders() {
  const orders = await listOrders(30);
  return (
    <>
      <h1 className={s.h1}>Sandbox orders</h1>
      <p className={s.lead}>Every order placed in this sandbox, by anyone. Only the last 4 digits of the test card are kept.</p>
      {orders.length === 0 ? (
        <p className={s.lead} style={{ marginTop: 24 }}>
          No orders yet.
        </p>
      ) : (
        <table className={s.table}>
          <thead>
            <tr>
              <th>Order</th>
              <th>Placed</th>
              <th className={s.right}>Items</th>
              <th className={s.right}>Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>
                  <a href={`/shop/orders/${o.id}`}>{o.id}</a>
                </td>
                <td>{new Date(o.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}</td>
                <td className={s.right}>{o.items.reduce((n, l) => n + l.qty, 0)}</td>
                <td className={s.right}>{inr(o.total_inr)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
