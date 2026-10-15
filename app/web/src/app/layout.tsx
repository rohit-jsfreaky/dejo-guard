import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Motion } from "@/components/Motion";
import { DESCRIPTION, SITE_URL } from "@/lib/content";
import "./globals.css";

const geist = Geist({ variable: "--font-geist", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

const TITLE = "Dejo Guard: your agent clicks, ArmorIQ decides";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  applicationName: "Dejo Guard",
  keywords: ["ArmorIQ", "MCP", "browser agent", "AI agent security", "Claude Code", "intent drift", "prompt injection"],
  alternates: { canonical: "/" },
  openGraph: { type: "website", url: "/", siteName: "Dejo Guard", title: TITLE, description: DESCRIPTION },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
};

export const viewport: Viewport = { themeColor: "#ffffff" };

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <body>
        {children}
        <Motion />
      </body>
    </html>
  );
}
