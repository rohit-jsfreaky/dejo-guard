import Image from "next/image";
import { ArrowRightIcon, GithubLogoIcon } from "@phosphor-icons/react/dist/ssr";
import { heroTiles } from "@/lib/heroTiles";
import { ATTACKS, FALSE_HOLDS, UNSAFE_GUARD, UNSAFE_NAMES } from "@/lib/numbers";
import { GITHUB_URL, NAV, TAGLINE } from "@/lib/content";
import { HeroTrail } from "./HeroTrail";
import { Logo } from "./Logo";
import s from "./Hero.module.css";

const TILES = heroTiles();

export function Hero() {
  return (
    <div className={s.page}>
      <header className={s.nav}>
        <a className={s.brand} href="/" aria-label="Dejo Guard home">
          <Logo size={24} />
          dejo guard
        </a>
        <nav className={s.links}>
          {NAV.map((n) => (
            <a key={n.label} href={n.href}>
              {n.label}
            </a>
          ))}
        </nav>
        <div className={s.navRight}>
          <a className={s.gh} href={GITHUB_URL}>
            <GithubLogoIcon size={16} />
            GitHub
          </a>
          <a className={`btn btnInk ${s.navCta}`} href="#start">
            Get started
          </a>
        </div>
      </header>

      <div className={s.stage} data-hero-stage>
        <svg className={s.trail} aria-hidden="true">
          <path data-trail="base" className={s.base} fill="none" stroke="var(--ink)" strokeOpacity=".28" strokeWidth="1" />
          <path data-trail="walked" fill="none" stroke="var(--ink)" strokeOpacity=".85" strokeWidth="1.25" strokeLinecap="round" />
        </svg>
        {TILES.map((t, i) => (
          <div
            key={i}
            className={s.tile}
            data-stop={t.stop ?? undefined}
            style={{
              [t.side === "l" ? "left" : "right"]: t.x,
              top: t.y,
              width: t.w,
              opacity: 0.55 + t.depth * 0.45,
              animationDelay: `-${t.delay.toFixed(1)}s`,
              ["--d" as string]: t.depth.toFixed(2),
            }}
          >
            <Image src={`/tiles/${t.shot}.webp`} alt="" fill sizes="144px" className={s.shot} priority={t.y < 400} />
            <span className={s.tag} />
          </div>
        ))}
      </div>

      <main className={s.hero}>
        <a className={s.pill} href="/judges">
          Built for ArmorIQ Flow State <b>the 90-second tour</b> <ArrowRightIcon size={13} />
        </a>
        <h1 className={s.h1}>
          Your agent clicks.
          <br />
          ArmorIQ decides.
        </h1>
        <p className={s.sub}>{TAGLINE}</p>
        <div className={s.ctas}>
          <a className="btn btnInk" href="#start">
            Get started
          </a>
          <a className="btn btnLine" href="/shop/lab">
            Try to make it pay
          </a>
        </div>
        <div className={s.status} data-hero-status data-state="on">
          <i />
          <span data-st1>Allowed by ArmorIQ</span>
          <span className={s.sep} />
          <span data-st2>Search · navigate</span>
        </div>
      </main>

      <section className={s.numbers} aria-label="Eval results">
        <div className={s.num}>
          <b>{UNSAFE_NAMES}</b>
          <span>unsafe actions let through by a tool-name policy, on {ATTACKS} attack pages</span>
        </div>
        <div className={s.num}>
          <b>{UNSAFE_GUARD}</b>
          <span>let through by Dejo Guard, on the same pages</span>
        </div>
        <div className={s.num}>
          <b>{FALSE_HOLDS}</b>
          <span>of normal browsing steps held for approval</span>
        </div>
      </section>
      <HeroTrail />
    </div>
  );
}
