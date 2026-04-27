# web-builder Plan 4: Multi-Scope + Dev Mode

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support all 4 site scopes (single page, multi-page static, interactive static, full app) — in sade mode with auto-picked defaults, or in dev mode (`/web-builder-dev`) with user stack overrides at the frontend, backend, styling, and DB layers. Make existing agents stack/scope-aware (read `state.json`, branch internally) and add a new `backend-engineer` agent for full-app scope.

**Architecture:** Two slash commands (`/web-builder` sade, `/web-builder-dev` dev). Intake skill branches on `mode` to ask different question sets. All worker agents (`ui-ux-designer`, `content-writer`, `frontend-expert`, plus new `backend-engineer`) read `state.json.{scope, stack}` and branch internally — one agent per role, multiple stacks per agent. Orchestrator's agent execution graph adapts per scope (skip backend for static, run frontend+backend in parallel for full-app).

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). Generated projects span vanilla HTML/CSS/JS, Astro+Tailwind, Astro+islands, Next.js, SvelteKit, Node+Express, Go, Java/Spring, Python/FastAPI, SQLite/Postgres/MongoDB.

**v0.4.0 scope:**

| Scope | Sade default | Dev mode FE choices | Dev mode BE choices (full-app only) | Dev mode DB choices |
|---|---|---|---|---|
| Single page | Vanilla HTML/CSS/JS | Vanilla / Astro / Next.js | n/a | n/a |
| Multi-page static | Astro + Tailwind | Astro / Next.js / SvelteKit / vanilla | n/a | n/a |
| Interactive static | Astro + Tailwind + Preact islands | Astro / Next.js / SvelteKit | n/a | n/a |
| Full app | Next.js + Tailwind + Prisma + SQLite | Next.js / SvelteKit | Next.js API / Node+Express / Go (chi) / Java/Spring / Python/FastAPI | SQLite / Postgres / MongoDB / none |

**Definition of done:** A user can run `/web-builder` and pick any of the 4 scopes (Q&A asks). For each scope, sade mode picks the default stack silently and produces a buildable site. A user can run `/web-builder-dev` and override the stack at any layer (frontend/backend/styling/db) — the chosen stack is generated. All 4 agents handle their scope/stack branch correctly. Smoke test passes for at least 3 of the 4 scopes (single-page vanilla, multi-page-static Astro, full-app Next.js+SQLite — all in sade mode) plus 1 dev-mode override (multi-page-static + Next.js).

**Out of scope (deferred):**
- SEO + a11y agents (Plan 5) — they will join the impact-analysis table once added; orchestrator's table is forward-compatible
- Public Claude Code plugin distribution (Plan 6)
- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup (per spec §7.3)
- More frontend frameworks (Remix, Solid, Vue) — deferrable
- More backend frameworks (Rust, Elixir, .NET) — deferrable
- ORM choice (Prisma vs Drizzle vs raw SQL) — Prisma default for SQL stacks, Mongoose for MongoDB

---

## File Structure

```
web-builder/
├── plugin.json                                  # MODIFY: bump version to 0.4.0
├── README.md                                    # MODIFY: status to v0.4.0
├── commands/
│   ├── web-builder.md                           # MODIFY: enable scope question (no longer hardcoded)
│   └── web-builder-dev.md                       # CREATE: dev mode entry
├── skills/
│   ├── web-builder-orchestrator/SKILL.md        # MODIFY: scope-aware agent graph (parallel for full-app)
│   ├── web-builder-intake/SKILL.md              # MODIFY: scope question (sade) + stack questions (dev)
│   ├── web-builder-revise/SKILL.md              # MODIFY: technical category gains stack/scope sub-options
│   └── web-builder-deliver/SKILL.md             # MODIFY: scope-aware preview hint, deploy default
├── agents/
│   ├── ui-ux-designer.md                        # MODIFY: scope-aware (full-app component states)
│   ├── content-writer.md                        # MODIFY: scope-aware (full-app error states/button copy)
│   ├── frontend-expert.md                       # MAJOR MODIFY: 5 stack branches (vanilla / astro / astro+islands / nextjs / sveltekit)
│   ├── backend-engineer.md                      # CREATE: 5 BE stacks for full-app
│   └── deployer.md                              # MODIFY: scope-aware target defaults
├── tests/
│   ├── fixtures/
│   │   ├── sample-brief.md                      # unchanged (multi-page-static example)
│   │   ├── sample-brief-single-page.md          # CREATE
│   │   ├── sample-brief-full-app.md             # CREATE
│   │   ├── sample-style-guide.md                # unchanged
│   │   ├── sample-content.md                    # unchanged
│   │   └── sample-state.json                    # unchanged
│   ├── lint.sh                                  # unchanged (auto-picks up new agent)
│   └── smoke-test.md                            # MODIFY: add Tests 11-14 for new scopes + dev mode
└── docs/
    └── plans/
        ├── 2026-04-26-plan-2-preview-and-deploy.md
        ├── 2026-04-27-plan-3-revision-flow.md
        └── 2026-04-27-plan-4-multi-scope-and-dev-mode.md
```

**Responsibilities:**

| File | Owns |
|---|---|
| `commands/web-builder-dev.md` | Dev-mode entry; sets `mode=dev` for orchestrator |
| `agents/backend-engineer.md` | Full-app backend code generation across 5 BE stacks (Next.js API / Node+Express / Go / Java / Python) + DB setup (SQLite / Postgres / MongoDB) |
| Existing agents (modified) | Branch on `state.json.{scope, stack}` to produce per-scope/per-stack output |

---

## Task 1: `/web-builder-dev` Slash Command

**Files:**
- Create: `commands/web-builder-dev.md`

- [ ] **Step 1: Write the dev-mode command file**

Create `commands/web-builder-dev.md`:

```markdown
---
description: Build a website end-to-end through guided Q&A — dev mode (asks technical preferences: stack, styling, DB, lint).
---

You are entering the web-builder flow in **dev mode** (technical mode — user can pick framework, styling, database, etc.; technical terms are surfaced and explained inline).

Use the `Skill` tool to invoke the `web-builder-orchestrator` skill, passing `mode=dev`.

Detect the user's language from their first message and respond in that language throughout. Plain language is still preferred where possible, but you can use technical terms (Astro, Next.js, Prisma, etc.) — the user opted into dev mode.

Do not output anything to the user before invoking the skill — the skill itself handles all dialog.
```

- [ ] **Step 2: Verify**

Run: `head -3 commands/web-builder-dev.md`
Expected: starts with `---`, contains `description:`, ends `---`.

- [ ] **Step 3: Commit**

```bash
git add commands/web-builder-dev.md
git commit -m "feat: add /web-builder-dev slash command (dev mode entry)"
```

---

## Task 2: Update `/web-builder` Command

**Files:**
- Modify: `commands/web-builder.md`

The existing slash command says "no stack-choice questions". With Plan 4, sade mode still doesn't ask stack questions — but it does need to ask the SCOPE question now (whereas Plan 1 hardcoded multi-page-static). Update the command's prompt slightly so it doesn't claim "no scope-choice questions".

- [ ] **Step 1: Read current command**

Run: `cat commands/web-builder.md`

- [ ] **Step 2: Replace the body**

Use Edit to replace the line:

```
You are entering the web-builder flow in **sade mode** (plain language, no jargon, no stack-choice questions).
```

with:

```
You are entering the web-builder flow in **sade mode** (plain language, no jargon — the plugin asks plain-language questions about the kind of site you want, and picks the underlying technology automatically).
```

The rest of the file stays the same.

- [ ] **Step 3: Verify**

Run: `grep -c "no stack-choice questions" commands/web-builder.md`
Expected: 0.

Run: `grep -c "picks the underlying technology" commands/web-builder.md`
Expected: 1.

- [ ] **Step 4: Commit**

```bash
git add commands/web-builder.md
git commit -m "docs: update /web-builder description for multi-scope sade mode"
```

---

## Task 3: Update Intake Skill — Sade Mode Multi-Scope

**Files:**
- Modify: `skills/web-builder-intake/SKILL.md`

Currently the intake skill hardcodes scope=multi-page-static. Replace the constraints section + Q2 to actually ask the scope and let it vary among the 4 spec-defined options.

- [ ] **Step 1: Read current intake skill**

Run: `cat skills/web-builder-intake/SKILL.md`

Locate:
- The `## Constraints (MVP)` section
- The Q2 (`### Q2: Confirm scope interpretation`) section that currently confirms "multi-page-static"

- [ ] **Step 2: Replace constraints section**

Use Edit to replace:

```markdown
## Constraints (MVP)

- Hardcoded scope: multi-page static site (do **not** ask about scope; assume this).
- Hardcoded stack: Astro + Tailwind (do **not** mention this to the user).
- Hardcoded image strategy: contextual Unsplash placeholders.
```

with:

```markdown
## Constraints

- **Sade mode (this skill is invoked from `/web-builder`):** ask the user about scope (Q2 below); pick the default stack for that scope automatically and silently. Do not mention stack names.
- **Dev mode (invoked from `/web-builder-dev`):** ask scope (Q2), then ask stack overrides (frontend / styling / backend / DB / TypeScript / lint). See "Dev mode Q&A extension" below.
- Image strategy: contextual Unsplash placeholders for both modes.
- The orchestrator passes you a `mode` parameter (`simple` or `dev`); branch on it.
```

- [ ] **Step 3: Replace Q2**

Use Edit to replace the entire Q2 section (from `### Q2: Confirm scope interpretation` through the closing of that section before `### Q3: Project name`) with:

````markdown
### Q2: Site scope

> Ne tür bir site yapacağız?
>
> A) Tek sayfa (kısa tanıtım, one-pager)
> B) Çok sayfalı tanıtım (ana sayfa + hakkımızda + iletişim falan, etkileşim yok)
> C) Çok sayfalı + bir-iki etkileşim (form, galeri, küçük JS özellikleri)
> D) Üye girişi / sipariş / veri kaydı olan tam uygulama

Map the answer:
- A → `single-page`
- B → `multi-page-static`
- C → `interactive-static`
- D → `full-app`

Capture as `scope`.

In **dev mode**, after the user picks scope, also ask:

> Frontend için tercihin var mı, yoksa ben mi seçeyim?
>
> A) Sen seç (önereceklerin: {scope-default-stack-name})
> B) Vanilla HTML/CSS/JS
> C) Astro + Tailwind
> D) Next.js + Tailwind
> E) SvelteKit + Tailwind

Filter the option list per scope:
- single-page: A, B, C, D
- multi-page-static: A, C, D, E (vanilla rare for multi-page; offer if asked)
- interactive-static: A, C, D, E
- full-app: A, D, E

Capture as `stack` (e.g., `astro+tailwind`, `nextjs+tailwind`).

For **full-app** in dev mode, ask three more questions in order:

#### Q2-dev-be: Backend

> Backend için?
>
> A) Sen seç (önereceğim: Next.js API routes)
> B) Next.js API routes (frontend ile aynı pakette)
> C) Node + Express (ayrı paket)
> D) Go (chi router)
> E) Java + Spring Boot
> F) Python + FastAPI

Capture as `backend` (e.g., `nextjs-api`, `node-express`).

#### Q2-dev-db: Database

> Database için?
>
> A) Sen seç (önereceğim: SQLite, file tabanlı, en kolay)
> B) SQLite (Prisma)
> C) Postgres (Prisma)
> D) MongoDB (Mongoose)
> E) Yok / kendim halledeceğim

Capture as `database` (e.g., `sqlite-prisma`).

#### Q2-dev-extra: TypeScript / Lint

> Birkaç teknik tercih:
>
> - TypeScript: {default per stack — açık for Astro/Next/SvelteKit, kapalı for vanilla}. Değiştirmek ister misin? (E/H)
> - ESLint + Prettier: default açık. Kapatmak ister misin? (E/H)

Capture `typescript: bool`, `linter: bool`.
````

- [ ] **Step 4: Update side effects to include scope/stack/dev fields**

Locate the `## Side effects` section. Update step 5 (writing state.json) to use the captured values instead of hardcoding:

Old wording fragment (in step 5):
```
Set `mode: "simple"`, `scope: "multi-page-static"`, `stack: "astro+tailwind"`, ...
```

New wording:
```
Set `mode` to the value passed by the orchestrator (`simple` or `dev`), `scope` to the value captured in Q2, `stack` to either the captured value (dev mode) or the scope-default (sade mode — use the table below), and the remaining captured fields (`backend`, `database`, `typescript`, `linter`) only if mode is `dev`.

Scope → default-stack mapping (sade mode):
- single-page → vanilla
- multi-page-static → astro+tailwind
- interactive-static → astro+tailwind+preact-islands
- full-app → nextjs+tailwind+prisma+sqlite (full-app sade also implies backend=nextjs-api, database=sqlite-prisma)
```

- [ ] **Step 5: Verify**

Run: `grep -c "scope-default-stack-name" skills/web-builder-intake/SKILL.md`
Expected: at least 1 (in the dev mode question).

Run: `grep -c "Q2-dev-be" skills/web-builder-intake/SKILL.md`
Expected: 1.

Run: `grep -c "single-page" skills/web-builder-intake/SKILL.md`
Expected: at least 2 (in Q2 mapping + scope-default table).

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.` (after Task 1 added the new `/web-builder-dev` command file; backend-engineer not yet created)

- [ ] **Step 6: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "feat: intake supports 4 scopes (sade) + stack overrides (dev mode)"
```

---

## Task 4: Update `brief.md` Template

**Files:**
- Modify: `skills/web-builder-intake/SKILL.md` (the brief.md template inside it)

The current template has a `## Teknik` section labeled "(only filled in dev mode)" — that's correct for dev mode. We need to make sure scope is captured in the brief regardless, so downstream agents can read it. Add a Scope line.

- [ ] **Step 1: Locate brief.md template**

In `skills/web-builder-intake/SKILL.md`, find the section starting `## brief.md template` and the markdown content inside it.

- [ ] **Step 2: Add Scope section to template**

After the `# Site Briefi: {siteName}` heading, the existing template has `## Amaç`. Insert a new `## Scope` section right after Amaç (or before Hedef Kitle):

```markdown
## Scope
{scope value: single-page | multi-page-static | interactive-static | full-app}
```

Translate to English headings if site language is English (`Scope` stays the same in English).

- [ ] **Step 3: Update Teknik section template**

Currently:
```
## Teknik (only filled in dev mode)
- Stack: [...]
- Deploy hedefi: [...]
```

Replace with:
```
## Teknik
- Stack: {stack value, e.g. "astro+tailwind"}
- Backend: {backend value if full-app, else "n/a"}
- Database: {database value if full-app, else "n/a"}
- TypeScript: {true | false}
- Linter: {true | false}
- Deploy hedefi: {default per scope, will be confirmed at deploy time}
```

(Sade mode populates this with the scope-default stack; dev mode populates with the user's picks. Either way, the brief is complete.)

- [ ] **Step 4: Verify**

Run: `grep -c "## Scope" skills/web-builder-intake/SKILL.md`
Expected: at least 1.

Run: `grep -c "Backend:" skills/web-builder-intake/SKILL.md`
Expected: at least 1.

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "docs: brief.md template adds Scope + full Teknik (always populated)"
```

---

## Task 5: Make `ui-ux-designer` Scope-Aware

**Files:**
- Modify: `agents/ui-ux-designer.md`

Add a "Scope branching" section so the agent reads `state.json.scope` and adapts the style guide. Component sets vary by scope (single page = minimal, full app = many states).

- [ ] **Step 1: Read current agent**

Run: `cat agents/ui-ux-designer.md`

- [ ] **Step 2: Insert scope-branching guidance**

Use Edit to insert a new section between `## Output` and `## style-guide.md template`:

```markdown
## Scope-aware extensions

Read `{projectPath}/.web-builder/state.json` to get `scope`. Extend the style guide depending on scope:

- **single-page:** Minimal extension. Just the standard palette, fonts, spacing. The "Component notes" section can omit Cards if the page doesn't have them.
- **multi-page-static:** Standard. All sections of the template apply.
- **interactive-static:** Add a "## Interactive components" section: input field styling, button hover/active/disabled states, modal/dialog tokens, animation easing curves.
- **full-app:** Add three sections beyond the standard template:
  - **## Component states** — for buttons, inputs, links, cards: states for `default | hover | active | disabled | loading | error`
  - **## Layout patterns** — sidebar+main, dashboard grid, form layouts, list/detail views
  - **## Empty / error / loading states** — visual treatments for "no data", "error", "loading skeleton"
```

- [ ] **Step 3: Verify**

Run: `grep -c "Scope-aware extensions" agents/ui-ux-designer.md`
Expected: 1.

Run: `grep -c "Component states" agents/ui-ux-designer.md`
Expected: 1.

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.` (after Task 1 added the new `/web-builder-dev` command file; backend-engineer not yet created)

- [ ] **Step 5: Commit**

```bash
git add agents/ui-ux-designer.md
git commit -m "feat: ui-ux-designer adapts style guide to project scope"
```

---

## Task 6: Make `content-writer` Scope-Aware

**Files:**
- Modify: `agents/content-writer.md`

Similar pattern: read scope, adapt content. Full-app needs UI strings (button labels, error messages, empty states); static sites only need page text.

- [ ] **Step 1: Insert scope-branching section**

Use Edit to insert a new section between `## Output` and `## content.md template` in `agents/content-writer.md`:

```markdown
## Scope-aware extensions

Read `{projectPath}/.web-builder/state.json` to get `scope`. Extend `content.md` depending on scope:

- **single-page:** Standard template — site-wide, hero, sections.
- **multi-page-static:** Standard template — multiple pages.
- **interactive-static:** After the per-page content sections, add:
  - **## Interaction copy** — labels for buttons in interactive components (form submit, gallery prev/next, slider play/pause, etc.)
- **full-app:** Add three sections beyond the standard:
  - **## UI strings** — button labels, link text, form field labels, validation messages, error messages, empty-state messages, loading text. Keep them concrete and action-oriented.
  - **## Auth flow strings** — sign-in / sign-up / reset-password page copy if the brief mentions auth
  - **## Notification / toast messages** — for common actions (saved, deleted, error)

For all scopes, the existing site-wide and per-page sections still apply.
```

- [ ] **Step 2: Verify**

Run: `grep -c "Scope-aware extensions" agents/content-writer.md`
Expected: 1.

Run: `grep -c "UI strings" agents/content-writer.md`
Expected: 1.

- [ ] **Step 3: Lint**

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.` (after Task 1 added the new `/web-builder-dev` command file; backend-engineer not yet created)

- [ ] **Step 4: Commit**

```bash
git add agents/content-writer.md
git commit -m "feat: content-writer adapts content to project scope (UI strings, auth, notifications)"
```

---

## Task 7: Make `frontend-expert` Stack-Aware (5 Stacks)

**Files:**
- Modify: `agents/frontend-expert.md` (major)

This is the biggest task in Plan 4. The agent currently only knows Astro+Tailwind. Add per-stack branches for: vanilla, astro (existing), astro+islands, nextjs, sveltekit.

- [ ] **Step 1: Read the current agent file**

Run: `cat agents/frontend-expert.md`. The current file is ~206 lines and is structured around an Astro+Tailwind project.

- [ ] **Step 2: Restructure the file**

Use Edit (or full rewrite via Write — whichever is cleaner) to restructure into:

```
# frontend-expert agent

(intro line)

## Inputs

(read brief, style-guide, content, state.json — same as before)

## Stack branching

Read `state.json.stack`. Branch on the value:

| state.json.stack | Section to follow |
|---|---|
| `vanilla` | ## Vanilla branch |
| `astro+tailwind` | ## Astro branch |
| `astro+tailwind+preact-islands` | ## Astro+islands branch |
| `nextjs+tailwind` (or `nextjs+tailwind+prisma+sqlite`) | ## Next.js branch |
| `sveltekit+tailwind` | ## SvelteKit branch |

If `state.json.stack` is unknown, treat as `astro+tailwind` (the default for multi-page-static).

For full-app stacks (e.g., `nextjs+tailwind+prisma+sqlite`), only generate the frontend portion. The `backend-engineer` agent generates the API routes and DB schema separately.

## Vanilla branch

(content for vanilla HTML/CSS/JS — minimal directory: `index.html`, `style.css`, `main.js`, plus per-page HTML files if scope > single-page)

Layout:
- `{projectPath}/index.html` — main page
- `{projectPath}/style.css` — Tailwind compiled output OR raw CSS
- `{projectPath}/main.js` — minimal JS
- For multi-page: additional `{page}.html` files at root with kebab-case names
- No build step needed — files runnable directly via any static server

Concrete templates:
- index.html using palette/typography from style-guide.md
- style.css with custom properties for the palette
- main.js minimal (page nav highlight, etc.)

## Astro branch

(existing content from Plan 1 — Astro + Tailwind project structure)

(existing concrete file contents stay)

## Astro+islands branch

Same as Astro branch but with `@astrojs/preact` integration added in `astro.config.mjs` and one or two example interactive components in `src/components/{Name}.tsx` (Preact). Include them in `index.astro` with `client:load`.

Add to package.json dependencies: `@astrojs/preact`, `preact`.

Update astro.config.mjs to include the preact integration.

Add example: a contact form component or a counter component, depending on what content.md describes.

## Next.js branch

(content for Next.js App Router project — for both static-only and full-app cases)

Project layout:
- `package.json` (deps: next ^15, react ^18, tailwindcss ^3, plus prisma if full-app)
- `next.config.mjs` (minimal)
- `tailwind.config.ts` (palette from style-guide)
- `app/` — App Router structure:
  - `layout.tsx` — root layout (analog to BaseLayout.astro)
  - `page.tsx` — home (Ana sayfa)
  - `{slug}/page.tsx` — one per non-home page
  - For full-app: `app/api/{route}/route.ts` SHELLS only (backend-engineer fills these)
- `components/` — Header.tsx, Footer.tsx
- `globals.css` — Tailwind directives + Google fonts

If full-app: also write `prisma/schema.prisma` SHELL (backend-engineer will populate with models).

After writing files: run `npm install --silent` then `npm run build`. (Use `pnpm` if available; fall back to npm.)

(Concrete templates for each file — Next.js App Router style)

## SvelteKit branch

(content for SvelteKit project)

Project layout:
- `package.json` (deps: @sveltejs/kit ^2, svelte ^4, vite, tailwindcss)
- `svelte.config.js`, `vite.config.js`, `tailwind.config.js`
- `src/routes/+layout.svelte`, `+page.svelte`, `{slug}/+page.svelte`
- `src/lib/components/` — Header.svelte, Footer.svelte
- `src/app.css` — Tailwind directives + fonts

Use kit's static adapter (`@sveltejs/adapter-static`) for static scopes; `adapter-auto` for full-app.

After writing: `npm install` + `npm run build`.

(Concrete templates)

## After writing files (all stacks)

Run inside the project directory:

```bash
pnpm install --silent || npm install --silent
pnpm run build || npm run build
```

If the build fails, fix the offending file and retry. Report failure only after 2 attempts.

## Constraints

(same as before — read-only inputs, write only frontend files, etc.)

Output one-line summary: `frontend generated: stack={stack} pages={N} build={ok|failed}`.
```

The full file will be ~500-700 lines. Each stack section has its own concrete file templates analogous to the Astro section.

- [ ] **Step 3: Verify the structure**

Run: `grep -nE "^## (Vanilla|Astro|Astro\+islands|Next\.js|SvelteKit) branch" agents/frontend-expert.md`
Expected: 5 lines (one per stack branch).

Run: `grep -c "state.json.stack" agents/frontend-expert.md`
Expected: at least 1.

Run: `wc -l agents/frontend-expert.md`
Expected: 500-800 lines (large file, reflects the per-stack content).

Run: `grep -c '^```' agents/frontend-expert.md`
Expected: EVEN, large number (each stack has many embedded code blocks).

Run: `grep -c '^````' agents/frontend-expert.md`
Expected: 0.

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.` (after Task 1 added the new `/web-builder-dev` command file; backend-engineer not yet created)

- [ ] **Step 5: Commit**

```bash
git add agents/frontend-expert.md
git commit -m "feat: frontend-expert handles 5 stacks (vanilla, astro, astro+islands, nextjs, sveltekit)"
```

---

## Task 8: Create `backend-engineer` Agent

**Files:**
- Create: `agents/backend-engineer.md`

For full-app scope only. Generates backend code in 5 stacks (Next.js API routes / Node+Express / Go chi / Java/Spring / Python/FastAPI) with DB integration in 3 options (SQLite-Prisma / Postgres-Prisma / MongoDB-Mongoose).

- [ ] **Step 1: Write the agent**

Create `agents/backend-engineer.md`:

````markdown
---
name: backend-engineer
description: Reads brief.md and content.md (auth flow strings) to produce backend code (API routes, DB schema, auth) in the chosen backend stack. Only invoked for full-app scope.
tools: Read, Write, Edit, Bash
---

# backend-engineer agent

You generate backend code for a full-app project. The frontend is generated by `frontend-expert` in parallel; you handle the API + database + auth.

## Inputs

Read in this order:
1. `{projectPath}/.web-builder/state.json` — `scope` (must be `full-app`), `backend`, `database`
2. `{projectPath}/brief.md` — feature list (what entities exist, what auth is needed)
3. `{projectPath}/content.md` "Auth flow strings" section if present — page copy for sign-in / sign-up / reset

## Pre-flight

If `state.json.scope` is not `full-app`, exit immediately with:
```
status: skipped
reason: not-full-app
```

The orchestrator will only invoke you for full-app — but defensive check.

## Stack branching

Read `state.json.backend` and `state.json.database`. Branch on backend:

| state.json.backend | Section |
|---|---|
| `nextjs-api` | ## Next.js API routes |
| `node-express` | ## Node + Express |
| `go-chi` | ## Go (chi router) |
| `java-spring` | ## Java / Spring Boot |
| `python-fastapi` | ## Python / FastAPI |

If unknown: default to `nextjs-api`.

DB branching is consistent across BE stacks:
- `sqlite-prisma`, `postgres-prisma` → use Prisma (Node-based stacks) or equivalent ORM
- `mongodb-mongoose` → Mongoose (Node-based) or pymongo / java mongo driver depending on BE
- `none` → skip DB setup

## Common deliverables (all stacks)

- `README.md` section in the project explaining how to run the backend
- DB schema / migration if applicable
- 2-3 example API endpoints inferred from brief (CRUD on the main entity, plus /api/health)
- Auth scaffolding if brief mentions login (basic email+password, no OAuth in v0.4.0)
- Dev script (e.g., add to package.json or Makefile)

## ## Next.js API routes

(For when frontend is also Next.js — backend lives in same package)

Generate:
- `app/api/{entity}/route.ts` — list/create
- `app/api/{entity}/[id]/route.ts` — get/update/delete
- `app/api/auth/[...]/route.ts` if auth needed (use NextAuth or simple JWT)
- `prisma/schema.prisma` populated with models from brief
- Update `package.json` to add `prisma`, `@prisma/client`, `bcrypt` (if auth)
- `lib/db.ts` — Prisma client singleton

After writing: run `npx prisma generate && npx prisma migrate dev --name init` (silenced).

(Concrete code templates for each route file)

## ## Node + Express

(For when frontend is Astro/SvelteKit and backend is a separate Node service)

Generate in a `backend/` subdirectory:
- `backend/package.json` (express, prisma, bcrypt for auth)
- `backend/src/server.ts` — Express app + middleware
- `backend/src/routes/{entity}.ts` — CRUD endpoints
- `backend/src/auth/middleware.ts` if auth
- `backend/prisma/schema.prisma`
- `backend/.env.example`

After writing: `cd backend && npm install && npx prisma generate`.

(Concrete templates)

## ## Go (chi router)

(For when user prefers Go)

Generate in `backend/`:
- `backend/go.mod` with chi, sqlite/pgx, bcrypt deps
- `backend/main.go` — chi mux + routes
- `backend/handlers/{entity}.go` — CRUD
- `backend/db/db.go` — DB connection (sqlite via mattn/go-sqlite3, postgres via jackc/pgx)
- `backend/auth/middleware.go` if auth
- `backend/migrations/0001_init.sql`

After writing: `cd backend && go mod tidy && go build`.

(Concrete templates with Go idioms)

## ## Java / Spring Boot

Generate in `backend/`:
- `backend/pom.xml` — Spring Boot starter web, jpa, security if auth
- `backend/src/main/java/com/{siteSlug}/Application.java`
- `backend/src/main/java/com/{siteSlug}/controllers/{Entity}Controller.java`
- `backend/src/main/java/com/{siteSlug}/repositories/{Entity}Repository.java`
- `backend/src/main/java/com/{siteSlug}/entities/{Entity}.java`
- `backend/src/main/resources/application.properties` — DB connection
- DB migration via Flyway: `backend/src/main/resources/db/migration/V1__init.sql`

After writing: `cd backend && mvn package` (skipped if maven not installed; warn user).

(Concrete templates)

## ## Python / FastAPI

Generate in `backend/`:
- `backend/pyproject.toml` (or requirements.txt) with fastapi, uvicorn, sqlalchemy, alembic, passlib if auth
- `backend/app/main.py` — FastAPI app + routes import
- `backend/app/routers/{entity}.py` — CRUD
- `backend/app/auth/jwt.py` if auth
- `backend/app/db.py` — SQLAlchemy session
- `backend/app/models/{entity}.py` — SQLAlchemy model
- `backend/alembic/versions/0001_init.py`

After writing: `cd backend && pip install -e . && alembic upgrade head` (or similar).

(Concrete templates)

## DB-specific notes (all stacks)

- **SQLite** — file at `backend/data.db` (or `prisma/dev.db` for Prisma); easy local dev, no server needed
- **Postgres** — connection string from env `DATABASE_URL`; the agent assumes a running Postgres instance and notes this in README
- **MongoDB** — for Node stacks: Mongoose models; for Python: motor / pymongo
- **none** — skip all DB code; backend is in-memory only (warn user this means data is lost on restart)

## Constraints

- Read brief.md, content.md, state.json. Write only backend files (typically inside `backend/` subdirectory; for nextjs-api, into the existing Next.js project's `app/api/` and `prisma/`).
- Do not modify frontend files (frontend-expert owns those).
- Output one-line summary: `backend generated: stack={backend} db={database} routes={N} build={ok|failed}`.
````

This file will be ~600-800 lines once concrete templates are filled in. Use this skeleton; expand each backend section with real, working code templates.

- [ ] **Step 2: Verify**

Run: `head -5 agents/backend-engineer.md`
Expected: frontmatter with `name: backend-engineer`, `tools: Read, Write, Edit, Bash`.

Run: `grep -nE "^## ## " agents/backend-engineer.md`
Expected: 5 backend stack sections.

Run: `grep -c '^```' agents/backend-engineer.md`
Expected: EVEN, around 30-50 (multiple code examples per BE stack).

Run: `grep -c '^````' agents/backend-engineer.md`
Expected: 0.

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.` (Task 1's new command + Task 8's new agent file).

- [ ] **Step 3: Commit**

```bash
git add agents/backend-engineer.md
git commit -m "feat: add backend-engineer agent (Next.js API / Node+Express / Go / Java / Python)"
```

---

## Task 9: Update Orchestrator — Scope-Aware Agent Graph

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md`

The orchestrator's step 3 currently runs ui-ux-designer → content-writer → frontend-expert sequentially. For full-app, we need to add backend-engineer running in parallel with frontend-expert. Also, for single-page scope, content-writer's output is smaller and could run in parallel with designer.

- [ ] **Step 1: Read current orchestrator step 3**

Run: `grep -nA 30 "^3\. " skills/web-builder-orchestrator/SKILL.md` to find the agent execution graph section.

- [ ] **Step 2: Replace step 3's agent graph with scope-aware version**

Use Edit to replace the sequential A→B→C list with this graph definition:

````markdown
3. From this point on, **all file operations happen inside the project subdirectory.** `cd` into it before invoking agents. Run the agent execution graph against the project directory. The graph is scope-aware:

   **Sequential phase 1 (always):**
   
   **Step A — `ui-ux-designer` agent**
   
   Use the `Agent` tool with `subagent_type: "ui-ux-designer"`. Pass:
   
   > Project path: `{projectPath}`. Read brief.md and write style-guide.md per your instructions.
   
   Wait for completion. Append to `state.json.agentRuns`. Standard retry policy.

   **Parallel phase 2 (after designer completes):**
   
   **Step B — `content-writer` agent**
   
   Use Agent tool with `subagent_type: "content-writer"`. Same prompt pattern.
   
   **Parallel phase 3 (after content-writer completes):**
   
   **Step C — `frontend-expert` agent**
   
   Use Agent tool with `subagent_type: "frontend-expert"`. Same prompt pattern. The agent reads state.json.stack and branches.
   
   **Step D — `backend-engineer` agent (only if scope = full-app)**
   
   In parallel with Step C: use Agent tool with `subagent_type: "backend-engineer"`. The agent reads state.json.{backend, database} and branches. Skip this step entirely if scope is not `full-app`.
   
   Wait for both C and D to complete before proceeding.
````

(Steps E onward — accessibility-reviewer in Plan 5 — would slot in here in the future.)

- [ ] **Step 3: Verify**

Run: `grep -c "subagent_type: \"backend-engineer\"" skills/web-builder-orchestrator/SKILL.md`
Expected: 1.

Run: `grep -c "scope = full-app" skills/web-builder-orchestrator/SKILL.md`
Expected: at least 1.

Run: `grep -c "Parallel phase" skills/web-builder-orchestrator/SKILL.md`
Expected: at least 1.

- [ ] **Step 4: Update impact analysis table to handle backend changes**

Locate the impact analysis table in step 1c.2. Add a new column or extend `technical` to mention backend changes. Updated table:

```
| Change category | Agents to re-run (in order) |
|---|---|
| `style` | `ui-ux-designer`, `frontend-expert` |
| `content` | `content-writer`, `frontend-expert` |
| `structure` | `ui-ux-designer` (if layout shifts), `content-writer`, `frontend-expert` |
| `behavior` | `frontend-expert` (and `backend-engineer` if the change involves form submission, auth, or any server interaction) |
| `technical` | depends on sub-detail: stack/scope change → all agents re-run; deploy target change → deliver skill's deploy flow; backend-only change → `backend-engineer` only |
| `undo` | (no agents — see step 1d) |
| `cancel` | exit cleanly |
```

- [ ] **Step 5: Lint**

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 6: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: orchestrator runs frontend+backend in parallel for full-app scope"
```

---

## Task 10: Update `revise` Skill — Stack/Scope Sub-Options

**Files:**
- Modify: `skills/web-builder-revise/SKILL.md`

The `technical` category in revise asks about "deploy target / site name / SEO / performance". Add stack and scope changes as new sub-options.

- [ ] **Step 1: Locate technical category section**

In `skills/web-builder-revise/SKILL.md`, find `### If user picks E (technical)`.

- [ ] **Step 2: Replace the sub-question list**

Use Edit to replace the current sub-question:

```markdown
> Teknik konularda?
>
> A) Deploy hedefi değiştir (örn. Cloudflare → Vercel)
> B) Site adı / URL slug değiştir
> C) SEO meta (title, description) değiştir
> D) Performance / cache ayarları
```

with:

```markdown
> Teknik konularda?
>
> A) Deploy hedefi değiştir (örn. Cloudflare → Vercel)
> B) Site adı / URL slug değiştir
> C) SEO meta (title, description) değiştir
> D) Performance / cache ayarları
> E) Stack değiştir (örn. Astro → Next.js — siteyi baştan üreteceğim)
> F) Scope değiştir (örn. tek sayfa → çok sayfalı — büyük değişiklik)
> G) Backend stack değiştir (sadece full-app için, örn. Next.js API → Go)
> H) Database değiştir (sadece full-app için)
```

For E and F, surface a confirmation: "Bu büyük bir değişiklik — site yeniden üretilecek. Devam edelim mi?" before returning the change record.

For G and H, only show in revise if `state.json.scope == "full-app"`. If scope is not full-app, skip these options.

- [ ] **Step 3: Verify**

Run: `grep -c "Stack değiştir" skills/web-builder-revise/SKILL.md`
Expected: 1.

Run: `grep -c "Backend stack değiştir" skills/web-builder-revise/SKILL.md`
Expected: 1.

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-revise/SKILL.md
git commit -m "feat: revise skill technical category gains stack/scope/backend/db options"
```

---

## Task 11: Update Deployer — Scope-Aware Defaults

**Files:**
- Modify: `agents/deployer.md`

Currently deployer treats all scopes the same. Spec says full-app's default is Vercel (not Cloudflare Pages). Add a hint at the top of the deployer's pre-flight that surfaces the recommended target per scope.

- [ ] **Step 1: Edit pre-flight section**

Open `agents/deployer.md` and locate the `## Pre-flight (for all cloud targets)` section.

- [ ] **Step 2: Add scope-aware default note**

Insert at the top of the pre-flight section, before the dist-missing check:

```markdown
Read `state.json.scope`. The recommended deploy target depends on scope:

- `single-page`, `multi-page-static`, `interactive-static` → **Cloudflare Pages** (free tier, custom domain easy)
- `full-app` → **Vercel** (native Next.js / SvelteKit support, serverless functions for API routes)

The deliver skill will already have asked the user; this is just for your reference. If the user chose a target inappropriate for the scope (e.g., Cloudflare Pages for a Next.js full-app), warn them via the `human-readable` field but proceed with their choice — they may have their reasons.
```

- [ ] **Step 3: Lint**

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 4: Commit**

```bash
git add agents/deployer.md
git commit -m "docs: deployer documents scope-aware target recommendations"
```

---

## Task 12: Update Deliver Skill — Deploy Default Per Scope

**Files:**
- Modify: `skills/web-builder-deliver/SKILL.md`

Deploy prompt currently says "A) Cloudflare Pages (önerilen)". For full-app, the recommendation should be Vercel. Make the recommendation dynamic.

- [ ] **Step 1: Locate deploy prompt**

In `skills/web-builder-deliver/SKILL.md`, find step 5 (the deploy prompt with options A-E).

- [ ] **Step 2: Update the option labels**

Use Edit to replace:

```
   > A) Cloudflare Pages (önerilen — en cömert ücretsiz plan, custom domain kolay)
   > B) Vercel (Next.js için en doğal, statik için de iyi)
```

with:

```
   > A) Cloudflare Pages ({"önerilen — en cömert ücretsiz plan, custom domain kolay" if scope is static, otherwise "iyi statik seçenek"})
   > B) Vercel ({"önerilen — Next.js / SvelteKit için en doğal" if scope is full-app, otherwise "Next.js için iyi, statik için de uygun"})
```

The text inside `{}` is a directive to the skill: "show this label if the condition holds, otherwise the alternative". The skill can render the right label by reading state.json.scope.

- [ ] **Step 3: Verify**

Run: `grep -c "önerilen — en cömert" skills/web-builder-deliver/SKILL.md`
Expected: 1.

Run: `grep -c "önerilen — Next.js / SvelteKit" skills/web-builder-deliver/SKILL.md`
Expected: 1.

- [ ] **Step 4: Commit**

```bash
git add skills/web-builder-deliver/SKILL.md
git commit -m "feat: deploy prompt recommends scope-appropriate target (CF Pages vs Vercel)"
```

---

## Task 13: Add Fixtures for New Scopes

**Files:**
- Create: `tests/fixtures/sample-brief-single-page.md`
- Create: `tests/fixtures/sample-brief-full-app.md`

Reference fixtures for the new scopes so smoke tests have concrete inputs.

- [ ] **Step 1: Write `tests/fixtures/sample-brief-single-page.md`**

```markdown
# Site Briefi: ada-yazilim-cv

## Scope
single-page

## Amaç
Ada Yılmaz'ın yazılım geliştirici CV / portfolio tek sayfası. Kendi adıyla domain alacak (ada.dev gibi).

## Hedef Kitle
İşveren ve teknik recruiter'lar.

## Sayfa Listesi
- Ana sayfa (tek sayfa içinde: hakkımda + projeler + iletişim bölümleri)

## İçerik Kaynağı
Plugin örnek içerik üretecek (kullanıcı sonra düzenleyecek).

## Stil Tercihi
Hazır stil: minimalist (siyah-beyaz + bir accent rengi)

## Davranış / Etkileşim
- Tek sayfa, scroll-to-section navigasyonu yeterli.

## Teknik
- Stack: vanilla
- Backend: n/a
- Database: n/a
- TypeScript: false
- Linter: false
- Deploy hedefi: Cloudflare Pages
```

- [ ] **Step 2: Write `tests/fixtures/sample-brief-full-app.md`**

```markdown
# Site Briefi: takim-takip

## Scope
full-app

## Amaç
Küçük ekipler için basit görev takip uygulaması. Kullanıcılar üye olur, görev oluşturur, atayan, durumunu işaretler.

## Hedef Kitle
3-10 kişilik ekipler.

## Sayfa Listesi
- Giriş / Üye Ol
- Dashboard (kendi görevlerim)
- Tüm görevler (filtre ile)
- Görev detay
- Ekip üyeleri

## İçerik Kaynağı
Plugin örnek içerik üretecek (UI string'ler dahil — buton labelları, hata mesajları, boş state'ler).

## Stil Tercihi
Hazır stil: kurumsal (mavi-gri palet, sade)

## Davranış / Etkileşim
- Auth: email + parola (OAuth yok bu sürümde)
- CRUD: görev oluştur, düzenle, sil, atayan değiştir
- Real-time: yok (manuel refresh yeterli)

## Teknik
- Stack: nextjs+tailwind
- Backend: nextjs-api
- Database: sqlite-prisma
- TypeScript: true
- Linter: true
- Deploy hedefi: Vercel
```

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/sample-brief-single-page.md tests/fixtures/sample-brief-full-app.md
git commit -m "test: add brief fixtures for single-page and full-app scopes"
```

---

## Task 14: Smoke Tests for New Scopes + Dev Mode

**Files:**
- Modify: `tests/smoke-test.md`

Add Tests 11-14:
- Test 11: single-page scope sade mode (vanilla output)
- Test 12: full-app scope sade mode (Next.js + SQLite)
- Test 13: dev mode multi-page-static with stack override (user picks Next.js instead of Astro)
- Test 14: revise — change scope (multi-page → interactive)

- [ ] **Step 1: Append the new tests just before `## Pass criteria`**

(Same insertion approach as previous plans — use Edit to find `## Pass criteria` and insert the new tests above it.)

Test 11 outline:
```
## Test 11: Single-page scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At the scope question, pick A (tek sayfa).
3. Continue with default content + minimalist style.
4. Plugin generates vanilla HTML/CSS/JS site (no node_modules).
5. Verify: open index.html in browser.

Pass: index.html exists, opens directly without any build step, has site title from content.md, palette from style-guide.md visible.
```

Test 12 outline:
```
## Test 12: Full-app scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At scope question, pick D (üye girişi / sipariş / veri kaydı).
3. Use the takim-takip example from sample-brief-full-app.md as inspiration for your answers.
4. Plugin generates Next.js + Prisma + SQLite project.
5. Both frontend-expert and backend-engineer ran (verified in state.json.agentRuns).
6. Verify: `npm install && npm run build` succeeds.

Pass: dist exists OR `next build` succeeds; prisma/schema.prisma has models; app/api/ has route files; sign-in / dashboard pages exist.
```

Test 13 outline:
```
## Test 13: Dev mode with stack override

1. Run `/web-builder-dev` in a clean dir.
2. At scope, pick B (multi-page-static).
3. At stack question, pick D (Next.js + Tailwind) — overriding the Astro default.
4. Continue with defaults.
5. Plugin generates Next.js multi-page site (NOT Astro).

Pass: package.json has next as dep; app/ directory exists; no astro.config.mjs.
```

Test 14 outline:
```
## Test 14: Revise — scope change (multi-page → interactive)

1. After Test 1 generation succeeds, run `/web-builder` again.
2. Pick A (devam et / revize), then E (technical), then F (Scope değiştir).
3. Pick interactive-static.
4. Plugin warns "büyük değişiklik" and asks confirmation.
5. Confirm.
6. Plugin re-runs all agents; new project structure has Astro+islands.

Pass: state.json.scope is now interactive-static; package.json has @astrojs/preact; an example interactive component exists in src/components/.
```

(Each test gets its own h2 section; full body included in the smoke-test doc.)

- [ ] **Step 2: Verify test count**

Run: `grep -nE "^## Test [0-9]+:" tests/smoke-test.md`
Expected: 14 test sections (Tests 1-14).

- [ ] **Step 3: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: smoke tests for single-page, full-app, dev mode, scope-change revision"
```

---

## Task 15: Update README + plugin.json to v0.4.0

**Files:**
- Modify: `README.md`
- Modify: `plugin.json`

- [ ] **Step 1: Replace README Status section**

Use Edit to change Status to:

```markdown
## Status

**v0.4.0.** All 4 site scopes supported (single page, multi-page static, interactive static, full app), in sade or dev mode.

- ✅ Generate any of 4 scope types from Q&A
- ✅ Sade mode: plugin picks stack defaults silently
- ✅ Dev mode (`/web-builder-dev`): user overrides frontend / backend / database / TypeScript / lint
- ✅ 5 frontend stacks supported (vanilla / Astro / Astro+islands / Next.js / SvelteKit)
- ✅ 5 backend stacks for full-app (Next.js API / Node+Express / Go / Java/Spring / Python/FastAPI)
- ✅ 3 database options (SQLite / Postgres / MongoDB) plus none
- ✅ Preview locally with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages (scope-aware default)
- ✅ Auto git initialization in sade mode
- ✅ Revise existing projects with structured Q&A + impact analysis + undo

Not yet supported (coming in later versions): SEO/accessibility agents, custom domain automation, multi-language site output, public Claude Code plugin distribution.
```

- [ ] **Step 2: Update architecture line**

Replace the architecture one-liner with:

```
Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle the dialog. Agents (`ui-ux-designer`, `content-writer`, `frontend-expert`, `backend-engineer`, `deployer`) write the actual files in their own context — each is stack/scope-aware (reads `state.json` and branches). State lives in `state.json` plus a few human-readable markdown files.
```

- [ ] **Step 3: Update Use section**

Add a paragraph about dev mode:

```markdown
For technical users who want to pick the stack (Astro vs Next.js vs SvelteKit, Node vs Go vs Python backend, SQLite vs Postgres):

```
/web-builder-dev
```

Same Q&A flow but with stack-choice questions added.
```

- [ ] **Step 4: Bump plugin.json version**

Change `"version": "0.3.0"` to `"version": "0.4.0"`.

- [ ] **Step 5: Verify**

Run: `python3 -c "import json; print(json.load(open('plugin.json'))['version'])"`
Expected: `0.4.0`.

Run: `grep -c "v0.4.0" README.md`
Expected: at least 1.

Run: `grep -c "/web-builder-dev" README.md`
Expected: at least 1 (in the Use section).

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 6: Commit**

```bash
git add README.md plugin.json
git commit -m "docs: bump to v0.4.0 (multi-scope + multi-stack + dev mode shipped)"
```

---

## Task 16: Final Lint, Structural Smoke Test, Tag v0.4.0, Push, Merge

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 2: Structural smoke test — single-page sade mode**

Create a temp project, copy `sample-brief-single-page.md` as the brief, write a sample state.json with `scope: single-page, stack: vanilla, mode: simple`, and dispatch the frontend-expert agent. Verify it generates `index.html`, `style.css`, `main.js` (no node_modules, no build step).

- [ ] **Step 3: Structural smoke test — full-app sade mode**

Similar setup with full-app fixture; dispatch frontend-expert AND backend-engineer in sequence (or simulate parallel dispatch). Verify:
- frontend-expert produces Next.js project files (app/, package.json with next dep)
- backend-engineer produces app/api/ routes + prisma/schema.prisma

- [ ] **Step 4: Structural smoke test — dev mode override**

Create state.json with `mode: dev, scope: multi-page-static, stack: nextjs+tailwind`. Dispatch frontend-expert. Verify it generates Next.js project (not Astro), confirming the agent reads state.json.stack.

- [ ] **Step 5: Tag v0.4.0**

```bash
git tag -a v0.4.0 -m "v0.4.0: multi-scope + multi-stack + dev mode

- 4 site scopes: single-page, multi-page-static, interactive-static, full-app
- 5 frontend stacks: vanilla / Astro / Astro+islands / Next.js / SvelteKit
- 5 backend stacks for full-app: Next.js API / Node+Express / Go / Java / Python
- 3 database options: SQLite / Postgres / MongoDB (plus none)
- New /web-builder-dev slash command for dev mode
- All agents stack/scope-aware (read state.json, branch internally)
- New backend-engineer agent for full-app scope
- Orchestrator runs frontend+backend in parallel for full-app
- Revise skill technical category gains stack/scope/backend/db options
- Smoke tests for new scopes + dev mode + scope-change revision
"
```

- [ ] **Step 6: Push and merge**

```bash
git push origin plan-4-multi-scope-and-dev-mode
git push --tags
git checkout main
git merge --ff-only plan-4-multi-scope-and-dev-mode
git push origin main
git branch -d plan-4-multi-scope-and-dev-mode
```

---

## Done criteria for this plan

- [ ] All 16 tasks complete with lint passing (`12 passed, 0 failed` — 1 plugin.json + 2 commands + 4 skills + 5 agents).
- [ ] `/web-builder-dev` exists and triggers dev mode.
- [ ] Intake skill asks 4-scope question (sade) + stack/backend/db questions (dev).
- [ ] `frontend-expert` has 5 stack branches (vanilla/astro/astro+islands/nextjs/sveltekit).
- [ ] `backend-engineer` agent exists with 5 backend branches.
- [ ] Orchestrator runs backend in parallel with frontend for full-app.
- [ ] Revise skill technical category lists 8 sub-options including stack/scope/backend/db.
- [ ] Deployer + deliver use scope-aware defaults.
- [ ] At least 3 of 4 scopes pass structural smoke (single-page vanilla, full-app Next.js+SQLite, dev-mode multi-page-static + Next.js override).
- [ ] `git tag --list` shows `v0.4.0`.
- [ ] No `TBD` / `TODO` strings in any active plugin file.

## Out of scope for this plan (deferred)

- SEO + accessibility agents (Plan 5)
- Public Claude Code plugin distribution (Plan 6 — repo already exists privately)
- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup (per spec)
- More frontend frameworks (Remix, Solid, Vue) — tractable adds in v0.5
- More backend frameworks (Rust, .NET, Elixir) — tractable adds in v0.5
- ORM choice between Prisma / Drizzle / raw SQL — Prisma is hardcoded for SQL stacks in v0.4.0
- OAuth / SSO authentication (only email+password in v0.4.0)
- Real-time features (websockets, SSE) — not in v0.4.0

## Risks and edge cases

- **Frontend-expert file size**: ~600-800 lines in v0.4.0. Acceptable for MVP. If it grows beyond 1000, consider splitting into per-stack agent files in a future plan.
- **Backend-engineer file size**: similar, ~600-800 lines.
- **Stack mismatch during revision**: if user revises stack (option E in technical category), all agents re-run. The pre-revision auto-commit ensures undo works.
- **Auth scaffolding scope**: limited to email+password in v0.4.0. OAuth requires additional setup (env vars, callback URLs) that's out of scope for an MVP backend agent.
- **Build time**: full-app scope (Next.js + Prisma) takes longer than single-page (no build). Acceptable; the `--silent` flag keeps output manageable.
- **Java/Spring tooling**: requires Maven installed locally. If absent, backend-engineer warns and skips the build step.
- **Go module path**: `backend/go.mod` uses a default module name (e.g., `siteName/backend`). Users with their own Go convention can edit afterward.
