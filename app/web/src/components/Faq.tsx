"use client";

import { useState } from "react";
import { FAQ } from "@/lib/content";
import { Corners } from "./Corners";
import s from "./Faq.module.css";

// Graphify's FAQ: heading left; one dashed box per question; the open one gets corner brackets.
export function Faq() {
  const [open, setOpen] = useState<Set<number>>(() => new Set([0]));

  function toggle(i: number) {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else {
        next.add(i);
      }
      return next;
    });
  }

  return (
    <section className={s.faq} id="faq">
      <div className={s.wrap}>
        <div className={s.left} data-reveal>
          <div className="eyebrow">FAQ</div>
          <h2>Frequently asked questions</h2>
          <p>The honest answers, including where Dejo is not the right tool.</p>
        </div>
        <div className={s.list}>
          {FAQ.map((f, i) => {
            const isOpen = open.has(i);
            return (
              <div key={f.q} className={s.qa} data-open={isOpen || undefined} data-reveal-item>
                <Corners />
                <h3>
                  <button type="button" aria-expanded={isOpen} aria-controls={`faq-${i}`} onClick={() => toggle(i)}>
                    <span>{f.q}</span>
                    <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
                      <path d="M2 8h12" stroke="currentColor" />
                      <path className={s.v} d="M8 2v12" stroke="currentColor" />
                    </svg>
                  </button>
                </h3>
                <div className={s.a} id={`faq-${i}`}>
                  <p>{f.a}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
