"use client";

import { useEffect, useRef, useState } from "react";
import type { ScrollTrigger } from "gsap/ScrollTrigger";
import { STEPS } from "@/lib/content";
import { loadGsap } from "@/lib/gsap";
import { scrollToY } from "@/lib/smoothScroll";
import { Corners } from "./Corners";
import { DecisionFigure } from "./DecisionFigure";
import s from "./HowItWorks.module.css";

const PIN_HALF = 250; // half the sticky panel's height: the panel sits centred while pinned
const NARROW = "(max-width: 900px)";

// Graphify's "How it works": the panel stays put while each step owns an equal slice of the scroll.
export function HowItWorks() {
  const [active, setActive] = useState(0);
  const section = useRef<HTMLElement>(null);
  const trigger = useRef<ScrollTrigger | null>(null);

  useEffect(() => {
    let undo: (() => void) | null = null;
    let cancelled = false;
    loadGsap().then(({ gsap, ScrollTrigger }) => {
      if (cancelled) return;
      const mm = gsap.matchMedia();
      mm.add(`not ${NARROW}`, () => {
        trigger.current = ScrollTrigger.create({
          trigger: section.current,
          start: `top center-=${PIN_HALF}`,
          end: `bottom center+=${PIN_HALF}`,
          onUpdate: (self) => setActive(Math.min(2, Math.floor(self.progress * 3))),
        });
      });
      // on phones the steps stack; they take turns instead
      mm.add(NARROW, () => {
        const id = setInterval(() => setActive((a) => (a + 1) % 3), 9000);
        return () => clearInterval(id);
      });
      undo = () => mm.revert();
    });
    return () => {
      cancelled = true;
      undo?.();
    };
  }, []);

  function pick(i: number) {
    const t = trigger.current;
    if (!t || matchMedia(NARROW).matches) return setActive(i);
    scrollToY(t.start + ((t.end - t.start) * (i + 0.5)) / 3);
  }

  return (
    <section className={s.how} id="how" ref={section}>
      <div className={s.sticky}>
        <div className={s.body}>
          <div className={s.steps}>
            <h2 className={`eyebrow ${s.eyebrow}`}>How it works</h2>
            <div className={s.list}>
              {STEPS.map((step, i) => (
                <div key={step.title} className={s.stepWrap}>
                  {i > 0 && <div className={s.rule} />}
                  <div className={s.step} data-on={i === active || undefined}>
                    <h3>
                      <button type="button" onClick={() => pick(i)}>
                        {step.title}
                      </button>
                    </h3>
                    <p>{step.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className={s.frame}>
            <Corners />
            <DecisionFigure active={active} />
          </div>
        </div>
      </div>
    </section>
  );
}
