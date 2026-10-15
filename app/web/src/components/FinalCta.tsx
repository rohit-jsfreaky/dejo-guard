import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import s from "./FinalCta.module.css";

// Graphify's closing line in a dashed frame; the frame marches like the hero's trail.
export function FinalCta() {
  return (
    <section className={s.cta}>
      <div className={s.wrap}>
        <div className={s.frame}>
          <svg className={s.dash} aria-hidden="true">
            <rect x=".5" y=".5" fill="none" stroke="var(--ink)" strokeOpacity=".28" strokeDasharray="4 4" />
          </svg>
          <h2 data-reveal>Try to make it pay.</h2>
          <p>Eight pages built to trick a browser agent. Point yours at them with Dejo Guard on, then check the live feed.</p>
          <div className={s.btns}>
            <a className="btn btnInk" href="#start">
              Get started <ArrowRightIcon size={15} />
            </a>
            <a className="btn btnLine" href="/shop/lab">
              Open the attack lab
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
