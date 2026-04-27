# web-builder Plan 4: Multi-Scope + Dev Mode (Stack-Agnostic)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support all 4 site scopes (single page, multi-page static, interactive static, full app) — in sade mode with sensible defaults, or in dev mode where the user can express preferences (interactivity level, performance priority, preferred language). The plugin **does not name specific frameworks anywhere**. Worker agents read user preferences from `state.json` and pick the most appropriate stack at runtime using Claude's current ecosystem knowledge.

**Why stack-agnostic:** Frameworks evolve fast. A plan that hardcodes "Astro / Next.js / SvelteKit" is brittle — in 1-2 years a different stack may dominate. By delegating the choice to Claude at runtime, the plugin remains future-proof: whatever framework is best when the plugin runs gets used.

**Architecture:** Two slash commands (`/web-builder` sade, `/web-builder-dev` dev). Intake asks scope (always) + preferences (dev mode only) — never enumerates frameworks. Worker agents (`ui-ux-designer`, `content-writer`, `frontend-expert`, new `backend-engineer`) each read scope + preferences from `state.json` and decide what to produce; `frontend-expert` and `backend-engineer` additionally pick a specific stack at runtime and record their choice in `state.json.chosenStack`. Orchestrator's agent execution graph adapts per scope (skip backend for static, parallel frontend+backend for full-app).

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). Generated projects span whatever Claude picks — typically modern frontend frameworks (vanilla / Astro-like / Next-like / SvelteKit-like / new entrants like Solid/Qwik) and backend frameworks (Node / Go / Python / Java / etc.) plus a database appropriate to the choice.

**v0.4.0 scope:**
- 4 user-facing scopes (single-page, multi-page-static, interactive-static, full-app) — the only enumeration the plugin owns
- Sade mode: agents pick stack silently from minimal user input
- Dev mode: agents pick stack informed by user preferences (or fully delegate if user says "you decide")
- New `backend-engineer` agent for full-app
- All agents stack-agnostic in code; pick at runtime

**Definition of done:**
- A user can run `/web-builder`, pick any of 4 scopes, and end up with a working project in **whatever stack the agent picked** for that scope. No errors about "stack not supported".
- A user can run `/web-builder-dev` and express preferences (interactivity / performance / preferred language). The agent's pick respects those preferences when reasonable.
- `state.json.chosenStack` is populated after first agent run with the agent's decision (frontend / backend / database / rationale).
- Smoke test: structurally verify each scope produces a buildable artifact. Don't pin the stack name — verify only that some recognizable framework files exist.

**Out of scope (deferred):**
- SEO + accessibility agents (Plan 5)
- Public Claude Code plugin distribution (Plan 6)
- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup (per spec)
- OAuth / SSO authentication (only email+password possible if Claude picks an auth scheme)
- Real-time features (websockets, SSE) — only if Claude picks a stack that includes them and the brief requests it

---

## File Structure

```
web-builder/
├── plugin.json                                  # MODIFY: bump version to 0.4.0
├── README.md                                    # MODIFY: status to v0.4.0; emphasize "Claude picks the stack"
├── commands/
│   ├── web-builder.md                           # MODIFY: small body update (no longer claims "no scope questions")
│   └── web-builder-dev.md                       # CREATE: dev mode entry
├── skills/
│   ├── web-builder-orchestrator/SKILL.md        # MODIFY: scope-aware agent graph (parallel for full-app)
│   ├── web-builder-intake/SKILL.md              # MODIFY: scope question (sade) + preference questions (dev)
│   ├── web-builder-revise/SKILL.md              # MODIFY: technical category gains preference-change option
│   └── web-builder-deliver/SKILL.md             # MODIFY: scope-aware preview, deploy default
├── agents/
│   ├── ui-ux-designer.md                        # MODIFY: scope-aware (no stack mention)
│   ├── content-writer.md                        # MODIFY: scope-aware (no stack mention)
│   ├── frontend-expert.md                       # REWRITE: stack-agnostic — agent picks at runtime
│   ├── backend-engineer.md                      # CREATE: stack-agnostic backend; only invoked for full-app
│   └── deployer.md                              # MODIFY: scope-aware target defaults (Cloudflare Pages vs Vercel)
├── tests/
│   ├── fixtures/
│   │   ├── sample-brief.md                      # unchanged
│   │   ├── sample-brief-single-page.md          # CREATE (preferences-based, no stack pinned)
│   │   ├── sample-brief-full-app.md             # CREATE (preferences-based, no stack pinned)
│   │   ├── sample-style-guide.md                # unchanged
│   │   ├── sample-content.md                    # unchanged
│   │   └── sample-state.json                    # unchanged (Plan 5 will extend if needed)
│   ├── lint.sh                                  # unchanged (auto-picks up new agent + command)
│   └── smoke-test.md                            # MODIFY: add Tests 11-14 for new scopes + dev mode
└── docs/
    └── plans/
        ├── 2026-04-26-plan-2-preview-and-deploy.md
        ├── 2026-04-27-plan-3-revision-flow.md
        └── 2026-04-27-plan-4-multi-scope-and-dev-mode.md  # this file
```

**Responsibilities:**

| File | Owns |
|---|---|
| `commands/web-builder-dev.md` | Dev-mode entry; sets `mode=dev` for orchestrator |
| `agents/backend-engineer.md` | Full-app backend code generation. Reads scope + preferences, picks a backend stack and database appropriate for "right now", generates code, records choice in `state.json.chosenStack.backend` and `.database` |
| `agents/frontend-expert.md` (rewritten) | Picks a frontend stack at runtime based on scope + preferences, generates code, records choice in `state.json.chosenStack.frontend` |
| Existing agents (modified) | Read scope from `state.json` and adapt their output template (e.g., designer adds component states for full-app); none of them name specific frameworks |

---

## Task 1: `/web-builder-dev` Slash Command

**Files:**
- Create: `commands/web-builder-dev.md`

- [ ] **Step 1: Write the dev-mode command file**

Create `commands/web-builder-dev.md`:

```markdown
---
description: Build a website end-to-end through guided Q&A — dev mode (asks technical preferences like interactivity level, performance priority, language preference; the plugin still picks the framework, but with your input).
---

You are entering the web-builder flow in **dev mode** — a slightly more technical Q&A. The user can express preferences (e.g., "I care about fast initial load", "I prefer Python on the backend", "let me write the JavaScript myself") and these inform the agent's framework choice. Plain language is still preferred.

Use the `Skill` tool to invoke the `web-builder-orchestrator` skill, passing `mode=dev`.

Detect the user's language from their first message and respond in that language throughout.

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

The Plan 1 command says "no stack-choice questions". With Plan 4, the plugin still doesn't ask stack questions in sade mode — but it does ask the SCOPE question now. Update the description so it doesn't make a misleading claim.

- [ ] **Step 1: Read current command**

Run: `cat commands/web-builder.md`

- [ ] **Step 2: Replace the "sade mode" line**

Use Edit to replace:

```
You are entering the web-builder flow in **sade mode** (plain language, no jargon, no stack-choice questions).
```

with:

```
You are entering the web-builder flow in **sade mode** (plain language, no jargon — the plugin asks plain-language questions about the kind of site you want, and the framework/language choice is made automatically by the agent at generation time).
```

- [ ] **Step 3: Verify**

Run: `grep -c "no stack-choice questions" commands/web-builder.md`
Expected: 0.

Run: `grep -c "framework/language choice is made automatically" commands/web-builder.md`
Expected: 1.

- [ ] **Step 4: Commit**

```bash
git add commands/web-builder.md
git commit -m "docs: update /web-builder description for multi-scope sade mode"
```

---

## Task 3: Update Intake Skill — Scope + Preferences (No Stack Names)

**Files:**
- Modify: `skills/web-builder-intake/SKILL.md`

Currently intake hardcodes scope=multi-page-static. Plan 4 makes it ask the scope question and (in dev mode only) collect preferences. Critically: **no specific framework names appear in the questions or the brief.**

- [ ] **Step 1: Replace the constraints section**

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

- **Sade mode (this skill is invoked from `/web-builder`):** ask scope (Q2 below); do NOT ask about frameworks or languages; the worker agents will pick automatically.
- **Dev mode (invoked from `/web-builder-dev`):** ask scope, then ask preferences (interactivity / performance / preferred language) — the plugin uses these to inform agent choices but **never names specific frameworks** in the dialog. The agent picks at runtime.
- Image strategy: contextual Unsplash placeholders for both modes.
- The orchestrator passes you a `mode` parameter (`simple` or `dev`); branch on it.
- **Do not enumerate frameworks anywhere.** No "Astro vs Next.js" choice. The agents decide.
```

- [ ] **Step 2: Replace Q2 with the new scope question**

Use Edit to replace the entire current Q2 section (the one that confirms multi-page-static) with:

````markdown
### Q2: Site scope

> Ne tür bir site yapacağız?
>
> A) Tek sayfa (kısa tanıtım, one-pager)
> B) Çok sayfalı tanıtım (ana sayfa + hakkımızda + iletişim falan, hafif ya da hiç etkileşim yok)
> C) Çok sayfalı + bir-iki etkileşim (form, galeri, küçük JS özellikleri)
> D) Üye girişi / sipariş / veri kaydı olan tam uygulama

Map the answer:
- A → `single-page`
- B → `multi-page-static`
- C → `interactive-static`
- D → `full-app`

Capture as `scope`.

In **dev mode only**, after scope, also ask the preference questions below. In **sade mode**, skip them entirely — the agents will pick reasonable defaults based on scope alone.
````

- [ ] **Step 3: Add a new "Dev mode preferences" section after Q2**

Insert this new section right after Q2 (before Q3 — project name):

````markdown
### Q2-dev-prefs: Dev mode preferences (only if mode == dev)

#### Q2-dev-prefs-1: Performance vs simplicity

> Bu site için ne daha önemli?
>
> A) Mümkün olduğunca basit ve hızlı kurulum (build step bile olmasın istersen)
> B) Modern, hızlı (küçük bundle, fast page loads)
> C) İçerik/feature ağırlıklı (build complexity sorun değil, ama maintainable olsun)
> D) Fark etmez, sen seç

Capture as `preferences.priority` (one of `simple`, `performance`, `feature-richness`, `claude-decides`).

#### Q2-dev-prefs-2: Interactivity (only ask for `interactive-static` or `full-app`)

> Sitede ne kadar JS-tabanlı etkileşim olacak?
>
> A) Az (sadece bir-iki yerde küçük etkileşim)
> B) Orta (form'lar, küçük UI bileşenleri, biraz dinamik içerik)
> C) Çok (gerçek anlamda app — sürekli state, complex flows)
> D) Fark etmez, sen seç

Capture as `preferences.interactivity` (one of `low`, `medium`, `high`, `claude-decides`).

#### Q2-dev-prefs-3: Backend language (only ask for `full-app`)

> Backend tarafı için bir dil/ekosistem tercihin var mı?
>
> A) Frontend'le aynı paket olsun (tek node projesi)
> B) Ayrı bir Node servisi
> C) Python kullanmak isterim
> D) Go / Rust / başka bir compiled language
> E) Java / .NET ekosistemi
> F) Fark etmez, sen seç

Capture as `preferences.backendLang` (one of `same-as-frontend`, `node-separate`, `python`, `compiled`, `enterprise-jvm`, `claude-decides`).

The plugin does NOT enumerate specific frameworks (Express vs Fastify vs Hono; Django vs FastAPI vs Flask). The agent picks within whichever bucket the user chose.

#### Q2-dev-prefs-4: Database (only ask for `full-app`)

> Database için tercihin?
>
> A) En basit (file-based, sıfır ayar — sen seçersin)
> B) Klasik SQL (Postgres ya da benzeri — sen seçersin)
> C) Document DB (MongoDB ya da benzeri — sen seçersin)
> D) Yok / kendim halledeceğim
> E) Fark etmez, sen seç

Capture as `preferences.dbStyle` (one of `simple`, `sql`, `document`, `none`, `claude-decides`).

#### Q2-dev-prefs-5: TypeScript

> TypeScript kullanalım mı?
>
> A) Evet
> B) Hayır
> C) Sen seç (scope'a göre uygun olanı)

Capture as `preferences.typescript` (one of `true`, `false`, `claude-decides`).

The whole point is: dev mode collects user-facing intent ("I want fast", "I prefer Python") — never specific tool names. The agent's job is to translate intent into the most appropriate tool **right now**.
````

- [ ] **Step 4: Update the side effects section (state.json write) to include preferences and chosenStack placeholder**

In the `## Side effects` step that currently writes initial state.json, update it to write:

```
mode: <simple|dev>
scope: <captured value>
siteName: <captured>
siteLanguage: <captured>
createdAt: <ISO>
lastModified: <ISO>
agentRuns: []
preferences: {
  // Only in dev mode; sade mode leaves this as null or empty {}
  priority: <captured | null>,
  interactivity: <captured | null>,
  backendLang: <captured | null>,
  dbStyle: <captured | null>,
  typescript: <captured | null>
}
chosenStack: {
  // Populated by frontend-expert (and backend-engineer for full-app) on first run.
  // Intake leaves this as null.
  frontend: null,
  backend: null,
  database: null,
  rationale: null
}
```

The orchestrator and agents will populate `chosenStack` as they run. Intake just initializes the field structure.

- [ ] **Step 5: Verify**

Run: `grep -c "Astro\|Next\.js\|SvelteKit\|Vue\|React\|Django\|FastAPI\|Express" skills/web-builder-intake/SKILL.md`
Expected: 0. (Critical — the intake skill must not name any specific framework.)

Run: `grep -c "preferences" skills/web-builder-intake/SKILL.md`
Expected: at least 5.

Run: `grep -c "chosenStack" skills/web-builder-intake/SKILL.md`
Expected: at least 1.

Run: `grep -c "claude-decides" skills/web-builder-intake/SKILL.md`
Expected: at least 4.

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.` (after Task 1 added the new command file).

- [ ] **Step 6: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "feat: intake supports 4 scopes (sade) + framework-agnostic preferences (dev)"
```

---

## Task 4: Update `brief.md` Template

**Files:**
- Modify: `skills/web-builder-intake/SKILL.md` (the brief.md template inside it)

The current template has a `## Teknik` section with "Stack: ...". Plan 4 changes this to be intent-focused: `## Scope` (the user-facing concept) and `## Preferences` (intent in dev mode). The agent records its actual stack choice in `state.json.chosenStack`, NOT in `brief.md`.

- [ ] **Step 1: Locate brief.md template**

In `skills/web-builder-intake/SKILL.md`, find the section starting `## brief.md template` and the markdown content inside it.

- [ ] **Step 2: Add Scope section + replace Teknik with Preferences**

Restructure the brief template as:

```markdown
# Site Briefi: {siteName}

## Scope
{scope value: single-page | multi-page-static | interactive-static | full-app}

## Amaç
{user goal}

## Hedef Kitle
{target audience}

## Sayfa Listesi
- ...

## İçerik Kaynağı
{user-provided | plugin-generated}

## Stil Tercihi
{preset name}

## Davranış / Etkileşim
{interaction notes}

## Preferences (only populated in dev mode)
- Priority: {simple | performance | feature-richness | claude-decides | null}
- Interactivity: {low | medium | high | claude-decides | null}
- Backend language: {same-as-frontend | node-separate | python | compiled | enterprise-jvm | claude-decides | null}
- Database style: {simple | sql | document | none | claude-decides | null}
- TypeScript: {true | false | claude-decides | null}
```

If the user is writing in English, use English headings (`Scope`, `Goal`, `Audience`, `Pages`, `Content Source`, `Style`, `Interactivity`, `Preferences`).

The brief deliberately does NOT mention specific frameworks. The agent's choice is logged in `state.json.chosenStack`, not in brief.md.

- [ ] **Step 3: Verify**

Run: `grep -c "## Scope" skills/web-builder-intake/SKILL.md`
Expected: at least 1.

Run: `grep -c "## Preferences" skills/web-builder-intake/SKILL.md`
Expected: at least 1.

Run: `grep -c "Stack:" skills/web-builder-intake/SKILL.md`
Expected: 0. (Old template had this. Should be removed.)

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.`

- [ ] **Step 4: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "docs: brief.md template uses Scope + Preferences (no stack names)"
```

---

## Task 5: Make `ui-ux-designer` Scope-Aware (Stack-Agnostic)

**Files:**
- Modify: `agents/ui-ux-designer.md`

The designer's output (palette, typography, spacing, component notes) is already stack-agnostic by nature. We just need to extend the template per scope (full-app needs more component states, layout patterns, empty/error/loading designs). No stack mentions.

- [ ] **Step 1: Insert scope-aware extensions section**

Use Edit to insert a new section between `## Output` and `## style-guide.md template`:

```markdown
## Scope-aware extensions

Read `{projectPath}/.web-builder/state.json` to get `scope`. Extend the style guide depending on scope:

- **single-page:** Standard palette, typography, spacing. Component notes can omit Cards if the page doesn't have them.
- **multi-page-static:** Standard. All sections of the template apply.
- **interactive-static:** Add a `## Interactive components` section: input field styling, button hover/active/disabled states, modal/dialog tokens, animation easing curves.
- **full-app:** Add three sections beyond the standard:
  - `## Component states` — for buttons, inputs, links, cards: visual treatments for `default | hover | active | disabled | loading | error`
  - `## Layout patterns` — sidebar+main, dashboard grid, form layouts, list/detail views (these are visual patterns, not framework-specific)
  - `## Empty / error / loading states` — visual treatments for "no data", "error", "loading skeleton"

Do not name any specific framework or library. The output is design tokens and visual descriptions only — `frontend-expert` translates them into whatever stack it picks.
```

- [ ] **Step 2: Verify**

Run: `grep -c "Scope-aware extensions" agents/ui-ux-designer.md`
Expected: 1.

Run: `grep -cE "Astro|Next\.js|SvelteKit|React|Vue" agents/ui-ux-designer.md`
Expected: 0.

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/ui-ux-designer.md
git commit -m "feat: ui-ux-designer adapts style guide to project scope (no stack mention)"
```

---

## Task 6: Make `content-writer` Scope-Aware (Stack-Agnostic)

**Files:**
- Modify: `agents/content-writer.md`

Same pattern: scope-aware additions, no framework mentions. Full-app needs UI strings, auth flow strings, notification messages. These are language-of-the-site copy, not framework-specific.

- [ ] **Step 1: Insert scope-aware extensions section**

Use Edit to insert a new section between `## Output` and `## content.md template` in `agents/content-writer.md`:

```markdown
## Scope-aware extensions

Read `{projectPath}/.web-builder/state.json` to get `scope`. Extend `content.md` depending on scope:

- **single-page:** Standard template — site-wide, hero, sections.
- **multi-page-static:** Standard template — multiple pages.
- **interactive-static:** After per-page sections, add:
  - `## Interaction copy` — labels for buttons in interactive components (form submit, gallery prev/next, slider play/pause, etc.)
- **full-app:** Add three sections:
  - `## UI strings` — button labels, link text, form field labels, validation messages, error messages, empty-state messages, loading text. Action-oriented and concrete.
  - `## Auth flow strings` — sign-in / sign-up / reset-password page copy if the brief mentions auth
  - `## Notification / toast messages` — for common actions (saved, deleted, error)

Output is copy in the user's site language. Do not mention any specific framework or library — the frontend-expert and backend-engineer agents pick those at generation time.
```

- [ ] **Step 2: Verify**

Run: `grep -c "Scope-aware extensions" agents/content-writer.md`
Expected: 1.

Run: `grep -c "UI strings" agents/content-writer.md`
Expected: 1.

Run: `grep -cE "Astro|Next\.js|SvelteKit|React|Vue" agents/content-writer.md`
Expected: 0.

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/content-writer.md
git commit -m "feat: content-writer adapts content to project scope (UI strings, auth, notifications)"
```

---

## Task 7: Rewrite `frontend-expert` to Pick Stack at Runtime

**Files:**
- Modify: `agents/frontend-expert.md` (rewrite — significantly smaller than v0.1's hardcoded-Astro version)

This is the heart of the stack-agnostic approach. The agent reads brief, style-guide, content, scope, preferences — then picks a frontend stack appropriate for *right now* (Claude's current ecosystem knowledge), generates the project, and records the choice.

- [ ] **Step 1: Rewrite the agent file**

Replace the entire body of `agents/frontend-expert.md` (preserve frontmatter) with:

````markdown
# frontend-expert agent (stack-agnostic)

You generate a working frontend project. You pick the framework/language at runtime based on the user's scope and preferences — the plugin does NOT prescribe a stack. Choose what is most appropriate **right now**, given current ecosystem maturity, popularity, and fit.

## Inputs

Read in this order:
1. `{projectPath}/.web-builder/state.json` — `scope`, `mode`, `preferences`, `siteLanguage`
2. `{projectPath}/brief.md` — page list, site name
3. `{projectPath}/style-guide.md` — palette, typography, spacing, component notes
4. `{projectPath}/content.md` — per-page content, image URLs

If `state.json.chosenStack.frontend` is already populated (from a prior run), respect it — generate in that same stack. The user expects continuity across revisions unless they explicitly ask for a stack change.

## Decision: pick the frontend stack

You are deciding between any modern frontend approach available **today**. Your decision should consider, in order:

1. **Scope** — drives the upper bound:
   - `single-page`: simplest is best. Vanilla HTML/CSS/JS often wins. No build step preferred unless interactivity demands it.
   - `multi-page-static`: a content-oriented framework that can statically generate multiple pages, or a meta-framework with SSG support.
   - `interactive-static`: same as multi-page-static but with island/partial-hydration capability for interactive components.
   - `full-app`: a mature meta-framework that handles routing, server functions, data fetching, and (often) auth out of the box.

2. **User preferences** (from `state.json.preferences`):
   - `priority: simple` → lean toward zero-build or minimal-config solutions
   - `priority: performance` → lean toward small-bundle, fast-hydration solutions
   - `priority: feature-richness` → lean toward batteries-included frameworks
   - `priority: claude-decides` (or null in sade mode) → use your judgment; default to the most popular & well-maintained option for the scope
   - `interactivity: low` → static-first, hydrate sparingly
   - `interactivity: high` → SPA-like or full reactive framework
   - `typescript: true` → ensure TS support out of the box
   - `typescript: false` → plain JavaScript only
   - `typescript: claude-decides` → default per stack convention

3. **Current ecosystem snapshot** (use your knowledge as of the run date):
   - Pick frameworks that are actively maintained, well-documented, with healthy community
   - Avoid abandoned or niche projects unless they uniquely fit a preference
   - Avoid bleeding-edge tools that lack production usage

You are NOT restricted to any specific list. If today the best fit is a framework that didn't exist 12 months ago, pick that. The plugin trusts your judgment.

## Decision: record your choice

After deciding, write to `state.json.chosenStack`:

```json
"chosenStack": {
  "frontend": "<framework name and version, e.g., 'astro@4.16' or 'vanilla' or 'qwik@1.5'>",
  "backend": <existing value or null>,
  "database": <existing value or null>,
  "rationale": "<one or two sentences explaining why this stack fits, in the user's language>"
}
```

The rationale is user-facing — write it in plain language matching `state.json.siteLanguage`. Example rationales:
- "Tek sayfa için vanilla HTML/CSS/JS yeterli; build step yok, herhangi bir hosting'de çalışır."
- "Çok sayfalı statik site için içerik-odaklı bir SSG framework seçtim; kullanıcı tercihi 'simple' olduğu için."
- "Full-app + 'Python istiyorum' tercihi olduğu için backend'i Python ile yapacağız; frontend tarafında SSR'ı destekleyen modern bir meta-framework seçtim."

## Output: the project files

Generate the project per the stack you picked. Standard expectations:

1. **All required files for the stack to build** — package manifests, config files, entry points, components, styles, assets
2. **Reflect style-guide.md** — palette → CSS variables / theme config; typography → font loading + scale; spacing → utility classes or design tokens
3. **Reflect content.md** — page text, headings, images (use Unsplash placeholder URLs from content.md verbatim), nav labels, footer text
4. **Match the site language** in `state.json.siteLanguage` (set `<html lang>` correctly, etc.)
5. **Pages map** — each page in brief.md becomes a corresponding file in the framework's routing convention (e.g., `app/page.tsx` or `src/pages/index.astro` or `src/routes/+page.svelte` or `index.html`)

## After writing files

Run from inside the project directory:

1. **Install** — pick the right package manager based on what's installed (`pnpm` if available, else `npm`; for Python-based stacks use `pip` or `uv`; for Go use `go mod tidy`; etc.)
2. **Build** — run the framework's build command (`npm run build`, `vite build`, `astro build`, `next build`, `go build`, etc.)
3. If build fails: try once to fix the offending file, then report.

## Constraints

- Read brief, style-guide, content, state.json. Write only frontend files.
- Do not modify brief.md, style-guide.md, content.md, or other agents' outputs.
- Match siteLanguage everywhere user-visible (page titles, alt text, nav labels).
- Record your stack pick in `state.json.chosenStack.frontend` AND `chosenStack.rationale`.
- If `chosenStack.frontend` is already set from a prior run, use that same stack — don't switch unless the user's preferences have explicitly changed.
- Output a one-line summary: `frontend generated: stack=<your-pick> pages=<N> build=<ok|failed>`
````

- [ ] **Step 2: Verify**

Run: `head -5 agents/frontend-expert.md`
Expected: frontmatter with `name: frontend-expert`, tools list.

Run: `wc -l agents/frontend-expert.md`
Expected: 100-200 lines (much smaller than v0.1's 240 lines because no per-stack templates).

Run: `grep -c "chosenStack" agents/frontend-expert.md`
Expected: at least 4 (multiple references — read, write, persist).

Run: `grep -cE "^# |^## |^### " agents/frontend-expert.md`
Expected: at least 8 (h1 + Inputs + Decision (×2) + Output + After + Constraints + sub-sections).

Run: `grep -c '^```' agents/frontend-expert.md`
Expected: EVEN, around 2-4 (only the chosenStack JSON example block).

Run: `grep -c '^````' agents/frontend-expert.md`
Expected: 0.

Run: `tests/lint.sh`
Expected: `11 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/frontend-expert.md
git commit -m "feat: frontend-expert is now stack-agnostic — picks framework at runtime"
```

---

## Task 8: Create `backend-engineer` Agent (Stack-Agnostic)

**Files:**
- Create: `agents/backend-engineer.md`

For full-app scope only. Stack-agnostic: reads scope + preferences, picks a backend framework + database appropriate for *right now*, generates code, records the choice.

- [ ] **Step 1: Write the agent file**

Create `agents/backend-engineer.md`:

````markdown
---
name: backend-engineer
description: For full-app scope only. Reads brief and content (auth strings) plus user preferences, picks a backend framework + database appropriate for right now, generates the API + DB schema + auth scaffolding, and records the stack choice in state.json.chosenStack.
tools: Read, Write, Edit, Bash
---

# backend-engineer agent (stack-agnostic)

You generate backend code for a full-app project. The frontend is generated by `frontend-expert` in parallel. You pick the backend framework + database at runtime — the plugin does NOT prescribe a stack.

## Inputs

Read in this order:
1. `{projectPath}/.web-builder/state.json` — `scope` (must be `full-app`), `preferences`, `chosenStack` (you may run after frontend-expert; respect what it picked)
2. `{projectPath}/brief.md` — feature list, entities, auth needs
3. `{projectPath}/content.md` "Auth flow strings" / "UI strings" sections if present

## Pre-flight

If `state.json.scope` is not `full-app`, exit immediately:
```
status: skipped
reason: not-full-app
```

If `state.json.chosenStack.backend` is already populated (from a prior run), respect it — use the same backend stack.

## Decision: pick the backend stack

Consider, in order:

1. **`preferences.backendLang`** (the strongest signal):
   - `same-as-frontend` → use the frontend's framework if it has API capability (most modern meta-frameworks do); otherwise pick a Node-based backend
   - `node-separate` → a Node-based service in a `backend/` subdirectory
   - `python` → a Python-based service
   - `compiled` → Go / Rust / similar
   - `enterprise-jvm` → JVM-based (Java / Kotlin)
   - `claude-decides` (or null in sade mode) → default to the simplest viable option for the user's scope. For most users, "same-as-frontend" is simplest. If frontend is static/no-server, default to a Node service.

2. **`preferences.dbStyle`**:
   - `simple` → file-based DB (SQLite-like, zero setup)
   - `sql` → relational DB (Postgres or similar — note: requires a running server, document setup in README)
   - `document` → document DB (MongoDB or similar)
   - `none` → in-memory only; warn user data is lost on restart
   - `claude-decides` → start with a simple file-based DB for MVP

3. **brief.md feature list**:
   - Auth → include auth scaffolding (email + password by default; no OAuth in v0.4.0)
   - CRUD on entities → generate CRUD endpoints
   - Admin/dashboard → role middleware

4. **Current ecosystem snapshot** (use your knowledge as of run date):
   - Pick well-maintained, popular frameworks
   - For each language preference, pick the most natural choice today (e.g., for Python, the dominant fast/async framework — whatever that currently is)

## Decision: record your choice

After deciding, write to `state.json.chosenStack`:

```json
"chosenStack": {
  "frontend": <existing value, set by frontend-expert>,
  "backend": "<your pick, e.g., 'next-api' or 'fastapi@0.115' or 'go-chi'>",
  "database": "<your pick, e.g., 'sqlite-prisma' or 'postgres-via-prisma' or 'mongodb-mongoose'>",
  "rationale": "<existing rationale, OR append your backend reasoning if rationale was empty>"
}
```

If `rationale` already exists (frontend-expert wrote it), prepend your one-line backend reasoning to the existing rationale.

## Output: the project files

Generate the project per the stack you picked. Common deliverables:

1. **Package/dependency manifest** — appropriate to the language (`package.json` for Node, `pyproject.toml` for Python, `go.mod` for Go, `pom.xml` for Java)
2. **Server entry point** with appropriate configuration
3. **Routes / endpoints** — at least:
   - `/api/health` — simple healthcheck
   - CRUD endpoints for the main entities mentioned in brief.md (one entity = list, get, create, update, delete)
   - Auth endpoints if brief mentions login: signup, login, logout (and reset-password if `preferences.priority` includes feature-richness)
4. **Database schema / migration**:
   - For SQL: schema file + migration tooling appropriate to the framework (e.g., Prisma migrations, Alembic, Flyway)
   - For document DBs: schema/model files
   - For `none`: in-memory data structures with a warning at startup
5. **Auth middleware** (if auth is needed): hash passwords, JWT or session-based auth, middleware to protect routes
6. **README section** explaining how to run the backend (env vars, dev command, migration command)

If the frontend stack already has its own backend conventions (e.g., the frontend is a meta-framework with built-in API routes), generate the backend files in that framework's expected location instead of a separate `backend/` directory. Otherwise, use a `backend/` subdirectory at the project root.

## After writing files

Run install + build for the language you picked:
- Node: `pnpm install || npm install`, then a build/check command
- Python: `pip install -e .` or `uv sync`, then a syntax check
- Go: `go mod tidy && go build ./...`
- Java: `mvn package` (skip if maven absent — warn user)
- For DB migrations: run them if non-destructive (e.g., Prisma `migrate dev` on SQLite is safe; on Postgres only if connection is configured)

If something fails, try once to fix and retry. Report failure if 2 attempts both fail.

## Constraints

- Read brief, content, state.json. Write only backend files.
- Do not modify frontend files (frontend-expert owns those).
- Do not modify brief.md, style-guide.md, content.md.
- Record your picks in `state.json.chosenStack.{backend, database}`.
- If `chosenStack.backend` is already set from a prior run, use that same stack.
- Output a one-line summary: `backend generated: backend=<your-backend> db=<your-db> routes=<N> build=<ok|failed>`
````

- [ ] **Step 2: Verify**

Run: `head -5 agents/backend-engineer.md`
Expected: frontmatter with `name: backend-engineer`, `tools: Read, Write, Edit, Bash`.

Run: `wc -l agents/backend-engineer.md`
Expected: 100-200 lines (small, because no per-stack templates).

Run: `grep -c "chosenStack" agents/backend-engineer.md`
Expected: at least 4.

Run: `grep -cE "Express|FastAPI|Django|Spring|chi|gin|fastify|hono" agents/backend-engineer.md`
Expected: 0. (Critical — no specific frameworks named.)

Run: `grep -c "^## " agents/backend-engineer.md`
Expected: at least 6 (Inputs, Pre-flight, Decision×2, Output, After, Constraints).

Run: `grep -c '^````' agents/backend-engineer.md`
Expected: 0.

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.` (Task 1's new command + Task 8's new agent file).

- [ ] **Step 3: Commit**

```bash
git add agents/backend-engineer.md
git commit -m "feat: add backend-engineer agent (stack-agnostic, picks framework + DB at runtime)"
```

---

## Task 9: Update Orchestrator — Scope-Aware Agent Graph

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md`

The orchestrator's step 3 currently runs ui-ux-designer → content-writer → frontend-expert sequentially. For full-app, add backend-engineer in parallel with frontend-expert.

- [ ] **Step 1: Read step 3**

Run: `grep -nA 30 "From this point on" skills/web-builder-orchestrator/SKILL.md`

- [ ] **Step 2: Replace the agent graph**

Use Edit to replace the existing Step A/B/C list inside step 3 with:

````markdown
3. From this point on, **all file operations happen inside the project subdirectory.** `cd` into it before invoking agents. Run the agent execution graph against the project directory. The graph is scope-aware:

   **Sequential phase 1 (always):**

   **Step A — `ui-ux-designer` agent**

   Use the `Agent` tool with `subagent_type: "ui-ux-designer"`. Pass:

   > Project path: `{projectPath}`. Read brief.md and write style-guide.md per your instructions.

   Wait for completion. Append to `state.json.agentRuns`. Standard retry policy.

   **Sequential phase 2 (after designer completes):**

   **Step B — `content-writer` agent**

   Same pattern, `subagent_type: "content-writer"`.

   **Parallel phase 3 (after content-writer completes):**

   **Step C — `frontend-expert` agent**

   Use Agent tool with `subagent_type: "frontend-expert"`. The agent reads scope + preferences and picks a frontend stack at runtime. After it runs, `state.json.chosenStack.frontend` is populated.

   **Step D — `backend-engineer` agent (only if scope = full-app)**

   In parallel with Step C: use Agent tool with `subagent_type: "backend-engineer"`. The agent reads scope + preferences (and may read `state.json.chosenStack.frontend` after frontend-expert completes — minor sequencing note: run backend-engineer SLIGHTLY AFTER frontend-expert starts to give it a chance to read the frontend pick, OR run them truly in parallel and let the backend agent default if frontend pick isn't yet known). Skip this step entirely if scope is not `full-app`.

   Wait for both C and D to complete before proceeding.
````

- [ ] **Step 3: Update impact analysis table to mention backend**

Locate the impact analysis table in step 1c.2. Update the rows to mention backend-engineer where appropriate:

```
| Change category | Agents to re-run (in order) |
|---|---|
| `style` | `ui-ux-designer`, `frontend-expert` |
| `content` | `content-writer`, `frontend-expert` (and `backend-engineer` if content includes UI strings used by API responses) |
| `structure` | `ui-ux-designer` (if layout shifts), `content-writer`, `frontend-expert` |
| `behavior` | `frontend-expert` (and `backend-engineer` if change involves auth or API endpoints) |
| `technical` | depends on sub-detail: preference change → all agents re-pick + regenerate; deploy target change → deliver skill's deploy flow |
| `undo` | (no agents — see step 1d) |
| `cancel` | exit cleanly |
```

- [ ] **Step 4: Verify**

Run: `grep -c "subagent_type: \"backend-engineer\"" skills/web-builder-orchestrator/SKILL.md`
Expected: 1.

Run: `grep -c "scope = full-app" skills/web-builder-orchestrator/SKILL.md`
Expected: at least 1.

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: orchestrator runs frontend+backend in parallel for full-app scope"
```

---

## Task 10: Update `revise` Skill — Preferences-Change Option

**Files:**
- Modify: `skills/web-builder-revise/SKILL.md`

The `technical` category currently asks about deploy target / SEO / performance. Add a "preferences-change" sub-option that triggers agents to re-pick the stack. This replaces a "stack-change" option (which would name specific frameworks — we don't do that).

- [ ] **Step 1: Replace the technical category sub-question**

Use Edit to replace:

```
> Teknik konularda?
>
> A) Deploy hedefi değiştir (örn. Cloudflare → Vercel)
> B) Site adı / URL slug değiştir
> C) SEO meta (title, description) değiştir
> D) Performance / cache ayarları
```

with:

```
> Teknik konularda?
>
> A) Deploy hedefi değiştir (örn. Cloudflare → Vercel)
> B) Site adı / URL slug değiştir
> C) SEO meta (title, description) değiştir
> D) Performance / cache ayarları
> E) Tercihlerimi değiştir (interaktivite, performans, dil tercihi vs. — agent yeniden stack seçecek)
> F) Scope değiştir (örn. tek sayfa → çok sayfalı — büyük değişiklik, site yeniden üretilir)
```

For E (preferences-change): the revise skill walks the user through dev-mode preference questions again (just like Q2-dev-prefs in intake), captures new values, returns:

```
category: technical
detail: preferences-change
description: <summary of what changed>
new-preferences: <object with the new preference values>
```

The orchestrator on receiving this re-runs all agents, which will read new preferences and may pick a different stack (recorded in `state.json.chosenStack`).

For F (scope-change): the revise skill confirms the new scope, returns `{category: technical, detail: scope-change, new-scope: <value>}`. The orchestrator regenerates everything for the new scope.

- [ ] **Step 2: Verify**

Run: `grep -c "Tercihlerimi değiştir" skills/web-builder-revise/SKILL.md`
Expected: 1.

Run: `grep -c "Scope değiştir" skills/web-builder-revise/SKILL.md`
Expected: 1.

Run: `grep -cE "Astro|Next\.js|SvelteKit|Vue|React" skills/web-builder-revise/SKILL.md`
Expected: 0. (No framework names — we ask about preferences, not stacks.)

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-revise/SKILL.md
git commit -m "feat: revise skill technical category gains preferences/scope change (no stack names)"
```

---

## Task 11: Update Deployer — Scope-Aware Defaults

**Files:**
- Modify: `agents/deployer.md`

Deployer continues to support the same 5 deploy targets (Cloudflare Pages / Vercel / Netlify / GitHub Pages / local). Spec says full-app's recommended target is Vercel (broad serverless support); statics → Cloudflare Pages. Add a scope-aware note. (Frameworks change but deployment platforms don't — these target names are stable.)

- [ ] **Step 1: Add scope-aware note in pre-flight**

Insert at the top of the pre-flight section in `agents/deployer.md`:

```markdown
Read `state.json.scope`. The recommended deploy target depends on scope:

- `single-page`, `multi-page-static`, `interactive-static` → **Cloudflare Pages** (free tier, custom domain easy, CDN included)
- `full-app` → **Vercel** (broadest support for server functions, edge, modern meta-frameworks)

The deliver skill prompts the user; this is for your awareness. If the user picked an unusual combination (e.g., Cloudflare Pages for a full-app), warn via `human-readable` but still proceed — they may know what they're doing.
```

- [ ] **Step 2: Verify**

Run: `grep -c "single-page\|multi-page-static\|interactive-static" agents/deployer.md`
Expected: at least 1.

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/deployer.md
git commit -m "docs: deployer documents scope-aware target recommendations"
```

---

## Task 12: Update Deliver Skill — Scope-Aware Deploy Default

**Files:**
- Modify: `skills/web-builder-deliver/SKILL.md`

Make the deploy prompt's "(önerilen)" label dynamic based on scope.

- [ ] **Step 1: Update deploy prompt option labels**

Use Edit to replace:

```
   > A) Cloudflare Pages (önerilen — en cömert ücretsiz plan, custom domain kolay)
   > B) Vercel (Next.js için en doğal, statik için de iyi)
```

with:

```
   > A) Cloudflare Pages ({"önerilen — en cömert ücretsiz plan, custom domain kolay" if scope is static, otherwise "iyi statik seçenek"})
   > B) Vercel ({"önerilen — modern full-app için en doğal" if scope is full-app, otherwise "full-app için en iyi, statik için de uygun"})
```

The braces denote runtime conditional labels — the skill renders the right label by reading `state.json.scope`.

- [ ] **Step 2: Verify**

Run: `grep -c "önerilen — en cömert" skills/web-builder-deliver/SKILL.md`
Expected: 1.

Run: `grep -c "önerilen — modern full-app" skills/web-builder-deliver/SKILL.md`
Expected: 1.

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-deliver/SKILL.md
git commit -m "feat: deploy prompt recommends scope-appropriate target"
```

---

## Task 13: Add Fixtures for New Scopes (Preferences-Based)

**Files:**
- Create: `tests/fixtures/sample-brief-single-page.md`
- Create: `tests/fixtures/sample-brief-full-app.md`

These fixtures use the new brief format (Scope + Preferences, no stack names).

- [ ] **Step 1: Write `tests/fixtures/sample-brief-single-page.md`**

```markdown
# Site Briefi: ada-yazilim-cv

## Scope
single-page

## Amaç
Ada Yılmaz'ın yazılım geliştirici CV / portfolio tek sayfası. Kendi adıyla domain alacak.

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

## Preferences
- Priority: simple
- Interactivity: low
- Backend language: null
- Database style: null
- TypeScript: false
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

## Preferences
- Priority: feature-richness
- Interactivity: high
- Backend language: same-as-frontend
- Database style: simple
- TypeScript: true
```

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/sample-brief-single-page.md tests/fixtures/sample-brief-full-app.md
git commit -m "test: add brief fixtures for single-page and full-app scopes (preferences-based)"
```

---

## Task 14: Smoke Tests for New Scopes + Dev Mode

**Files:**
- Modify: `tests/smoke-test.md`

Add Tests 11-14:
- Test 11: single-page sade mode — agent picks a stack, builds successfully
- Test 12: full-app sade mode — frontend AND backend agents run; both pick stacks; both build
- Test 13: dev mode with preference for "Python on backend" — backend-engineer picks a Python framework
- Test 14: revise — change preferences (E option), agent re-picks stack

Critically: smoke tests **don't pin specific stack names**. They verify behavior:
- "After Test 11, `state.json.chosenStack.frontend` is non-null"
- "After Test 11, the build succeeds (some build command exited 0)"
- Not: "After Test 11, package.json has Astro as a dependency"

- [ ] **Step 1: Append the new tests just before `## Pass criteria`**

Use Edit. Insert this content before the existing `## Pass criteria` line:

````markdown
## Test 11: Single-page scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At the scope question, pick A (tek sayfa).
3. Continue with default content + minimalist style.
4. Plugin generates a project. The agent picks whatever it deems best for "tek sayfa" — could be vanilla HTML/CSS/JS, could be a tiny static site framework, depending on Claude's current view.
5. Verify: the project builds (or runs without a build, if vanilla); `state.json.chosenStack.frontend` is populated; `state.json.chosenStack.rationale` is non-empty.

Pass:
- `state.json.chosenStack.frontend` is non-null and reasonable for single-page (the rationale should explain "why this stack for a one-pager")
- The project either has no build step (vanilla case) or `npm run build` (or equivalent) succeeds
- Generated files reflect content.md (site title, sections) and style-guide.md (palette in CSS)

## Test 12: Full-app scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At scope question, pick D (üye girişi / sipariş / veri kaydı).
3. Use the takim-takip example from sample-brief-full-app.md as inspiration for your answers (or any small CRUD app description).
4. Plugin runs frontend-expert AND backend-engineer (state.json.agentRuns has both, with status=success).
5. Both agents populate state.json.chosenStack (frontend, backend, database, rationale).

Pass:
- `state.json.chosenStack.frontend`, `chosenStack.backend`, `chosenStack.database` are all non-null
- The build/install commands run successfully (whatever they are for the picked stacks)
- The project has at least: a way to run the frontend (dev or preview command), a way to run the backend, a database file or migration script
- An `/api/health` endpoint or equivalent exists

## Test 13: Dev mode with backend language preference

1. Run `/web-builder-dev` in a clean dir.
2. At scope, pick D (full-app).
3. At preference questions, set `backendLang` to `python` (option C).
4. Plugin generates the project; backend-engineer's pick should be a Python framework (whatever it considers best for full-app + Python today).

Pass:
- `state.json.preferences.backendLang` is `python`
- `state.json.chosenStack.backend` is a Python-based framework (rationale mentions Python)
- The backend directory has Python project files (`pyproject.toml` or `requirements.txt`, `.py` source files)

## Test 14: Revise — change preferences (re-pick stack)

1. After Test 11 generation succeeds, run `/web-builder` again.
2. Pick A (devam et / revize), then E (technical), then E (Tercihlerimi değiştir).
3. Walk through the preference questions; change `priority` from `simple` to `feature-richness`.
4. Plugin regenerates; the frontend-expert may pick a different stack (richer framework) and update `state.json.chosenStack.frontend`.

Pass:
- `state.json.preferences.priority` is updated to `feature-richness`
- A `Pre-revision snapshot` commit precedes the change
- A `Revision: technical — preferences-change` commit follows
- `state.json.chosenStack.frontend` may differ from before; rationale updated
````

- [ ] **Step 2: Verify**

Run: `grep -nE "^## Test [0-9]+:" tests/smoke-test.md`
Expected: 14 tests (Tests 1-14).

- [ ] **Step 3: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: smoke tests for new scopes + preference-based revision (no stack pinning)"
```

---

## Task 15: Update README + plugin.json to v0.4.0

**Files:**
- Modify: `README.md`
- Modify: `plugin.json`

- [ ] **Step 1: Replace README Status section**

Use Edit to change Status from v0.3.0 to:

```markdown
## Status

**v0.4.0.** All 4 site scopes supported (single page, multi-page static, interactive static, full app), in sade or dev mode. Stack-agnostic — Claude picks the best framework/language for your project at generation time.

- ✅ Generate any of 4 scope types from Q&A
- ✅ Sade mode: minimal Q&A, plugin agents pick stack silently
- ✅ Dev mode (`/web-builder-dev`): user expresses preferences (interactivity / performance / preferred backend language); agent picks accordingly
- ✅ Stack-agnostic plugin: no hardcoded framework list. The agents pick from current ecosystem at runtime — future-proof against framework churn
- ✅ Stack pick recorded in `state.json.chosenStack` so revisions stay consistent
- ✅ Preview locally with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages (scope-aware default)
- ✅ Auto git initialization in sade mode
- ✅ Revise existing projects: structured Q&A + impact analysis + undo + preferences-change

Not yet supported (coming in later versions): SEO/accessibility agents, custom domain automation, multi-language site output, public Claude Code plugin distribution.
```

- [ ] **Step 2: Update architecture line**

Replace the architecture one-liner with:

```
Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle the dialog. Worker agents (`ui-ux-designer`, `content-writer`, `frontend-expert`, `backend-engineer`, `deployer`) write the actual files in their own context. `frontend-expert` and `backend-engineer` are stack-agnostic — they pick the framework/language at runtime based on user preferences and current ecosystem knowledge, then record the choice in `state.json.chosenStack`.
```

- [ ] **Step 3: Add a small "Use" subsection for dev mode**

Insert this paragraph at the end of the Use section:

```
For technical users who want to influence the stack pick (preference for Python on backend, "I want it as simple as possible", "I prioritize performance", etc.):

```

/web-builder-dev

```

Same flow but with preference questions added. The plugin still picks the framework — but informed by your preferences.
```

- [ ] **Step 4: Bump plugin.json version**

Change `"version": "0.3.0"` to `"version": "0.4.0"`.

- [ ] **Step 5: Verify**

Run: `python3 -c "import json; print(json.load(open('plugin.json'))['version'])"`
Expected: `0.4.0`.

Run: `grep -c "v0.4.0" README.md`
Expected: at least 1.

Run: `grep -c "stack-agnostic" README.md`
Expected: at least 1.

Run: `grep -c "/web-builder-dev" README.md`
Expected: at least 1.

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 6: Commit**

```bash
git add README.md plugin.json
git commit -m "docs: bump to v0.4.0 (multi-scope + dev mode + stack-agnostic agents)"
```

---

## Task 16: Final Lint, Structural Smoke Test, Tag v0.4.0, Push, Merge

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `12 passed, 0 failed.`

- [ ] **Step 2: Structural smoke test — single-page sade mode**

Set up a temp project with `sample-brief-single-page.md` as `brief.md` plus minimal style-guide and content; write a sample `state.json` with `scope: single-page, mode: simple, chosenStack: null`. Dispatch a subagent acting as `frontend-expert`. Verify:
- The agent reads state.json + brief
- The agent picks SOME frontend stack (records in chosenStack.frontend)
- The agent generates project files appropriate to its pick
- The project builds OR runs without build (vanilla case)

Don't pin which stack the agent picks. Verify the BEHAVIOR is correct.

- [ ] **Step 3: Structural smoke test — full-app sade mode**

Similar setup with `sample-brief-full-app.md`. Dispatch frontend-expert AND backend-engineer (sequentially is fine for smoke). Verify:
- Both populate state.json.chosenStack
- Both produce buildable projects (whatever stacks they picked)
- Backend generates `/api/health` (or equivalent healthcheck) and CRUD endpoints

- [ ] **Step 4: Structural smoke test — dev mode with Python preference**

State.json: `mode: dev, scope: full-app, preferences: { backendLang: 'python', ... }`. Dispatch backend-engineer. Verify:
- The agent honors `backendLang: python` and picks a Python framework
- `state.json.chosenStack.backend` mentions Python
- Backend directory has Python files

- [ ] **Step 5: Tag v0.4.0**

```bash
git tag -a v0.4.0 -m "v0.4.0: multi-scope + dev mode + stack-agnostic agents

- 4 site scopes: single-page, multi-page-static, interactive-static, full-app
- Sade vs dev mode (/web-builder-dev for preferences)
- Stack-agnostic agents: frontend-expert and backend-engineer pick the
  framework/language at runtime based on user preferences + current
  ecosystem knowledge (Claude decides — no hardcoded stack list)
- New backend-engineer agent for full-app
- state.json.chosenStack records the picks for consistency across revisions
- Revise skill: 'Tercihlerimi değiştir' option triggers re-pick
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
- [ ] `/web-builder-dev` exists.
- [ ] Intake supports all 4 scopes; dev mode adds preference questions; **no specific framework names appear in any plugin file** (intake, brief template, agents, revise — all framework-agnostic in the plugin code).
- [ ] `frontend-expert` and `backend-engineer` are stack-agnostic — they pick framework at runtime based on scope + preferences.
- [ ] `state.json.chosenStack` is populated by agents (not by intake) and stays consistent across revisions unless user explicitly changes preferences.
- [ ] Orchestrator runs frontend+backend in parallel for full-app.
- [ ] Smoke tests pass structurally (state.json field populated, build succeeds — without pinning specific stacks).
- [ ] `git tag --list` shows `v0.4.0`.
- [ ] No `TBD` / `TODO` strings in any active plugin file.
- [ ] Critical guardrail: `grep -rE "Astro|Next\.js|SvelteKit|Vue|React|Express|FastAPI|Django|Spring|chi|gin|fastify" agents/ skills/ commands/` returns 0 results in plugin code (only allowed in README.md if needed for context).

## Out of scope for this plan (deferred)

- SEO + accessibility agents (Plan 5)
- Public Claude Code plugin distribution (Plan 6)
- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup (per spec)
- OAuth / SSO (only email+password feasible from agent's pick)
- Real-time features (websockets, SSE) — only if agent's picked stack supports them and brief requests
- Pinning a specific framework via state.json (user can edit chosenStack.frontend manually if they want; orchestrator respects existing picks)

## Risks and edge cases

- **Agent picks an obscure framework**: agents are instructed to prefer well-maintained, popular frameworks. Risk is low but possible. Mitigation: rationale field is user-visible; user can revise via "Tercihlerimi değiştir".
- **Agent's knowledge is stale**: when Claude's training data ages, its framework picks may not reflect the latest landscape. Acceptable for this plugin's scope — better than hardcoding stale picks in plugin code.
- **Stack inconsistency across revisions**: orchestrator instructs agents to respect existing `state.json.chosenStack` if set. Only explicit "Tercihlerimi değiştir" triggers a re-pick.
- **Frontend and backend pick incompatible stacks**: parallel execution risks frontend and backend agents picking unrelated frameworks. Mitigation: backend-engineer reads `state.json.chosenStack.frontend` if frontend-expert finished first; if not yet set, defaults to a generic backend stack.
- **Build failures from agent's pick**: if Claude picks a framework but generates broken code, the agent's retry policy kicks in. If it still fails after 1 retry, the orchestrator surfaces the failure and offers manual recovery.
- **No stack restriction in plugin = no static guarantees**: a tradeoff. Users get future-proof flexibility; lose ability to "always get the same stack". The state.json.chosenStack record is the source of truth for what was actually picked.
