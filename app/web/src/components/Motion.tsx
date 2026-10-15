"use client";

import { useEffect } from "react";
import { loadGsap } from "@/lib/gsap";
import { setLenis } from "@/lib/smoothScroll";

// Lenis smooth scroll, driven by GSAP's ticker so ScrollTrigger and Lenis agree on every frame,
// plus one quiet reveal: section headings and grid items rise 16px and fade in, once.
// Both libraries load after first paint.
export function Motion() {
  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let undo: (() => void) | null = null;
    let cancelled = false;

    Promise.all([loadGsap(), import("lenis")]).then(([{ gsap, ScrollTrigger }, { default: Lenis }]) => {
      if (cancelled) return;
      const lenis = new Lenis({ autoRaf: false, anchors: true });
      setLenis(lenis);
      lenis.on("scroll", ScrollTrigger.update);
      const tick = (time: number) => lenis.raf(time * 1000);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);

      const ctx = gsap.context(() => {
        for (const el of gsap.utils.toArray<HTMLElement>("[data-reveal]")) {
          // anything already on screen when GSAP arrives stays as it is
          if (el.getBoundingClientRect().top < innerHeight) continue;
          gsap.from(el, { y: 16, opacity: 0, duration: 0.7, ease: "power2.out", scrollTrigger: { trigger: el, start: "top 88%", once: true } });
        }
        const items = gsap.utils.toArray<HTMLElement>("[data-reveal-item]").filter((el) => el.getBoundingClientRect().top >= innerHeight);
        gsap.set(items, { y: 16, opacity: 0 });
        ScrollTrigger.batch(items, {
          start: "top 90%",
          once: true,
          onEnter: (batch) => gsap.to(batch, { y: 0, opacity: 1, duration: 0.6, ease: "power2.out", stagger: 0.08 }),
        });
      });

      undo = () => {
        ctx.revert();
        gsap.ticker.remove(tick);
        lenis.destroy();
        setLenis(null);
      };
    });

    return () => {
      cancelled = true;
      undo?.();
    };
  }, []);
  return null;
}
