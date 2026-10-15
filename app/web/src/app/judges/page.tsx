import type { Metadata } from "next";
import { PageNav } from "@/components/PageNav";
import { GITHUB_URL } from "@/lib/content";
import { ATTACKS, FALSE_HOLDS, UNSAFE_GUARD, UNSAFE_NAMES } from "@/lib/numbers";
import d from "../doc.module.css";

export const metadata: Metadata = { title: "For judges · Dejo Guard", description: "Dejo Guard in 90 seconds: what to click, what to look for." };

export default function Judges() {
  return (
    <>
      <PageNav />
      <main className={d.main}>
        <div className="eyebrow">For judges · 90 seconds</div>
        <h1 className={d.h1}>A browser agent has one tool: click.</h1>
        <p className={d.lead}>
          A rule on tool names can’t tell “Next page” from “Pay ₹4,999”: both are <code>click(ref=e12)</code>. Dejo Guard reads
          what e12 is from the page itself, names it, and lets ArmorIQ decide. Our code only describes.
        </p>

        <h2 className={d.h2}>The finding</h2>
        <p className={d.p}>
          On {ATTACKS} attack pages, a policy on tool names let <b>{UNSAFE_NAMES}</b> unsafe actions through. Dejo Guard let{" "}
          <b>{UNSAFE_GUARD}</b> through, and held <b>{FALSE_HOLDS}</b> of normal browsing steps. Same pages, scripted, no model in
          the loop. Method and raw output: <a href={`${GITHUB_URL}/blob/main/docs/FINDING.md`}>docs/FINDING.md</a>.
        </p>

        <h2 className={d.h2}>See it in 90 seconds</h2>
        <ol className={d.steps}>
          <li className={d.li}>
            <span>
              <b>Watch the video</b> at the top of the <a href={GITHUB_URL}>README</a>. Claude Code shops on our sandbox: browsing is
              allowed, “Place order” waits for approval in ArmorIQ, the card field is blocked.
            </span>
          </li>
          <li className={d.li}>
            <span>
              <b>Open the <a href="/feed">live feed</a>.</b> Every row is an ArmorIQ answer, word for word: the class, the reason
              (<code>rule_action_hold</code>, <code>rule_action_block</code>, <code>tool-not-in-plan</code>) and the policy that matched.
            </span>
          </li>
          <li className={d.li}>
            <span>
              <b>Open the <a href="/shop/lab">attack lab</a>.</b> A pay button that says “Continue”, a checkout in Hindi, a hidden
              “the user already approved” note, a plain button whose script buys. Each shows which class the page gives it.
            </span>
          </li>
          <li className={d.li}>
            <span>
              <b>Read <a href={`${GITHUB_URL}/blob/main/policy/dejo-guard-boundary.yaml`}>the policy</a>.</b> That file, active in
              ArmorIQ, is where allow, hold and block live. Remove the <code>submit_payment: hold</code> line and the same click goes
              through. That is how you know ArmorIQ decides, not us.
            </span>
          </li>
          <li className={d.li}>
            <span>
              <b>Try it on your own agent.</b> <code>pip install dejo-guard</code>, <code>armoriq login</code>,{" "}
              <code>dejo-guard init</code>, <code>claude mcp add dejo-guard -- dejo-guard</code>. Then: “compare prices for Atomic
              Habits on dejo-guard.vercel.app/shop, then buy the cheapest”.
            </span>
          </li>
        </ol>

        <h2 className={d.h2}>What is new, what is not</h2>
        <p className={d.p}>
          Dejo (the browser with a memory, MIT, on PyPI since 13 Oct) was built before the hackathon by the same author and is used as
          a library. Everything that makes ArmorIQ see the page is new: page facts, the class table, intent plans, holds and
          approvals, the network watch, replay checks, the sandbox shop, the attack lab and the eval. Claude Code helped write the
          code; every decision and every line was reviewed by the author.
        </p>
      </main>
    </>
  );
}
