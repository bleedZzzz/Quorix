"use client";

import * as React from "react";
import { AgentStep } from "@/lib/api";
import { CheckCircle2, Loader2, Circle, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentProgressProps {
  steps: AgentStep[];
  defaultOpen?: boolean;
}

export function AgentProgress({ steps, defaultOpen = false }: AgentProgressProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  if (!steps || steps.length === 0) return null;

  const inProgressStep = steps.find((s) => s.status === "in_progress");
  const isAllComplete = steps.every((s) => s.status === "completed");

  return (
    <div className="rounded-lg border border-border-muted bg-surface-elevated/40 text-xs overflow-hidden my-3">
      {/* Header / Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-2.5 px-3 hover:bg-surface-hover/50 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          {isAllComplete ? (
            <CheckCircle2 size={14} className="text-success shrink-0" />
          ) : (
            <Loader2 size={14} className="text-accent animate-spin shrink-0" />
          )}
          <span className="font-medium text-text-primary">
            {isAllComplete
              ? `Evidence-first pipeline completed (${steps.length} stages)`
              : inProgressStep
              ? `${inProgressStep.name}...`
              : "Agent reasoning in progress..."}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-text-muted">
          <span className="text-[11px]">{isOpen ? "Hide steps" : "View steps"}</span>
          {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </button>

      {/* Expanded Step List */}
      {isOpen && (
        <div className="p-3 pt-1 space-y-2 border-t border-border-muted/50 bg-surface/50 font-mono text-[11px]">
          {steps.map((step, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="mt-0.5 shrink-0">
                {step.status === "completed" && (
                  <CheckCircle2 size={13} className="text-success" />
                )}
                {step.status === "in_progress" && (
                  <Loader2 size={13} className="text-accent animate-spin" />
                )}
                {step.status === "pending" && (
                  <Circle size={13} className="text-text-muted opacity-40" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <span
                  className={cn(
                    step.status === "completed"
                      ? "text-text-secondary"
                      : step.status === "in_progress"
                      ? "text-accent font-medium"
                      : "text-text-muted"
                  )}
                >
                  {step.name}
                </span>
                {step.detail && (
                  <span className="text-text-muted ml-2 font-sans text-[10.5px]">
                    — {step.detail}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
