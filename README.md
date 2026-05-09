# web-builder

> **Describe a website. Get a working, deployable project — without picking a framework, writing boilerplate, or touching a config file.**

A Claude Code plugin that turns a short conversation into a complete, runnable website — frontend, content, SEO, accessibility pass, and one-command deploy.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-orange)](https://claude.com/claude-code)
[![Status](https://img.shields.io/badge/status-v1.0.0-blue)](CHANGELOG.md)

![web-builder demo](docs/demo.gif)

<sub>*Illustrative demo of the `/web-builder:start` flow — actual session timing varies with model latency and project size.*</sub>

---

## 30-second quickstart

```bash
# 1. Install the plugin (inside a `claude` session)
/plugin marketplace add yavuzozguven/web-builder
/plugin install web-builder@web-builder

# 2. From any empty directory:
/web-builder:start
```

Answer 5–10 plain-language questions. The plugin generates the project, runs the build, and offers to preview + deploy.

---

## Why

Most "AI website builders" are locked to one stack (usually whatever was hot when the tool shipped). web-builder is **stack-agnostic by design**: the agents pick the framework, language, and database at runtime based on what the project actually needs and what's best in the current ecosystem.

Ask for a one-page CV → it might pick vanilla HTML/CSS.
Ask for a multi-page promo site → likely a content-focused SSG.
Ask for a full-app with auth and a database → frontend + backend + schema, picked together.

You don't choose the stack. You describe the goal. The plugin justifies its choice in `state.json.chosenStack.rationale`, and you can override via preferences.

## What you get

- **A complete project**, not a starter template — pages, components, real content, SEO metadata, accessibility-clean markup.
- **Human-readable source files** (`brief.md`, `content.md`, `style-guide.md`, `seo.md`) that you can hand-edit and the plugin will pick up on the next run.
- **Auto-commits before and after every revision**, so undo is always one command away.
- **One-command deploy** to Cloudflare Pages, Vercel, Netlify, GitHub Pages, or "just give me the files."

## Example

```
> /web-builder:start

Q1: What kind of site do you want?
> A small promo site for my coffee shop in Brooklyn.
   Coffee + sandwiches, neighborhood vibe.

Q2: Multi-page promo (home + menu + about + contact)?
> Yes.

Q3: Pick a name:
   A) brooklyn-coffee   B) corner-coffee   C) write your own
> A

Q4: Content source?
   A) I'll provide it   B) Generate placeholders
> B

Q5: Visual style?
   A) Minimalist  B) Warm  C) Playful  D) Corporate  E) Dark
> B

[designer → content-writer + seo-expert (parallel) → frontend-expert → a11y review]

✓ Generated: brooklyn-coffee/  (Astro + Tailwind, 4 pages, SEO + sitemap, a11y clean)
  Build succeeded. Want to preview locally? (Y/n)
```

## Two entry points

| Command | Audience | Behavior |
|---|---|---|
| `/web-builder:start` | Anyone | 5–10 plain-language questions, no jargon. |
| `/web-builder:dev` | Devs | Same flow + preference questions (backend language, TS yes/no, priority: simple vs feature-rich, etc.). |

The plugin still picks the stack in both modes — `:dev` just lets you constrain the choice.

## Revise without starting over

Run `/web-builder:start` from inside an existing project and the plugin detects state, then offers structured edits:

- **Style** — colors, fonts, layout
- **Content** — page text, contact info
- **Structure** — add/remove pages
- **Behavior** — forms, animations
- **Technical** — deploy target, SEO meta, scope change, a11y recheck
- **Free-form** — describe anything
- **Undo last change** — `git revert` the most recent revision commit

Each revision auto-commits a before/after pair. You can always go back.

## Deploy

After generation (or on revision), pick a target:

- **Cloudflare Pages** — free, easy custom domains
- **Vercel** — best for full-app workloads
- **Netlify** — classic alternative
- **GitHub Pages** — your own repo + GitHub Actions
- **Local files** — host it yourself

The plugin checks CLI auth (`wrangler login`, `vercel login`, etc.) and if you're not logged in, prints the exact command — never asks for credentials directly.

## What lives in a generated project

```
{project-name}/
├── brief.md              # what you told the plugin you wanted
├── style-guide.md        # palette, typography, layout decisions
├── content.md            # page-by-page text + images
├── seo.md                # titles, descriptions, og policy, sitemap, robots
├── a11y-report.md        # accessibility review results (inline fixes + report)
├── .web-builder/
│   └── state.json        # preferences + chosen stack + agent run log
└── (frontend / backend project files — picked at runtime)
```

The `.md` files are the source of truth. Edit them and re-run `/web-builder:start` — the plugin detects the edits (`briefHash` diff) and regenerates only the affected parts.

## Architecture (one paragraph)

**Skills** (`web-builder-orchestrator`, `-intake`, `-revise`, `-deliver`) drive the dialog. **Worker agents** (`ui-ux-designer`, `content-writer`, `seo-expert`, `frontend-expert`, `backend-engineer`, `accessibility-reviewer`, `deployer`) write files in isolated contexts. Pipeline:

```
designer → [content-writer + seo-expert ‖] → [frontend-expert + backend-engineer ‖ for full-app] → accessibility-reviewer
```

`frontend-expert` and `backend-engineer` carry no hardcoded stack list — they decide at runtime and record the rationale.

Full design: [`docs/specs/2026-04-26-web-builder-plugin-design.md`](docs/specs/2026-04-26-web-builder-plugin-design.md).

## Local development

To hack on the plugin itself:

```bash
git clone https://github.com/yavuzozguven/web-builder.git
cd web-builder
claude --plugin-dir .
```

This loads the plugin from your working copy. Re-run after each edit. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Status & roadmap

**v1.0.0** — first stable release. Functional surface complete; ready for public install.
See [CHANGELOG.md](CHANGELOG.md) for the full release history.

**Planned for v1.x:**
- Custom domain automation
- Multi-language site output (hreflang)
- Test framework setup
- AI-generated images (replacing Unsplash placeholders)
- Template marketplace

## Contributing

Issues and PRs welcome — bug reports, stack additions to the agents' decision space, new revision categories, deploy targets. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — use it, fork it, ship it.

---

If web-builder helped you ship something, a ⭐ on the repo is appreciated — it's the only signal the project gets.
