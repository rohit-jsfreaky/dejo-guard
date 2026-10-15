"use client";

import { useState } from "react";
import { CONNECT } from "@/lib/content";
import { CodeBlock } from "./CodeBlock";
import s from "./GetStarted.module.css";

// Stagehand's mono tabs: one snippet per agent, with where it goes.
export function ConnectTabs() {
  const [tab, setTab] = useState(0);
  const pane = CONNECT[tab];
  return (
    <>
      <div className={s.tabs} role="tablist">
        {CONNECT.map((c, i) => (
          <button
            key={c.tab}
            type="button"
            role="tab"
            aria-selected={i === tab}
            className={s.tab}
            onClick={() => {
              setTab(i);
            }}
          >
            {c.tab}
          </button>
        ))}
      </div>
      <p className={s.where}>{pane.where}</p>
      <CodeBlock code={pane.code} name={`connect ${pane.tab}`} />
    </>
  );
}
