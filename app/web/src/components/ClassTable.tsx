import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import { CLASS_ROWS, GITHUB_URL } from "@/lib/content";
import s from "./ClassTable.module.css";

const WORD = { allow: "allow", hold: "hold for you", block: "block" };

// The class table: what the page has to say for a click to be each class, and what the default ArmorIQ
// policy does with it. The rule column is the policy file, not code — change it in ArmorIQ.
export function ClassTable() {
  return (
    <section className={s.sec} id="classes">
      <div className={s.wrap}>
        <div className="eyebrow">What a click means</div>
        <div className={s.head} data-reveal>
          <div>
            <h2>
              Read from the page.
              <br />
              Decided by ArmorIQ.
            </h2>
            <p>
              Every action gets one class from the page’s structure. The right-hand column is the default ArmorIQ policy. It lives
              in your ArmorIQ org, so you change it there, not here.
            </p>
          </div>
          <a className={s.btn} href={`${GITHUB_URL}/blob/main/policy/dejo-guard-boundary.yaml`}>
            See the policy <ArrowRightIcon size={14} />
          </a>
        </div>
        <div className={s.table} role="table">
          <div className={s.row} role="row" data-head>
            <span role="columnheader">Class</span>
            <span role="columnheader">The page says</span>
            <span role="columnheader">ArmorIQ</span>
          </div>
          {CLASS_ROWS.map((r) => (
            <div key={r.cls} className={s.row} role="row" data-reveal-item>
              <code role="cell">{r.cls}</code>
              <span role="cell">{r.from}</span>
              <span role="cell">
                <i className={s.rule} data-k={r.rule}>
                  {WORD[r.rule]}
                </i>
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
