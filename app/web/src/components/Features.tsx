import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import { FEATURES } from "@/lib/content";
import { WireIcon } from "./WireIcon";
import s from "./Features.module.css";

// Graphify's "Trust" grid: eyebrow, mono heading, grey lead, a small link button; 96px icon, 15px title, 15px grey body.
export function Features() {
  return (
    <section className={s.feats} id="feats">
      <div className={s.wrap}>
        <div className="eyebrow">Built against real tricks</div>
        <div className={s.head} data-reveal>
          <div>
            <h2>
              Pages lie to agents.
              <br />
              Structure doesn’t.
            </h2>
            <p>Every trick below is a real page in the attack lab. Point your own agent at it with Dejo Guard on.</p>
          </div>
          <a className={s.btn} href="/shop/lab">
            Open the attack lab <ArrowRightIcon size={14} />
          </a>
        </div>
        <div className={s.grid}>
          {FEATURES.map((f) => (
            <div key={f.title} data-reveal-item>
              <WireIcon shape={f.shape} />
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
