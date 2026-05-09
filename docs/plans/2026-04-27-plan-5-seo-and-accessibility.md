# web-builder Plan 5: SEO + Accessibility Agents

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two quality-pass agents to the pipeline: `seo-expert` (produces per-page SEO data — titles, descriptions, og policy, sitemap structure, robots) and `accessibility-reviewer` (reviews generated frontend code, applies fixes in place, writes `a11y-report.md`). Update the orchestrator's agent graph to run them at the right points: SEO in parallel with content-writer (both read the brief, both produce input for frontend-expert); accessibility review AFTER frontend code is generated.

**Architecture:** Both new agents are stack-agnostic (consistent with Plan 4). `seo-expert` reads brief + content, writes `seo.md` — a structured markdown file that `frontend-expert` and (for full-app) `backend-engineer` consume to inject meta tags, generate sitemap, etc. `accessibility-reviewer` runs LAST, reads the generated code (whatever the chosen stack), applies inline fixes for common a11y issues (missing alt text, missing aria labels, color contrast, semantic HTML, keyboard navigation), and writes a report; in simple mode the fixes are silent, in dev mode the report is surfaced.

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). The agents inspect generated code in any framework — they're framework-agnostic in their checks.

**v0.5.0 scope:**
- 2 new agents: `seo-expert`, `accessibility-reviewer`
- Updated orchestrator agent execution graph (parallel content + seo; a11y at end)
- Updated impact analysis table (entries for the new agents)
- `frontend-expert` and `backend-engineer` updated to read `seo.md` if present
- Revise skill technical category gains a dedicated A11y option (G); existing SEO option (C) becomes fully supported
- New fixture `sample-seo.md`
- Smoke tests for SEO + a11y
- README + plugin.json bumped to v0.5.0

**Definition of done:**
- After running the full plugin pipeline, every project has `seo.md` (with per-page title/description/og policy/sitemap/robots) and `a11y-report.md` (or inline fixes if simple mode).
- Generated frontend code includes correct meta tags from `seo.md`.
- Generated frontend code passes basic a11y checks: every `<img>` has alt, every form input has label, headings hierarchical, no `<div>`-only nav, color contrast verified against style-guide palette.
- Smoke test verifies both new agents ran successfully and their artifacts exist.

**Out of scope (deferred):**
- Public Claude Code plugin distribution (Plan 6)
- Custom domain automation (v1.1)
- Multi-language site output / hreflang (v1.1)
- Schema.org structured data beyond basic Open Graph (v1.x)
- Lighthouse / Pa11y automated runs in CI (v1.x — would require running headless browser)
- Deep WCAG 3.0 audits (only WCAG 2.1 AA basics in v0.5.0)

---

## File Structure

```
web-builder/
├── plugin.json                                  # MODIFY: bump version to 0.5.0
├── README.md                                    # MODIFY: status to v0.5.0
├── commands/
│   ├── web-builder.md                           # unchanged
│   └── web-builder-dev.md                       # unchanged
├── skills/
│   ├── web-builder-orchestrator/SKILL.md        # MODIFY: agent graph (add SEO parallel, a11y final)
│   ├── web-builder-intake/SKILL.md              # unchanged
│   ├── web-builder-revise/SKILL.md              # MODIFY: technical category gains A11y option
│   └── web-builder-deliver/SKILL.md             # unchanged
├── agents/
│   ├── ui-ux-designer.md                        # unchanged
│   ├── content-writer.md                        # unchanged
│   ├── seo-expert.md                            # CREATE
│   ├── frontend-expert.md                       # MODIFY: read seo.md, inject meta tags
│   ├── backend-engineer.md                      # MODIFY: read seo.md, generate sitemap.xml/robots.txt routes
│   ├── accessibility-reviewer.md                # CREATE
│   └── deployer.md                              # unchanged
├── tests/
│   ├── fixtures/
│   │   ├── sample-brief.md                      # unchanged
│   │   ├── sample-brief-single-page.md          # unchanged
│   │   ├── sample-brief-full-app.md             # unchanged
│   │   ├── sample-style-guide.md                # unchanged
│   │   ├── sample-content.md                    # unchanged
│   │   ├── sample-seo.md                        # CREATE
│   │   └── sample-state.json                    # unchanged
│   ├── lint.sh                                  # unchanged (auto-picks up new agents)
│   └── smoke-test.md                            # MODIFY: add Tests 15-16 for SEO + a11y
└── docs/
    └── plans/
        └── 2026-04-27-plan-5-seo-and-accessibility.md  # this file
```

**Responsibilities:**

| File | Owns |
|---|---|
| `agents/seo-expert.md` | Per-page SEO data (titles, descriptions, og-image policy, sitemap structure, robots.txt rules); writes `seo.md` |
| `agents/accessibility-reviewer.md` | Reviews generated frontend code, applies inline fixes for common a11y issues, writes `a11y-report.md` |
| `agents/frontend-expert.md` (modified) | Additionally reads `seo.md` and injects meta tags into rendered output |
| `agents/backend-engineer.md` (modified) | For full-app: reads `seo.md` and generates `sitemap.xml` route + `robots.txt` static file (or framework equivalent) |

---

## Task 1: Create `seo-expert` Agent

**Files:**
- Create: `agents/seo-expert.md`

This agent runs in parallel with `content-writer` (both depend only on brief + designer). It produces `seo.md`, which `frontend-expert` and `backend-engineer` then consume.

- [ ] **Step 1: Write the agent file**

Create `agents/seo-expert.md`:

````markdown
---
name: seo-expert
description: Reads brief.md, content.md, and style-guide.md; produces seo.md — per-page titles, descriptions, og-image policy, sitemap structure, and robots.txt rules. Stack-agnostic; downstream agents (frontend-expert, backend-engineer) translate seo.md into framework-specific meta tags and route artifacts.
tools: Read, Write
---

# seo-expert agent

You produce SEO data for every page of the site. Your output is `seo.md` — a structured markdown file that frontend-expert and backend-engineer translate into the framework's meta tags, sitemap, and robots.txt at generation time.

## Inputs

Read in this order:
1. `{projectPath}/.web-builder/state.json` — `scope`, `siteLanguage`, `siteName`
2. `{projectPath}/brief.md` — goal, target audience (these inform tone of meta descriptions)
3. `{projectPath}/content.md` — page list, hero text, section headings (page titles often derived from these)
4. `{projectPath}/style-guide.md` — vibe / palette (informs og-image style note)

## Output: `seo.md`

Write `{projectPath}/seo.md`. Overwrite if exists.

## seo.md template

```markdown
# SEO: {siteName}

## Site-wide

- Default site name (used in `<title>` template): {short, ≤30 chars}
- Default description (homepage fallback): {one short sentence, action-oriented, includes primary keyword}
- Default keywords: {comma-separated, 3-7 keywords most relevant to brief.md goal}
- Open Graph image policy:
  - Style: {description matching style-guide vibe — e.g., "warm, hand-drawn, single accent color"}
  - Recommended dimensions: 1200x630 (Facebook/Twitter standard)
  - Placeholder URL: {Unsplash URL matching the topic, or `https://picsum.photos/seed/{slug}/1200/630` as fallback}
  - PLACEHOLDER: yes

## Per-page SEO

### Page: Home (/)
- Title (used in `<title>`): {compelling, includes primary keyword, ≤60 chars}
- Meta description: {summary tied to hero subheading, ≤160 chars, action-oriented}
- Canonical: /
- Open Graph: title=above, description=above, type=website, image=site-wide og image
- Indexable: yes

### Page: {next page} (/slug)
- (same fields)

(... one ### Page block per page in brief.md/content.md)

## Sitemap

```
- / (priority 1.0, changefreq weekly)
- /menu (priority 0.8, changefreq weekly)
- /about (priority 0.5, changefreq monthly)
- /contact (priority 0.5, changefreq monthly)
```

(Adjust priorities/frequencies based on page importance from brief.md.)

## robots.txt

```
User-agent: *
Allow: /

Sitemap: https://{deployedDomain}/sitemap.xml
```

(For simple mode, leave `{deployedDomain}` as a placeholder; deployer fills it in if a deploy happens.)

For full-app scope where some pages are auth-walled (e.g., /dashboard, /tasks), add `Disallow:` rules for those paths.
```

## Scope-aware extensions

- **single-page:** Just one ### Page block (the home page) plus site-wide section. Sitemap has only `/`.
- **multi-page-static / interactive-static:** ### Page block per page in brief.md.
- **full-app:** Include `Disallow:` rules in robots.txt for auth-protected paths (e.g., `/dashboard`, `/api/*`). Add `noindex` meta tag note for those pages in their per-page section. Public pages (sign-in, marketing) get standard SEO.

## Constraints

- Read brief, content, style-guide, state.json. Write only `seo.md`.
- Do not modify brief.md, content.md, style-guide.md, or any other agent's output.
- Match `siteLanguage` for all human-readable strings (titles, descriptions).
- Keep titles ≤60 chars, descriptions ≤160 chars (search engine display limits).
- Do not name specific frameworks. Output is framework-agnostic markdown.
- Output a one-line summary at the end: `seo.md written: {N pages}, og-policy=set, sitemap=set, robots=set`.
````

- [ ] **Step 2: Verify**

Run: `head -5 agents/seo-expert.md`
Expected: frontmatter with `name: seo-expert`, `tools: Read, Write`.

Run: `wc -l agents/seo-expert.md`
Expected: 70-110 lines.

Run: `grep -c '^```' agents/seo-expert.md`
Expected: EVEN (one inner fenced markdown block for the template plus a couple inner blocks for sitemap and robots).

Run: `grep -c '^````' agents/seo-expert.md`
Expected: 0.

Run: `grep -cE "Astro|Next\.js|SvelteKit|Vue|React|Solid|Qwik" agents/seo-expert.md`
Expected: 0 (stack-agnostic).

Run: `tests/lint.sh`
Expected: `13 passed, 0 failed.` (one more than v0.4.0's 12).

- [ ] **Step 3: Commit**

```bash
git add agents/seo-expert.md
git commit -m "feat: add seo-expert agent (per-page SEO, sitemap, robots — stack-agnostic)"
```

---

## Task 2: Create `accessibility-reviewer` Agent

**Files:**
- Create: `agents/accessibility-reviewer.md`

This agent runs LAST in the pipeline (after frontend-expert and backend-engineer). It reads the generated frontend code, applies inline fixes for common a11y issues, and writes `a11y-report.md`.

- [ ] **Step 1: Write the agent file**

Create `agents/accessibility-reviewer.md`:

````markdown
---
name: accessibility-reviewer
description: Reviews the generated frontend code for accessibility issues (missing alt text, missing labels, semantic HTML, color contrast, keyboard nav). Applies inline fixes where straightforward. Writes a11y-report.md summarizing the review. Stack-agnostic; works with whatever frontend the project uses.
tools: Read, Write, Edit, Glob, Bash
---

# accessibility-reviewer agent

You are the final pass in the generation pipeline. Frontend code is already written (in whatever stack frontend-expert picked). Your job: find common accessibility issues, fix them inline if straightforward, and produce an a11y-report.md so the user (or future revision) knows the state.

## Inputs

Read:
1. `{projectPath}/.web-builder/state.json` — `mode` (simple or dev), `scope`, `chosenStack.frontend`
2. `{projectPath}/style-guide.md` — palette (for color contrast checks)
3. The generated frontend code in the project directory — discover via `Glob` (e.g., `**/*.{html,astro,tsx,jsx,vue,svelte}` or whatever extensions the chosen stack uses)

## Pre-flight

If `state.json.chosenStack.frontend` is null (frontend-expert hasn't run yet), exit with:
```
status: skipped
reason: frontend-not-yet-generated
```

## Review checklist

For each frontend source file, scan for these common issues:

### Images
- Every `<img>` (or framework equivalent like `<Image>`, `<img />`, `<Image src=...>`) MUST have a non-empty `alt=""` attribute.
- If alt is missing or empty: add a descriptive alt attribute. Try to infer from the surrounding context (e.g., the section's heading, image filename, or a generic descriptive phrase appropriate to the brief).
- Decorative images (background images via CSS) are exempt; foreground `<img>` is not.

### Form inputs
- Every `<input>`, `<textarea>`, `<select>` (or framework equivalent) MUST have an associated `<label>` (via `for`/`id` linking, or implicit wrapping, or `aria-label`/`aria-labelledby`).
- If missing: add a `<label>` if there's a visible text near it; else add `aria-label` matching the input's purpose.

### Buttons and links
- Every `<button>` and `<a>` MUST have visible text content OR an `aria-label`.
- Icon-only buttons need `aria-label`.
- Links opening in new tab should have `aria-label` mentioning that or visible "(opens in new tab)" text.

### Headings hierarchy
- Each page should have exactly one `<h1>`.
- Heading levels should not skip (don't go from `<h2>` directly to `<h4>`).
- If violation found: report (don't auto-fix; restructuring headings often changes semantics).

### Semantic HTML
- Navigation should use `<nav>` not `<div role="navigation">`.
- Main content should use `<main>`.
- Articles use `<article>`, sections use `<section>`.
- Footer use `<footer>`, header use `<header>`.
- If `<div>` is used where a semantic element fits: replace inline.

### Color contrast
- Read style-guide.md palette: text/text-muted vs background, primary on background.
- Compute contrast ratios (WCAG: text needs 4.5:1, large text 3:1).
- If any text/background pair fails: report (don't auto-fix; require user decision on palette change).

### Keyboard navigation
- Custom interactive components (modals, dropdowns) should have keyboard handlers (Esc to close, arrow keys for nav).
- Focus traps for modals.
- This is a code review check; surface findings in report. Auto-fix only if the framework/stack has a standard pattern (e.g., for stacks that use a popular component library, suggest the library's accessible-by-default component).

### Page language
- The root element (`<html>`) must have `lang="..."` matching `state.json.siteLanguage`.
- If missing: add inline.

### Skip-to-content link
- For multi-page sites, recommend a "skip to main content" link as the first focusable element.
- Surface in report (auto-add only for very simple stacks like vanilla; for framework-managed layouts, suggest in report).

## Fix policy

- **Simple mode (`state.json.mode === "simple"`):** Apply all auto-fixable issues silently. Surface in `a11y-report.md` what was fixed and what was reported (not fixed). The user sees the summary in the deliver skill's closing message.
- **Dev mode (`state.json.mode === "dev"`):** Apply auto-fixes AND surface the full report inline (as part of the deliver skill's closing). Dev users want to see what the reviewer did.

## Output: `a11y-report.md`

Write `{projectPath}/a11y-report.md`:

```markdown
# Accessibility Review

Reviewed at: {ISO timestamp}
Mode: {simple | dev}
Stack: {state.json.chosenStack.frontend}

## Summary

- Files scanned: {N}
- Issues auto-fixed: {N}
- Issues reported (not auto-fixed): {N}

## Auto-fixed issues

- [{file}:{line approx}] Missing alt on `<img src="hero.jpg">` → added `alt="Hero image showing {context}"`
- [{file}:{line approx}] Missing `<label>` for email input → added `<label for="email">{copy}</label>`
- [{file}] `<div role="navigation">` → replaced with `<nav>`
- ... (one bullet per fix)

## Issues reported (need user attention)

- [{file}] `<h2>` followed by `<h4>` (heading skip) — restructure heading hierarchy
- [color-contrast] Primary text `#abc` on background `#def` has ratio 3.2:1 (fails WCAG AA 4.5:1) — consider darkening primary text
- ... (one bullet per reportable issue)

## Notes
- Skip-to-content link: {present | suggested in {file} but not auto-added because framework manages layout}
- Page language: {set to {lang} in {file} | added}
```

## Constraints

- Read only files. Edit frontend source files for auto-fixes (use Edit tool). Write only `a11y-report.md`.
- Do not modify brief.md, content.md, style-guide.md, seo.md, state.json.
- Match `siteLanguage` for any user-facing strings inserted (e.g., labels).
- Output a one-line summary: `a11y review: scanned={N} fixed={N} reported={N}`.
````

- [ ] **Step 2: Verify**

Run: `head -5 agents/accessibility-reviewer.md`
Expected: frontmatter with `name: accessibility-reviewer`, `tools: Read, Write, Edit, Glob, Bash`.

Run: `wc -l agents/accessibility-reviewer.md`
Expected: 100-180 lines.

Run: `grep -c '^```' agents/accessibility-reviewer.md`
Expected: EVEN.

Run: `grep -cE "Astro|Next\.js|SvelteKit|Vue|React|Solid|Qwik" agents/accessibility-reviewer.md`
Expected: 0 (stack-agnostic).

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.` (two new agent files since v0.4.0).

- [ ] **Step 3: Commit**

```bash
git add agents/accessibility-reviewer.md
git commit -m "feat: add accessibility-reviewer agent (inline a11y fixes + a11y-report.md)"
```

---

## Task 3: Update Orchestrator Agent Graph

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md`

The current graph runs designer → content → frontend (+ backend parallel for full-app). Plan 5 changes this:
- After designer: content-writer AND seo-expert run in parallel (both produce input files for frontend)
- After both complete: frontend-expert + backend-engineer (parallel for full-app)
- After frontend code is generated: accessibility-reviewer runs as final pass

- [ ] **Step 1: Locate step 3 (agent execution graph)**

Run: `grep -nA 50 "## Step A — \`ui-ux-designer\`" skills/web-builder-orchestrator/SKILL.md`

- [ ] **Step 2: Replace the graph structure**

Replace the existing Step A/B/C/D structure with this new content:

````markdown
3. From this point on, **all file operations happen inside the project subdirectory.** `cd` into it before invoking agents. Run the agent execution graph against the project directory:

   **Sequential phase 1 (always):**

   **Step A — `ui-ux-designer` agent**

   Use the `Agent` tool with `subagent_type: "ui-ux-designer"`. Pass:

   > Project path: `{projectPath}`. Read brief.md and write style-guide.md per your instructions.

   Wait for completion. Append to `state.json.agentRuns`. Standard retry policy.

   **Parallel phase 2 (after designer completes):**

   **Step B — `content-writer` agent**

   Use Agent tool with `subagent_type: "content-writer"`. Same prompt pattern.

   **Step C — `seo-expert` agent**

   In parallel with B: use Agent tool with `subagent_type: "seo-expert"`. Same prompt pattern. Writes `seo.md`.

   Wait for both B and C to complete before proceeding.

   **Parallel phase 3 (after content-writer + seo-expert complete):**

   **Step D — `frontend-expert` agent**

   Use Agent tool with `subagent_type: "frontend-expert"`. The agent reads scope + preferences and picks a frontend stack at runtime. After it runs, `state.json.chosenStack.frontend` is populated. The agent also reads `seo.md` and injects meta tags into the generated output.

   **Step E — `backend-engineer` agent (only if scope = full-app)**

   In parallel with Step D: use Agent tool with `subagent_type: "backend-engineer"`. Reads `seo.md` and generates a sitemap route + robots.txt for the full-app deployment. Skip entirely if scope is not `full-app`.

   Wait for both D and E to complete before proceeding.

   **Sequential phase 4 (final pass after all generation is done):**

   **Step F — `accessibility-reviewer` agent**

   Use Agent tool with `subagent_type: "accessibility-reviewer"`. Reads `state.json.chosenStack.frontend` (must be non-null), scans the generated code, applies inline fixes, writes `a11y-report.md`. In simple mode the fixes are silent; in dev mode the report is surfaced in the deliver step.
````

- [ ] **Step 3: Update impact analysis table to include new agents**

Locate the impact analysis table in step 1c.2. Replace it with:

```
| Change category | Agents to re-run (in order) |
|---|---|
| `style` | `ui-ux-designer`, `frontend-expert`, `accessibility-reviewer` (palette change may affect contrast) |
| `content` | `content-writer`, `seo-expert` (titles/descriptions derived from content), `frontend-expert`, `accessibility-reviewer` (alt text changes) |
| `structure` | `ui-ux-designer` (if layout shifts), `content-writer`, `seo-expert` (sitemap changes), `frontend-expert`, `accessibility-reviewer` |
| `behavior` | `frontend-expert` (and `backend-engineer` if change involves auth or API endpoints), `accessibility-reviewer` (interactive elements need a11y review) |
| `technical` | depends on sub-detail: preference change → all agents re-pick + regenerate; deploy target change → deliver skill's deploy flow; SEO meta change → `seo-expert` + `frontend-expert`; A11y check → `accessibility-reviewer` only |
| `undo` | (no agents — see step 1d) |
| `cancel` | exit cleanly |
```

- [ ] **Step 4: Verify**

Run: `grep -c "subagent_type: \"seo-expert\"" skills/web-builder-orchestrator/SKILL.md`
Expected: 1.

Run: `grep -c "subagent_type: \"accessibility-reviewer\"" skills/web-builder-orchestrator/SKILL.md`
Expected: 1.

Run: `grep -c "Sequential phase 4" skills/web-builder-orchestrator/SKILL.md`
Expected: 1.

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: orchestrator graph adds seo-expert (parallel) + accessibility-reviewer (final)"
```

---

## Task 4: Update `frontend-expert` to Read seo.md

**Files:**
- Modify: `agents/frontend-expert.md`

Add a small note instructing the agent to also read `seo.md` and inject meta tags.

- [ ] **Step 1: Update the Inputs section**

Find the `## Inputs` section in `agents/frontend-expert.md`. The current list reads brief, style-guide, content. Add seo.md as a 5th input, and in the Output section note that meta tags should come from seo.md.

Use Edit to find the Inputs list (the 4 numbered items) and add a 5th:

```
5. `{projectPath}/seo.md` — per-page titles, descriptions, og policy, robots — used to inject meta tags into the rendered output
```

Then in the Output section, add a bullet about meta tags:

```
- Inject meta tags from seo.md: `<title>` from per-page title, `<meta name="description">` from per-page description, `<meta property="og:*">` from og policy, `<link rel="canonical">` from canonical, `<html lang>` from siteLanguage
- For routes covered by sitemap.md: include them in the framework's sitemap convention if it has one (otherwise the static sitemap.xml goes in `public/`)
```

- [ ] **Step 2: Verify**

Run: `grep -c "seo.md" agents/frontend-expert.md`
Expected: at least 2 (Inputs list + Output bullet).

Run: `grep -c "meta tags" agents/frontend-expert.md`
Expected: at least 1.

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/frontend-expert.md
git commit -m "feat: frontend-expert reads seo.md and injects meta tags into rendered output"
```

---

## Task 5: Update `backend-engineer` to Read seo.md (full-app sitemap + robots)

**Files:**
- Modify: `agents/backend-engineer.md`

Full-app projects often have dynamic sitemap generation (especially if pages are CMS-driven). Add a note instructing backend-engineer to read `seo.md` and produce a sitemap route + static robots.txt.

- [ ] **Step 1: Update Inputs**

In `agents/backend-engineer.md`, locate the `## Inputs` section. Add seo.md as input.

Then in the Output section (or its deliverables list), add bullets:

```
- Sitemap route or static file: read `seo.md`'s Sitemap section, generate either `/sitemap.xml` route (if backend serves it dynamically) or `public/sitemap.xml` (if static)
- robots.txt: read `seo.md`'s robots section, write to `public/robots.txt` (or framework equivalent)
- For auth-protected pages, ensure they include `noindex` meta tag (frontend-expert handles the meta; backend-engineer may also set the appropriate cache headers like `X-Robots-Tag: noindex` for API responses)
```

- [ ] **Step 2: Verify**

Run: `grep -c "seo.md" agents/backend-engineer.md`
Expected: at least 2.

Run: `grep -c "sitemap" agents/backend-engineer.md`
Expected: at least 2.

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add agents/backend-engineer.md
git commit -m "feat: backend-engineer reads seo.md and generates sitemap + robots for full-app"
```

---

## Task 6: Update Revise Skill — A11y Sub-Option Under Technical

**Files:**
- Modify: `skills/web-builder-revise/SKILL.md`

The technical category currently has options A-F. Plan 5 makes SEO meta (option C) actually backed by a re-run of seo-expert + frontend-expert. Add a new option G specifically for an a11y re-check.

- [ ] **Step 1: Update technical category sub-questions**

In `skills/web-builder-revise/SKILL.md`, find the technical category sub-question listing options A-F. Add option G:

```
> G) Re-run accessibility (a11y) check / apply improvements
```

For G, return:

```
category: technical
detail: a11y-recheck
description: User asked to re-run accessibility review
```

The orchestrator on receiving `detail: a11y-recheck` runs ONLY the `accessibility-reviewer` agent (not the full pipeline) and refreshes `a11y-report.md`.

For C (SEO meta): now actually backed by `seo-expert + frontend-expert` re-run. Update the C wording slightly:

```
> C) Change SEO meta (title, description, og policy)
```

And the return record can stay the same `category: technical, detail: seo-meta` — orchestrator's impact analysis already says "SEO meta change → seo-expert + frontend-expert".

- [ ] **Step 2: Verify**

Run: `grep -c "a11y-recheck" skills/web-builder-revise/SKILL.md`
Expected: at least 1.

Run: `grep -c "accessibility" skills/web-builder-revise/SKILL.md`
Expected: 1.

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.`

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-revise/SKILL.md
git commit -m "feat: revise skill technical category gains a11y recheck option (G)"
```

---

## Task 7: Add `sample-seo.md` Fixture

**Files:**
- Create: `tests/fixtures/sample-seo.md`

A reference seo.md fixture for the brooklyn-coffee project (consistent with existing fixtures).

- [ ] **Step 1: Write the fixture**

Create `tests/fixtures/sample-seo.md`:

```markdown
# SEO: brooklyn-coffee

## Site-wide

- Default site name (used in `<title>` template): Brooklyn Coffee
- Default description (homepage fallback): Brooklyn's little coffee shop — third-wave coffee and homemade sandwiches.
- Default keywords: brooklyn coffee, third-wave coffee, homemade sandwiches, neighborhood cafe
- Open Graph image policy:
  - Style: warm, low-key, neighborhood-cafe vibe — single warm-tone hero
  - Recommended dimensions: 1200x630
  - Placeholder URL: https://picsum.photos/seed/cafe/1200/630
  - PLACEHOLDER: yes

## Per-page SEO

### Page: Home (/)
- Title: Brooklyn Coffee — The neighborhood's little coffee shop
- Meta description: Third-wave coffee and homemade sandwiches in Brooklyn. The neighborhood's gathering spot.
- Canonical: /
- Open Graph: title=Brooklyn Coffee, description=The neighborhood's little coffee shop, type=website, image=site-wide
- Indexable: yes

### Page: Menu (/menu)
- Title: Menu — Brooklyn Coffee
- Meta description: Our third-wave coffee and homemade sandwich menu. Fresh every morning.
- Canonical: /menu
- Open Graph: title=Menu, description=Our coffee and sandwich menu, type=website, image=site-wide
- Indexable: yes

### Page: About (/about)
- Title: About — Brooklyn Coffee
- Meta description: We've been in Brooklyn since 2018. Our little cafe, founded by three friends.
- Canonical: /about
- Open Graph: title=About, description=Our cafe's story, type=website, image=site-wide
- Indexable: yes

### Page: Contact (/contact)
- Title: Contact — Brooklyn Coffee
- Meta description: We're on Brooklyn's Main Street. Phone, map, hours.
- Canonical: /contact
- Open Graph: title=Contact, description=Our address and hours, type=website, image=site-wide
- Indexable: yes

## Sitemap

- / (priority 1.0, changefreq weekly)
- /menu (priority 0.8, changefreq weekly)
- /about (priority 0.5, changefreq monthly)
- /contact (priority 0.5, changefreq monthly)

## robots.txt

User-agent: *
Allow: /

Sitemap: https://{deployedDomain}/sitemap.xml
```

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/sample-seo.md
git commit -m "test: add sample-seo.md fixture (brooklyn-coffee project)"
```

---

## Task 8: Smoke Tests for SEO + A11y

**Files:**
- Modify: `tests/smoke-test.md`

Add Tests 15 and 16 just before `## Pass criteria`:
- Test 15: SEO smoke — verifies seo-expert produces seo.md with expected fields
- Test 16: A11y smoke — verifies accessibility-reviewer produces a11y-report.md and applies fixes

- [ ] **Step 1: Append the new tests**

Use Edit to insert the following before `## Pass criteria`:

````markdown
## Test 15: SEO smoke (seo-expert agent)

After Test 1 generation succeeds:

1. Run `/web-builder` again from the parent (or look at the existing `brooklyn-coffee/` project).
2. Plugin runs the full pipeline; verify `seo.md` exists in the project directory.
3. Open `seo.md` and verify it has:
   - Site-wide section with default site name, description, keywords, og policy
   - Per-page sections — one ### Page block per page in brief.md
   - Sitemap section listing all pages with priority + changefreq
   - robots.txt section with User-agent + Allow + Sitemap line

Pass:
- `seo.md` exists at `{projectPath}/seo.md`
- Site title is in the user's language (Turkish for Test 1, English for Test 2)
- All page slugs (e.g., /, /menu, /about, /contact) appear in both Per-page SEO and Sitemap sections
- `state.json.agentRuns` has an entry for `seo-expert` with `wrote: ["seo.md"]` and `status: success`

## Test 16: A11y smoke (accessibility-reviewer agent)

After Test 1 generation succeeds:

1. Verify `a11y-report.md` exists in the project directory.
2. Open `a11y-report.md` and verify it has:
   - Summary section (files scanned, issues fixed, issues reported)
   - Auto-fixed issues section (or "no auto-fixes needed" if the generated code was already clean)
   - Issues reported section (or empty if everything passed)
   - Notes section (skip-to-content link, page language)
3. Spot-check the generated frontend code for a11y basics:
   - At least one `<img>` has a non-empty `alt` attribute
   - The root `<html>` has `lang="..."` matching state.json.siteLanguage
   - At least one form input (if present) has an associated `<label>` or aria-label

Pass:
- `a11y-report.md` exists at `{projectPath}/a11y-report.md`
- The summary numbers add up correctly (scanned ≥ 1, fixed + reported = total issues found)
- Spot-checks pass: no `<img>` without alt, `<html lang="...">` set
- `state.json.agentRuns` has an entry for `accessibility-reviewer`

## Test 17: A11y recheck via revise (optional)

1. After Test 1 + Test 16, manually edit a frontend file to introduce an a11y issue (e.g., remove an alt attribute from an `<img>`).
2. Run `/web-builder` and pick A (revize) → E (technical) → G (a11y recheck).
3. Plugin re-runs only `accessibility-reviewer`.
4. Verify the missing alt was auto-fixed and `a11y-report.md` lists it under "Auto-fixed issues".

Pass:
- Only `accessibility-reviewer` ran (state.json.agentRuns has new entry; no new entries for content-writer / frontend-expert / etc.)
- The `<img>` you broke has an alt again
- `a11y-report.md` mentions the fix
````

- [ ] **Step 2: Verify**

Run: `grep -nE "^## Test [0-9]+:" tests/smoke-test.md`
Expected: 17 tests (Tests 1-17).

- [ ] **Step 3: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: add SEO + a11y smoke tests (Tests 15-17)"
```

---

## Task 9: Update README + plugin.json to v0.5.0

**Files:**
- Modify: `README.md`
- Modify: `plugin.json`

- [ ] **Step 1: Update README Status section**

Find the v0.4.0 Status section. Replace with:

```markdown
## Status

**v0.5.0.** Full quality pass: per-page SEO and accessibility review run as part of every generation. All 4 site scopes supported, simple and dev modes, stack-agnostic agents.

- ✅ Generate any of 4 scope types from Q&A
- ✅ Simple mode + dev mode (`/web-builder-dev`)
- ✅ Stack-agnostic plugin: agents pick framework/language at runtime
- ✅ Stack pick recorded in `state.json.chosenStack`
- ✅ Preview locally + deploy to Cloudflare Pages / Vercel / Netlify / GitHub Pages
- ✅ Auto git initialization in simple mode
- ✅ Revise existing projects: structured Q&A + impact analysis + undo + preferences-change + a11y recheck
- ✅ Per-page SEO: every site gets `seo.md` with titles, descriptions, og policy, sitemap, robots
- ✅ Accessibility review: every generated frontend gets a pass for missing alt text, labels, semantic HTML, color contrast; auto-fixes inline + `a11y-report.md`

Not yet supported (coming in later versions): public Claude Code plugin distribution, custom domain automation, multi-language site output, Schema.org structured data, automated Lighthouse / Pa11y runs.
```

- [ ] **Step 2: Update architecture line**

Replace with:

```
Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle the dialog. Worker agents (`ui-ux-designer`, `content-writer`, `seo-expert`, `frontend-expert`, `backend-engineer`, `accessibility-reviewer`, `deployer`) write the actual files in their own context. The pipeline runs: designer → [content-writer + seo-expert parallel] → [frontend-expert + backend-engineer parallel for full-app] → accessibility-reviewer (final pass). All agents stack-agnostic.
```

- [ ] **Step 3: Bump plugin.json version**

Change `"version": "0.4.0"` to `"version": "0.5.0"`.

- [ ] **Step 4: Verify**

Run: `python3 -c "import json; print(json.load(open('plugin.json'))['version'])"` → `0.5.0`
Run: `grep -c "v0.5.0" README.md` — at least 1
Run: `grep -c "seo-expert" README.md` — at least 1
Run: `grep -c "accessibility-reviewer" README.md` — at least 1
Run: `tests/lint.sh` → `14 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add README.md plugin.json
git commit -m "docs: bump to v0.5.0 (SEO + accessibility agents shipped)"
```

---

## Task 10: Final Lint, Structural Smoke, Tag v0.5.0, Push, Merge

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.` (1 plugin.json + 2 commands + 4 skills + 7 agents).

- [ ] **Step 2: Critical guardrail — framework names in plugin code**

Run:
```bash
grep -rE "Astro|Next\.js|SvelteKit|Vue|React|Solid|Qwik|Express|FastAPI|Django|Spring|Fastify|Hono" agents/ skills/ commands/
```
Expected: 0 matches (or only in meta-comments where intentional). Plan 4 cleared this; new agents in Plan 5 must remain framework-agnostic.

- [ ] **Step 3: Structural smoke — seo-expert agent**

Set up a temp project with sample-brief.md, sample-style-guide.md, sample-content.md, and minimal state.json (`scope: multi-page-static`, mode: simple). Dispatch a subagent acting as seo-expert. Verify:
- The agent produces `seo.md` with the expected sections
- The site name and language match state.json
- All pages from brief.md appear in the per-page section + sitemap

- [ ] **Step 4: Structural smoke — accessibility-reviewer agent**

Set up a temp project with a generated frontend (re-use Plan 1's smoke output if available, or create minimal HTML files). Inject a known a11y issue (e.g., `<img src="x.jpg">` with no alt). Dispatch a subagent acting as accessibility-reviewer. Verify:
- The agent finds the missing alt and adds one
- `a11y-report.md` is produced
- The report mentions the auto-fix

- [ ] **Step 5: Tag v0.5.0**

```bash
git tag -a v0.5.0 -m "v0.5.0: SEO + accessibility agents

- New seo-expert agent (per-page titles, descriptions, og policy, sitemap, robots)
- New accessibility-reviewer agent (inline fixes + a11y-report.md)
- Orchestrator graph: designer → [content + seo parallel] → [frontend + backend parallel] → a11y-reviewer (final)
- frontend-expert and backend-engineer read seo.md for meta tags and sitemap
- Revise skill: 'Re-run accessibility check' (G) re-runs only a11y agent
- Stack-agnostic guardrail still clean (0 framework names in plugin code)
"
```

- [ ] **Step 6: Push and merge**

```bash
git push origin plan-5-seo-and-accessibility
git push --tags
git checkout main
git merge --ff-only plan-5-seo-and-accessibility
git push origin main
git branch -d plan-5-seo-and-accessibility
```

---

## Done criteria for this plan

- [ ] All 10 tasks complete with lint passing (`14 passed, 0 failed`).
- [ ] `seo-expert` and `accessibility-reviewer` agents exist with stack-agnostic prompts.
- [ ] Orchestrator graph runs them in the correct phases.
- [ ] Impact analysis table mentions both new agents.
- [ ] `frontend-expert` and `backend-engineer` reference `seo.md` as input.
- [ ] Revise skill technical category has option G (a11y recheck).
- [ ] `git tag --list` shows `v0.5.0`.
- [ ] No `TBD` / `TODO` strings in any active plugin file.
- [ ] Critical guardrail still clean: framework names absent from plugin code.

## Out of scope for this plan (deferred)

- Public Claude Code plugin distribution (Plan 6)
- Custom domain automation (v1.1)
- Multi-language site output (hreflang) (v1.1)
- Schema.org structured data (v1.x)
- Lighthouse / Pa11y automated runs (v1.x)
- Deep WCAG 3.0 audits (only WCAG 2.1 AA basics in v0.5.0)
- AI-generated og images (image gen out of scope per spec)

## Risks and edge cases

- **Color contrast checks require parsing hex values from style-guide.md**: the agent computes contrast ratios from text vs. background colors. If style-guide format drifts, contrast checks may break. Mitigation: style-guide template has a stable format (Plan 1).
- **Large project a11y review takes time**: a project with many components has many files to scan. Acceptable for MVP. Future optimization: only review files changed since last revision.
- **Auto-fixes can introduce regressions**: the agent's edits modify generated code. If the agent over-fixes (e.g., adds an alt that's wrong for the context), the user catches it on visual review. Mitigation: every fix logged in a11y-report.md so user can audit.
- **Heading hierarchy fixes are dangerous**: restructuring headings often changes content semantics. Plan 5 deliberately surfaces these as REPORTED-only, not auto-fixed.
- **seo.md generation depends on content.md being well-structured**: if content-writer produced unusual content (e.g., page titles missing), seo-expert has to infer or use placeholders. Acceptable for MVP.
- **A11y report and SEO data should NOT mention frameworks**: both are stack-agnostic by design. The guardrail check enforces this.
