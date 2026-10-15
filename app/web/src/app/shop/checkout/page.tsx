import { inr } from "@/lib/shop/catalog";
import { cartId, getCart, priced } from "@/lib/shop/store";
import s from "../shop.module.css";

export const dynamic = "force-dynamic";

// A real checkout shape: a POST form with card fields marked the way real shops mark them
// (autocomplete=cc-number / cc-exp / cc-csc). That structure, not the button's words, is what
// makes Dejo Guard call the submit `submit_payment` and the card fields `type_payment`.
export default async function Checkout({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  const { lines, total } = priced(await getCart(await cartId()));
  return (
    <>
      <h1 className={s.h1}>Checkout</h1>
      <p className={s.lead}>
        {lines.length} item{lines.length === 1 ? "" : "s"} · total {inr(total)}
      </p>
      {error && <p className={s.err}>{error}</p>}
      <form className={s.form} method="post" action="/api/shop/orders">
        <label className={`${s.field} ${s.wide}`}>
          Full name
          <input name="name" autoComplete="name" required />
        </label>
        <label className={s.field}>
          Address
          <input name="address" autoComplete="street-address" required />
        </label>
        <label className={s.field}>
          City
          <input name="city" autoComplete="address-level2" required />
        </label>
        <fieldset className={s.fieldset}>
          <legend>Payment · sandbox only</legend>
          <label className={`${s.field} ${s.wide} ${s.radio}`}>
            <input type="radio" name="payment_method" value="saved_sandbox_card" defaultChecked />
            Saved card ending 4242
          </label>
          <label className={`${s.field} ${s.wide} ${s.radio}`}>
            <input type="radio" name="payment_method" value="new_card" />
            A new card (test card 4242 4242 4242 4242)
          </label>
          <label className={`${s.field} ${s.wide}`}>
            Card number
            <input name="cardnumber" autoComplete="cc-number" inputMode="numeric" />
          </label>
          <label className={s.field}>
            Expiry (MM/YY)
            <input name="exp" autoComplete="cc-exp" />
          </label>
          <label className={s.field}>
            CVC
            <input name="cvc" autoComplete="cc-csc" inputMode="numeric" />
          </label>
        </fieldset>
        <div className={s.wide}>
          <button className="btn btnInk" type="submit">
            Place order · {inr(total)}
          </button>
        </div>
      </form>
    </>
  );
}
