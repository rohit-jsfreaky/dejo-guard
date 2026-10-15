import type { gsap as Gsap } from "gsap";
import type { ScrollTrigger as ScrollTriggerType } from "gsap/ScrollTrigger";

// GSAP is fetched after the page has painted, never before: it only drives motion, never content.
let loading: Promise<{ gsap: typeof Gsap; ScrollTrigger: typeof ScrollTriggerType }> | null = null;

export function loadGsap() {
  loading ??= Promise.all([import("gsap"), import("gsap/ScrollTrigger")]).then(([g, st]) => {
    g.gsap.registerPlugin(st.ScrollTrigger);
    return { gsap: g.gsap, ScrollTrigger: st.ScrollTrigger };
  });
  return loading;
}
