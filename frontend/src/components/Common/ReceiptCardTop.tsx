import { cn } from "@/lib/utils";
import { ReactNode } from "react";

export function ReceiptCardTop({
  children,
  className,
  shadow = true,
}: {
  children: React.ReactNode;
  className?: string;
  shadow?: boolean;
}) {
  const teeth = 50;
  const top = Array.from(
    { length: teeth },
    (_, i) => `${(i / teeth) * 100},${i % 2 === 0 ? 2 : 0}`,
  ).join(" ");
  const mask = `url("data:image/svg+xml,<svg viewBox='0 0 100 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'><polygon points='0,2 ${top} 100,2 100,100 0,100' fill='black'/></svg>")`;

  return (
    <div
      style={{
        filter: shadow ? "drop-shadow(0 4px 6px rgba(0,0,0,0.1))" : "none",
      }}
    >
      <div
        className={cn("h-full", className)}
        style={{
          maskImage: mask,
          maskSize: "100% 100%",
          WebkitMaskImage: mask,
          WebkitMaskSize: "100% 100%",
        }}
      >
        {children}
      </div>
    </div>
  );
}
