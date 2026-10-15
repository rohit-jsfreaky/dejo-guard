"use client";

import { useEffect, useRef } from "react";
import type { Shape } from "@/lib/content";

// Graphify's 96px feature icons, read from its bundle (component "tf", function eg): one dashed path,
// yaw .6 + .32t, pitch .5, perspective 7 / (7 + z), scale 31.68; points near the pointer are pushed away.
type P = [number, number, number];
type Edge = [P, P];
const TAU = Math.PI * 2;

const ring = (n: number, f: (a: number) => P): Edge[] => Array.from({ length: n }, (_, i) => [f((i / n) * TAU), f(((i + 1) / n) * TAU)]);

function cubeEdges(cx: number, s: number, scale = 1): Edge[] {
  const v: P[] = [];
  for (const a of [-s, s]) for (const b of [-s, s]) for (const c of [-s, s]) v.push([cx + a, b, c]);
  const out: Edge[] = [];
  for (let i = 0; i < 8; i++)
    for (let j = i + 1; j < 8; j++) {
      if (v[i].filter((q, k) => q !== v[j][k]).length !== 1) continue;
      const mid = v[i].map((q, k) => (q + v[j][k]) / 2);
      const at = (p: P) => p.map((q, k) => mid[k] + (q - mid[k]) * scale) as P;
      out.push([at(v[i]), at(v[j])]);
    }
  return out;
}

const SHAPES: Record<Shape, (t: number) => Edge[]> = {
  // a padlock: a short cylinder with an arch on top
  lock: () => {
    const r = 0.82;
    const e: Edge[] = [];
    for (const y of [-0.05, 0.95]) e.push(...ring(16, (a) => [Math.cos(a) * r, y, Math.sin(a) * r * 0.55]));
    for (let i = 0; i < 16; i += 2) {
      const a = (i / 16) * TAU;
      e.push([
        [Math.cos(a) * r, -0.05, Math.sin(a) * r * 0.55],
        [Math.cos(a) * r, 0.95, Math.sin(a) * r * 0.55],
      ]);
    }
    for (let i = 0; i < 12; i++) {
      const a = (Math.PI * i) / 12;
      const b = (Math.PI * (i + 1)) / 12;
      e.push([
        [-Math.cos(a) * 0.5, -0.05 - Math.sin(a) * 0.85, 0],
        [-Math.cos(b) * 0.5, -0.05 - Math.sin(b) * 0.85, 0],
      ]);
    }
    return e;
  },
  // three profiles: three stacked squares
  stack: () =>
    [-0.55, 0, 0.55].flatMap((y) => {
      const s = 0.7;
      const c: P[] = [
        [-s, y, -s],
        [s, y, -s],
        [s, y, s],
        [-s, y, s],
      ];
      return [...c.map((p, i) => [p, c[(i + 1) % 4]] as Edge), [[-s * 0.5, y, 0], [s * 0.5, y, 0]] as Edge];
    }),
  // a map of the site: latitude and longitude rings
  globe: () => {
    const r = 0.9;
    const e: Edge[] = [];
    for (const lat of [-0.75, 0, 0.75]) {
      const rr = Math.cos(lat) * r;
      const y = Math.sin(lat) * r;
      e.push(...ring(18, (a) => [Math.cos(a) * rr, y, Math.sin(a) * rr]));
    }
    for (let k = 0; k < 4; k++) {
      const lon = (k / 4) * Math.PI;
      e.push(...ring(18, (a) => [Math.cos(lon) * Math.cos(a) * r, Math.sin(a) * r, Math.sin(lon) * Math.cos(a) * r]));
    }
    return e;
  },
  // one route, many subjects: a trunk that opens into branches
  fan: () => {
    const fork: P = [0, 0.15, 0];
    const e: Edge[] = [[[0, 1.1, 0], fork]];
    for (let k = 0; k < 5; k++) {
      const a = (k / 5) * TAU;
      const tip: P = [Math.cos(a), -0.95, Math.sin(a)];
      e.push([fork, tip], ...ring(10, (b) => [tip[0] + Math.cos(b) * 0.18, tip[1], tip[2] + Math.sin(b) * 0.18]));
    }
    return e;
  },
  // a trail passed between agents: two cubes, one line
  link: () => [
    ...cubeEdges(-0.72, 0.42),
    ...cubeEdges(0.72, 0.42),
    [
      [-0.3, 0, 0],
      [0.3, 0, 0],
    ],
  ],
  // forget: a cube whose edges shrink away, then come back
  fade: (t) => cubeEdges(0, 0.8, 0.5 + 0.5 * Math.cos(t * 0.9)),
};

export function WireIcon({ shape }: { shape: Shape }) {
  const svg = useRef<SVGSVGElement>(null);
  const path = useRef<SVGPathElement>(null);

  useEffect(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let mx = -1e9;
    let my = -1e9;
    let px = 0;
    let py = 0;
    let pc = 0;
    const onMove = (e: PointerEvent) => {
      mx = e.clientX;
      my = e.clientY;
    };
    addEventListener("pointermove", onMove, { passive: true });

    function draw(t: number) {
      const b = svg.current!.getBoundingClientRect();
      const cx = b.left + 48;
      const cy = b.top + 48;
      const dist = Math.hypot(mx - cx, my - cy);
      const near = dist < 130;
      px += ((near ? Math.max(-1, Math.min(1, (mx - cx) / 130)) : 0) - px) * 0.08;
      py += ((near ? Math.max(-1, Math.min(1, (my - cy) / 130)) : 0) - py) * 0.08;
      pc += ((near ? 1 - dist / 130 : 0) - pc) * 0.08;
      const yaw = 0.6 + 0.32 * t + 0.5 * px;
      const pitch = 0.5 - 0.35 * py;
      const [c, h, d, u] = [Math.cos(yaw), Math.sin(yaw), Math.cos(pitch), Math.sin(pitch)];
      const f = (p: P) => {
        const x = p[0] * c + p[2] * h;
        const s = -p[0] * h + p[2] * c;
        const r = p[1] * d - s * u;
        const a = 7 / (7 + (p[1] * u + s * d));
        let X = 48 + x * a * 31.68;
        let Y = 48 + r * a * 31.68;
        if (pc > 0.01) {
          const gx = b.left + X - mx;
          const gy = b.top + Y - my;
          const o = Math.hypot(gx, gy);
          if (o < 130 && o > 0.001) {
            const k = 1 - o / 130;
            X += (gx / o) * 7 * k * k * pc;
            Y += (gy / o) * 7 * k * k * pc;
          }
        }
        return `${X.toFixed(1)} ${Y.toFixed(1)}`;
      };
      let dd = "";
      for (const [p, q] of SHAPES[shape](t)) dd += `M${f(p)}L${f(q)}`;
      path.current!.setAttribute("d", dd);
      path.current!.setAttribute("stroke-dashoffset", (-(11 * t) % 8).toFixed(2));
    }

    let raf = 0;
    let on = false;
    const tick = (now: number) => {
      draw(now / 1000);
      if (on) raf = requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver(([e]) => {
      on = e.isIntersecting && !reduce;
      if (on) raf = requestAnimationFrame(tick);
    });
    draw(0);
    io.observe(svg.current!);
    return () => {
      io.disconnect();
      cancelAnimationFrame(raf);
      removeEventListener("pointermove", onMove);
    };
  }, [shape]);

  return (
    <svg ref={svg} viewBox="0 0 96 96" width="96" height="96" aria-hidden="true" style={{ display: "block", margin: "0 0 16px -8px", overflow: "visible" }}>
      <path ref={path} fill="none" stroke="var(--ink)" strokeWidth="1" strokeDasharray="4 4" strokeLinecap="butt" />
    </svg>
  );
}
