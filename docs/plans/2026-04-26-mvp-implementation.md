# web-builder MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Claude Code plugin where running `/web-builder` produces a working Astro+Tailwind multi-page static website in a subfolder, after a short Q&A.

**Architecture:** A Claude Code plugin with one slash command (`/web-builder`), three skills (orchestrator, intake, deliver), and three sub-agents (`ui-ux-designer`, `content-writer`, `frontend-expert`). Skills handle user dialog and routing; agents own discrete artifacts (`brief.md`, `style-guide.md`, `content.md`, generated site code). State lives on disk in `.web-builder/state.json` plus human-readable markdown briefs.

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). Node + pnpm to install Astro for the smoke test. No build system for the plugin itself.

**MVP scope (vs. full spec):**
- Simple mode only (`/web-builder` only; no `/web-builder-dev`)
- Hardcoded scope: multi-page static site
- Hardcoded stack: Astro + Tailwind
- 3 agents only (no `seo-expert`, `accessibility-reviewer`, `backend-engineer`, `deployer`)
- No revision flow, no preview, no deploy (Plan 2 / Plan 3)
- Image policy: Unsplash placeholder URLs
- Language: auto-detect TR vs. EN
- Output: project files on disk only; user runs the site themselves

**Definition of done:** A non-technical user runs `/web-builder` from any folder, answers ~5 questions, and ends up with a subfolder containing a runnable Astro site (passes `pnpm install && pnpm build`). Generated `brief.md`, `style-guide.md`, `content.md`, and `state.json` are present and consistent. Smoke test passes.

---

## File Structure

```
web-builder/                                  # plugin repo root
├── plugin.json                               # plugin manifest
├── README.md                                 # install + usage
├── commands/
│   └── web-builder.md                        # /web-builder entry
├── skills/
│   ├── web-builder-orchestrator/
│   │   └── SKILL.md
│   ├── web-builder-intake/
│   │   └── SKILL.md
│   └── web-builder-deliver/
│       └── SKILL.md
├── agents/
│   ├── ui-ux-designer.md
│   ├── content-writer.md
│   └── frontend-expert.md
├── tests/
│   ├── fixtures/
│   │   ├── sample-brief.md
│   │   ├── sample-style-guide.md
│   │   └── sample-content.md
│   ├── lint.sh                               # frontmatter + json validation
│   └── smoke-test.md                         # manual smoke test procedure
└── docs/
    ├── specs/
    │   └── 2026-04-26-web-builder-plugin-design.md   # already exists
    └── plans/
        └── 2026-04-26-mvp-implementation.md          # this file
```

**Responsibilities:**

| File | Owns |
|---|---|
| `plugin.json` | Plugin metadata (name, version, description) |
| `commands/web-builder.md` | Thin entry; instructs Claude to load orchestrator skill in simple mode |
| `skills/web-builder-orchestrator/SKILL.md` | Top-level routing: read state → call intake → call agents in order → call deliver |
| `skills/web-builder-intake/SKILL.md` | Q&A flow; writes `brief.md` |
| `skills/web-builder-deliver/SKILL.md` | Final summary message; lists generated files |
| `agents/ui-ux-designer.md` | Reads `brief.md`, writes `style-guide.md` |
| `agents/content-writer.md` | Reads `brief.md`, writes `content.md` |
| `agents/frontend-expert.md` | Reads brief + style-guide + content, writes Astro project files |
| `tests/lint.sh` | Validates plugin.json schema + every md file's frontmatter |
| `tests/smoke-test.md` | Step-by-step manual smoke test |

---

## Task 1: Plugin Manifest Skeleton

**Files:**
- Create: `plugin.json`
- Create: `.gitignore`

- [ ] **Step 1: Create the plugin manifest**

Write `plugin.json`:

```json
{
  "name": "web-builder",
  "version": "0.1.0",
  "description": "Build a website end-to-end through guided Q&A. Asks what you want, picks the stack, generates the code.",
  "author": "Yavuz Ozguven <yavuz.ozguven@useinsider.com>",
  "license": "MIT"
}
```

- [ ] **Step 2: Create `.gitignore`**

```
.DS_Store
node_modules/
*.log
```

- [ ] **Step 3: Verify the manifest is valid JSON**

Run: `python3 -c "import json; json.load(open('plugin.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add plugin.json .gitignore
git commit -m "chore: add plugin manifest and gitignore"
```

---

## Task 2: `/web-builder` Slash Command (Thin Entry)

**Files:**
- Create: `commands/web-builder.md`

- [ ] **Step 1: Write the command file**

Create `commands/web-builder.md`:

```markdown
---
description: Build a website end-to-end through guided Q&A.
---

You are entering the web-builder flow in **simple mode** (plain language, no jargon, no stack-choice questions).

Use the `Skill` tool to invoke the `web-builder-orchestrator` skill, passing `mode=simple`.

Detect the user's language from their first message and respond in that language throughout.

Do not output anything to the user before invoking the skill — the skill itself handles all dialog.
```

- [ ] **Step 2: Verify the file is written and parses as a markdown frontmatter doc**

Run: `head -3 commands/web-builder.md`
Expected: first line is `---`, second is `description: ...`, third is `---`.

- [ ] **Step 3: Commit**

```bash
git add commands/web-builder.md
git commit -m "feat: add /web-builder slash command entry"
```

---

## Task 3: `web-builder-orchestrator` Skill — Skeleton

**Files:**
- Create: `skills/web-builder-orchestrator/SKILL.md`

This task creates the orchestrator with routing logic only — no agent invocations yet (those come in Task 8).

- [ ] **Step 1: Write the orchestrator skill**

Create `skills/web-builder-orchestrator/SKILL.md`:

```markdown
---
name: web-builder-orchestrator
description: Use when the user invokes /web-builder. Coordinates intake → agent execution → delivery for a new website project.
---

# web-builder Orchestrator (MVP)

You are the orchestrator for the web-builder plugin. You coordinate the flow but do not write content yourself — skills handle dialog, agents write artifacts.

## Inputs

- `mode`: always `simple` for this MVP (the dev-mode entry comes later).
- The user's current working directory.

## Routing logic

1. Look in the current working directory for a file at `.web-builder/state.json`.
   - **If it exists:** tell the user "since this is the MVP version I can't edit an existing project right now, but I can create a new one — should we continue?" (translate to the user's language if needed). If they decline, exit. If they accept, proceed to step 2.
   - **If it does not exist:** proceed to step 2.

2. Invoke the `web-builder-intake` skill via the `Skill` tool. Wait for it to complete. Intake will:
   - Ask the user 5 short questions
   - Create a project subdirectory under cwd, named per the user's choice
   - Write `brief.md` inside that subdirectory
   - Return the absolute path to that subdirectory

3. From this point on, **all file operations happen inside the project subdirectory.** `cd` into it before invoking agents.

4. Run the agent execution graph (see Task 8 for the full version). For now, end here with a placeholder message: "intake bitti, agent'lar Task 8'de gelecek."

5. (Future) Invoke the `web-builder-deliver` skill.

## Language

Detect the user's language from their messages and respond in that language. Default to English if unclear.

## State persistence

After every successful step, ensure `.web-builder/state.json` reflects the current state. Schema is defined in the design spec at `docs/specs/2026-04-26-web-builder-plugin-design.md` §6.2. Always include `version`, `mode`, `language`, `siteName`, `createdAt`, `lastModified`, and an append-only `agentRuns` array.

## Tone

Plain language. Never use technical terms (framework, dev server, deploy) without translating them. The user may be non-technical.
```

- [ ] **Step 2: Verify the file exists and has correct frontmatter**

Run: `head -4 skills/web-builder-orchestrator/SKILL.md`
Expected: starts with `---`, contains `name: web-builder-orchestrator`, contains `description:`, ends `---`.

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: add orchestrator skill skeleton"
```

---

## Task 4: `web-builder-intake` Skill

**Files:**
- Create: `skills/web-builder-intake/SKILL.md`

- [ ] **Step 1: Write the intake skill**

Create `skills/web-builder-intake/SKILL.md`:

````markdown
---
name: web-builder-intake
description: Use to collect the user's requirements for a new website project via short, plain-language Q&A. Writes brief.md and returns the project path.
---

# web-builder Intake (MVP)

You collect what the user wants to build through a short Q&A and write the result to `brief.md`.

## Constraints (MVP)

- Hardcoded scope: multi-page static site (do **not** ask about scope; assume this).
- Hardcoded stack: Astro + Tailwind (do **not** mention this to the user).
- Hardcoded image strategy: contextual Unsplash placeholders.

## Q&A flow

Ask one question at a time. Wait for the user's answer before asking the next.

### Q1: Free-form intro

> Hi! I'll help you out. First, tell me a bit: what is this site for, and who is it for? A couple of sentences is enough.

(English version: "Tell me about it: what is this site for, and who is it for? A couple of sentences is enough.")

Capture the answer as `goal`.

### Q2: Confirm scope interpretation

Summarize what you understood and confirm the user wants a multi-page static site (a few simple pages, no logins, no shopping cart). Example phrasing:

> Got it — sounds like a multi-page promo site (home + about + contact, etc.). Does that sound right?
>
> A) Yes
> B) Daha basit, tek sayfa yeter
> C) More complex (with sign-in / orders, etc.)

If the user picks **B** or **C**, respond:

> In the current MVP I can only make multi-page promo sites. Single-page or more complex sites are coming soon. Want to continue with multi-page anyway?

If they decline, exit cleanly. Otherwise proceed.

### Q3: Project name

Suggest **3 names** based on the goal description from Q1 — make them concrete (mention location/topic if mentioned), short (kebab-case, ≤20 chars), and distinct. Add a "kendin yaz" option.

Example:

> Here are a few names I came up with — pick one you like, or write your own:
>
> • brooklyn-coffee
> • mavi-kapi-cafe
> • corner-coffee
> • [veya kendin yaz]

Validate the chosen name: must be kebab-case, no spaces, no special characters except `-`. If invalid, ask again.

### Q4: Content source

> For the content (name, menu, photos, about text, etc.):
>
> A) I'll provide it
> B) You generate sample content, I'll edit later

If A: ask follow-ups in a focused way — collect the specific content the user has (name, contact info, page-specific text) in 1-3 follow-up questions, then move on. Don't drag this out.
If B: note in the brief that placeholders will be used.

### Q5: Style preset

> Pick a visual style:
>
> A) Minimalist (clean, white/black, few colors)
> B) Playful (colorful, fun, rounded shapes)
> C) Kurumsal (ciddi, mavi/gri, klasik)
> D) Vintage (warm tones, retro fonts)
> E) Dark/Modern (koyu zemin, vurgulu renkler)

Capture the choice as `stylePreset`.

## Side effects

After all 5 questions are answered:

1. Compute project subdirectory path: `{cwd}/{siteName}/`. If it already exists, ask the user to pick another name.
2. Create the subdirectory: `mkdir -p {projectPath}`.
3. Create `{projectPath}/.web-builder/` directory.
4. Write `{projectPath}/brief.md` using the template below.
5. Write `{projectPath}/.web-builder/state.json` with initial state (see schema in design spec §6.2). Set `mode: "simple"`, `scope: "multi-page-static"`, `stack: "astro+tailwind"`, `language` to the detected language, `siteLanguage` to the same value (MVP: assumes site is in same language the user is writing in), `createdAt` and `lastModified` to ISO timestamps, empty `agentRuns: []`.

## brief.md template

```markdown
# Site Brief: {siteName}

## Goal
{goal verbatim from Q1}

## Audience
{infer 1-2 lines from goal; if unsure, write "Not specified"}

## Pages
- Home
- About
- {plus 1-3 more pages inferred from goal: e.g., "Menu", "Services", "Contact"}

## Content Source
{"User-provided" or "Plugin will generate sample content (user will edit it later)"}

{If user provided specific content in Q4-A, append a "## User-Provided Content" section listing the items.}

## Style Preference
Preset style: {stylePreset name}

## Behavior / Interaction
- Static site, no forms.
```

If the user is writing in English, use English headings: `Goal`, `Audience`, `Pages`, `Content Source`, `User-Provided Content`, `Style`, `Interactivity`.

## Return value

Return the absolute path of the project subdirectory to the orchestrator.
````

- [ ] **Step 2: Verify the file exists and has correct frontmatter**

Run: `head -4 skills/web-builder-intake/SKILL.md`
Expected: frontmatter with `name: web-builder-intake`.

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "feat: add intake skill (5-question Q&A → brief.md)"
```

---

## Task 5: `ui-ux-designer` Agent

**Files:**
- Create: `agents/ui-ux-designer.md`

- [ ] **Step 1: Write the agent definition**

Create `agents/ui-ux-designer.md`:

````markdown
---
name: ui-ux-designer
description: Reads brief.md and produces style-guide.md (color palette, typography, spacing, layout grid, vibe notes). Specialist in translating verbal style preferences into concrete design tokens.
tools: Read, Write
---

# ui-ux-designer agent

You are a UI/UX designer. Your job is to read the brief and write a `style-guide.md` file with concrete design decisions.

## Input

You will be given the absolute path of the project directory. Read `{projectPath}/brief.md` and base your decisions on:

- The "Style" section (preset name)
- The "Goal" section (context — a cafe site warrants warm tones, a tech consultancy warrants cool tones)

## Output

Write **only** `{projectPath}/style-guide.md`. Overwrite if it exists.

## style-guide.md template

```markdown
# Style Guide

## Vibe
{1-2 sentences describing the overall feeling — "warm, inviting, low-key"}

## Color Palette
- Primary: #{hex}
- Secondary: #{hex}
- Accent: #{hex}
- Background: #{hex}
- Surface: #{hex}
- Text (primary): #{hex}
- Text (muted): #{hex}
- Border: #{hex}

## Typography
- Heading font: {Google Font name}, fallback sans-serif
- Body font: {Google Font name}, fallback sans-serif
- Heading scale: h1 2.5rem, h2 2rem, h3 1.5rem, h4 1.25rem
- Body size: 1rem
- Line height: 1.6

## Spacing scale
4px base: xs 4, sm 8, md 16, lg 24, xl 32, 2xl 48, 3xl 64

## Layout
- Container max-width: 1100px
- Grid: 12-column, 24px gutter
- Breakpoints: mobile <640px, tablet 640-1024px, desktop >1024px

## Component notes
- Buttons: {rounded vs square; filled vs outline; preset-appropriate}
- Cards: {shadow / border / radius decisions}
- Imagery: {full-bleed / contained / aspect ratios}
```

## Preset → palette guidance

If the brief's preset is one of the standard 5, use a palette appropriate to that preset (use your judgment — these are starting points, not rigid):

- **Minimalist:** mostly neutrals (white background, near-black text), one restrained accent color (often dark green, navy, or terracotta).
- **Playful:** saturated palette, multiple bright colors, soft rounded shapes.
- **Kurumsal / Corporate:** blues and grays, conservative serif or sans-serif, generous whitespace.
- **Vintage:** warm earth tones (cream, rust, mustard), serif typography, slightly muted contrast.
- **Dark/Modern:** dark background (#0a0a0a or similar), bright single accent (cyan, magenta, electric green), modern geometric sans-serif.

If the brief's "Goal" mentions a specific industry or location, lean into colors that fit (e.g., "cafe" → warm browns/creams even if preset is minimalist).

## Constraints

- Pick fonts that exist on Google Fonts.
- Ensure the primary text color has WCAG AA contrast (4.5:1) against background.
- Do not write any other files. Do not modify the brief.
- Output a one-line summary at the end of your turn for the orchestrator: `style-guide.md written: <2-line summary of palette + fonts>`.
````

- [ ] **Step 2: Verify file**

Run: `head -5 agents/ui-ux-designer.md`
Expected: frontmatter with `name`, `description`, `tools: Read, Write`.

- [ ] **Step 3: Commit**

```bash
git add agents/ui-ux-designer.md
git commit -m "feat: add ui-ux-designer agent"
```

---

## Task 6: `content-writer` Agent

**Files:**
- Create: `agents/content-writer.md`

- [ ] **Step 1: Write the agent definition**

Create `agents/content-writer.md`:

````markdown
---
name: content-writer
description: Reads brief.md and produces content.md (per-page text, headings, image placeholder URLs). Generates contextually appropriate copy in the user's language.
tools: Read, Write
---

# content-writer agent

You write the actual text content of the site, page by page.

## Input

Read `{projectPath}/brief.md`. Pay attention to:

- Page list (use exactly these pages, in this order)
- Content source: if "user-provided", use user-provided content verbatim and only fill gaps; if "plugin-generated", invent contextually appropriate placeholder content
- Goal and audience (set tone accordingly)
- Site language (use the same language as the brief)

## Output

Write **only** `{projectPath}/content.md`. Overwrite if exists.

## content.md template

```markdown
# Site Content

## Site-wide

- Site title: {short, ≤30 chars}
- Tagline: {one short sentence}
- Logo text: {usually same as site title}
- Footer text: © {year} {site title} — {1 short line}

## Page: Home

### Hero
- Heading: {compelling primary headline, 5-9 words}
- Subheading: {1-2 sentences elaborating}
- Primary CTA label: {"See the Menu", "Get in Touch", etc. — tied to goal}
- Hero image: https://images.unsplash.com/photo-{appropriate-id}?w=1600&q=80
  - Alt text: {descriptive}
  - PLACEHOLDER: yes

### Section: {whatever section makes sense}
- Heading: {...}
- Body: {2-4 sentences}
- {repeat for 2-3 sections on the home page}

## Page: {next page}

{same structure: page-appropriate sections, headings, body, images-with-alt-text-and-PLACEHOLDER-flag}

(... repeat for all pages in brief)

## Image Inventory

| File | Used on | Source | Replace with own? |
|---|---|---|---|
| hero-home | Ana sayfa hero | Unsplash {url} | Recommended |
| {...} | {...} | {...} | {...} |
```

## Image policy

- All images are Unsplash placeholders. Use real Unsplash URLs (`https://images.unsplash.com/photo-{id}?w={width}&q=80`). Pick photo IDs that genuinely match the topic — search Unsplash mentally for "cafe interior" if it's a cafe brief, etc. If unsure of a real ID, use a parameterized placeholder URL like `https://source.unsplash.com/1600x900/?cafe,coffee`.
- Always mark images as `PLACEHOLDER: yes` in the content document and include in the Image Inventory.
- Always provide descriptive alt text in the language of the site.

## Constraints

- Match the site language (read it from the brief).
- Keep copy short and concrete. No lorem ipsum.
- Match the tone implied by the goal: a cafe site is warm and informal; a consultancy site is concise and professional.
- Do not write any other files. Do not modify the brief or style-guide.
- Output a one-line summary at the end: `content.md written: {N pages}, {N images}.`
````

- [ ] **Step 2: Verify file**

Run: `head -5 agents/content-writer.md`
Expected: frontmatter present.

- [ ] **Step 3: Commit**

```bash
git add agents/content-writer.md
git commit -m "feat: add content-writer agent"
```

---

## Task 7: `frontend-expert` Agent

**Files:**
- Create: `agents/frontend-expert.md`

- [ ] **Step 1: Write the agent definition**

Create `agents/frontend-expert.md`:

````markdown
---
name: frontend-expert
description: Reads brief, style-guide, and content; produces a complete Astro + Tailwind CSS multi-page static site project that builds successfully.
tools: Read, Write, Edit, Bash, Glob
---

# frontend-expert agent (MVP)

You generate a working Astro + Tailwind CSS project from `brief.md`, `style-guide.md`, and `content.md`.

## Input

Read in this order:
1. `{projectPath}/brief.md` (page list, site name)
2. `{projectPath}/style-guide.md` (palette, typography, spacing)
3. `{projectPath}/content.md` (per-page content, image URLs)

## Output: Astro project structure

Generate the following files inside `{projectPath}/` (alongside the existing brief/style-guide/content):

```
{projectPath}/
├── astro.config.mjs
├── package.json
├── tsconfig.json
├── tailwind.config.mjs
├── postcss.config.cjs
├── src/
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── components/
│   │   ├── Header.astro
│   │   └── Footer.astro
│   ├── pages/
│   │   ├── index.astro                  # for "Ana sayfa"
│   │   └── {one .astro file per other page in brief, kebab-case filename}
│   └── styles/
│       └── global.css                    # contains @tailwind directives + CSS variables for the palette
└── public/
    └── favicon.svg                       # simple monochrome SVG using primary color
```

## Concrete file contents

### `package.json`

```json
{
  "name": "{siteName from brief}",
  "type": "module",
  "version": "0.1.0",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^4.16.0",
    "@astrojs/tailwind": "^5.1.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### `astro.config.mjs`

```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind({ applyBaseStyles: false })],
});
```

### `tsconfig.json`

```json
{
  "extends": "astro/tsconfigs/strict"
}
```

### `tailwind.config.mjs`

Map the colors from `style-guide.md` into the tailwind theme:

```javascript
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: '{from style-guide}',
        secondary: '{from style-guide}',
        accent: '{from style-guide}',
        bg: '{from style-guide}',
        surface: '{from style-guide}',
        text: { DEFAULT: '{from style-guide}', muted: '{from style-guide}' },
        border: '{from style-guide}',
      },
      fontFamily: {
        sans: ['{body font from style-guide}', 'system-ui', 'sans-serif'],
        heading: ['{heading font from style-guide}', 'system-ui', 'sans-serif'],
      },
      maxWidth: { container: '1100px' },
    },
  },
  plugins: [],
};
```

### `postcss.config.cjs`

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### `src/styles/global.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family={heading-font-name-spaces-as-+}:wght@400;600;700&family={body-font-name-spaces-as-+}:wght@400;500;600&display=swap');

html { font-family: theme('fontFamily.sans'); color: theme('colors.text.DEFAULT'); background: theme('colors.bg'); }
h1, h2, h3, h4 { font-family: theme('fontFamily.heading'); }
```

### `src/layouts/BaseLayout.astro`

```astro
---
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import '../styles/global.css';

interface Props { title: string; description?: string; }
const { title, description = '{site tagline from content.md}' } = Astro.props;
---
<!DOCTYPE html>
<html lang="{siteLanguage from state.json}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <meta name="description" content={description} />
  </head>
  <body class="bg-bg text-text">
    <Header />
    <main class="max-w-container mx-auto px-4 py-8"><slot /></main>
    <Footer />
  </body>
</html>
```

### `src/components/Header.astro`

```astro
---
const navItems = [
  { label: 'Ana sayfa', href: '/' },
  // one per page in brief, with proper paths
];
---
<header class="border-b border-border">
  <div class="max-w-container mx-auto px-4 py-4 flex items-center justify-between">
    <a href="/" class="font-heading font-bold text-xl text-primary">{site title from content.md}</a>
    <nav class="flex gap-6">
      {navItems.map(item => <a href={item.href} class="text-text-muted hover:text-text">{item.label}</a>)}
    </nav>
  </div>
</header>
```

### `src/components/Footer.astro`

```astro
<footer class="border-t border-border mt-16">
  <div class="max-w-container mx-auto px-4 py-6 text-text-muted text-sm">
    {footer text from content.md}
  </div>
</footer>
```

### `src/pages/index.astro` (Ana sayfa)

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="{site title}">
  <section class="py-16 text-center">
    <h1 class="text-5xl font-heading mb-4">{hero heading from content.md}</h1>
    <p class="text-xl text-text-muted mb-8">{hero subheading}</p>
    <a href="{appropriate link, e.g. /menu}" class="inline-block bg-primary text-white px-6 py-3 rounded-md font-medium">
      {hero CTA label}
    </a>
  </section>

  <img src="{hero image URL from content.md}" alt="{alt text}" class="w-full rounded-lg" />

  <!-- Render additional sections from content.md "Page: Ana sayfa" -->
</BaseLayout>
```

### Other pages (one per page from brief)

Use the same pattern: import `BaseLayout`, render the page-specific content from `content.md` into appropriately structured sections (heading, paragraphs, images).

### `public/favicon.svg`

A simple SVG using the primary color, e.g.:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="{primary color hex}"/></svg>
```

## After writing files

Run `pnpm install --silent` (or `npm install --silent` if pnpm absent) **inside the project directory**, then run `pnpm build` (or `npm run build`).

If the build fails, fix the offending file and retry. Report the failure to the orchestrator only if you cannot resolve it after 2 attempts.

## Constraints

- Read brief, style-guide, content. Write only Astro project files.
- Do not modify brief.md, style-guide.md, content.md.
- Respect the language: page titles, headings, alt text, nav labels all come from content.md (which is already in the user's language).
- Output a one-line summary at the end: `frontend generated: {N pages}, build {ok|failed}.`
````

- [ ] **Step 2: Verify file**

Run: `head -5 agents/frontend-expert.md`
Expected: frontmatter present.

- [ ] **Step 3: Commit**

```bash
git add agents/frontend-expert.md
git commit -m "feat: add frontend-expert agent (Astro + Tailwind generator)"
```

---

## Task 8: Wire Up the Orchestrator to Run Agents

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md`

- [ ] **Step 1: Replace the orchestrator skill body**

Open `skills/web-builder-orchestrator/SKILL.md` and replace **everything below the frontmatter** with:

````markdown
# web-builder Orchestrator (MVP)

You are the orchestrator for the web-builder plugin. Skills handle dialog, agents write artifacts, you coordinate.

## Inputs

- `mode`: always `simple` for this MVP.
- The user's current working directory.

## Routing logic

1. Look in cwd for `.web-builder/state.json`.
   - **If it exists:** tell the user "since this is the MVP I can't edit an existing project right now, but I can create a new one — should we continue?" (translate to the user's language if needed). If they decline, exit. Otherwise proceed.
   - **If it does not exist:** proceed.

2. Invoke the `web-builder-intake` skill via the `Skill` tool. Wait for completion.
   - Intake returns the absolute path of the project subdirectory it created.
   - If intake exits early (user declined the scope), exit too.

3. Run the agent execution graph against the project directory:

   **Step A — `ui-ux-designer` agent**

   Use the `Agent` tool with `subagent_type: "ui-ux-designer"`. Pass a prompt that includes the absolute project path:

   > Project path: `{projectPath}`. Read brief.md and write style-guide.md per your instructions.

   Wait for completion. Append to `state.json` `agentRuns`:
   ```json
   {"agent": "ui-ux-designer", "at": "<ISO>", "wrote": ["style-guide.md"], "status": "<success|failed>"}
   ```

   On failure: retry once with the same prompt. If it fails again, report to the user, append the failure to `agentRuns`, and ask whether to abort or try once more. Do not silently continue.

   **Step B — `content-writer` agent**

   Same pattern, `subagent_type: "content-writer"`, writes `content.md`. Same retry policy.

   **Step C — `frontend-expert` agent**

   Same pattern, `subagent_type: "frontend-expert"`, writes the Astro project files and runs the build. Same retry policy.

4. Update `state.json`:
   - Set `lastModified` to current ISO timestamp.
   - Set `briefHash` to SHA-256 of the current `brief.md` contents (compute via `Bash`: `shasum -a 256 brief.md | cut -d' ' -f1`).

5. Invoke the `web-builder-deliver` skill via the `Skill` tool, passing the project path.

## Error handling

For every agent invocation:
- Auto-retry once on failure.
- Always report the failure (and retry result) to the user — never silent.
- After two consecutive failures, pause and present three options: "retry" / "skip this agent" (only allowed for non-blocking agents — this MVP has none, so disable for now) / "cancel".
- Append every attempt (success or failure) to `state.json` `agentRuns` with timestamp and outcome.

## Concurrency

Runs sequentially in the MVP: ui-ux-designer → content-writer → frontend-expert. (Spec calls for parallel content+seo, but seo isn't in MVP and parallel adds complexity for one extra agent.)

## Tone

Plain language. Translate every technical term. The user may be non-technical.

## Language

Detect from the user's first message; respond in that language throughout.
````

- [ ] **Step 2: Verify the orchestrator now references all three agents and the deliver skill**

Run:
```bash
grep -c "subagent_type" skills/web-builder-orchestrator/SKILL.md
grep -c "web-builder-deliver" skills/web-builder-orchestrator/SKILL.md
grep -c "web-builder-intake" skills/web-builder-orchestrator/SKILL.md
```
Expected: at least `3`, `1`, `1` respectively.

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: wire orchestrator to invoke 3 agents + deliver skill"
```

---

## Task 9: `web-builder-deliver` Skill (Local-Only MVP)

**Files:**
- Create: `skills/web-builder-deliver/SKILL.md`

- [ ] **Step 1: Write the deliver skill**

Create `skills/web-builder-deliver/SKILL.md`:

````markdown
---
name: web-builder-deliver
description: Use after a successful web-builder generation to summarize what was created and tell the user how to view it, in plain language.
---

# web-builder Deliver (MVP)

You wrap up the generation by summarizing what's on disk and telling the user how to see the site.

## Inputs

- `projectPath`: absolute path to the generated project directory.

## Behavior

1. List the top-level files in `projectPath` (Bash: `ls {projectPath}`).
2. Open `{projectPath}/state.json` to read the site name and language.
3. Output a friendly summary in the user's language. The summary must include:
   - Confirmation that the site is ready
   - The absolute path of the project directory
   - A 1-sentence explanation of what each top-level markdown file is (`brief.md`, `style-guide.md`, `content.md`) and that the user can edit them by hand
   - Instructions to view the site, in plain language. **Do not say "run the dev server"** — say something like:

     > To view the site in your browser: cd into this folder and run these commands:
     >
     > ```
     > cd {projectPath}
     > pnpm dev
     > ```
     >
     > Then open [http://localhost:4321](http://localhost:4321) in your browser.

   - A note that preview, deploy, and revision features are coming in the next versions of the plugin.

4. Do not start a dev server yourself. (That's a Plan 2 feature.)

## Tone

Warm, plain language, no jargon. If the user has been technical, you can be slightly less verbose with explanations.
````

- [ ] **Step 2: Verify file**

Run: `head -4 skills/web-builder-deliver/SKILL.md`
Expected: frontmatter with `name: web-builder-deliver`.

- [ ] **Step 3: Commit**

```bash
git add skills/web-builder-deliver/SKILL.md
git commit -m "feat: add deliver skill (MVP: local-only summary)"
```

---

## Task 10: Test Fixtures

**Files:**
- Create: `tests/fixtures/sample-brief.md`
- Create: `tests/fixtures/sample-style-guide.md`
- Create: `tests/fixtures/sample-content.md`

These fixtures exist so you can sanity-check agent behavior without going through the full intake flow.

- [ ] **Step 1: Write `tests/fixtures/sample-brief.md`**

```markdown
# Site Brief: brooklyn-coffee

## Goal
A promo site for a small cafe in Brooklyn. Third-wave coffee and homemade sandwiches.

## Audience
Neighborhood residents and visitors.

## Pages
- Home
- Menu
- About
- Contact

## Content Source
Plugin will generate sample content (user will edit it later).

## Style Preference
Preset style: minimalist

## Behavior / Interaction
- Static site, no forms.
```

- [ ] **Step 2: Write `tests/fixtures/sample-style-guide.md`**

A representative output the `ui-ux-designer` agent should approximate when given the sample brief. Used as a sanity reference, not a strict expectation.

```markdown
# Style Guide

## Vibe
Warm, low-key, neighborhood-friendly. Plenty of whitespace, one earthy accent.

## Color Palette
- Primary: #3F4B3B
- Secondary: #C9B79C
- Accent: #C2410C
- Background: #FAFAF7
- Surface: #FFFFFF
- Text (primary): #1F1F1F
- Text (muted): #6B6B6B
- Border: #E5E5E0

## Typography
- Heading font: Fraunces, fallback serif
- Body font: Inter, fallback sans-serif
- Heading scale: h1 2.5rem, h2 2rem, h3 1.5rem, h4 1.25rem
- Body size: 1rem
- Line height: 1.6

## Spacing scale
4px base: xs 4, sm 8, md 16, lg 24, xl 32, 2xl 48, 3xl 64

## Layout
- Container max-width: 1100px
- Grid: 12-column, 24px gutter
- Breakpoints: mobile <640px, tablet 640-1024px, desktop >1024px

## Component notes
- Buttons: square corners, filled with primary, white text
- Cards: subtle 1px border, no shadow
- Imagery: full-bleed hero, contained for body images, 3:2 aspect ratio
```

- [ ] **Step 3: Write `tests/fixtures/sample-content.md`**

```markdown
# Site Content

## Site-wide
- Site title: Brooklyn Coffee
- Tagline: The neighborhood's little coffee shop.
- Logo text: Brooklyn Coffee
- Footer text: © 2026 Brooklyn Coffee — Third-wave coffee and homemade sandwiches.

## Page: Home

### Hero
- Heading: Brooklyn's Coziest Coffee Shop
- Subheading: Hand-crafted coffee, homestyle sandwiches, and a neighborhood vibe.
- Primary CTA label: See the Menu
- Hero image: https://source.unsplash.com/1600x900/?cafe,coffee
  - Alt text: A cup full of coffee in warm light
  - PLACEHOLDER: yes

### Section: Our Story
- Heading: We've been in Brooklyn since 2018
- Body: This little place, opened by three friends, became the neighborhood's gathering spot. We grind fresh coffee every morning and prepare sandwiches by hand.

## Page: Menu
{... abbreviated for fixture purposes ...}

## Image Inventory

| File | Used on | Source | Replace with own? |
|---|---|---|---|
| hero-home | Home hero | Unsplash | Recommended |
```

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add sample brief / style-guide / content fixtures"
```

---

## Task 11: Lint Script

**Files:**
- Create: `tests/lint.sh`

- [ ] **Step 1: Write the lint script**

Create `tests/lint.sh`:

```bash
#!/usr/bin/env bash
# Lint the plugin: validate plugin.json + every md file's frontmatter.
set -euo pipefail

cd "$(dirname "$0")/.."

ok=0
fail=0

# --- plugin.json ---
echo -n "plugin.json valid JSON: "
if python3 -c "import json,sys; d=json.load(open('plugin.json')); assert 'name' in d and 'version' in d and 'description' in d" 2>/dev/null; then
  echo "OK"; ok=$((ok+1))
else
  echo "FAIL"; fail=$((fail+1))
fi

# --- frontmatter check ---
check_frontmatter() {
  local file="$1"
  local needs_name="$2"   # "yes" for skills/agents, "no" for commands
  local first_line
  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    echo "FAIL ($file: missing frontmatter opening)"; return 1
  fi
  if ! grep -q "^description:" "$file"; then
    echo "FAIL ($file: missing description)"; return 1
  fi
  if [[ "$needs_name" == "yes" ]] && ! grep -q "^name:" "$file"; then
    echo "FAIL ($file: missing name)"; return 1
  fi
  echo "OK ($file)"; return 0
}

# Commands: name not required (filename is the command name).
for f in commands/*.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "no"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

# Skills: name required.
for f in skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "yes"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

# Agents: name required.
for f in agents/*.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "yes"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

echo
echo "Summary: ${ok} passed, ${fail} failed."
[[ $fail -eq 0 ]]
```

- [ ] **Step 2: Make executable**

```bash
chmod +x tests/lint.sh
```

- [ ] **Step 3: Run it**

Run: `tests/lint.sh`
Expected: every line ends in `OK`, summary is `N passed, 0 failed.`, exit code 0.

- [ ] **Step 4: Commit**

```bash
git add tests/lint.sh
git commit -m "test: add lint script for manifest + frontmatter validation"
```

---

## Task 12: Smoke Test Procedure

**Files:**
- Create: `tests/smoke-test.md`

Since the plugin's behavior depends on Claude Code execution, the smoke test is a documented manual procedure rather than an automated script.

- [ ] **Step 1: Write the smoke test doc**

Create `tests/smoke-test.md`:

```markdown
# web-builder MVP Smoke Test

Run this from a terminal with Claude Code installed and the web-builder plugin loaded.

## Setup

1. Install the plugin locally (until v1.0 ships publicly):

   ```bash
   # From the web-builder repo root:
   claude code plugin install .
   # or whatever the local install command is for the current Claude Code version
   ```

2. Create a clean working directory and cd into it:

   ```bash
   mkdir -p /tmp/web-builder-smoke && cd /tmp/web-builder-smoke
   ```

## Test 1: Turkish, plugin-generated content, minimalist

1. Run: `claude` (start Claude Code in this directory).
2. In the prompt, type: `/web-builder`
3. Expected: plugin asks Q1 in Turkish (because no language signal yet — should default to whichever; if it picks English, type your answer in Turkish and it should switch).
4. Answer Q1: `I have a small cafe in Brooklyn, I sell coffee and sandwiches, I want a promo site.`
5. Expected: plugin summarizes "multi-page promo site" interpretation; presents A/B/C choice. Pick A.
6. Expected: plugin suggests 3 names + "write your own" option. Pick the first suggestion (or type a custom name like `brooklyn-coffee`).
7. Expected: plugin asks content source (A/B). Pick B.
8. Expected: plugin asks style preset (A-E). Pick A (Minimalist).
9. Expected: plugin runs three agents sequentially (designer → content → frontend), reporting progress. Frontend agent runs `pnpm install` and `pnpm build`.
10. Expected: deliver skill summarizes the output and tells you how to view the site (`cd brooklyn-coffee && pnpm dev`).

## Verify

```bash
cd /tmp/web-builder-smoke/<chosen-name>
ls -la
```

Expected files present:
- `brief.md`, `style-guide.md`, `content.md`
- `.web-builder/state.json`
- `package.json`, `astro.config.mjs`, `tailwind.config.mjs`, `tsconfig.json`, `postcss.config.cjs`
- `src/layouts/BaseLayout.astro`, `src/components/Header.astro`, `src/components/Footer.astro`
- `src/pages/index.astro` plus one `.astro` file per non-home page from the brief
- `src/styles/global.css`
- `public/favicon.svg`
- `node_modules/`, `dist/` (if build succeeded)

Run: `pnpm dev` and open http://localhost:4321.

Expected: all pages render, navigation between pages works, hero image loads, palette and fonts match the style-guide.

Run: `cat .web-builder/state.json | python3 -m json.tool`
Expected: `mode=simple`, `scope=multi-page-static`, `stack=astro+tailwind`, `siteName` matches chosen name, `agentRuns` has 3 entries, all `status=success`.

## Test 2: English, user-provided content, dark/modern preset

Repeat Test 1 but in English. At Q4 pick A (user-provided), and supply a name + tagline + 1-2 lines of about-us text. At Q5 pick E.

Expected: brief.md, content.md, and rendered site are in English.

## Pass criteria

- Both tests complete without manual intervention beyond answering questions.
- Both generated sites build successfully (`pnpm build` exits 0).
- Both sites render in the browser without console errors.
- `state.json` is well-formed in both runs.

## If a test fails

Log the failure: which task's output broke things, what error was reported, what files were/weren't written. File a follow-up bug for the broken task.
```

- [ ] **Step 2: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: add manual smoke test procedure"
```

---

## Task 13: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

Create `README.md`:

````markdown
# web-builder

A Claude Code plugin that builds you a website end-to-end through guided Q&A. You describe what you want, the plugin asks a few quick questions, and you end up with a working site in a folder.

## Status

**v0.1.0 — MVP.** Multi-page static sites only (Astro + Tailwind). Simple mode only.

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), preview/deploy, revision flow, SEO/accessibility agents.

## Install (local, pre-v1.0)

```bash
git clone https://github.com/<your-username>/web-builder.git
cd web-builder
claude code plugin install .   # or the equivalent local-install command for your Claude Code version
```

## Use

```bash
mkdir my-projects && cd my-projects
claude
```

In the Claude prompt:

```
/web-builder
```

Answer 5 short questions. The plugin creates a subfolder with a working Astro site and tells you how to view it.

## What the plugin generates

```
{project-name}/
├── brief.md              # what you told the plugin you wanted
├── style-guide.md        # color palette, fonts, layout decisions
├── content.md            # page-by-page text and images
├── .web-builder/
│   └── state.json        # plugin's own state (you don't need to touch this)
├── package.json
├── astro.config.mjs
├── src/
│   ├── layouts/
│   ├── components/
│   ├── pages/
│   └── styles/
└── public/
```

You can edit `brief.md`, `style-guide.md`, or `content.md` by hand — the plugin will honor those edits in future versions when the revision flow ships.

## View your site

```bash
cd {project-name}
pnpm dev
# open http://localhost:4321
```

## Architecture (one-liner)

Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-deliver`) handle the dialog with you. Agents (`ui-ux-designer`, `content-writer`, `frontend-expert`) write the actual files in their own context. State lives in `state.json` plus a few human-readable markdown files.

See `docs/specs/2026-04-26-web-builder-plugin-design.md` for the full design.

## License

MIT
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Task 14: Run Lint, Run Smoke Test, Tag v0.1.0

- [ ] **Step 1: Run the lint script**

Run: `tests/lint.sh`
Expected: all `OK`, exit 0.

- [ ] **Step 2: Run the manual smoke test**

Follow `tests/smoke-test.md` end to end. Both Test 1 and Test 2 must pass.

- [ ] **Step 3: If smoke test reveals bugs**

Fix them. Re-run lint and smoke test. Commit the fixes with descriptive messages.

- [ ] **Step 4: Tag the release**

```bash
git tag -a v0.1.0 -m "v0.1.0 MVP: simple mode + multi-page-static + 3 agents"
git log --oneline
git tag --list
```

Expected: tag `v0.1.0` is present and points at the latest commit.

- [ ] **Step 5: Push (when ready)**

The plan stops here for the MVP. Pushing to GitHub and registering as a public Claude Code plugin is **Plan 6: Public Distribution.** Until then, this stays local.

---

## Done criteria for this plan

- [ ] All 14 tasks complete with tests/lint passing.
- [ ] Smoke test (Test 1 + Test 2) passes manually.
- [ ] `git tag --list` shows `v0.1.0`.
- [ ] No `TBD` / `TODO` strings in any file in `commands/`, `skills/`, `agents/`, `plugin.json`, or `README.md`.

## Out of scope for this plan (deferred to later plans)

- Preview / deploy → Plan 2
- Revision flow → Plan 3
- Other scopes (single page, interactive, full app) + `/web-builder-dev` + stack overrides → Plan 4
- `seo-expert`, `accessibility-reviewer` agents → Plan 5
- Public GitHub publish + Claude Code public plugin registration → Plan 6
