"use client";

import * as React from "react";
import { INITIAL_PAPERS, Paper } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  GitCompareArrows,
  CheckCircle2,
  FileSpreadsheet,
  Download,
  Plus,
  X,
  Sparkles,
} from "lucide-react";

interface ComparisonRow {
  dimension: string;
  data: Record<string, string>;
}

const COMPARISON_DIMENSIONS: ComparisonRow[] = [
  {
    dimension: "Core Architecture",
    data: {
      "p1-vaswani-2017": "Encoder-Decoder with Multi-Head Scaled Dot-Product Self-Attention and Sinusoidal Positional Encoding.",
      "p2-devlin-2018": "Multi-layer Bidirectional Transformer Encoder with learned positional embeddings.",
      "p4-lewis-2020": "Hybrid generator-retriever coupling DPR (Dense Passage Retriever) with BART seq2seq generator.",
    },
  },
  {
    dimension: "Training Objective",
    data: {
      "p1-vaswani-2017": "Standard autoregressive cross-entropy sequence-to-sequence loss (WMT English-to-German / French).",
      "p2-devlin-2018": "Masked Language Modeling (MLM 15% masking) + Next Sentence Prediction (NSP).",
      "p4-lewis-2020": "Marginal log-likelihood over top-k retrieved latent documents conditioned on query and generated tokens.",
    },
  },
  {
    dimension: "Key Empirical Findings",
    data: {
      "p1-vaswani-2017": "Established state-of-the-art BLEU score of 28.4 on WMT 2014 En-De at a fraction of recurrent training cost.",
      "p2-devlin-2018": "Outperformed previous models on 11 NLP tasks, including GLUE score of 80.5% and SQuAD 1.1 F1 of 93.2.",
      "p4-lewis-2020": "Substantially reduced hallucinations on Open-domain QA benchmarks (Natural Questions, TriviaQA).",
    },
  },
  {
    dimension: "Key Strengths",
    data: {
      "p1-vaswani-2017": "Eliminates sequential recurrences; constant O(1) path length connecting distant input positions.",
      "p2-devlin-2018": "True bidirectional context representation across both left and right directions simultaneously.",
      "p4-lewis-2020": "Modular factual memory that can be dynamically updated without retraining neural parameters.",
    },
  },
  {
    dimension: "Stated Limitations",
    data: {
      "p1-vaswani-2017": "Quadratic computational and memory complexity O(N²) in self-attention with respect to sequence length.",
      "p2-devlin-2018": "Pretrain-finetune mismatch due to [MASK] tokens; computationally intensive bidirectional representations.",
      "p4-lewis-2020": "Vulnerable to retrieval false positives; requires synchronized indexing of massive passage corpora.",
    },
  },
];

export default function ComparePage() {
  const [selectedPaperIds, setSelectedPaperIds] = React.useState<string[]>([
    "p1-vaswani-2017",
    "p2-devlin-2018",
  ]);

  const selectedPapers = INITIAL_PAPERS.filter((p) =>
    selectedPaperIds.includes(p.id)
  );

  const availablePapers = INITIAL_PAPERS.filter(
    (p) => !selectedPaperIds.includes(p.id)
  );

  const addPaper = (id: string) => {
    if (selectedPaperIds.length < 3) {
      setSelectedPaperIds([...selectedPaperIds, id]);
    }
  };

  const removePaper = (id: string) => {
    if (selectedPaperIds.length > 1) {
      setSelectedPaperIds(selectedPaperIds.filter((pId) => pId !== id));
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Paper Comparison Matrix
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Side-by-side evidence extraction across architectures, methodologies, and limitations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {availablePapers.length > 0 && selectedPaperIds.length < 3 && (
            <select
              onChange={(e) => {
                if (e.target.value) addPaper(e.target.value);
                e.target.value = "";
              }}
              className="bg-surface border border-border rounded-lg text-xs text-text-primary px-3 py-2 focus:outline-none focus:border-accent"
              defaultValue=""
            >
              <option value="" disabled>
                + Add Paper to Matrix...
              </option>
              {availablePapers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          )}

          <Button variant="secondary" size="sm">
            <Download size={14} />
            Export Matrix
          </Button>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto rounded-xl border border-border-muted bg-surface shadow-sm">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border-muted bg-surface-muted/50">
              <th className="p-4 w-48 text-xs font-semibold uppercase tracking-wider text-text-muted">
                Dimension
              </th>
              {selectedPapers.map((paper) => (
                <th key={paper.id} className="p-4 min-w-[280px] max-w-[340px]">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-sm font-semibold text-text-primary line-clamp-1">
                        {paper.title}
                      </h4>
                      <p className="text-xs text-text-muted mt-0.5">
                        {paper.authors[0]} et al. ({paper.year})
                      </p>
                    </div>
                    {selectedPapers.length > 1 && (
                      <button
                        onClick={() => removePaper(paper.id)}
                        className="text-text-muted hover:text-text-primary p-1 rounded hover:bg-surface-hover"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-muted/50 text-xs text-text-secondary">
            {COMPARISON_DIMENSIONS.map((row, idx) => (
              <tr key={idx} className="hover:bg-surface-hover/30 transition-colors">
                <td className="p-4 font-semibold text-text-primary bg-surface-muted/20 align-top">
                  {row.dimension}
                </td>
                {selectedPapers.map((paper) => (
                  <td key={paper.id} className="p-4 leading-relaxed align-top">
                    {row.data[paper.id] || "Data synthesis in progress..."}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
