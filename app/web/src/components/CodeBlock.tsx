"use client";

import { useState } from "react";
import { CheckIcon, CopyIcon } from "@phosphor-icons/react/dist/ssr";
import s from "./GetStarted.module.css";

// Smithery's code block: light box, 1px border, mono 12.5px, a copy button top right. Copies the code, never the note.
export function CodeBlock({ code, note, name }: { code: string; note?: string; name: string }) {
  const [ok, setOk] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
    } catch {
      return;
    }
    setOk(true);
    setTimeout(() => setOk(false), 1400);
  }

  return (
    <div className={s.cb}>
      <pre>
        {code}
        {note && <span className={s.cm}> {note}</span>}
      </pre>
      <button type="button" className={s.cp} aria-label={`Copy ${name}`} onClick={copy} data-ok={ok || undefined}>
        {ok ? <CheckIcon size={15} /> : <CopyIcon size={15} />}
      </button>
    </div>
  );
}
