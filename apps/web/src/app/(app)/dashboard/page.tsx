import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Upload,
  Search,
  MessageSquare,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">
          Research Workspace
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Evidence-first. Intelligence second.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Link href="/discover">
          <Card variant="interactive" className="group">
            <CardContent className="flex items-center gap-3 py-4">
              <div className="w-8 h-8 rounded-[var(--radius-md)] bg-accent-muted flex items-center justify-center shrink-0">
                <Search size={16} className="text-accent" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-text-primary">Discover</p>
                <p className="text-xs text-text-muted">Search academic papers</p>
              </div>
              <ArrowRight
                size={14}
                className="ml-auto text-text-muted opacity-0 group-hover:opacity-100 transition-opacity"
              />
            </CardContent>
          </Card>
        </Link>

        <Card variant="interactive" className="group cursor-pointer">
          <CardContent className="flex items-center gap-3 py-4">
            <div className="w-8 h-8 rounded-[var(--radius-md)] bg-success-muted flex items-center justify-center shrink-0">
              <Upload size={16} className="text-success" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-text-primary">Import</p>
              <p className="text-xs text-text-muted">Upload a PDF or paste a link</p>
            </div>
            <ArrowRight
              size={14}
              className="ml-auto text-text-muted opacity-0 group-hover:opacity-100 transition-opacity"
            />
          </CardContent>
        </Card>

        <Link href="/chat">
          <Card variant="interactive" className="group">
            <CardContent className="flex items-center gap-3 py-4">
              <div className="w-8 h-8 rounded-[var(--radius-md)] bg-info-muted flex items-center justify-center shrink-0">
                <MessageSquare size={16} className="text-info" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-text-primary">Research Chat</p>
                <p className="text-xs text-text-muted">Ask evidence-backed questions</p>
              </div>
              <ArrowRight
                size={14}
                className="ml-auto text-text-muted opacity-0 group-hover:opacity-100 transition-opacity"
              />
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Main Empty State */}
      <Card>
        <CardContent className="py-0">
          <EmptyState
            icon={
              <div className="w-14 h-14 rounded-2xl bg-surface-elevated border border-border-muted flex items-center justify-center">
                <Sparkles size={24} className="text-accent" />
              </div>
            }
            title="Your research workspace is ready"
            description="Import your first paper to begin. Quorix will parse, chunk, embed, and index it so you can ask evidence-grounded questions."
            action={
              <div className="flex items-center gap-2">
                <Button variant="primary" size="md">
                  <Upload size={14} />
                  Import Paper
                </Button>
                <Button variant="secondary" size="md">
                  <Search size={14} />
                  Discover Papers
                </Button>
              </div>
            }
          />
        </CardContent>
      </Card>

      {/* Sections */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-text-primary">Recent Papers</h2>
              <Badge variant="muted">0</Badge>
            </div>
            <p className="text-xs text-text-muted">
              Papers you&apos;ve recently imported or read will appear here.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-text-primary">Active Conversations</h2>
              <Badge variant="muted">0</Badge>
            </div>
            <p className="text-xs text-text-muted">
              Your research conversations will appear here.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
