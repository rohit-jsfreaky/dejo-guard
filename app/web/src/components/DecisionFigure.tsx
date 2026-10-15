import s from "./DecisionFigure.module.css";

// "How it works", one panel per step: the plan ArmorIQ signs, the page facts of one click, ArmorIQ's answer.
// The values are the real ones from evidence/probe-day0.md, not invented.
export function DecisionFigure({ active }: { active: number }) {
  return (
    <div className={s.fig}>
      <div className={s.panel} data-on={active === 0 || undefined}>
        <div className={s.head}>guard_task</div>
        <p className={s.quote}>“compare prices for Atomic Habits”</p>
        <div className={s.chips}>
          {["read", "navigate", "type_text", "interact", "download", "new_domain"].map((c) => (
            <span key={c} className={s.chip}>
              {c}
            </span>
          ))}
        </div>
        <div className={s.foot}>
          <span className={s.dot} /> plan signed by ArmorIQ · no submit_payment in it
        </div>
      </div>

      <div className={s.panel} data-on={active === 1 || undefined}>
        <div className={s.head}>dejo_act · click · ref e12</div>
        <pre className={s.code}>
          {`<form method="post" action="/api/shop/orders">
  <input autocomplete="cc-number">
  <button type="submit">`}
          <s className={s.words}>Continue</s>
          {`</button>
</form>`}
        </pre>
        <dl className={s.facts}>
          <dt>control</dt>
          <dd>button · submits its form</dd>
          <dt>form</dt>
          <dd>POST · has a card field</dd>
          <dt>words</dt>
          <dd>shown to you, never used</dd>
        </dl>
        <div className={s.foot}>
          <span className={s.dot} /> class <b>submit_payment</b>
        </div>
      </div>

      <div className={s.panel} data-on={active === 2 || undefined}>
        <div className={s.head}>ArmorIQ · check(dejo__submit_payment)</div>
        <div className={s.verdicts}>
          <div className={s.v} data-k="allow">
            <b>navigate</b>
            <span>allow</span>
          </div>
          <div className={s.v} data-k="hold">
            <b>submit_form</b>
            <span>hold · rule_action_hold</span>
          </div>
          <div className={s.v} data-k="block">
            <b>type_payment</b>
            <span>block · rule_action_block</span>
          </div>
          <div className={s.v} data-k="block">
            <b>submit_payment</b>
            <span>block · not in the signed plan</span>
          </div>
        </div>
        <div className={s.foot}>
          <span className={s.dot} /> policy dejo-guard-boundary · decided on platform.armoriq.ai
        </div>
      </div>
    </div>
  );
}
