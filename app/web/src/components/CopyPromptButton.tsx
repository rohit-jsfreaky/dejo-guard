"use client";

import { useState, type ReactNode } from "react";
import { ClipboardTextIcon } from "@phosphor-icons/react/dist/ssr";
import { SETUP_PROMPT } from "@/lib/content";

// Copies the setup prompt; pasted into an agent, it installs Dejo Guard by itself.
export function CopyPromptButton({ className, children }: { className: string; children?: ReactNode }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(SETUP_PROMPT);
    } catch {
      return;
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  return (
    <button type="button" className={className} onClick={copy}>
      <ClipboardTextIcon size={16} />
      <span>{copied ? "Copied" : "Copy setup prompt"}</span>
      {children}
    </button>
  );
}
