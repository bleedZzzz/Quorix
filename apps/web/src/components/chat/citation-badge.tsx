"use client";

import * as React from "react";
import { Citation } from "@/lib/api";
import { cn } from "@/lib/utils";

interface CitationBadgeProps {
  citation: Citation;
  onSelect: (citation: Citation) => void;
  className?: string;
}

export function CitationBadge({ citation, onSelect, className }: CitationBadgeProps) {
  const [showTooltip, setShowTooltip] = React.useState(false);

  return (
    <span className="relative inline-block mx-0.5 align-baseline">
      <button
        onClick={() => onSelect(citation)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={cn(
          "inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[11px] font-mono font-medium",
          "bg-accent-muted text-accent hover:bg-accent hover:text-white transition-all duration-150",
          "border border-accent/30 cursor-pointer shadow-sm",
          className
        )}
        title={`Citation [${citation.number}]: ${citation.paper_title}, Page ${citation.page_number}`}
      >
        [{citation.number}]
      </button>

      {showTooltip && (
        <div
          className={cn(
            "absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-72 p-3 rounded-lg",
            "bg-surface-elevated border border-border text-left shadow-xl pointer-events-none",
            "animate-in fade-in zoom-in-95 duration-100"
          )}
        >
          <div className="flex items-center justify-between text-[11px] text-text-muted mb-1 font-mono">
            <span className="text-accent font-semibold">[{citation.number}] Page {citation.page_number}</span>
            <span className="text-success font-medium">
              {Math.round(citation.confidence_score * 100)}% match
            </span>
          </div>
          <p className="text-xs font-semibold text-text-primary line-clamp-1 mb-1">
            {citation.paper_title}
          </p>
          <p className="text-[11px] text-text-secondary line-clamp-3 italic bg-surface/60 p-1.5 rounded border border-border-muted font-sans">
            &ldquo;{citation.exact_text}&rdquo;
          </p>
        </div>
      )}
    </span>
  );
}
