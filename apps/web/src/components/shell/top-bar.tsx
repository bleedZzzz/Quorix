"use client";

import { cn } from "@/lib/utils";
import { Search, User } from "lucide-react";

export function TopBar() {
  return (
    <header
      className={cn(
        "fixed top-0 right-0 z-20 flex items-center justify-between",
        "h-[var(--topbar-height)] bg-surface/80 backdrop-blur-sm",
        "border-b border-border-muted px-4",
        "left-[var(--sidebar-width)]"
      )}
    >
      {/* Search */}
      <button
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-[var(--radius-md)]",
          "bg-surface-muted border border-border-muted",
          "text-sm text-text-muted hover:text-text-secondary hover:border-border",
          "transition-colors cursor-pointer w-64"
        )}
      >
        <Search size={14} />
        <span>Search your research…</span>
        <kbd className="ml-auto text-[10px] text-text-muted bg-surface-elevated px-1.5 py-0.5 rounded-[var(--radius-sm)] border border-border-muted">
          ⌘K
        </kbd>
      </button>

      {/* User */}
      <div className="flex items-center gap-2">
        <button
          className={cn(
            "w-7 h-7 rounded-[var(--radius-full)] bg-surface-elevated",
            "border border-border-muted flex items-center justify-center",
            "hover:border-border transition-colors cursor-pointer"
          )}
        >
          <User size={14} className="text-text-muted" />
        </button>
      </div>
    </header>
  );
}
