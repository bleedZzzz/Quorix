"use client";

import * as React from "react";
import { Citation } from "@/lib/api";
import { X, ExternalLink, CheckCircle2, Bookmark, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface EvidenceDrawerProps {
  citation: Citation | null;
  onClose: () => void;
}

export function EvidenceDrawer({ citation, onClose }: EvidenceDrawerProps) {
  if (!citation) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[420px] bg-surface border-l border-border shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-muted bg-surface-muted/40">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-accent-muted flex items-center justify-center text-accent text-xs font-mono font-bold">
            [{citation.number}]
          </div>
          <div>
            <h3 className="text-sm font-semibold text-text-primary">Evidence Inspector</h3>
            <p className="text-[11px] text-text-muted">Grounded retrieval passage</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-text-muted hover:bg-surface-hover hover:text-text-primary transition-colors"
        >
          <X size={16} />
        </button>
      </div>

      {/* Drawer Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Source Paper Card */}
        <div className="p-3.5 rounded-lg bg-surface-elevated/70 border border-border-muted space-y-2">
          <div className="flex items-center justify-between">
            <Badge variant="accent">Source Paper</Badge>
            <span className="text-[11px] text-success flex items-center gap-1 font-medium">
              <CheckCircle2 size={12} />
              {Math.round(citation.confidence_score * 100)}% Confidence
            </span>
          </div>
          <h4 className="text-sm font-medium text-text-primary leading-snug">
            {citation.paper_title}
          </h4>
          <div className="flex items-center gap-3 text-xs text-text-muted pt-1">
            <span>Page <strong className="text-text-primary">{citation.page_number}</strong></span>
            {citation.section_title && (
              <>
                <span>•</span>
                <span>Section: <strong className="text-text-primary">{citation.section_title}</strong></span>
              </>
            )}
          </div>
        </div>

        {/* Verbatim Excerpt */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-text-muted">
              Verbatim Text Chunk
            </span>
            <span className="text-[10px] text-text-muted font-mono">
              chunk_id: {citation.chunk_id.slice(0, 8)}...
            </span>
          </div>
          <div className="p-4 rounded-lg bg-surface-muted border border-border text-sm leading-relaxed text-text-primary relative group">
            <p className="italic font-serif text-[13.5px] text-text-primary/95 selection:bg-accent-muted selection:text-accent-text">
              &ldquo;{citation.exact_text}&rdquo;
            </p>
          </div>
        </div>

        {/* Audit Context */}
        <div className="p-3 rounded-lg bg-surface-hover/50 border border-border-muted space-y-1.5 text-xs text-text-secondary">
          <p className="font-medium text-text-primary">Grounding Verification</p>
          <p>
            This chunk was extracted by PyMuPDF semantic chunking and scored top rank in Reciprocal Rank Fusion (Dense Qdrant + Lexical BM25).
          </p>
        </div>
      </div>

      {/* Drawer Footer Actions */}
      <div className="p-4 border-t border-border-muted bg-surface-muted/30 flex items-center gap-2">
        <Button variant="primary" size="sm" className="flex-1">
          <BookOpen size={14} />
          View in PDF (Page {citation.page_number})
        </Button>
        <Button variant="secondary" size="sm">
          <Bookmark size={14} />
        </Button>
      </div>
    </div>
  );
}
