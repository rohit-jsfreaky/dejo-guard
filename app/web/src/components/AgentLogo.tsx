import Image from "next/image";
import { logoWidth } from "@/lib/logos";

// A LobeHub icon (MIT, @lobehub/icons-static-svg 1.95.1) from public/agents, sized by height. Server only.
export function AgentLogo({ file, height, className }: { file: string; height: number; className?: string }) {
  return (
    <Image
      src={`/agents/${file}.svg`}
      width={logoWidth(file, height)}
      height={height}
      alt=""
      unoptimized
      className={className}
    />
  );
}
