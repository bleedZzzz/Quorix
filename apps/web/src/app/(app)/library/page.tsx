"use client";

import * as React from "react";
import { fetchPapers, Paper, INITIAL_PAPERS } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Tabs } from "@/components/ui/tabs";
import {
  Upload,
  Search,
  BookOpen,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  Filter,
  Layers,
  Calendar,
  ExternalLink,
  Trash2,
} from "lucide-react";

export default function LibraryPage() {
  const [papers, setPapers] = React.useState<Paper[]>(INITIAL_PAPERS);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("all");
  const [isUploadOpen, setIsUploadOpen] = React.useState(false);
  const [isUploading, setIsUploading] = React.useState(false);
  const [selectedPaper, setSelectedPaper] = React.useState<Paper | null>(null);

  // New paper form state
  const [newTitle, setNewTitle] = React.useState("");
  const [newAuthors, setNewAuthors] = React.useState("");
  const [newAbstract, setNewAbstract] = React.useState("");

  React.useEffect(() => {
    fetchPapers().then((res) => {
      if (res && res.length > 0) setPapers(res);
    });
  }, []);

  const filteredPapers = papers.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.authors.some((a) => a.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus =
      statusFilter === "all" || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsUploading(true);
    setTimeout(() => {
      const added: Paper = {
        id: `paper-${Date.now()}`,
        title: newTitle.trim(),
        authors: newAuthors ? newAuthors.split(",").map((s) => s.trim()) : ["Author et al."],
        year: new Date().getFullYear(),
        abstract: newAbstract.trim() || "User imported document via PDF semantic parser.",
        status: "ready",
        chunks_count: 32,
        citation_count: 0,
        tags: ["Custom Import", "PDF"],
      };
      setPapers([added, ...papers]);
      setIsUploading(false);
      setIsUploadOpen(false);
      setNewTitle("");
      setNewAuthors("");
      setNewAbstract("");
    }, 1200);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header & Primary Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Paper Library</h1>
          <p className="text-sm text-text-muted mt-0.5">
            Indexed academic literature grounded for multi-document agentic retrieval.
          </p>
        </div>
        <Button variant="primary" size="md" onClick={() => setIsUploadOpen(true)}>
          <Upload size={16} />
          Import PDF Paper
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter library by title, author, keyword, or concept..."
            icon={<Search size={16} />}
          />
        </div>
        <div className="flex items-center gap-1.5 self-start sm:self-auto">
          {["all", "ready", "ingesting"].map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                statusFilter === filter
                  ? "bg-accent-muted text-accent font-semibold"
                  : "bg-surface text-text-muted hover:text-text-primary border border-border-muted"
              }`}
            >
              {filter} {filter === "all" ? `(${papers.length})` : ""}
            </button>
          ))}
        </div>
      </div>

      {/* Paper Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredPapers.map((paper) => (
          <Card
            key={paper.id}
            variant="interactive"
            className="flex flex-col justify-between cursor-pointer group"
            onClick={() => setSelectedPaper(paper)}
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  {paper.status === "ready" && (
                    <Badge variant="success">
                      <CheckCircle2 size={12} className="mr-1" />
                      Ready
                    </Badge>
                  )}
                  {paper.status === "ingesting" && (
                    <Badge variant="warning">
                      <Clock size={12} className="mr-1 animate-spin" />
                      Processing
                    </Badge>
                  )}
                  {paper.year && (
                    <span className="text-xs text-text-muted flex items-center gap-1">
                      <Calendar size={12} />
                      {paper.year}
                    </span>
                  )}
                </div>
                <span className="text-xs text-text-muted flex items-center gap-1 font-mono">
                  <Layers size={12} />
                  {paper.chunks_count} chunks
                </span>
              </div>

              <div>
                <h3 className="text-base font-semibold text-text-primary group-hover:text-accent transition-colors line-clamp-2">
                  {paper.title}
                </h3>
                <p className="text-xs text-text-secondary mt-1 line-clamp-1">
                  {paper.authors.join(", ")}
                </p>
              </div>

              <p className="text-xs text-text-muted line-clamp-2 leading-relaxed">
                {paper.abstract}
              </p>

              {paper.tags && paper.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {paper.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded text-[11px] bg-surface-elevated text-text-muted border border-border-muted"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Upload Paper Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title="Import Research Paper"
        description="Upload a PDF file to run through Quorix's section detector and semantic chunker."
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4 pt-2">
          {/* Drag & Drop Area */}
          <div className="border-2 border-dashed border-border hover:border-accent/60 rounded-xl p-6 text-center transition-colors bg-surface-muted/30 cursor-pointer">
            <Upload size={24} className="mx-auto text-accent mb-2" />
            <p className="text-sm font-medium text-text-primary">
              Drag and drop paper PDF here, or browse
            </p>
            <p className="text-xs text-text-muted mt-1">
              Supports standard arXiv, IEEE, ACM, Nature, and OpenReview PDFs (max 50MB)
            </p>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Paper Title</label>
            <Input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Scaling Laws for Neural Language Models"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Authors (comma separated)</label>
            <Input
              value={newAuthors}
              onChange={(e) => setNewAuthors(e.target.value)}
              placeholder="e.g. Jared Kaplan, Sam McCandlish, Tom Henighan"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Abstract (optional)</label>
            <textarea
              value={newAbstract}
              onChange={(e) => setNewAbstract(e.target.value)}
              placeholder="Paste paper abstract if available..."
              className="w-full rounded-lg bg-surface border border-border p-2.5 text-xs text-text-primary focus:outline-none focus:border-accent h-20"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setIsUploadOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isUploading}>
              {isUploading ? "Chunking & Embedding..." : "Ingest & Index"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Selected Paper Details Drawer / Modal */}
      {selectedPaper && (
        <Modal
          isOpen={!!selectedPaper}
          onClose={() => setSelectedPaper(null)}
          title={selectedPaper.title}
          description={`Published ${selectedPaper.year || "Unknown"} • ${selectedPaper.chunks_count} semantic chunks indexed`}
        >
          <div className="space-y-4 pt-2">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-text-muted">Authors</p>
              <p className="text-sm text-text-secondary mt-0.5">{selectedPaper.authors.join(", ")}</p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-text-muted">Abstract</p>
              <p className="text-xs text-text-primary leading-relaxed mt-1 p-3 rounded-lg bg-surface-muted border border-border-muted font-serif">
                {selectedPaper.abstract}
              </p>
            </div>

            {selectedPaper.doi && (
              <div className="flex items-center justify-between text-xs text-text-muted pt-2 border-t border-border-muted">
                <span>DOI: <strong className="text-text-secondary font-mono">{selectedPaper.doi}</strong></span>
                {selectedPaper.citation_count !== undefined && (
                  <span>{selectedPaper.citation_count.toLocaleString()} citations</span>
                )}
              </div>
            )}

            <div className="flex items-center gap-2 pt-3">
              <Button variant="primary" size="sm" className="flex-1">
                <BookOpen size={14} />
                Ask Questions on this Paper
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  setPapers(papers.filter((p) => p.id !== selectedPaper.id));
                  setSelectedPaper(null);
                }}
              >
                <Trash2 size={14} />
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
