import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

function Spinner({ className, size = 16 }: { className?: string; size?: number }) {
  return (
    <Loader2
      className={cn("animate-spin text-text-muted", className)}
      style={{ width: size, height: size }}
      aria-hidden="true"
    />
  );
}

export { Spinner };
