# web-builder — Design Spec

**Date:** 2026-04-26
**Status:** Draft (post-brainstorm, pre-implementation plan)
**Owner:** Yavuz Ozguven

## 1. Overview

A Claude Code plugin that helps users build complete websites through structured Q&A. The plugin guides users (technical or not) from a vague idea ("kafem için bir site") to a working, deployed site, using a small team of specialized sub-agents that own discrete artifacts (style guide, content, SEO, frontend code, backend, accessibility, deployment).

The plugin's value over a free-form Claude conversation is:

- **Structured discovery** — adaptive Q&A guarantees that scope, content, style, and deployment intent are all captured before code is written.
- **Plain-language tone** — non-technical users never need to know what a "dev server" or "framework" is; the plugin translates.
- **Separation of decision and execution** — skills talk to the user, agents implement. Each agent has one focused responsibility and runs in its own context.
- **Brief-driven, editable state** — every plugin decision lives in human-readable markdown files the user can edit by hand. The plugin honors edits.
- **Same flow for revisions** — changes go through the same structured Q&A; orchestrator runs only the affected agents.

## 2. Goals & Non-Goals

### v1 Goals

- 2 slash commands: `/web-builder` (sade mode) and `/web-builder-dev` (technical mode)
- 4 skills: `web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`
- 7 agents: `ui-ux-designer`, `content-writer`, `seo-expert`, `frontend-expert`, `backend-engineer`, `accessibility-reviewer`, `deployer`
- 4 supported scopes: single page / multi-page static / interactive static / full web app
- 4 default stack mappings (vanilla / Astro / Astro+islands / Next.js)
- Adaptive Q&A flow with auto language detection (TR + EN at minimum)
- Brief-driven state model: `state.json` + `brief.md` + `style-guide.md` + `content.md` + `seo.md`
- Structured revision flow with impact analysis (only affected agents re-run)
- Automatic git commits (silent in sade mode, opt-in in dev mode)
- Deployment options: Cloudflare Pages, Vercel, Netlify, GitHub Pages, local-only
- Image policy: contextual Unsplash placeholders + user upload (no AI image generation)
- **Public distribution** as a Claude Code plugin via GitHub repo

### Non-Goals (v1)

- AI image generation (Claude has none; no external service binding)
- Custom domain automation (plugin explains, user does)
- Test framework setup (Vitest / Playwright / etc.)
- CMS integration (Sanity, Contentful, etc.)
- E-commerce (Stripe, product management)
- Multi-language site output (TR + EN switcher) — single site language only
- Plugin web dashboard / GUI — terminal Q&A only
- Multi-user collaboration on the same project
- Embedded telemetry / analytics
- Marketplace / template library — agents generate; no stored templates

### Roadmap (v1.1+)

- Cloudflare Pages automation, custom domain setup
- Multi-language site output
- Opt-in test framework setup
- AI image generation (if Claude gains image gen)
- Template marketplace (users share their briefs)

## 3. Design Principles

1. **Plain language always.** No technical term reaches a sade-mode user. In dev mode, terms are added but sentences stay human.
2. **Adaptive over standard.** Q&A length and depth scale with user level and chosen scope. Sade user / single page → ~5 questions. Dev user / full app → 15+.
3. **Human-readable state.** Every plugin decision lands in a markdown file the user can open and edit. The plugin re-reads on next invocation and reconciles.
4. **Decision = skill, execution = agent.** User-facing dialogue belongs to skills. Heavy generation belongs to agents in their own context.
5. **Generation = revision.** Not two flows — one mechanism with two entry points. Same files updated; impact analysis chooses which agents re-run.

## 4. User Flows

### 4.1 Initial Generation (sade mode example)

```
$ /web-builder
🤖 Selam! Sana yardım edeceğim. Önce bana biraz anlat:

1) Bu site ne için, kim için olacak? Birkaç cümle yeterli.
   > "Kafem için bir tanıtım sitesi. Kadıköy'de küçük bir yerim,
      kahve ve sandviç satıyorum."

2) [plugin özetler ve scope'u önerir]
   "Anladım — çok sayfalı bir tanıtım sitesi gibi duruyor
   (ana sayfa + menü + iletişim). Sence de öyle mi?"
   A) Evet     B) Daha basit, tek sayfa yeter
   C) Daha karmaşık, üye girişi/sipariş gibi şeyler de olsun
   > A

3) Sana birkaç isim önerdim — beğenirsen seç, beğenmezsen kendin yaz:
   • kadikoy-kahve
   • mavi-kapi-cafe
   • korner-kahve
   • [veya kendin yaz]
   > "kadikoy-kahve"

4) İçerik (isim, menü, fotoğraflar, hakkımızda metni vs.) için:
   A) Ben vereceğim    B) Sen örnek içerik üret, sonra değiştiririm
   > B

5) Görsel stil için:
   A) Hazır stillerden seç (minimalist / playful / kurumsal / vintage / dark-modern)
   B) Kendin tarif et    C) Bir referans site göster
   > A → "minimalist"

[adaptive: 0-10 follow-up questions based on scope and answers]
```

### 4.2 Initial Generation (dev mode delta)

`/web-builder-dev` runs the same flow but adds:

- After scope confirmation: stack override question ("Astro öneriyorum, değiştirmek ister misin?")
- After content/style: lint, formatter, TypeScript, package manager preferences
- A summary at the end naming the exact packages to be installed
- All agent outputs are surfaced verbose (a11y report shown, not silent)

### 4.3 Behind the Scenes (initial generation)

```
intake skill            → brief.md
        ↓
orchestrator            → reads brief, plans agent execution graph
        ↓
ui-ux-designer agent    → style-guide.md
        ↓ (sequential — others depend on style decisions)
[parallel:]
  content-writer        → content.md
  seo-expert            → seo.md
        ↓
frontend-expert         → site source files
backend-engineer        → API/DB (only if scope = full app; parallel with frontend)
        ↓
accessibility-reviewer  → in-place fixes + a11y-report.md
        ↓
deliver skill           → "site hazır, görmek ister misin?" → optional deployer
```

### 4.4 Revision Flow

Trigger: user invokes `/web-builder` or `/web-builder-dev` again. Plugin sees `.web-builder/state.json` in the cwd and asks "geçen sefer şunu yapmıştık, devam edelim mi yoksa yeni bir site mi?"

```
🤖 Tamam, kadikoy-kahve'ye dönüyoruz. Neyi değiştirmek istersin?

A) Görsel stil (renkler, font, layout)
B) İçerik (metinler, menü, kontak)
C) Yapı/sayfa eklemek-çıkarmak
D) Davranış (form, animasyon, etkileşim)
E) Teknik (deploy ayarı, performance, SEO meta)
F) Bunlar değil, ben tarif edeyim — serbest yazayım
> A

Stil için ne değiştirelim?
A) Renk paletini değiştir    B) Font değiştir
C) Genel havayı değiştir     D) Belirli bir bölüm
> A

Şu an: minimalist, beyaz/siyah/açık-yeşil. Ne istersin?
> "biraz daha sıcak olsun, kahverengi ağırlıklı"
```

### 4.5 Revision Behind the Scenes

```
revise skill   → user intent normalized to a structured change record
        ↓
orchestrator   → impact analysis: which artifact(s) and which agent(s)?
        ↓
[for the example above:]
  ui-ux-designer → updates style-guide.md
        ↓
  frontend-expert → re-renders code against new style-guide
        ↓
  (content unchanged → content-writer skipped)
  (seo unchanged → seo-expert skipped)
        ↓
deliver skill  → "değişiklikler hazır, bakar mısın?"
```

Rules:

- **Impact analysis** — orchestrator runs the minimum set. "Renk değiştir" → designer + frontend. "Yeni sayfa" → designer + content-writer + seo + frontend.
- **Manual brief edits** — plugin compares current `brief.md` hash with last-known hash from `state.json`. If different, asks "brief'i değiştirmişsin, etkilenen kısımları yeniden üreteyim mi?"
- **Undo** — every revision is preceded by an automatic git commit. "Son değişikliği geri al" reverts to the previous commit.
- **Free-form mode (F)** — plugin maps the user's free-form description to a structured category, confirms, then routes through the normal flow.

## 5. Architecture

### 5.1 Plugin Layout

```
web-builder/
├── plugin.json
├── commands/
│   ├── web-builder.md          # /web-builder (sade entry)
│   └── web-builder-dev.md      # /web-builder-dev (dev entry)
├── skills/
│   ├── web-builder-orchestrator/
│   ├── web-builder-intake/
│   ├── web-builder-revise/
│   └── web-builder-deliver/
└── agents/
    ├── ui-ux-designer.md
    ├── content-writer.md
    ├── seo-expert.md
    ├── frontend-expert.md
    ├── backend-engineer.md
    ├── accessibility-reviewer.md
    └── deployer.md
```

### 5.2 Responsibilities

| Component | Type | Job |
|---|---|---|
| `web-builder.md` / `web-builder-dev.md` | command | Thin entry; sets mode flag; invokes orchestrator |
| `web-builder-orchestrator` | skill | Reads state, routes to intake/revise, plans agent execution graph, runs impact analysis on revisions |
| `web-builder-intake` | skill | Initial Q&A (free-form intro → scope → name → content source → style → adaptive extras), writes `brief.md` |
| `web-builder-revise` | skill | Revision mini Q&A; normalizes user intent to a structured change record |
| `web-builder-deliver` | skill | Plain-language explanation of preview / git / deploy options; invokes `deployer` agent based on user choice |
| `ui-ux-designer` | agent | brief.md → `style-guide.md` (palette, typography, spacing, layout grid, vibe notes) |
| `content-writer` | agent | brief.md + (optional) user-supplied content → `content.md` (per-page text, headings) |
| `seo-expert` | agent | brief.md + content.md → `seo.md` (titles, descriptions, og policy, sitemap, robots) |
| `frontend-expert` | agent | brief + style-guide + content + seo → frontend source files |
| `backend-engineer` | agent | brief → API routes, DB schema, auth (only if scope = full app) |
| `accessibility-reviewer` | agent | Reviews generated code; applies fixes in place; writes `a11y-report.md` |
| `deployer` | agent | Per user choice: git init+push, or Cloudflare Pages / Vercel / Netlify deploy |

### 5.3 Orchestrator Logic

```
1. On invocation, read state.json from cwd:
   - Missing → call intake skill
   - Present → ask "continue or new?" → route to revise or new intake

2. Once brief.md is ready (or updated), build agent execution graph:
   - ui-ux-designer (always)
   - content-writer + seo-expert (parallel, after designer)
   - frontend-expert (after the above)
   - backend-engineer (only if scope = full app; parallel with frontend)
   - accessibility-reviewer (after code is written)

3. After all agents complete, hand off to deliver skill.

4. On revision, run impact analysis: identify which artifacts the change
   affects, then run only the agents that own those artifacts (plus
   downstream dependents).
```

### 5.4 Inter-Agent Communication

Agents communicate **only through files** (`brief.md`, `style-guide.md`, `content.md`, `seo.md`, `a11y-report.md`). They do not pass messages directly. This keeps:

- Each agent's input/output auditable
- The user able to inspect or edit any artifact between runs
- Re-execution deterministic given the same artifact state

Each agent is spawned via Claude Code's `Agent` tool, runs in its own context, reads only the files it needs, writes only the file(s) it owns, and returns a short summary to the orchestrator.

## 6. File Layout & State Model

### 6.1 Generated Project Folder

```
kadikoy-kahve/                          # user-chosen project name
├── .web-builder/                       # plugin's own state (hidden)
│   ├── state.json                      # machine-readable
│   ├── history/                        # snapshots per revision (state + brief diff)
│   └── locks/                          # concurrent invocation guard
├── brief.md                            # ⭐ intake decisions (human-editable)
├── style-guide.md                      # ⭐ ui-ux-designer output
├── content.md                          # ⭐ content-writer output
├── seo.md                              # ⭐ seo-expert output
├── a11y-report.md                      # accessibility-reviewer output (if any)
├── README.md                           # auto-generated user-facing readme
└── src/  (or root)                     # actual site code — varies by stack
```

### 6.2 `state.json` Schema

```json
{
  "version": "1",
  "mode": "simple",
  "language": "tr",
  "scope": "multi-page-static",
  "stack": "astro+tailwind",
  "siteName": "kadikoy-kahve",
  "siteLanguage": "tr",
  "createdAt": "2026-04-26T10:00:00Z",
  "lastModified": "2026-04-26T11:30:00Z",
  "briefHash": "sha256:...",
  "agentRuns": [
    {"agent": "ui-ux-designer", "at": "...", "wrote": ["style-guide.md"], "status": "success"}
  ],
  "deployment": {
    "type": "cloudflare-pages",
    "url": "kadikoy-kahve.pages.dev",
    "lastDeployAt": "..."
  }
}
```

Field meanings:

- `mode` — `simple` or `dev`; controls verbosity, stack-choice exposure, agent output detail.
- `language` — plugin's conversation language, auto-detected on first interaction.
- `scope` — one of `single-page`, `multi-page-static`, `interactive-static`, `full-app`.
- `stack` — stack identifier; in sade mode auto-derived from scope, in dev mode user-chosen.
- `siteLanguage` — language of the generated site (asked separately during intake).
- `briefHash` — hash of `brief.md` after the last successful agent run; used to detect manual edits.
- `agentRuns` — append-only audit log of every agent invocation.

### 6.3 `brief.md` Template

Every `brief.md` follows the same section order so agents can parse predictably:

```markdown
# Site Briefi: kadikoy-kahve

## Amaç
[one-paragraph user goal]

## Hedef Kitle
[target audience]

## Sayfa Listesi
- [page]
- [page]

## İçerik Kaynağı
[user-provided | plugin-generated placeholders]

## Stil Tercihi
[preset name | freeform description | reference URL]

## Davranış / Etkileşim
- [forms, animations, interactivity choices]

## Teknik (only filled in dev mode)
- Stack: [...]
- Deploy hedefi: [...]
```

### 6.4 Multi-Project Handling

Each project lives in its own subdirectory under whatever folder the user invoked the plugin from. The plugin looks for `.web-builder/` in the cwd — it does not walk up. Invocation in a parent folder always means "new project; ask for a subdirectory name."

### 6.5 Git Behavior

- **Sade mode:** plugin runs `git init` silently on first generation, makes an initial commit once the site is generated, and auto-commits before every revision. The "undo" feature uses these commits. The user does not need to know `git` exists.
- **Dev mode:** plugin asks before `git init` and before each auto-commit. User can opt out.

## 7. Tech Stack Policy

### 7.1 Default Stack Mapping (sade mode)

| Scope | Default Stack | Rationale |
|---|---|---|
| Single page | Vanilla HTML + CSS + minimal JS | No build step; runs anywhere; simplest |
| Multi-page static | **Astro** + Tailwind | Fast, modern, content-oriented, simple build, cheap hosting |
| Interactive static | Astro + Tailwind + island components (as needed) | Static with selective JS islands fits Astro naturally |
| Full app | **Next.js** (App Router) + Tailwind + Prisma + SQLite | Single package for FE+BE; widespread; deploy-friendly |

### 7.2 Dev Mode Overrides

`/web-builder-dev` shows the same defaults but lets the user pick:

- Frontend: Astro / Next.js / SvelteKit / Remix / vanilla
- Backend (full app only): Next.js API routes / Node+Express / Go / Java/Spring / Python/FastAPI
- Styling: Tailwind / CSS modules / vanilla CSS / styled-components
- Database (full app only): SQLite (Prisma) / Postgres / MongoDB / none

### 7.3 Fixed Decisions (both modes)

- **Package manager:** `pnpm`, fall back to `npm` if absent. Not asked.
- **Linter/Formatter:** Off in sade mode (extra noise). Default `eslint + prettier` in dev mode; can be disabled.
- **Test framework:** Never auto-installed. The user adds later if wanted.
- **TypeScript:** Default on for Astro/Next.js. Default off for vanilla.
- **CSS framework:** Tailwind always in sade mode; overridable in dev mode.

## 8. Image Policy

- No AI image generation in v1 (Claude lacks image gen; no external service binding).
- Default: contextual Unsplash URLs, marked as placeholder in `content.md`.
- If the user said they will provide content, plugin asks for images explicitly; falls back to Unsplash placeholders if not supplied.
- All images listed in `content.md` so the user can swap them later by editing the file.

## 9. Deployment Policy

| Scope | Default Target | Rationale |
|---|---|---|
| Static (single / multi / interactive) | **Cloudflare Pages** | Most generous free tier; easy custom domain |
| Full app | **Vercel** | Native Next.js deployment story |

Alternatives offered: Netlify, GitHub Pages, "files only — I'll upload myself."

Before deploying, plugin checks the relevant CLI auth status. If missing, it explains in plain language which command the user should run (interactive login is not the plugin's job).

## 10. Error Handling

Agents can fail (rate limits, model error, malformed output, missing inputs). Policy:

- Orchestrator **automatically retries once** on agent failure (including in sade mode).
- Regardless of mode, the orchestrator **always reports the failure to the user** — what failed, what was attempted, and what the retry result was.
- After two consecutive failures, the orchestrator pauses and surfaces clear options: retry manually, skip this agent (only allowed for non-blocking agents — `accessibility-reviewer`, `seo-expert`, and `content-writer` when the user supplied their own content; never allowed for `ui-ux-designer` or `frontend-expert`), or abort.
- All failures and retries are appended to `agentRuns` in `state.json`.

This is identical in sade and dev modes — the user is never silently left with a partially generated site.

## 11. Versioning & Distribution

- **Versioning:** semantic versioning. `v0.x` for early/breaking iteration. `v1.0` is cut when the v1 goals above are all met and the plugin has been used end-to-end on at least 2 distinct project types.
- **Distribution:** plugin lives in its own GitHub repository. Released as a public Claude Code plugin from v1.0 onward (pre-v1 may be local-only or a private install for testing).
- **Repository structure** mirrors the layout in §5.1.

## 12. Open Decisions

- **Pre-v1 distribution method** — local install only, or also a private GitHub-based install for early testers? (Decide before first end-to-end test.)
- **README content for generated projects** — minimal (just project name + how to run) vs. rich (decisions made, agents that ran, where to edit content). Recommend rich — it doubles as documentation of the plugin's value.
- **`.web-builder/history/` retention** — unbounded vs. last-N. Unbounded is simpler and disk cost is trivial for markdown; recommend unbounded for v1.
