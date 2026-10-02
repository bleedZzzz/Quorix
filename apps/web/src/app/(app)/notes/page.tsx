"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import {
  StickyNote,
  Plus,
  Trash2,
  Calendar,
  Tag,
  BookOpen,
  Search,
} from "lucide-react";

interface Note {
  id: string;
  title: string;
  content: string;
  paper_title?: string;
  tags: string[];
  updated_at: string;
}

const INITIAL_NOTES: Note[] = [
  {
    id: "n-1",
    title: "Path length comparison in Self-Attention vs RNNs",
    content: "Vaswani Table 1 shows that Maximum Path Length is O(1) for self-attention, compared to O(n) for recurrent layers. This explains why gradient backpropagation over long documents remains stable without vanishing gradients.",
    paper_title: "Attention Is All You Need",
    tags: ["Complexity", "Attention", "Gradients"],
    updated_at: "Today, 14:20",
  },
  {
    id: "n-2",
    title: "Why BERT masked 15% instead of higher ratios",
    content: "Masking too many tokens removes context needed for recovery; masking too few makes pretraining too slow and computationally expensive. 80% [MASK], 10% random, 10% unchanged balances representation learning.",
    paper_title: "BERT: Pre-training of Deep Bidirectional Transformers",
    tags: ["MLM", "Pre-training"],
    updated_at: "Yesterday",
  },
];

export default function NotesPage() {
  const [notes, setNotes] = React.useState<Note[]>(INITIAL_NOTES);
  const [search, setSearch] = React.useState("");
  const [isNewOpen, setIsNewOpen] = React.useState(false);
  const [newTitle, setNewTitle] = React.useState("");
  const [newContent, setNewContent] = React.useState("");
  const [newTags, setNewTags] = React.useState("");

  const filteredNotes = notes.filter(
    (n) =>
      n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.content.toLowerCase().includes(search.toLowerCase()) ||
      n.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
  );

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const added: Note = {
      id: `n-${Date.now()}`,
      title: newTitle.trim(),
      content: newContent.trim(),
      tags: newTags ? newTags.split(",").map((s) => s.trim()) : ["Research"],
      updated_at: "Just now",
    };

    setNotes([added, ...notes]);
    setIsNewOpen(false);
    setNewTitle("");
    setNewContent("");
    setNewTags("");
  };

  const deleteNote = (id: string) => {
    setNotes(notes.filter((n) => n.id !== id));
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Research Notes & Annotations
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Capture mathematical formulations, paper takeaways, and experiment observations.
          </p>
        </div>

        <Button variant="primary" size="md" onClick={() => setIsNewOpen(true)}>
          <Plus size={16} />
          New Note
        </Button>
      </div>

      <div className="relative">
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search notes by keyword, tag, or paper reference..."
          icon={<Search size={16} />}
        />
      </div>

      {/* Notes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredNotes.map((note) => (
          <Card key={note.id} className="border-border hover:border-accent/40 transition-colors flex flex-col justify-between">
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-base font-semibold text-text-primary line-clamp-1">
                  {note.title}
                </h3>
                <button
                  onClick={() => deleteNote(note.id)}
                  className="text-text-muted hover:text-error p-1 rounded transition-colors"
                >
                  <Trash2 size={14} />
                </button>
              </div>

              {note.paper_title && (
                <div className="flex items-center gap-1.5 text-xs text-accent">
                  <BookOpen size={12} />
                  <span className="font-medium">{note.paper_title}</span>
                </div>
              )}

              <p className="text-xs text-text-secondary leading-relaxed whitespace-pre-wrap">
                {note.content}
              </p>

              <div className="flex items-center justify-between pt-2 border-t border-border-muted text-xs text-text-muted">
                <div className="flex flex-wrap gap-1">
                  {note.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded text-[10px] bg-surface-elevated text-text-muted border border-border-muted"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
                <span>{note.updated_at}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* New Note Modal */}
      <Modal
        isOpen={isNewOpen}
        onClose={() => setIsNewOpen(false)}
        title="Create Research Note"
        description="Write notes, thoughts, and citations linked to your library."
      >
        <form onSubmit={handleCreate} className="space-y-4 pt-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Note Title</label>
            <Input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Scaling laws derivation notes"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Content</label>
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="Write your research notes, insights, or mathematical observations..."
              rows={5}
              className="w-full rounded-lg bg-surface border border-border p-3 text-xs text-text-primary focus:outline-none focus:border-accent"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Tags (comma separated)</label>
            <Input
              value={newTags}
              onChange={(e) => setNewTags(e.target.value)}
              placeholder="e.g. Scaling, Transformers, Loss"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setIsNewOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save Note
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
