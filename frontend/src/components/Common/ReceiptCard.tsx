import { type ReactNode, useEffect, useRef, useState } from "react";

interface ReceiptCardProps {
  children: ReactNode;
  className?: string;
  hoverShadow?: boolean;
  toothSize?: number;
  toothHeight?: number;
}

export function ReceiptCard({
  children,
  className = "",
  hoverShadow = false,
  toothSize = 10,
  toothHeight = 3,
  ...props
}: ReceiptCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const update = () => {
      if (ref.current) {
        setDimensions({
          width: ref.current.offsetWidth,
          height: ref.current.offsetHeight,
        });
      }
    };
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const { width, height } = dimensions;
  const rawTeeth = width > 0 ? Math.max(4, Math.round(width / toothSize)) : 20;
  const teeth = rawTeeth % 2 === 0 ? rawTeeth : rawTeeth + 1;

  // This ensures zigzag goes from x=0 to x=width exactly
  const numPoints = teeth * 2 + 1;
  const spacing = width / (numPoints - 1);

  // Pattern: valley(0) -> peak -> valley -> peak -> ... -> valley(width)
  const top = Array.from({ length: numPoints }, (_, i) => {
    const x = i * spacing;
    const y = i % 2 === 0 ? toothHeight : 0;
    return `${x},${y}`;
  }).join(" ");

  const bottom = Array.from({ length: numPoints }, (_, i) => {
    const x = width - i * spacing;
    const y = i % 2 === 0 ? height - toothHeight : height;
    return `${x},${y}`;
  }).join(" ");

  const points = `0,0 ${top} ${width},0 ${width},${height} ${bottom} 0,${height}`;

  const mask =
    width > 0 && height > 0
      ? `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${width} ${height}' preserveAspectRatio='none'%3E%3Cpolygon fill='white' points='${points}'/%3E%3C/svg%3E")`
      : undefined;

  return (
    <div
      className={`${className} ${hoverShadow ? "transition-all duration-300 hover:drop-shadow-xl hover:drop-shadow-black/10 dark:drop-shadow-2xl dark:hover:drop-shadow-zinc-400/5" : ""} drop-shadow-lg drop-shadow-black/10 dark:drop-shadow-xl dark:drop-shadow-zinc-400/5 h-full`}
      {...props}
    >
      <div
        className="h-full"
        ref={ref}
        style={{
          maskImage: mask,
          WebkitMaskImage: mask,
        }}
      >
        {children}
      </div>
    </div>
  );
}
