import type { Metadata } from "next";
import { FeedLive } from "@/components/FeedLive";
import { PageNav } from "@/components/PageNav";
import { DEMO_FEED, rows } from "@/lib/feed";
import d from "../doc.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Live feed · Dejo Guard", description: "Every ArmorIQ decision on our own demo runs, live." };

export default async function Feed() {
  const initial = await rows(DEMO_FEED).catch(() => []);
  return (
    <>
      <PageNav />
      <main className={d.main}>
        <div className="eyebrow">Live feed</div>
        <h1 className={d.h1}>Every decision, as ArmorIQ makes it.</h1>
        <p className={d.lead}>
          This is our own guard, streaming from the demo machine. Each row is one action: the class the page gave it, and
          ArmorIQ’s answer, word for word. Want your own? Run <code>dejo-guard share</code> and you get a link like this one.
        </p>
        <div className={d.feedWrap}>
          <FeedLive id={DEMO_FEED} initial={initial} />
        </div>
      </main>
    </>
  );
}
