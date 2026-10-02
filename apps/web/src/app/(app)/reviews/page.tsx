"use client";

import * as React from "react";
import { INITIAL_PAPERS } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Sparkles,
  Download,
  Share2,
  BookOpen,
  CheckCircle2,
  Clock,
  Printer,
} from "lucide-react";

export default function ReviewsPage() {
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [topic, setTopic] = React.useState(
    "Evolution of Attention Mechanisms: From Recurrent Neural Networks to Dense RAG Architectures"
  );

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Literature Reviews
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Grounded, multi-paper synthesis with verbatim citations and methodology comparisons.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm">
            <Download size={14} />
            Export Markdown
          </Button>
          <Button variant="primary" size="sm">
            <Sparkles size={14} />
            New Review
          </Button>
        </div>
      </div>

      <Card className="border-border bg-surface shadow-md">
        <CardContent className="p-6 sm:p-10 space-y-8 font-serif leading-relaxed text-text-secondary text-sm">
          {/* Paper Title Header */}
          <div className="font-sans border-b border-border-muted pb-6 space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="accent">Automated Synthesis</Badge>
              <span className="text-xs text-text-muted">4 Papers Cited • Grounded Passages</span>
            </div>
            <h2 className="text-2xl font-bold text-text-primary font-sans leading-tight">
              {topic}
            </h2>
            <p className="text-xs text-text-muted">
              Synthesized by Quorix Agentic Engine • Evidence-First Grounding
            </p>
          </div>

          <section className="space-y-2">
            <h3 className="font-sans text-sm font-semibold uppercase tracking-wider text-text-primary">
              1. Abstract
            </h3>
            <p>
              The transition from sequential recurrent computation to non-local attention networks represents a foundational paradigm shift in deep representation learning. While recurrent networks suffered from vanishing gradient pathologies and strict temporal dependency barriers (Vaswani et al., 2017), self-attention architectures parallelized training operations across sequence dimensions. Subsequent developments extended these representations through bidirectional masked pretraining (Devlin et al., 2018) and external non-parametric knowledge retrieval (Lewis et al., 2020), culminating in modern decoder-only language model families (Touvron et al., 2023).
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="font-sans text-sm font-semibold uppercase tracking-wider text-text-primary">
              2. Architectural Foundations: Recurrence vs. Attention
            </h3>
            <p>
              Traditional recurrent neural networks compute representations by sequentially propagating an internal hidden state:
            </p>
            <div className="p-3 my-2 bg-surface-muted border border-border-muted rounded-md text-xs font-mono text-center text-text-primary">
              h_t = f(h_(t-1), x_t)
            </div>
            <p>
              As established by Vaswani et al. (2017), this formulation introduces an $O(N)$ sequential operations bottleneck. By substituting recurrence with Scaled Dot-Product Attention:
            </p>
            <div className="p-3 my-2 bg-surface-muted border border-border-muted rounded-md text-xs font-mono text-center text-text-primary">
              Attention(Q, K, V) = softmax((Q K^T) / sqrt(d_k)) V
            </div>
            <p>
              the model connects all pairs of positions in $O(1)$ operations, facilitating parallel tensor computation across high-throughput accelerator hardware.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="font-sans text-sm font-semibold uppercase tracking-wider text-text-primary">
              3. Non-Parametric Memory and RAG
            </h3>
            <p>
              Despite the expressive capacity of pure parametric models, factual hallucinations and parametric obsolescence remain acute vulnerabilities. Lewis et al. (2020) demonstrated that coupling a pre-trained sequence-to-sequence model with a dense passage retriever (DPR) enables dynamic factual grounding without weight modification. The hybrid integration of dense vector similarity with sparse lexical scoring (BM25) provides the robust dual-retrieval backbone employed in contemporary academic research systems.
            </p>
          </section>

          <section className="font-sans border-t border-border-muted pt-6 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Cited Publications
            </h3>
            <div className="space-y-2 text-xs">
              {INITIAL_PAPERS.map((paper, idx) => (
                <div key={paper.id} className="flex items-start gap-2 text-text-secondary">
                  <span className="font-mono text-accent">[{idx + 1}]</span>
                  <div>
                    <span className="font-medium text-text-primary">{paper.authors.join(", ")}</span> ({paper.year}).{" "}
                    <span className="italic">{paper.title}</span>. {paper.venue || "arXiv"}.
                  </div>
                </div>
              ))}
            </div>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
