"use client";

import * as React from "react";
import { searchSemanticScholar, Paper, INITIAL_PAPERS } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  BookPlus,
  Check,
  Calendar,
  ExternalLink,
  Sparkles,
  TrendingUp,
  FileText,
} from "lucide-react";

export default function DiscoverPage() {
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<Paper[]>(INITIAL_PAPERS);
  const [isSearching, setIsSearching] = React.useState(false);
  const [importedIds, setImportedIds] = React.useState<Set<string>>(new Set());

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    const data = await searchSemanticScholar(query);
    setResults(data);
    setIsSearching(false);
  };

  const toggleImport = (paperId: string) => {
    const next = new Set(importedIds);
    if (next.has(paperId)) next.delete(paperId);
    else next.add(paperId);
    setImportedIds(next);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Discover Academic Papers</h1>
        <p className="text-sm text-text-muted mt-1">
          Search over 200M+ research papers across Semantic Scholar, arXiv, and CrossRef.
        </p>
      </div>

      {/* Search Input */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by topic, paper title, author, or DOI (e.g., 'Agentic RAG' or 'Transformers')..."
            icon={<Search size={16} />}
          />
        </div>
        <Button variant="primary" type="submit" disabled={isSearching}>
          {isSearching ? "Searching..." : "Search"}
        </Button>
      </form>

      {/* Suggested Trending Topics */}
      <div className="flex items-center gap-2 overflow-x-auto text-xs pb-1">
        <span className="text-text-muted flex items-center gap-1 shrink-0">
          <TrendingUp size={13} />
          Trending:
        </span>
        {[
          "Mechanistic Interpretability",
          "Test-Time Compute Scaling",
          "Dense Retrieval RAG",
          "State Space Models Mamba",
          "Synthetic Data Alignment",
        ].map((topic) => (
          <button
            key={topic}
            onClick={() => {
              setQuery(topic);
              setIsSearching(true);
              searchSemanticScholar(topic).then((res) => {
                setResults(res);
                setIsSearching(false);
              });
            }}
            className="px-2.5 py-1 rounded-full bg-surface-elevated hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border-muted shrink-0 transition-colors"
          >
            {topic}
          </button>
        ))}
      </div>

      {/* Results List */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between text-xs text-text-muted pb-1 border-b border-border-muted">
          <span>Found {results.length} relevant publications</span>
          <span>Sources: Semantic Scholar & arXiv</span>
        </div>

        {results.map((paper) => {
          const isImported = importedIds.has(paper.id);
          return (
            <Card key={paper.id} className="group hover:border-border transition-colors">
              <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-text-muted flex items-center gap-1">
                      <Calendar size={12} />
                      {paper.year}
                    </span>
                    {paper.citation_count !== undefined && (
                      <Badge variant="muted">
                        {paper.citation_count.toLocaleString()} citations
                      </Badge>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-text-primary group-hover:text-accent transition-colors">
                    {paper.title}
                  </h3>

                  <p className="text-xs text-text-secondary">
                    {paper.authors.join(", ")}
                  </p>

                  <p className="text-xs text-text-muted leading-relaxed line-clamp-2">
                    {paper.abstract}
                  </p>
                </div>

                <div className="shrink-0 self-end sm:self-center">
                  <Button
                    variant={isImported ? "secondary" : "primary"}
                    size="sm"
                    onClick={() => toggleImport(paper.id)}
                    className={isImported ? "text-success border-success/30" : ""}
                  >
                    {isImported ? (
                      <>
                        <Check size={14} className="mr-1 text-success" />
                        In Library
                      </>
                    ) : (
                      <>
                        <BookPlus size={14} className="mr-1" />
                        Import Paper
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
