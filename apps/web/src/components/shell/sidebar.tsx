"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Search,
  Library,
  MessageSquare,
  GitCompareArrows,
  Network,
  Lightbulb,
  FileText,
  StickyNote,
  Settings,
  Bookmark,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navigation: NavSection[] = [
  {
    title: "Workspace",
    items: [
      { label: "Overview", href: "/dashboard", icon: <LayoutDashboard size={16} /> },
      { label: "Discover", href: "/discover", icon: <Search size={16} /> },
      { label: "Library", href: "/library", icon: <Library size={16} /> },
    ],
  },
  {
    title: "Research",
    items: [
      { label: "Chat", href: "/chat", icon: <MessageSquare size={16} /> },
      { label: "Compare", href: "/compare", icon: <GitCompareArrows size={16} /> },
      { label: "Knowledge Graph", href: "/graph", icon: <Network size={16} /> },
      { label: "Research Gaps", href: "/gaps", icon: <Lightbulb size={16} /> },
      { label: "Literature Reviews", href: "/reviews", icon: <FileText size={16} /> },
    ],
  },
  {
    title: "Personal",
    items: [
      { label: "Notes", href: "/notes", icon: <StickyNote size={16} /> },
      { label: "Saved Searches", href: "/saved", icon: <Bookmark size={16} /> },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed top-0 left-0 z-30 flex h-full flex-col",
        "w-[var(--sidebar-width)] bg-surface border-r border-border-muted",
        "overflow-y-auto"
      )}
    >
      <div className="flex items-center h-[var(--topbar-height)] px-4 border-b border-border-muted shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <div className="w-6 h-6 rounded-[var(--radius-md)] bg-accent flex items-center justify-center">
            <span className="text-xs font-bold text-white">Q</span>
          </div>
          <span className="text-sm font-semibold text-text-primary group-hover:text-accent transition-colors">
            QUORIX
          </span>
        </Link>
      </div>

      <nav className="flex-1 py-3 px-2 space-y-5">
        {navigation.map((section) => (
          <div key={section.title}>
            <p className="px-2 mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
              {section.title}
            </p>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-2.5 px-2 py-1.5 rounded-[var(--radius-md)] text-sm",
                        "transition-colors duration-[var(--duration-fast)]",
                        isActive
                          ? "bg-accent-muted text-accent-text font-medium"
                          : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                      )}
                    >
                      <span className={cn(isActive ? "text-accent" : "text-text-muted")}>
                        {item.icon}
                      </span>
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-border-muted p-2 shrink-0">
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-2.5 px-2 py-1.5 rounded-[var(--radius-md)] text-sm",
            "text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
          )}
        >
          <Settings size={16} className="text-text-muted" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
