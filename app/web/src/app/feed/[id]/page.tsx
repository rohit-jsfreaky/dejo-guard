import type { Metadata } from "next";
import { FeedLive } from "@/components/FeedLive";
import { PageNav } from "@/components/PageNav";
import { rows } from "@/lib/feed";
import d from "../../doc.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Your feed · Dejo Guard", robots: { index: false } };

export default async function OwnFeed({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const initial = await rows(id).catch(() => []);
  return (
    <>
      <PageNav />
      <main className={d.main}>
        <div className="eyebrow">Feed {id}</div>
        <h1 className={d.h1}>Your guard, live.</h1>
        <p className={d.lead}>Decisions from a guard running on someone’s own machine, streamed as ArmorIQ answers them.</p>
        <div className={d.feedWrap}>
          <FeedLive id={id} initial={initial} />
        </div>
      </main>
    </>
  );
}
