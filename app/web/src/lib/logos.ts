import { readFileSync } from "node:fs";
import { join } from "node:path";

// Width of a logo drawn at a given height, from its SVG viewBox. Read at build time; server components only.
export function logoWidth(file: string, height: number): number {
  const svg = readFileSync(join(process.cwd(), "public", "agents", `${file}.svg`), "utf8");
  const vb = /viewBox="([\d.\s-]+)"/.exec(svg)?.[1].trim().split(/\s+/).map(Number);
  if (!vb || vb.length !== 4) throw new Error(`no viewBox in ${file}.svg`);
  return Math.round((height * vb[2]) / vb[3]);
}
