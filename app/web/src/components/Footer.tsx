import { GithubLogoIcon } from "@phosphor-icons/react/dist/ssr";
import { ARMORIQ_URL, DEJO_URL, GITHUB_URL, PYPI_URL } from "@/lib/content";
import { Logo } from "./Logo";
import s from "./Footer.module.css";

const COLUMNS = [
  {
    head: "Product",
    links: [
      ["How it works", "/#how"],
      ["What a click means", "/#classes"],
      ["Attack lab", "/shop/lab"],
      ["Live feed", "/feed"],
      ["For judges", "/judges"],
    ],
  },
  {
    head: "Developers",
    links: [
      ["GitHub", GITHUB_URL],
      ["PyPI", PYPI_URL],
      ["Built on Dejo", DEJO_URL],
      ["ArmorIQ", ARMORIQ_URL],
    ],
  },
];

// Graphify's footer mark: 5 copies of the outline, each 0.99x the last, shrunk toward the top centre and painted
// largest first. Each is filled with the footer colour, so it hides the copies behind it: the extruded look.
const LAYERS = [0, 1, 2, 3, 4];

export function Footer() {
  return (
    <footer className={s.foot}>
      <div className={s.wrap}>
        <div className={s.top}>
          <div className={s.brandCol}>
            <a className={s.brand} href="/">
              <Logo size={22} />
              dejo guard
            </a>
            <p>A browser agent on your logged-in sites, with ArmorIQ deciding every click by what it means on the page.</p>
            <a className={s.social} href={GITHUB_URL} aria-label="Dejo Guard on GitHub">
              <GithubLogoIcon size={17} />
            </a>
          </div>
          <div className={s.cols}>
            {COLUMNS.map((c) => (
              <div key={c.head}>
                <h3>{c.head}</h3>
                {c.links.map(([label, href]) => (
                  <a key={label} href={href}>
                    {label}
                  </a>
                ))}
              </div>
            ))}
          </div>
        </div>
        <div className={s.bottom}>
          <span>&copy; 2026 Rohit Kashyap · Boundary Labs. MIT licensed.</span>
          <span>Built for ArmorIQ Flow State, October 2026</span>
        </div>
      </div>
      <div className={s.markBox}>
        <svg className={s.mark} viewBox="-20 -20 1040 320" aria-hidden="true">
          {LAYERS.map((k) => (
            <text
              key={k}
              className={s.wm}
              data-layer={k}
              x="500"
              y="268"
              textAnchor="middle"
              textLength="1000"
              lengthAdjust="spacingAndGlyphs"
              transform={`translate(500 0) scale(${(0.99 ** k).toFixed(4)}) translate(-500 0)`}
            >
              guard
            </text>
          ))}
        </svg>
      </div>
    </footer>
  );
}
