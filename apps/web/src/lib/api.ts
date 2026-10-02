// API client and types

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue?: string;
  abstract: string;
  doi?: string;
  citation_count?: number;
  status: "ready" | "ingesting" | "queued" | "failed";
  chunks_count: number;
  tags?: string[];
  pdf_url?: string;
}

export interface Citation {
  id: string;
  number: number;
  chunk_id: string;
  paper_id: string;
  paper_title: string;
  page_number: number;
  section_title?: string;
  exact_text: string;
  confidence_score: number;
}

export interface Claim {
  id: string;
  statement: string;
  citation_ids: string[];
  verification_status: "verified" | "partial" | "extrapolated";
}

export interface AgentStep {
  name: string;
  status: "completed" | "in_progress" | "pending";
  detail?: string;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  agent_steps?: AgentStep[];
  claims?: Claim[];
  citations?: Citation[];
  knowledge_audit?: {
    sufficient: boolean;
    missing_aspects?: string[];
  };
}

export interface KnowledgeGap {
  id: string;
  title: string;
  domain: string;
  unexplored_area: string;
  evidence_summary: string;
  proposed_hypothesis: string;
  confidence: "High" | "Medium" | "Exploratory";
}

export interface ComparisonDimension {
  dimension: string;
  values: Record<string, string>; // paper_id -> summary string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const INITIAL_PAPERS: Paper[] = [
  {
    id: "p1-vaswani-2017",
    title: "Attention Is All You Need",
    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
    year: 2017,
    venue: "NeurIPS 2017",
    abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer, a model architecture eschewing recurrence and entirely relying on an attention mechanism to draw global dependencies between input and output.",
    doi: "10.48550/arXiv.1706.03762",
    citation_count: 114820,
    status: "ready",
    chunks_count: 48,
    tags: ["Transformers", "Attention", "NLP", "Deep Learning"],
  },
  {
    id: "p2-devlin-2018",
    title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
    year: 2018,
    venue: "NAACL-HLT 2019",
    abstract: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text.",
    doi: "10.48550/arXiv.1810.04805",
    citation_count: 89310,
    status: "ready",
    chunks_count: 56,
    tags: ["Pretraining", "Encoders", "Masked LM"],
  },
  {
    id: "p3-touvron-2023",
    title: "Llama 2: Open Foundation and Fine-Tuned Chat Models",
    authors: ["Hugo Touvron", "Louis Martin", "Kevin Stone", "Peter Albert", "Amjad Almahairi", "Yasmine Babaei"],
    year: 2023,
    venue: "Meta AI Technical Report",
    abstract: "In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7B to 70B parameters. Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases.",
    doi: "10.48550/arXiv.2307.09288",
    citation_count: 14200,
    status: "ready",
    chunks_count: 72,
    tags: ["LLMs", "RLHF", "Safety Alignment"],
  },
  {
    id: "p4-lewis-2020",
    title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
    authors: ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus", "Fabio Petroni", "Vladimir Karpukhin", "Naman Goyal"],
    year: 2020,
    venue: "NeurIPS 2020",
    abstract: "Large pre-trained language models have been shown to store factual knowledge in their parameters, yet their ability to access and precisely manipulate knowledge is still limited. We explore general-purpose fine-tuning recipes for retrieval-augmented generation (RAG).",
    doi: "10.48550/arXiv.2005.11401",
    citation_count: 6310,
    status: "ready",
    chunks_count: 42,
    tags: ["RAG", "Dense Retrieval", "Factual Grounding"],
  },
];

export async function fetchPapers(): Promise<Paper[]> {
  try {
    const res = await fetch(`${API_BASE}/papers?page=1&page_size=20`, {
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.items && data.items.length > 0) {
        return data.items.map((p: any) => ({
          id: p.id,
          title: p.title,
          authors: p.authors || ["Unknown Author"],
          year: p.publication_year || new Date().getFullYear(),
          abstract: p.abstract || "No abstract available.",
          doi: p.doi,
          citation_count: p.citation_count || 0,
          status: p.processing_status || "ready",
          chunks_count: p.chunk_count || 0,
          tags: p.topics || ["Academic"],
        }));
      }
    }
  } catch (err) {
    // Graceful fallback to mock data
  }
  return INITIAL_PAPERS;
}

export async function searchSemanticScholar(query: string): Promise<Paper[]> {
  try {
    const res = await fetch(`${API_BASE}/discovery/search?query=${encodeURIComponent(query)}&limit=10`, {
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(4000),
    });
    if (res.ok) {
      const data = await res.json();
      return (data.results || []).map((r: any) => ({
        id: r.paperId || `s2-${Math.random()}`,
        title: r.title,
        authors: (r.authors || []).map((a: any) => a.name || a),
        year: r.year || 2024,
        abstract: r.abstract || "No abstract retrieved.",
        citation_count: r.citationCount || 0,
        status: "ready" as const,
        chunks_count: 0,
        tags: ["Semantic Scholar"],
      }));
    }
  } catch (err) {
    // Return filtered local matches
  }
  return INITIAL_PAPERS.filter(
    (p) =>
      p.title.toLowerCase().includes(query.toLowerCase()) ||
      p.abstract.toLowerCase().includes(query.toLowerCase())
  );
}
