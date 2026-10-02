"use client";

import * as React from "react";
import { INITIAL_PAPERS } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Network,
  Share2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Layers,
  Sparkles,
} from "lucide-react";

export default function GraphPage() {
  const [selectedNode, setSelectedNode] = React.useState<string | null>("p1-vaswani-2017");

  const nodes = [
    { id: "p1-vaswani-2017", label: "Attention Is All You Need", type: "paper", year: 2017, x: 250, y: 150, citations: 114820 },
    { id: "p2-devlin-2018", label: "BERT Pre-training", type: "paper", year: 2018, x: 500, y: 100, citations: 89310 },
    { id: "p3-touvron-2023", label: "Llama 2 Foundation Models", type: "paper", year: 2023, x: 550, y: 280, citations: 14200 },
    { id: "p4-lewis-2020", label: "RAG for NLP Tasks", type: "paper", year: 2020, x: 200, y: 320, citations: 6310 },
    { id: "c-self-attn", label: "Self-Attention Mechanism", type: "concept", x: 380, y: 200 },
    { id: "c-masked-lm", label: "Masked LM Pre-training", type: "concept", x: 420, y: 80 },
    { id: "c-dense-retrieval", label: "Dense Passage Retrieval", type: "concept", x: 140, y: 240 },
  ];

  const edges = [
    { from: "p1-vaswani-2017", to: "c-self-attn" },
    { from: "p2-devlin-2018", to: "c-self-attn" },
    { from: "p3-touvron-2023", to: "c-self-attn" },
    { from: "p2-devlin-2018", to: "c-masked-lm" },
    { from: "p4-lewis-2020", to: "c-dense-retrieval" },
    { from: "p1-vaswani-2017", to: "p2-devlin-2018" },
    { from: "p1-vaswani-2017", to: "p3-touvron-2023" },
    { from: "p1-vaswani-2017", to: "p4-lewis-2020" },
  ];

  const activePaper = INITIAL_PAPERS.find((p) => p.id === selectedNode);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Citation & Concept Graph
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Visualizing topological connections, citation influence, and concept co-occurrence across your library.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="accent">Interactive Canvas</Badge>
          <Button variant="secondary" size="sm">
            <Maximize2 size={14} />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Interactive SVG Graph Canvas */}
        <div className="lg:col-span-2 rounded-xl border border-border-muted bg-surface-muted/40 p-4 relative overflow-hidden h-[480px] flex items-center justify-center shadow-inner">
          <svg className="w-full h-full" viewBox="0 0 700 400">
            {edges.map((e, idx) => {
              const src = nodes.find((n) => n.id === e.from);
              const dst = nodes.find((n) => n.id === e.to);
              if (!src || !dst) return null;
              return (
                <line
                  key={idx}
                  x1={src.x}
                  y1={src.y}
                  x2={dst.x}
                  y2={dst.y}
                  stroke="rgba(255, 255, 255, 0.15)"
                  strokeWidth="1.5"
                  strokeDasharray={src.type === "concept" || dst.type === "concept" ? "3,3" : undefined}
                />
              );
            })}

            {nodes.map((n) => {
              const isSelected = selectedNode === n.id;
              const isPaper = n.type === "paper";
              return (
                <g
                  key={n.id}
                  className="cursor-pointer transition-transform duration-200"
                  onClick={() => setSelectedNode(n.id)}
                >
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={isPaper ? 22 : 14}
                    fill={isPaper ? (isSelected ? "#3b82f6" : "#1e1e24") : "#10b981"}
                    stroke={isSelected ? "#93bbfd" : isPaper ? "#3b82f6" : "#34d399"}
                    strokeWidth={isSelected ? 3 : 1.5}
                    className="hover:scale-110 transition-transform"
                  />
                  <text
                    x={n.x}
                    y={n.y + (isPaper ? 34 : 24)}
                    textAnchor="middle"
                    fill={isSelected ? "#ffffff" : "#a1a1aa"}
                    fontSize="11"
                    fontWeight={isSelected ? "600" : "400"}
                    className="select-none pointer-events-none"
                  >
                    {n.label}
                  </text>
                </g>
              );
            })}
          </svg>

          <div className="absolute bottom-4 right-4 flex items-center gap-1 bg-surface border border-border rounded-lg p-1 shadow-md">
            <button className="p-1.5 rounded hover:bg-surface-hover text-text-muted hover:text-text-primary">
              <ZoomIn size={14} />
            </button>
            <button className="p-1.5 rounded hover:bg-surface-hover text-text-muted hover:text-text-primary">
              <ZoomOut size={14} />
            </button>
          </div>
        </div>

        <Card className="border-border bg-surface">
          <CardContent className="p-5 space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Node Inspector
            </h3>

            {activePaper ? (
              <div className="space-y-3">
                <Badge variant="accent">Paper Node</Badge>
                <h4 className="text-base font-semibold text-text-primary">
                  {activePaper.title}
                </h4>
                <p className="text-xs text-text-secondary">
                  {activePaper.authors.join(", ")}
                </p>
                <div className="p-3 rounded-lg bg-surface-muted border border-border-muted text-xs text-text-muted leading-relaxed font-serif">
                  {activePaper.abstract}
                </div>
                <div className="flex items-center justify-between text-xs text-text-muted pt-2 border-t border-border-muted">
                  <span>Year: <strong className="text-text-primary">{activePaper.year}</strong></span>
                  <span>Citations: <strong className="text-accent">{activePaper.citation_count?.toLocaleString()}</strong></span>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Badge variant="success">Concept Node</Badge>
                <h4 className="text-base font-semibold text-text-primary">
                  {nodes.find((n) => n.id === selectedNode)?.label || "Select a Node"}
                </h4>
                <p className="text-xs text-text-muted">
                  Mathematical formulation connecting sequence transductions, multi-head projections, and dense passage queries.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
