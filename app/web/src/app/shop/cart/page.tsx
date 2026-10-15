import { inr } from "@/lib/shop/catalog";
import { cartId, getCart, priced } from "@/lib/shop/store";
import s from "../shop.module.css";

export const dynamic = "force-dynamic";

export default async function CartPage() {
  const { lines, total } = priced(await getCart(await cartId()));
  return (
    <>
      <h1 className={s.h1}>Your cart</h1>
      {lines.length === 0 ? (
        <p className={s.lead}>
          Your cart is empty. <a href="/shop">Browse books</a>
        </p>
      ) : (
        <>
          <table className={s.table}>
            <thead>
              <tr>
                <th>Book</th>
                <th className={s.right}>Qty</th>
                <th className={s.right}>Price</th>
              </tr>
            </thead>
            <tbody>
              {lines.map((l) => (
                <tr key={l.id}>
                  <td>
                    <a href={`/shop/p/${l.id}`}>{l.title}</a>
                  </td>
                  <td className={s.right}>{l.qty}</td>
                  <td className={s.right}>{inr(l.price * l.qty)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={s.total}>
            <span>Total {inr(total)}</span>
            <a className="btn btnInk" href="/shop/checkout">
              Checkout
            </a>
          </div>
        </>
      )}
    </>
  );
}
