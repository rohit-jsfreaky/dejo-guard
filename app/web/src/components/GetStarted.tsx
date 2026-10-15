import { GithubLogoIcon, HardDrivesIcon, KeyIcon } from "@phosphor-icons/react/dist/ssr";
import { INSTALL } from "@/lib/content";
import { AgentLogo } from "./AgentLogo";
import { CodeBlock } from "./CodeBlock";
import { ConnectTabs } from "./ConnectTabs";
import { CopyPromptButton } from "./CopyPromptButton";
import s from "./GetStarted.module.css";

// Install steps from the README.
export function GetStarted() {
  return (
    <section className={s.inst} id="start">
      <div className={s.wrap}>
        <div className="eyebrow">Get started</div>
        <div className={s.grid} data-reveal>
          <div className={s.left}>
            <h2>
              Your agent,
              <br />
              your sites, 5 minutes.
            </h2>
            <p className={s.lead}>Install it, sign in to your own free ArmorIQ org, add it to your agent. Then ask for something on a website.</p>
            <CopyPromptButton className={s.prompt}>
              <span className={s.ag}>
                {["claude", "codex", "cursor"].map((f) => (
                  <AgentLogo key={f} file={f} height={15} />
                ))}
              </span>
            </CopyPromptButton>
            <p className={s.hint}>Paste it into your agent and it sets Dejo Guard up for you.</p>
          </div>
          <div>
            <div className={s.step}>
              <span className={s.n}>1</span>
              <div>
                <h3>Install</h3>
                <p className={s.where}>Python 3.12 or newer</p>
                {INSTALL.map((c) => (
                  <CodeBlock key={c.code} code={c.code} note={c.note} name={c.code} />
                ))}
              </div>
            </div>
            <div className={s.step}>
              <span className={s.n}>2</span>
              <div>
                <h3>Add it to your agent</h3>
                <ConnectTabs />
              </div>
            </div>
            <div className={s.step}>
              <span className={s.n}>3</span>
              <div>
                <h3>Ask for something on a website</h3>
                <p className={s.ask}>&ldquo;Compare prices for Atomic Habits on dejo-guard.vercel.app/shop&rdquo;</p>
                <p className={s.where}>Browsing goes through. Ask it to check out and watch ArmorIQ hold the order for you.</p>
              </div>
            </div>
          </div>
        </div>
        <div className={s.trust}>
          <div data-reveal-item>
            <KeyIcon size={20} />
            <h3>No model key</h3>
            <p>Dejo Guard never calls a model. The agent you already use does the thinking.</p>
          </div>
          <div data-reveal-item>
            <HardDrivesIcon size={20} />
            <h3>Fails closed</h3>
            <p>If ArmorIQ can’t be reached, nothing on the page is touched. No answer means no click.</p>
          </div>
          <div data-reveal-item>
            <GithubLogoIcon size={20} />
            <h3>Free and open source</h3>
            <p>MIT licensed, built on Dejo (MIT). Read the code, run it yourself, change the policy.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
