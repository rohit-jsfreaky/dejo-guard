import { AGENTS } from "@/lib/content";
import { AgentLogo } from "./AgentLogo";
import s from "./AgentsBand.module.css";

// Vercel's marquee: two identical tracks, 40s per 7 logos; Tavily's 8% edge fade; Exa's shared hairlines.
const SECONDS = Math.round((40 / 7) * AGENTS.length);

function Track({ hidden }: { hidden?: boolean }) {
  return (
    <div className={s.track} aria-hidden={hidden || undefined} style={{ animationDuration: `${SECONDS}s` }}>
      {AGENTS.map((a) => (
        <span key={a.file} className={s.cell} title={a.name}>
          <span className={s.mark}>
            <AgentLogo file={a.file} height={a.icon} />
            <AgentLogo file={`${a.file}-text`} height={a.text} />
          </span>
          {!hidden && <span className={s.sr}>{a.name}</span>}
        </span>
      ))}
    </div>
  );
}

export function AgentsBand() {
  return (
    <section className={s.band} aria-label="Works with">
      <p className={s.lab}>Works with the AI agent you already use</p>
      <div className={s.marquee}>
        <Track />
        <Track hidden />
      </div>
    </section>
  );
}
