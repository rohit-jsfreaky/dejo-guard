"use client";

import { useEffect } from "react";

// The hero's story on a loop: the agent walks a shop page by page and ArmorIQ decides each step by what it
// means — four allowed, "Place order" held for the human, the card field blocked.
// Trail: Graphify's marching dotted base + Inngest's draw-in curve, cubic-bezier(.22,.61,.27,1).
const RUN1 = 7.2;
const HOLD = 3.4;
const CYCLE = RUN1 + HOLD;
const STEPS: { page: string; cls: string; state: "on" | "held" | "blocked" }[] = [
  { page: "Search", cls: "navigate", state: "on" },
  { page: "Book page", cls: "navigate", state: "on" },
  { page: "Add to cart", cls: "state_change", state: "on" },
  { page: "Cart", cls: "navigate", state: "on" },
  { page: "Place order", cls: "submit_payment", state: "held" },
  { page: "Card number", cls: "type_payment", state: "blocked" },
];
const WORD = { on: "allowed", held: "held", blocked: "blocked" };

const bez = (t: number, a: number, b: number) => 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3;
function draw(x: number) {
  let lo = 0;
  let hi = 1;
  for (let i = 0; i < 18; i++) {
    const m = (lo + hi) / 2;
    if (bez(m, 0.22, 0.27) < x) lo = m;
    else hi = m;
  }
  return bez((lo + hi) / 2, 0.61, 1);
}

export function HeroTrail() {
  useEffect(() => {
    const stage = document.querySelector<HTMLElement>("[data-hero-stage]");
    const status = document.querySelector<HTMLElement>("[data-hero-status]");
    if (!stage || !status) return;
    const svg = stage.querySelector("svg")!;
    const base = stage.querySelector<SVGPathElement>('[data-trail="base"]')!;
    const walked = stage.querySelector<SVGPathElement>('[data-trail="walked"]')!;
    const st1 = status.querySelector("[data-st1]")!;
    const st2 = status.querySelector("[data-st2]")!;
    const stops = [...stage.querySelectorAll<HTMLElement>("[data-stop]")].sort((a, b) => +a.dataset.stop! - +b.dataset.stop!);
    const tags = stops.map((el) => el.querySelector("span")!);
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let L = 0;
    let at: number[] = [];

    function layout() {
      const box = stage!.getBoundingClientRect();
      svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
      const p = stops.map((el) => {
        const r = el.getBoundingClientRect();
        return [r.left - box.left + r.width / 2, r.top - box.top + r.height / 2];
      });
      const arcY = box.height * 0.72;
      const pts = [p[0], p[1], p[2], [box.width * 0.32, arcY], [box.width * 0.68, arcY], p[3], p[4], p[5]];
      let d = `M${pts[0][0]} ${pts[0][1]}`;
      for (let i = 0; i < pts.length - 1; i++) {
        const p0 = pts[i - 1] ?? pts[i];
        const p1 = pts[i];
        const p2 = pts[i + 1];
        const p3 = pts[i + 2] ?? p2;
        d += ` C${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6}, ${p2[0] - (p3[0] - p1[0]) / 6} ${p2[1] - (p3[1] - p1[1]) / 6}, ${p2[0]} ${p2[1]}`;
      }
      base.setAttribute("d", d);
      walked.setAttribute("d", d);
      L = walked.getTotalLength();
      walked.style.strokeDasharray = `${L} ${L}`;
      at = p.map((q) => {
        let best = 0;
        let bd = Infinity;
        for (let i = 0; i <= 800; i++) {
          const pt = walked.getPointAtLength((L * i) / 800);
          const dd = Math.hypot(pt.x - q[0], pt.y - q[1]);
          if (dd < bd) {
            bd = dd;
            best = (L * i) / 800;
          }
        }
        return best;
      });
    }

    function frame(T: number) {
      const n = at.length - 1;
      const per = RUN1 / n;
      const k = Math.min(Math.floor(T / per), n - 1);
      const f = T < RUN1 ? Math.min((T - k * per) / per / 0.7, 1) : 1;
      const pos = T < RUN1 ? at[k] + (at[k + 1] - at[k]) * draw(f) : at[n];
      const lit = T < RUN1 ? k + 1 + (f >= 1 ? 1 : 0) : at.length;
      const now = STEPS[Math.min(lit, STEPS.length) - 1];
      status!.dataset.state = now.state;
      st1.textContent = now.state === "held" ? "Held for your approval" : now.state === "blocked" ? "Blocked by ArmorIQ" : "Allowed by ArmorIQ";
      st2.textContent = `${now.page} · ${now.cls}`;
      walked.style.strokeDashoffset = String(L - (T > CYCLE - 0.4 ? 0 : pos));
      stops.forEach((el, i) => {
        const step = STEPS[i];
        el.dataset.state = i < lit && T <= CYCLE - 0.4 ? step.state : "";
        tags[i].textContent = WORD[step.state];
      });
    }

    layout();
    addEventListener("resize", layout);
    let raf = 0;
    let start: number | null = null;
    let visible = true;
    const loop = (now: number) => {
      if (start === null) start = now;
      frame(((now - start) / 1000) % CYCLE);
      if (visible) raf = requestAnimationFrame(loop);
    };
    // pause while the hero is off screen
    const io = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      if (visible && !reduce) raf = requestAnimationFrame(loop);
    });
    if (reduce) frame(RUN1 + 1);
    else io.observe(stage);
    return () => {
      removeEventListener("resize", layout);
      io.disconnect();
      cancelAnimationFrame(raf);
    };
  }, []);
  return null;
}
