import { ATTACKS } from "@/lib/shop/lab";
import s from "../shop.module.css";

export default function Lab() {
  return (
    <>
      <h1 className={s.h1}>Attack lab</h1>
      <p className={s.lead} style={{ maxWidth: 680 }}>
        Pages built to fool a browser agent into paying, typing a card or a password, or leaving the site. Point your own agent at
        any of them with Dejo Guard on. Try to make it pay.
      </p>
      <div className={s.labList}>
        {ATTACKS.map((a) => (
          <a key={a.slug} className={s.labCard} href={`/shop/lab/${a.slug}`}>
            <span className={s.chip}>
              expect {a.expect.cls} → {a.expect.decision}
            </span>
            <h3>{a.title}</h3>
            <p>{a.trick}</p>
          </a>
        ))}
      </div>
    </>
  );
}
