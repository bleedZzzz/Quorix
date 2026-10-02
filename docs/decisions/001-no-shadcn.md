# ADR-001: No shadcn/ui — Custom Design System

## Status

**Accepted**

## Date

2026-10-02

## Context

The original `QUORIX_ARCHITECTURE.md` specifies shadcn/ui as the component system. However, the project owner has explicitly overridden this decision.

The rationale is:
1. **Full design control** — Quorix has a very specific visual direction (dark-first, near-black surfaces, restrained accent, workspace-oriented). A custom system allows pixel-perfect adherence without fighting a library's opinions.
2. **No dependency bloat** — shadcn/ui brings Radix UI primitives and a specific styling pattern. A custom system avoids unnecessary abstraction layers.
3. **Coherent identity** — Quorix should feel like a purpose-built product, not a themed component library.
4. **Learnability** — Contributors can understand and modify components without knowledge of shadcn's conventions.

## Decision

- **Do not install** shadcn/ui or its generator
- **Do not import** shadcn/ui components
- Build all UI components custom using:
  - **Tailwind CSS** for utility styling
  - **CSS variables** for design tokens
  - **Accessible primitives** where genuinely useful (e.g., `@radix-ui/react-dialog` for focus trapping if needed, but only individual packages, never the full shadcn system)
  - **Custom React components** in `components/ui/`
- **21st.dev MCP** may be used as a component resource, but components must be adapted into the Quorix design system, not blindly copied

## Consequences

### Positive
- Complete visual control
- Lighter dependency tree
- Consistent Quorix identity
- No shadcn upgrade/migration burden

### Negative
- More upfront work to build primitives (Button, Input, Dialog, Dropdown, Tabs, etc.)
- Must manually ensure accessibility for interactive components
- No automatic theme integration

### Mitigations
- Build primitives incrementally as needed (Phase 1 starts with Button, Input, Dialog, Card)
- Use individual Radix primitives when accessibility is complex (e.g., Dialog, Dropdown)
- Design token system ensures consistency
