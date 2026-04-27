# web-builder

A Claude Code plugin that builds you a complete website end-to-end through guided Q&A.

You describe what you want — a one-pager for your CV, a multi-page tanıtım site for your café, a full-app for your team's tools — the plugin asks a few short questions, picks the most appropriate framework/language for the job, generates the code, and (optionally) deploys it.

The plugin is **stack-agnostic**: it doesn't ship with a hardcoded list of frameworks. The agents pick from the current ecosystem at runtime — so the choice tracks what's actually best today, not what was best when the plugin was authored.

## Install

The plugin is distributed as a single-plugin Claude Code marketplace. Add the marketplace and install in two steps (run inside a `claude` session):

```
/plugin marketplace add github:yavuzozguven/web-builder
/plugin install web-builder@web-builder
```

(The `@web-builder` after the plugin name is the marketplace name. They happen to match because this repo is its own single-plugin marketplace.)

Verify it loaded:

```
/plugin
```

You should see `web-builder` listed and the slash commands `/web-builder:start` and `/web-builder:dev` available.

### Local development install (clone + try it)

If you've cloned the repo locally and want to test changes without going through the marketplace:

```bash
cd path/to/web-builder
claude --plugin-dir .
```

This loads the plugin directly into the current `claude` session. Re-run after each change.

## Use

In any directory:

```
claude
```

then in the Claude prompt:

```
/web-builder:start
```

The plugin asks 5-10 questions in plain language, picks an appropriate framework, and generates a working project in a subfolder. Then it offers to preview the site locally and (if you want) deploy it to a free host.

For technical users who want to express preferences (e.g., "I prefer Python on the backend", "I want it as simple as possible", "I prioritize performance"):

```
/web-builder:dev
```

Same flow with extra preference questions. The plugin still picks the framework — but informed by your preferences.

## What you end up with

Each generated project lives in its own subfolder:

```
{project-name}/
├── brief.md              # what you told the plugin you wanted
├── style-guide.md        # color palette, fonts, layout decisions
├── content.md            # page-by-page text and images
├── seo.md                # per-page titles, descriptions, og policy, sitemap, robots
├── a11y-report.md        # accessibility review results (inline fixes + report)
├── .web-builder/
│   └── state.json        # plugin's own state (preferences + chosenStack)
└── (frontend project files — vary by stack the agent picked)
```

The `*.md` files are human-readable — you can edit them by hand, then re-run `/web-builder:start` from inside the project folder; the plugin detects your edits (briefHash diff) and offers to regenerate the affected parts.

## Revise an existing project

From inside a project folder:

```
/web-builder:start
```

The plugin asks "Devam et (revize) / Yeni site / İptal et". Pick "Devam et" and you get a structured Q&A:

- **Stil** (renkler, font, layout)
- **İçerik** (metinler, kontak)
- **Yapı** (yeni sayfa, sayfa silme)
- **Davranış** (form, animasyon)
- **Teknik** (deploy, SEO meta, tercih değişikliği, scope, a11y recheck)
- **Serbest yazım** (her şey)
- **Son değişikliği geri al** (`git revert`)

Each revision auto-commits before/after, so undo is always available.

## Deploy

After generation (or on revision), the plugin asks where to publish:

- **Cloudflare Pages** — free, custom domain easy
- **Vercel** — best for full-app
- **Netlify** — classic alternative
- **GitHub Pages** — your own repo + GitHub Actions
- **Local-only** — get the files, host yourself

The plugin checks CLI auth (`wrangler login`, `vercel login`, etc.); if you're not logged in, it tells you the exact command to run.

## Architecture

Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle dialog. Worker agents (`ui-ux-designer`, `content-writer`, `seo-expert`, `frontend-expert`, `backend-engineer`, `accessibility-reviewer`, `deployer`) write the actual files in their own context. The pipeline runs:

```
designer → [content-writer + seo-expert parallel] → [frontend-expert + backend-engineer parallel for full-app] → accessibility-reviewer (final pass)
```

`frontend-expert` and `backend-engineer` are stack-agnostic — they pick the framework/language at runtime based on your preferences and current ecosystem knowledge, then record the choice in `state.json.chosenStack`.

See `docs/specs/2026-04-26-web-builder-plugin-design.md` for the full design.

## Status

**v1.0.0** — first stable release. Functional surface complete; intended for public install.

See [CHANGELOG.md](CHANGELOG.md) for release history.

Not yet supported (planned for v1.x): custom domain automation, multi-language site output (hreflang), test framework setup, AI-generated images, template marketplace.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines.

## License

MIT — see [LICENSE](LICENSE).
