import { GithubLogoIcon } from "@phosphor-icons/react/dist/ssr";
import { GITHUB_URL, NAV } from "@/lib/content";
import { Logo } from "./Logo";
import s from "./PageNav.module.css";

// The top bar for every page that is not the landing page.
export function PageNav() {
  return (
    <header className={s.nav}>
      <a className={s.brand} href="/">
        <Logo size={22} />
        dejo guard
      </a>
      <nav className={s.links}>
        {NAV.map((n) => (
          <a key={n.label} href={n.href}>
            {n.label}
          </a>
        ))}
      </nav>
      <a className={s.gh} href={GITHUB_URL}>
        <GithubLogoIcon size={16} />
        GitHub
      </a>
    </header>
  );
}
