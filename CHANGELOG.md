# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-28

First stable release. The plugin's functional surface defined in the v1 design spec is complete and publicly installable.

Highlights of the journey from v0.1.0:

- All 4 site scopes (single page, multi-page static, interactive static, full app)
- Sade mode (`/web-builder:start`) and dev mode (`/web-builder:dev`)
- Stack-agnostic worker agents (frontend-expert and backend-engineer pick framework/language at runtime)
- Preview + deploy to Cloudflare Pages, Vercel, Netlify, GitHub Pages, or local
- Revision flow with impact analysis, undo, and manual-brief-edit detection
- Per-page SEO (titles, descriptions, og policy, sitemap, robots)
- Accessibility review (inline fixes + a11y-report.md)

This is the first version intended for public install via the Claude Code plugin mechanism. See README.md for installation and usage.

## [0.5.0] - 2026-04-27

### Added
- `seo-expert` agent (per-page titles, descriptions, og policy, sitemap, robots)
- `accessibility-reviewer` agent (inline a11y fixes + `a11y-report.md`)
- Orchestrator graph: 4 phases (designer → [content + seo parallel] → [frontend + backend parallel] → a11y final)
- Revise option G (a11y recheck — re-runs only a11y agent)
- Deliver skill surfaces a11y-report.md (sade summary, dev verbose)

### Changed
- `frontend-expert` reads seo.md and injects meta tags
- `backend-engineer` (full-app) reads seo.md and generates sitemap + robots

## [0.4.0] - 2026-04-27

### Added
- `/web-builder:dev` slash command (dev mode entry)
- All 4 site scopes (single page, multi-page static, interactive static, full app)
- `backend-engineer` agent (stack-agnostic, full-app only)
- Stack-agnostic worker agents (frontend-expert + backend-engineer pick at runtime)
- `state.json.preferences` (user input) + `state.json.chosenStack` (agent decision)
- Revise: "Tercihlerimi değiştir" + "Scope değiştir" options

### Changed
- Intake skill asks scope (sade) + preferences (dev) — never specific framework names
- Brief.md template uses Scope + Preferences sections
- Critical guardrail: 0 framework name references in plugin code (except design-spec docs)

## [0.3.0] - 2026-04-27

### Added
- `web-builder-revise` skill (7-option revision Q&A: style/content/structure/behavior/technical/free-form/undo)
- Orchestrator existing-project routing: manual-edit detection (briefHash diff), auto-commit before/after revisions, undo via git revert
- Smoke tests for revision (Tests 7-10)

## [0.2.0] - 2026-04-26

### Added
- `deployer` agent (Cloudflare Pages / Vercel / Netlify / GitHub Pages / local)
- Deliver skill: interactive preview + deploy flows
- Auto git initialization in sade mode
- Smoke tests for preview and local deploy (Tests 3-6)

## [0.1.0] - 2026-04-26

### Added
- Initial MVP release.
- 1 slash command (`/web-builder`)
- 3 skills (orchestrator, intake, deliver)
- 3 agents (ui-ux-designer, content-writer, frontend-expert)
- Multi-page static site generation (hardcoded scope and stack at this point)
- Auto language detection (TR/EN)

[1.0.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v1.0.0
[0.5.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v0.5.0
[0.4.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v0.4.0
[0.3.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v0.3.0
[0.2.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v0.2.0
[0.1.0]: https://github.com/yavuzozguven/web-builder/releases/tag/v0.1.0
