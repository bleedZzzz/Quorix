# Quorix — Frontend Architecture

## Framework

- **Next.js** (App Router) with **TypeScript**
- **Tailwind CSS** for utility styling
- **Custom design system** — no shadcn/ui (see ADR-001)
- **CSS variables** for design tokens
- **TanStack Query** for server-state management
- **React Hook Form + Zod** for forms and validation
- **React Flow** for knowledge graph visualization

---

## Visual Direction

Quorix is a dark-first, premium research workspace.

### Design Principles

- Near-black / charcoal surfaces
- Subtle borders (1px, low opacity)
- Restrained blue accent (single hue, 2–3 shades)
- Clean typography (Inter or similar)
- Generous whitespace
- Rounded containers (controlled radii, not excessive)
- Compact navigation
- Minimal visual noise
- Workspace-oriented, not dashboard-oriented
- Professional and calm

### Anti-Patterns (Do NOT)

- Giant dashboard cards
- Excessive gradients / glassmorphism
- Rainbow colors
- Oversized icons
- Animated particle backgrounds
- Huge empty hero sections
- Fake futuristic effects
- Visual clutter
- Generic AI SaaS dashboard aesthetics

---

## Design Token System

All tokens are defined as CSS variables in `:root` / `[data-theme="dark"]` and consumed through Tailwind's `theme.extend` configuration.

### Color Tokens

```css
:root {
  /* Backgrounds */
  --color-bg:              #0a0a0c;
  --color-surface:         #111114;
  --color-surface-muted:   #18181b;
  --color-surface-elevated:#1e1e22;
  --color-surface-hover:   #25252a;

  /* Borders */
  --color-border:          #2a2a30;
  --color-border-muted:    #1f1f24;
  --color-border-focus:    #3b82f6;

  /* Text */
  --color-text-primary:    #f0f0f3;
  --color-text-secondary:  #a1a1aa;
  --color-text-muted:      #6b6b76;
  --color-text-inverse:    #0a0a0c;

  /* Accent (restrained blue) */
  --color-accent:          #3b82f6;
  --color-accent-hover:    #2563eb;
  --color-accent-muted:    rgba(59, 130, 246, 0.15);
  --color-accent-text:     #93bbfd;

  /* Semantic */
  --color-success:         #22c55e;
  --color-success-muted:   rgba(34, 197, 94, 0.15);
  --color-warning:         #f59e0b;
  --color-warning-muted:   rgba(245, 158, 11, 0.15);
  --color-error:           #ef4444;
  --color-error-muted:     rgba(239, 68, 68, 0.15);
  --color-info:            #3b82f6;
  --color-info-muted:      rgba(59, 130, 246, 0.15);
}
```

### Spacing Scale

```css
:root {
  --space-0:  0;
  --space-px: 1px;
  --space-0-5: 0.125rem;  /* 2px  */
  --space-1:  0.25rem;    /* 4px  */
  --space-1-5: 0.375rem;  /* 6px  */
  --space-2:  0.5rem;     /* 8px  */
  --space-2-5: 0.625rem;  /* 10px */
  --space-3:  0.75rem;    /* 12px */
  --space-4:  1rem;       /* 16px */
  --space-5:  1.25rem;    /* 20px */
  --space-6:  1.5rem;     /* 24px */
  --space-8:  2rem;       /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */
}
```

### Border Radius

```css
:root {
  --radius-sm:  0.25rem;   /* 4px  */
  --radius-md:  0.375rem;  /* 6px  */
  --radius-lg:  0.5rem;    /* 8px  */
  --radius-xl:  0.75rem;   /* 12px */
  --radius-2xl: 1rem;      /* 16px */
  --radius-full: 9999px;
}
```

### Shadows

```css
:root {
  --shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md:  0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-lg:  0 4px 16px rgba(0, 0, 0, 0.4);
  --shadow-xl:  0 8px 32px rgba(0, 0, 0, 0.5);
}
```

### Typography

```css
:root {
  --font-sans:    'Inter', system-ui, -apple-system, sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;

  --text-xs:      0.75rem;    /* 12px */
  --text-sm:      0.8125rem;  /* 13px */
  --text-base:    0.875rem;   /* 14px — app default */
  --text-md:      1rem;       /* 16px */
  --text-lg:      1.125rem;   /* 18px */
  --text-xl:      1.25rem;    /* 20px */
  --text-2xl:     1.5rem;     /* 24px */
  --text-3xl:     1.875rem;   /* 30px */

  --leading-tight:   1.25;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;

  --font-normal:  400;
  --font-medium:  500;
  --font-semibold: 600;
  --font-bold:    700;
}
```

### Motion

```css
:root {
  --duration-fast:    100ms;
  --duration-normal:  200ms;
  --duration-slow:    300ms;
  --duration-slower:  500ms;
  --ease-default:     cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in:          cubic-bezier(0.4, 0, 1, 1);
  --ease-out:         cubic-bezier(0, 0, 0.2, 1);
  --ease-spring:      cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## Application Shell

```
┌──────────────────────────────────────────────────────────────┐
│ TopBar — workspace context, search, user menu               │
├───────────────┬───────────────────────────────┬──────────────┤
│   Sidebar     │        Main Workspace         │ Inspector /  │
│               │                               │ Context Pane │
│ Navigation    │ Reader / Chat / Research      │              │
│ Collections   │                               │ Sources      │
│ Projects      │                               │ Evidence     │
│               │                               │ Metadata     │
└───────────────┴───────────────────────────────┴──────────────┘
```

### Component Structure

```tsx
<AppShell>
  <Sidebar />
  <MainWorkspace>
    {/* Page content via App Router */}
  </MainWorkspace>
  <ContextInspector />   {/* Collapsible */}
</AppShell>
```

### Responsive Behavior

| Breakpoint   | Layout                                    |
|-------------|-------------------------------------------|
| Desktop (≥1280px) | Sidebar + Main + optional Inspector  |
| Tablet (768–1279px) | Drawer sidebar + Main + Sheet inspector |
| Mobile (<768px) | Main + Drawer navigation              |

---

## Route Structure

```
/                           → Redirect to /dashboard
/login                      → Authentication
/register                   → Registration
/dashboard                  → Research command center
/discover                   → Paper discovery/search
/library                    → Paper library
/library/[paperId]          → Paper detail
/read/[paperId]             → PDF reader
/chat                       → New conversation
/chat/[conversationId]      → Research conversation
/compare                    → Paper comparison
/graph                      → Knowledge graph
/gaps                       → Research gaps
/reviews                    → Literature reviews
/reviews/[reviewId]         → Literature review detail
/notes                      → Notes
/settings                   → Settings
/settings/models            → Model configuration
/settings/workspace         → Workspace settings
```

---

## Component Inventory

### Design System Primitives (`components/ui/`)

| Component        | Purpose                               |
|------------------|---------------------------------------|
| `Button`         | Primary, secondary, ghost, danger variants |
| `Input`          | Text input with label, error, helper  |
| `Textarea`       | Multi-line input                      |
| `Select`         | Single select dropdown                |
| `Checkbox`       | Checkbox with label                   |
| `Switch`         | Toggle switch                         |
| `Dialog`         | Modal dialog                          |
| `Dropdown`       | Dropdown menu                         |
| `Tabs`           | Tab navigation                        |
| `Tooltip`        | Hover tooltip                         |
| `Badge`          | Status/category badge                 |
| `Avatar`         | User/workspace avatar                 |
| `Spinner`        | Loading indicator                     |
| `Skeleton`       | Content skeleton loader               |
| `EmptyState`     | Empty state with icon, text, action   |
| `ErrorState`     | Error state with retry action         |
| `LoadingState`   | Full-area loading state               |
| `CommandPalette` | ⌘K command palette                    |
| `Card`           | Base card container                   |
| `Toast`          | Notification toast                    |
| `Progress`       | Progress bar                          |

### Domain Components

| Category       | Components                                                 |
|----------------|-------------------------------------------------------------|
| Shell          | `AppShell`, `Sidebar`, `TopBar`, `ContextInspector`, `WorkspaceSwitcher` |
| Papers         | `PaperCard`, `PaperList`, `PaperMetadata`, `PaperActions`  |
| Reader         | `PDFReader`, `PageThumbnail`, `HighlightLayer`, `AnnotationPopover` |
| Chat           | `ChatPanel`, `MessageBubble`, `StreamingMessage`, `ResearchEvent`, `ChatComposer` |
| Evidence       | `EvidenceCard`, `CitationCard`, `SourceCard`, `ClaimCard`  |
| Comparison     | `ComparisonTable`, `ComparisonCell`                         |
| Graph          | `GraphCanvas`, `GraphNode`, `GraphInspector`               |
| Reviews        | `ReviewTable`, `ScreeningCard`                              |
| Notes          | `NoteEditor`, `NoteCard`                                    |
| Common         | `TagPicker`, `JobProgress`, `SearchBar`                     |

---

## Data Fetching Strategy

### TanStack Query Conventions

```typescript
// Query key factory
export const paperKeys = {
  all:       ['papers'] as const,
  lists:     () => [...paperKeys.all, 'list'] as const,
  list:      (filters: PaperFilters) => [...paperKeys.lists(), filters] as const,
  details:   () => [...paperKeys.all, 'detail'] as const,
  detail:    (id: string) => [...paperKeys.details(), id] as const,
};

// Hook pattern
export function usePapers(filters: PaperFilters) {
  return useQuery({
    queryKey: paperKeys.list(filters),
    queryFn: () => api.papers.list(filters),
  });
}
```

### API Client

Typed API client using `fetch` with interceptors for auth tokens, error handling, and request/response typing.

```typescript
// lib/api/client.ts
class ApiClient {
  private baseUrl: string;
  private getToken: () => string | null;
  
  async get<T>(path: string, params?: Record<string, string>): Promise<T>;
  async post<T>(path: string, body: unknown): Promise<T>;
  async put<T>(path: string, body: unknown): Promise<T>;
  async delete(path: string): Promise<void>;
  
  // SSE streaming
  stream(path: string, body: unknown): AsyncIterable<StreamEvent>;
}
```

---

## State Management

- **Server state** → TanStack Query (papers, conversations, evidence, etc.)
- **URL state** → Next.js route params and searchParams
- **UI state** → React context for sidebar/inspector visibility, theme
- **Form state** → React Hook Form + Zod schemas
- **No global state library** — avoid Redux/Zustand unless complexity demands it

---

## Performance Considerations

- Next.js App Router with server components where possible
- Client components only where interactivity is needed
- Code-split heavy components (PDF reader, graph visualization)
- Optimistic updates for user actions (notes, tags, bookmarks)
- Virtual lists for large paper/note collections
- Debounced search inputs
- Prefetch on hover for likely navigations

---

## Accessibility

- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation (Tab, Enter, Escape, Arrow keys)
- Visible focus states
- Adequate contrast ratios (WCAG AA minimum)
- Reduced motion support via `prefers-reduced-motion`
- Correct focus trapping in modals/dialogs
- Screen-reader-friendly status announcements
