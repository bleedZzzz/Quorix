"use client";

import * as React from "react";
import { KnowledgeGap } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Lightbulb,
  Sparkles,
  ArrowRight,
  FlaskConical,
  Target,
  FileQuestion,
  HelpCircle,
} from "lucide-react";

const INITIAL_GAPS: KnowledgeGap[] = [
  {
    id: "gap-1",
    title: "Test-Time Inference Compute Trade-offs in Dense RAG",
    domain: "Retrieval-Augmented Generation",
    unexplored_area: "Existing literature predominantly evaluates top-k document retrieval under fixed latency budgets, neglecting dynamic inference-time compute scaling (e.g., iterative re-ranking or chain-of-thought verification on retrieved passages).",
    evidence_summary: "Lewis et al. (2020) and Touvron et al. (2023) focus on static passage k values without adaptive reasoning depth over noisy retrieval chunks.",
    proposed_hypothesis: "Allocating adaptive test-time compute to passage verification before synthesis will reduce retrieval-induced hallucinations by >35% on low-overlap questions.",
    confidence: "High",
  },
  {
    id: "gap-2",
    title: "Cross-Lingual Knowledge Transfer Degradation under Selective Attention",
    domain: "Transformer Architecture & Polyglot Modeling",
    unexplored_area: "Self-attention attention map dispersion across typologically distinct scripts (e.g., Latin vs. Devanagari or Logographic) under limited pre-training tokens.",
    evidence_summary: "Vaswani et al. (2017) demonstrated SOTA on English-German/French, leaving syntactic alignment across non-Indo-European languages unmeasured in zero-shot transfer.",
    proposed_hypothesis: "Language-specific routing tokens in multi-head attention preserve syntactic heads from semantic collapse in low-resource bilingual transfer.",
    confidence: "Medium",
  },
];

export default function GapsPage() {
  const [gaps, setGaps] = React.useState<KnowledgeGap[]>(INITIAL_GAPS);
  const [isScanning, setIsScanning] = React.useState(false);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      const newGap: KnowledgeGap = {
        id: `gap-${Date.now()}`,
        title: "Sparse vs. Dense Embedding Drift Under Rapid Domain Adaptation",
        domain: "Vector Retrieval & Knowledge Stores",
        unexplored_area: "Dense bi-encoders exhibit catastrophic out-of-distribution drift when deployed on emerging medical / legal corpora without continuous re-indexing.",
        evidence_summary: "Audited across 4 papers in workspace library; semantic representations collapse on unrepresented specialized jargon.",
        proposed_hypothesis: "Hybrid BM25 reciprocal rank fusion anchors high-dimensional vector representations against out-of-vocabulary degradation.",
        confidence: "High",
      };
      setGaps([newGap, ...gaps]);
      setIsScanning(false);
    }, 1500);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Research Gap Finder
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Auditing contradictions, unaddressed questions, and under-explored frontiers in your literature.
          </p>
        </div>

        <Button variant="primary" size="md" onClick={handleScan} disabled={isScanning}>
          <Sparkles size={16} />
          {isScanning ? "Auditing Literature..." : "Scan for New Gaps"}
        </Button>
      </div>

      {/* Gaps List */}
      <div className="space-y-4">
        {gaps.map((gap) => (
          <Card key={gap.id} className="border-border hover:border-accent/40 transition-colors">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-warning-muted flex items-center justify-center text-warning">
                    <Lightbulb size={16} />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-text-primary">{gap.title}</h3>
                    <p className="text-xs text-text-muted">{gap.domain}</p>
                  </div>
                </div>
                <Badge variant={gap.confidence === "High" ? "accent" : "muted"}>
                  {gap.confidence} Priority
                </Badge>
              </div>

              {/* Unexplored Area */}
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                  <FileQuestion size={13} className="text-text-muted" />
                  Identified Research Gap
                </p>
                <p className="text-xs text-text-secondary leading-relaxed bg-surface-muted/50 p-3 rounded-lg border border-border-muted">
                  {gap.unexplored_area}
                </p>
              </div>

              {/* Proposed Hypothesis */}
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-accent-text flex items-center gap-1.5">
                  <FlaskConical size={13} className="text-accent" />
                  Proposed Testable Hypothesis
                </p>
                <p className="text-xs text-text-primary leading-relaxed bg-accent-muted/20 p-3 rounded-lg border border-accent/20 font-medium">
                  {gap.proposed_hypothesis}
                </p>
              </div>

              {/* Action */}
              <div className="flex items-center justify-between pt-2 border-t border-border-muted text-xs">
                <span className="text-text-muted">Evidence: {gap.evidence_summary}</span>
                <Button variant="secondary" size="sm">
                  Generate Experiment Outline
                  <ArrowRight size={13} className="ml-1" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
