import type Lenis from "lenis";

// The page's single Lenis instance, set by <Motion>. Code that scrolls the page goes through here,
// so a jump still feels like the rest of the page.
let lenis: Lenis | null = null;

export function setLenis(instance: Lenis | null) {
  lenis = instance;
}

export function scrollToY(y: number) {
  if (lenis) lenis.scrollTo(y);
  else window.scrollTo({ top: y, behavior: "smooth" });
}
