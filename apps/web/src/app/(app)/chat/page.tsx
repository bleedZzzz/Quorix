"use client";

import * as React from "react";
import { Citation, Claim, AgentStep, ChatMessage, INITIAL_PAPERS } from "@/lib/api";
import { CitationBadge } from "@/components/chat/citation-badge";
import { EvidenceDrawer } from "@/components/chat/evidence-drawer";
import { AgentProgress } from "@/components/chat/agent-progress";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  CheckCircle2,
  Paperclip,
  RotateCcw,
  BookOpen,
  Filter,
} from "lucide-react";

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "msg-1",
    role: "assistant",
    content: "Welcome to Quorix Research Chat. I operate strictly under an **evidence-first principle**: every factual statement is grounded in verbatim chunks extracted from your indexed papers, verified by our knowledge auditor, and bound with inspectable citations.",
    timestamp: "Just now",
  },
  {
    id: "msg-2",
    role: "user",
    content: "How does the Transformer model overcome sequential computation bottlenecks compared to recurrent networks?",
    timestamp: "2 mins ago",
  },
  {
    id: "msg-3",
    role: "assistant",
    content: "The Transformer architecture fundamentally dispenses with recurrence and convolutions, relying entirely on self-attention mechanisms to compute representations of input and output without sequential alignment. In recurrent models like LSTMs or GRUs, sequential computation generates hidden states $h_t$ as a function of the previous hidden state $h_{t-1}$, inherently preventing parallelization within training examples. By replacing recurrence with multi-head self-attention, the Transformer connects all positions with a constant number of sequentially executed operations, reducing path length between distant tokens and enabling significant parallelization on modern hardware.",
    timestamp: "1 min ago",
    agent_steps: [
      { name: "Context & Intent Classification", status: "completed", detail: "Factual inquiry identified", timestamp: "1 min ago" },
      { name: "Query Analysis & Decomposition", status: "completed", detail: "Keywords: Transformer, recurrent, sequential, parallelization", timestamp: "1 min ago" },
      { name: "Hybrid Retrieval (Dense + Lexical)", status: "completed", detail: "Found 14 candidate chunks from Vaswani et al.", timestamp: "1 min ago" },
      { name: "Evidence Grading & Sufficiency Audit", status: "completed", detail: "Passed confidence threshold (0.92 score)", timestamp: "1 min ago" },
      { name: "Claim Construction & Citation Binding", status: "completed", detail: "2 claims bound to pages 1 & 2", timestamp: "1 min ago" },
    ],
    claims: [
      {
        id: "c1",
        statement: "The Transformer relies entirely on self-attention mechanisms to compute representations without sequential recurrence.",
        citation_ids: ["cit-1"],
        verification_status: "verified",
      },
      {
        id: "c2",
        statement: "Recurrence inherently precludes parallelization because computation relies on sequential dependency on the previous hidden state.",
        citation_ids: ["cit-2"],
        verification_status: "verified",
      },
    ],
    citations: [
      {
        id: "cit-1",
        number: 1,
        chunk_id: "chunk-vaswani-arch-01",
        paper_id: "p1-vaswani-2017",
        paper_title: "Attention Is All You Need",
        page_number: 1,
        section_title: "Introduction",
        exact_text: "The Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution.",
        confidence_score: 0.94,
      },
      {
        id: "cit-2",
        number: 2,
        chunk_id: "chunk-vaswani-arch-02",
        paper_id: "p1-vaswani-2017",
        paper_title: "Attention Is All You Need",
        page_number: 2,
        section_title: "Background",
        exact_text: "This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples.",
        confidence_score: 0.91,
      },
    ],
  },
];

export default function ChatPage() {
  const [messages, setMessages] = React.useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = React.useState("");
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [selectedCitation, setSelectedCitation] = React.useState<Citation | null>(null);
  const [selectedPaperScope, setSelectedPaperScope] = React.useState<string>("all");
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    const userText = input.trim();
    setInput("");

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: userText,
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);

    // Simulated multi-stage LangGraph Agent stream
    setTimeout(() => {
      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: "assistant",
        content: `Based on an evidence-first audit of your literature scope, the retrieved findings confirm that ${userText.toLowerCase().replace("?", "")} relies heavily on grounded semantic representation. Dense embedding vectors map conceptual semantics while lexical BM25 ensures exact mathematical term matching. The knowledge auditor verified full grounding with no hallucinated claims.`,
        timestamp: "Just now",
        agent_steps: [
          { name: "Context & Scope Resolution", status: "completed", detail: `Scope: ${selectedPaperScope === "all" ? "All Indexed Papers" : selectedPaperScope}`, timestamp: "Just now" },
          { name: "Query Expansion & Semantic Routing", status: "completed", detail: "Rewrote query for dense-vector precision", timestamp: "Just now" },
          { name: "Hybrid Retrieval Execution", status: "completed", detail: "Scored across Qdrant and lexical BM25 index", timestamp: "Just now" },
          { name: "Knowledge Sufficiency Audit", status: "completed", detail: "Evidence grade: 0.93 — Full Grounding", timestamp: "Just now" },
          { name: "Answer Synthesis with Verified Citations", status: "completed", detail: "Synthesized with 1 bound citation", timestamp: "Just now" },
        ],
        claims: [
          {
            id: `clm-${Date.now()}`,
            statement: "Query retrieval utilizes hybrid Reciprocal Rank Fusion of dense and lexical scores.",
            citation_ids: [`cit-${Date.now()}`],
            verification_status: "verified",
          },
        ],
        citations: [
          {
            id: `cit-${Date.now()}`,
            number: 1,
            chunk_id: "chunk-hybrid-rag-01",
            paper_id: "p4-lewis-2020",
            paper_title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            page_number: 3,
            section_title: "Methods",
            exact_text: "Dense retrieval leverages learned vector spaces to capture semantic similarities, while sparse retrieval ensures precision on low-frequency terminology and entity names.",
            confidence_score: 0.93,
          },
        ],
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setIsGenerating(false);
    }, 1800);
  };

  return (
    <div className="flex h-[calc(100vh-var(--topbar-height)-2rem)] relative">
      {/* Main Chat Column */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-2 sm:px-4">
        {/* Chat Header Toolbar */}
        <div className="flex items-center justify-between py-2 border-b border-border-muted shrink-0 mb-3">
          <div className="flex items-center gap-2">
            <Badge variant="accent">Agentic RAG</Badge>
            <span className="text-xs text-text-muted">Evidence-First Active</span>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-text-muted flex items-center gap-1">
              <Filter size={12} />
              Scope:
            </span>
            <select
              value={selectedPaperScope}
              onChange={(e) => setSelectedPaperScope(e.target.value)}
              className="bg-surface border border-border-muted rounded-md text-xs text-text-primary px-2 py-1 focus:outline-none focus:border-accent"
            >
              <option value="all">Entire Workspace Library ({INITIAL_PAPERS.length} papers)</option>
              {INITIAL_PAPERS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title.slice(0, 32)}...
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto space-y-5 pr-1 pb-4">
          {messages.map((message) => {
            const isUser = message.role === "user";
            return (
              <div
                key={message.id}
                className={`flex gap-3 text-sm ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot size={16} className="text-accent" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-xl p-4 ${
                    isUser
                      ? "bg-accent text-white ml-12 rounded-tr-sm shadow-md"
                      : "bg-surface-elevated/80 border border-border-muted rounded-tl-sm shadow-sm space-y-3"
                  }`}
                >
                  {/* Assistant reasoning stepper */}
                  {!isUser && message.agent_steps && (
                    <AgentProgress steps={message.agent_steps} defaultOpen={false} />
                  )}

                  {/* Message Text with interactive citation badges */}
                  <div className="leading-relaxed text-text-primary whitespace-pre-wrap">
                    {message.content}
                    {message.citations && message.citations.length > 0 && (
                      <span className="inline-block ml-1">
                        {message.citations.map((c) => (
                          <CitationBadge
                            key={c.id}
                            citation={c}
                            onSelect={setSelectedCitation}
                          />
                        ))}
                      </span>
                    )}
                  </div>

                  {/* Claims verification footer */}
                  {!isUser && message.claims && message.claims.length > 0 && (
                    <div className="pt-2 border-t border-border-muted/60 flex items-center justify-between text-xs text-text-muted">
                      <span className="flex items-center gap-1 text-success font-medium text-[11px]">
                        <ShieldCheck size={13} />
                        {message.claims.length} Claim{message.claims.length > 1 ? "s" : ""} Grounded
                      </span>
                      <span className="text-[11px] text-text-muted">
                        Click citations to inspect source PDF excerpts
                      </span>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-surface-elevated border border-border-muted flex items-center justify-center shrink-0 mt-0.5">
                    <User size={16} className="text-text-secondary" />
                  </div>
                )}
              </div>
            );
          })}

          {isGenerating && (
            <div className="flex gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-accent" />
              </div>
              <div className="rounded-xl p-4 bg-surface-elevated/80 border border-border-muted rounded-tl-sm w-full max-w-lg space-y-2">
                <AgentProgress
                  steps={[
                    { name: "Query Analysis & Intent Classifier", status: "completed", timestamp: "Just now" },
                    { name: "Hybrid Retrieval (Qdrant & BM25)", status: "in_progress", timestamp: "Just now" },
                    { name: "Knowledge Auditor & Citation Binder", status: "pending", timestamp: "Pending" },
                  ]}
                  defaultOpen={true}
                />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form & Suggestions */}
        <div className="shrink-0 pt-2 border-t border-border-muted space-y-2 bg-bg/80 backdrop-blur-md">
          {/* Quick Prompts */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            <span className="text-text-muted shrink-0 text-[11px]">Suggested:</span>
            {[
              "How does self-attention operate in Transformers?",
              "What are the primary contributions of BERT?",
              "Explain how RAG combines dense and lexical search",
            ].map((p, idx) => (
              <button
                key={idx}
                onClick={() => setInput(p)}
                className="px-2.5 py-1 rounded-full bg-surface-elevated hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border-muted shrink-0 transition-colors text-[11px]"
              >
                {p}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask an evidence-first research question across your papers..."
              disabled={isGenerating}
              className="w-full bg-surface border border-border hover:border-border-focus focus:border-accent rounded-xl py-3 pl-4 pr-24 text-sm text-text-primary placeholder:text-text-muted focus:outline-none transition-all shadow-sm"
            />
            <div className="absolute right-2 flex items-center gap-1.5">
              <Button
                variant="primary"
                size="sm"
                type="submit"
                disabled={!input.trim() || isGenerating}
                className="h-8 px-3"
              >
                <Send size={14} />
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Side Evidence Inspector Drawer */}
      <EvidenceDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}
