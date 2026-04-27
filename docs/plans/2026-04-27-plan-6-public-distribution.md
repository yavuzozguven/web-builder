# web-builder Plan 6: Public Distribution (v1.0.0)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut v1.0.0 — the first stable, publicly installable release of `web-builder`. Polish documentation for public consumption (LICENSE file, CHANGELOG, expanded README, optional CONTRIBUTING), expand `plugin.json` metadata with the fields a public Claude Code plugin registry expects, flip the GitHub repository from private to public, tag v1.0.0, and create a GitHub release with curated notes. No code/agent changes — Plans 1–5 already shipped the v1.0 functional surface; Plan 6 is the distribution layer.

**Architecture:** No architecture changes. The plugin's structure (commands/, skills/, agents/) and behavior remain identical to v0.5.0. Plan 6 only touches metadata, docs, and the repo's visibility setting.

**Tech Stack:** Markdown (LICENSE, CHANGELOG, CONTRIBUTING, README polish), JSON (plugin.json metadata expansion), `gh` CLI (repo visibility flip + release creation).

**v1.0.0 scope:**
- Add a real LICENSE file (MIT text)
- Add CHANGELOG.md covering v0.1.0 through v1.0.0
- Expand plugin.json metadata (`homepage`, `repository`, `keywords`)
- Expand README for public consumption (hero/intro, quick-start, install command, examples reference, contributing, license)
- Add CONTRIBUTING.md (issue + PR guidelines, dev setup, code style — concise)
- Verify the plugin can actually be installed via Claude Code's plugin mechanism (manual step — gates the v1.0 tag)
- Flip the GitHub repository from private to public (one-way action — gated behind user confirmation in implementation)
- Bump plugin.json version to 1.0.0
- Tag v1.0.0 + create GitHub release with curated notes

**Definition of done:**
- `LICENSE` file exists at repo root with MIT text
- `CHANGELOG.md` exists with chronological entries for each tag from v0.1.0 to v1.0.0
- `plugin.json` has `homepage`, `repository.type`, `repository.url`, `keywords`
- `README.md` opens with a 2-3 sentence pitch + a single-block install/use example
- Repo is **public** on GitHub
- `git tag --list` includes `v1.0.0`
- `gh release view v1.0.0` returns a release with curated notes
- Manual install verification: a fresh terminal can run the documented install command and `/web-builder` appears as a slash command in Claude Code

**Out of scope (deferred to v1.x):**
- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup
- AI-generated images
- Template marketplace
- Logo / brand assets / website
- Asciicast / video demo (could be a v1.1 README addition; not blocking v1.0)
- Plugin-registry submission beyond GitHub-based install (depends on Claude Code's roadmap; out of scope until that mechanism exists)

---

## File Structure

```
web-builder/
├── plugin.json                                  # MODIFY: bump to 1.0.0; add homepage, repository, keywords
├── README.md                                    # MAJOR MODIFY: public-friendly hero + quick start
├── LICENSE                                      # CREATE (MIT text)
├── CHANGELOG.md                                 # CREATE (v0.1 → v1.0)
├── CONTRIBUTING.md                              # CREATE (concise — issues, PRs, code style)
├── commands/                                    # unchanged
├── skills/                                      # unchanged
├── agents/                                      # unchanged
├── tests/                                       # unchanged
└── docs/
    ├── specs/                                   # unchanged
    └── plans/
        ├── ... (Plans 1-5)                      # unchanged
        └── 2026-04-27-plan-6-public-distribution.md  # this file
```

---

## Task 1: Add `LICENSE` File

**Files:**
- Create: `LICENSE`

The MIT license is already declared in `plugin.json`, but no LICENSE file exists at repo root. Public repos need one for users to know the license terms without parsing the manifest.

- [ ] **Step 1: Write the LICENSE file**

Create `LICENSE` with the standard MIT text:

```
MIT License

Copyright (c) 2026 Yavuz Özgüven

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Verify**

Run: `head -3 LICENSE` — first line should be `MIT License`.
Run: `wc -l LICENSE` — expect 21 lines (standard MIT length).

- [ ] **Step 3: Commit**

```bash
git add LICENSE
git commit -m "docs: add MIT LICENSE file"
```

---

## Task 2: Add `CHANGELOG.md`

**Files:**
- Create: `CHANGELOG.md`

Chronological release notes. Helps users understand what each version brought.

- [ ] **Step 1: Write CHANGELOG.md**

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-27

First stable release. The plugin's functional surface defined in the v1 design spec is complete and publicly installable.

Highlights of the journey from v0.1.0:

- All 4 site scopes (single page, multi-page static, interactive static, full app)
- Sade mode (`/web-builder`) and dev mode (`/web-builder-dev`)
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
- `/web-builder-dev` slash command (dev mode entry)
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
```

- [ ] **Step 2: Verify**

Run: `grep -c "^## \[" CHANGELOG.md` — expect 6 (one per version v0.1.0 → v1.0.0).
Run: `grep -c "^\[" CHANGELOG.md` — expect 6 (link references at the bottom).

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG.md (v0.1.0 → v1.0.0)"
```

---

## Task 3: Expand `plugin.json` Metadata

**Files:**
- Modify: `plugin.json`

Add the metadata fields a public Claude Code plugin registry expects: `homepage`, `repository`, `keywords`. Don't bump the version yet — that happens in Task 8 after public-flip is verified.

- [ ] **Step 1: Read current plugin.json**

Run: `cat plugin.json`. Current fields: `name`, `version`, `description`, `author`, `license`.

- [ ] **Step 2: Update plugin.json**

Use Edit (or Write to fully rewrite) to set the manifest to:

```json
{
  "name": "web-builder",
  "version": "0.5.0",
  "description": "Build a website end-to-end through guided Q&A. Asks what you want, picks the stack, generates the code.",
  "author": "Yavuz Ozguven <yavuz.ozguven@useinsider.com>",
  "license": "MIT",
  "homepage": "https://github.com/yavuzozguven/web-builder",
  "repository": {
    "type": "git",
    "url": "https://github.com/yavuzozguven/web-builder.git"
  },
  "keywords": [
    "claude-code",
    "claude-code-plugin",
    "website-generator",
    "site-builder",
    "static-site-generator",
    "web-development",
    "agent",
    "ai-tools"
  ]
}
```

(Note: version stays at `0.5.0` for this task. The bump to `1.0.0` happens in Task 8.)

- [ ] **Step 3: Verify**

Run: `python3 -c "import json; d=json.load(open('plugin.json')); print(d['homepage'], d['repository']['url'], len(d['keywords']))"`
Expected output: `https://github.com/yavuzozguven/web-builder https://github.com/yavuzozguven/web-builder.git 8`.

Run: `tests/lint.sh` — `14 passed, 0 failed`.

- [ ] **Step 4: Commit**

```bash
git add plugin.json
git commit -m "docs: expand plugin.json metadata for public distribution (homepage, repository, keywords)"
```

---

## Task 4: Polish README for Public Consumption

**Files:**
- Modify: `README.md`

The current README is OK for a private repo but misses several elements public users expect: a strong hero/intro, install command, a tiny worked example, contribution pointer, badges-or-status, license link.

- [ ] **Step 1: Read current README**

Run: `cat README.md`. Note the current sections: Status, Install, Use, What the plugin generates, View your site, Architecture, License.

- [ ] **Step 2: Replace README with the public-ready version**

Use Write to fully replace `README.md` with:

````markdown
# web-builder

A Claude Code plugin that builds you a complete website end-to-end through guided Q&A.

You describe what you want — a one-pager for your CV, a multi-page tanıtım site for your café, a full-app for your team's tools — the plugin asks a few short questions, picks the most appropriate framework/language for the job, generates the code, and (optionally) deploys it.

The plugin is **stack-agnostic**: it doesn't ship with a hardcoded list of frameworks. The agents pick from the current ecosystem at runtime — so the choice tracks what's actually best today, not what was best when the plugin was authored.

## Install

```bash
claude code plugin install yavuzozguven/web-builder
```

(Or, if you've cloned the repo locally:)

```bash
cd path/to/web-builder
claude code plugin install .
```

## Use

In any directory:

```
claude
```

then in the Claude prompt:

```
/web-builder
```

The plugin asks 5-10 questions in plain language, picks an appropriate framework, and generates a working project in a subfolder. Then it offers to preview the site locally and (if you want) deploy it to a free host.

For technical users who want to express preferences (e.g., "I prefer Python on the backend", "I want it as simple as possible", "I prioritize performance"):

```
/web-builder-dev
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

The `*.md` files are human-readable — you can edit them by hand, then re-run `/web-builder` from inside the project folder; the plugin detects your edits (briefHash diff) and offers to regenerate the affected parts.

## Revise an existing project

From inside a project folder:

```
/web-builder
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
````

- [ ] **Step 3: Verify**

Run: `head -1 README.md` → `# web-builder`.
Run: `grep -c "claude code plugin install" README.md` — at least 2 (the install command appears twice: GitHub-based + local).
Run: `grep -c "stack-agnostic" README.md` — at least 1.
Run: `grep -c "/web-builder-dev" README.md` — at least 1.
Run: `grep -c "CHANGELOG" README.md` — at least 1.
Run: `grep -c "CONTRIBUTING" README.md` — at least 1.
Run: `grep -c "LICENSE" README.md` — at least 1.
Run: `grep -cE "Astro|Next\.js|SvelteKit|Vue|React" README.md` — must be 0 (README must stay stack-agnostic).

Run: `tests/lint.sh` — `14 passed, 0 failed`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for public consumption (hero, install, examples, contributing)"
```

---

## Task 5: Add `CONTRIBUTING.md`

**Files:**
- Create: `CONTRIBUTING.md`

Concise: issues, PRs, dev setup, code style. Don't over-engineer for a small plugin project.

- [ ] **Step 1: Write CONTRIBUTING.md**

```markdown
# Contributing to web-builder

Thanks for your interest in contributing! This document covers the basics.

## Reporting issues

Open a GitHub issue with:
- What you tried (the slash command + your answers, in summary)
- What you expected to happen
- What actually happened (include any error message)
- Your platform (macOS / Linux / Windows + Claude Code version)

## Pull requests

1. Fork the repo, create a feature branch.
2. Run `tests/lint.sh` from the repo root — must pass (`14 passed, 0 failed`).
3. If you add a new agent or skill, add a corresponding entry to `tests/lint.sh`'s expected count and ensure frontmatter is well-formed.
4. Critical guardrail: no specific framework names (Astro, Next.js, SvelteKit, etc.) in `agents/`, `skills/`, or `commands/` files. The plugin is stack-agnostic — agents decide at runtime.
5. Keep the user-facing dialog in plain language; technical jargon goes in dev mode (`/web-builder-dev`) only.
6. Open the PR with a clear summary of what changed and why.

## Local development

```bash
git clone https://github.com/yavuzozguven/web-builder.git
cd web-builder
tests/lint.sh
```

To install the plugin from your local clone (for testing changes):

```bash
claude code plugin install .
```

Re-install after each change.

## Project structure

```
web-builder/
├── plugin.json        # plugin manifest
├── commands/          # slash commands (/web-builder, /web-builder-dev)
├── skills/            # user-facing dialog flows (orchestrator, intake, revise, deliver)
├── agents/            # worker agents (designer, content, seo, frontend, backend, a11y, deployer)
├── tests/
│   ├── lint.sh        # validates plugin.json + frontmatter for every md file
│   ├── fixtures/      # sample inputs for smoke tests
│   └── smoke-test.md  # manual smoke test procedures
└── docs/
    ├── specs/         # design spec
    └── plans/         # implementation plans (one per version bump)
```

## Code style

- Markdown frontmatter must include `name:` (skills/agents) and `description:` (everything).
- Plain-language tone in user-facing dialog; preserve Turkish + English support where present.
- Each agent has a single, well-bounded responsibility. If you find an agent doing two things, split it.
- Stack-agnostic principle: agents decide their concrete stack at runtime; the plugin code never enumerates frameworks.

## Reporting security issues

Please email `yavuz.ozguven@useinsider.com` rather than opening a public issue.
```

- [ ] **Step 2: Verify**

Run: `grep -c "stack-agnostic" CONTRIBUTING.md` — at least 1.
Run: `grep -c "lint.sh" CONTRIBUTING.md` — at least 1.

Run: `grep -cE "Astro|Next\.js|SvelteKit|Vue|React" CONTRIBUTING.md` — count is non-zero only because it lists framework names in the guardrail rule explicitly. That's expected — it's a meta-comment, not enumeration to users. Acceptable.

- [ ] **Step 3: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING.md (issues, PRs, dev setup, code style)"
```

---

## Task 6: Manual Install Verification (Gate Before Public Flip)

**This is a manual step — the implementing subagent cannot run interactive Claude Code.** The instructions are provided so the user can perform this gate before continuing to Task 7 (which flips the repo to public — a one-way action).

- [ ] **Step 1: Test local install**

In a terminal:

```bash
cd /Users/yavuz.ozguven/Desktop/web-builder
# (use whatever the current Claude Code version's command is)
claude code plugin install .
```

- [ ] **Step 2: Verify the plugin loads**

Open a fresh `claude` session in some other directory:

```bash
mkdir -p /tmp/web-builder-install-test
cd /tmp/web-builder-install-test
claude
```

Type `/web-builder` and verify the plugin's intake skill triggers (asking the first question — "Bu site ne için, kim için olacak?" or English equivalent). You don't have to complete the flow — just verify the slash command is recognized and the orchestrator routes correctly.

- [ ] **Step 3: Verify `/web-builder-dev` also works**

In the same `claude` session, type `/web-builder-dev` and verify the dev-mode entry triggers. You should see the same first question (since both modes share intake skill).

- [ ] **Step 4: Decision gate**

If both `/web-builder` and `/web-builder-dev` triggered correctly, proceed to Task 7.

If something is broken (slash command not recognized, orchestrator not loading, etc.), open an issue, fix it, re-run lint, then retry from Step 1. **Do not** proceed to Task 7 (public flip) until install verification passes.

---

## Task 7: Flip GitHub Repo to Public

**Files:** none modified — this is a `gh` CLI action.

**Important:** flipping a repo from private to public is one-way for practical purposes. Anyone who clones the repo while it's public has a copy. Before running this command, confirm:

- Task 6 install verification passed
- No secrets, credentials, or personal information in the repo's git history (run a quick scan: `git log --all --pretty=format:"%H %s" | head -50` and skim — verify no commits like "fix: remove leaked API key" recently)
- The user is OK with the repo being permanently public

- [ ] **Step 1: Final repo content scan**

Run: `git log --all --pretty=format:"%s" | grep -iE "secret|password|token|api[-_]?key|credential" || echo "no secret-related commits found"`

If anything matches, stop and review.

Run: `find . -type f \( -name "*.env*" -o -name "*.key" -o -name "*credentials*" \) | grep -v node_modules | head -20 || echo "no credential files"`

If anything matches, stop and review (likely add to .gitignore + never-commit, or remove from history).

- [ ] **Step 2: Confirm with user before flip**

Before running the flip command, the implementing subagent **MUST stop and ask the user for explicit confirmation**: "Plan 6 Task 7 flips the GitHub repo from private to public. This is a one-way action. Confirm to proceed?"

If user declines, exit cleanly and continue to Task 8 (which the user can run with the repo still private — Task 7 can be deferred indefinitely).

- [ ] **Step 3: Flip the repo**

```bash
gh repo edit yavuzozguven/web-builder \
  --visibility public \
  --accept-visibility-change-consequences
```

- [ ] **Step 4: Verify**

Run: `gh repo view yavuzozguven/web-builder --json visibility`
Expected: `{"visibility":"PUBLIC"}`.

- [ ] **Step 5: No commit needed (this is a GitHub setting change, not a file change).**

---

## Task 8: Bump Version to 1.0.0 + Update README Status

**Files:**
- Modify: `plugin.json`
- Modify: `README.md`

Now that the repo is public-ready (or already public), bump to 1.0.0. The README's Status section was already written with v1.0.0 in Task 4, so just update plugin.json.

- [ ] **Step 1: Bump plugin.json**

Use Edit to change `"version": "0.5.0"` to `"version": "1.0.0"` in `plugin.json`.

- [ ] **Step 2: Verify**

Run: `python3 -c "import json; print(json.load(open('plugin.json'))['version'])"` → `1.0.0`.

Run: `tests/lint.sh` → `14 passed, 0 failed`.

- [ ] **Step 3: Commit**

```bash
git add plugin.json
git commit -m "release: v1.0.0"
```

---

## Task 9: Tag v1.0.0 + Create GitHub Release

**Files:** none modified — `git tag` and `gh release create` actions.

- [ ] **Step 1: Tag v1.0.0**

```bash
git tag -a v1.0.0 -m "v1.0.0 — first stable release

The plugin's v1 functional surface (per design spec) is complete. Public install via Claude Code plugin mechanism.

Highlights:
- All 4 site scopes (single-page, multi-page-static, interactive-static, full-app)
- Sade + dev mode (/web-builder, /web-builder-dev)
- Stack-agnostic: agents pick framework/language at runtime — future-proof against framework churn
- Preview + deploy (Cloudflare Pages / Vercel / Netlify / GitHub Pages / local)
- Revision flow with impact analysis, undo, manual brief edit detection
- Per-page SEO + accessibility review baked into pipeline

See CHANGELOG.md for full release history.
"
```

- [ ] **Step 2: Push to GitHub**

```bash
git push origin main
git push --tags
```

- [ ] **Step 3: Create GitHub release**

```bash
gh release create v1.0.0 \
  --title "v1.0.0 — first stable release" \
  --notes "$(cat <<'EOF'
First stable, publicly installable release of `web-builder`.

## Install

```bash
claude code plugin install yavuzozguven/web-builder
```

## What's in v1.0.0

The full v1 functional surface from the design spec:

- **All 4 site scopes** — single page, multi-page static, interactive static, full app
- **Sade and dev modes** — `/web-builder` for plain-language Q&A; `/web-builder-dev` for preference-driven Q&A
- **Stack-agnostic** — `frontend-expert` and `backend-engineer` pick framework/language at runtime, not from a hardcoded list. Future-proof.
- **Preview and deploy** — `npm run dev` preview + Cloudflare Pages / Vercel / Netlify / GitHub Pages / local-only deployment
- **Revision flow** — structured Q&A for editing existing projects, impact-aware re-runs, automatic undo via `git revert`, manual `brief.md` edit detection
- **Per-page SEO** — `seo.md` with titles, descriptions, og policy, sitemap, robots
- **Accessibility review** — inline fixes + `a11y-report.md`

## Versioning

This is the first stable release. Subsequent v1.x versions add features without breaking the existing surface. v2.0 (if/when it happens) may break compatibility — there's no plan for one yet.

## Out of scope (planned for v1.x)

- Custom domain automation
- Multi-language site output (hreflang)
- Test framework setup
- AI-generated images
- Template marketplace

## Architecture

See README.md for the agent pipeline. The full design spec is at `docs/specs/2026-04-26-web-builder-plugin-design.md`.

## License

MIT.
EOF
)"
```

- [ ] **Step 4: Verify the release exists**

Run: `gh release view v1.0.0 --json url,tagName,name`
Expected output includes `tagName: v1.0.0` and a release URL.

---

## Task 10: Final Lint, Critical Guardrail, Done Verification

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `14 passed, 0 failed.` (1 plugin.json + 2 commands + 4 skills + 7 agents).

- [ ] **Step 2: Critical guardrail — framework names in plugin code**

Run:

```bash
grep -rE "Astro|Next\.js|SvelteKit|Vue|React|Solid|Qwik|Express|FastAPI|Django|Spring|Fastify|Hono" agents/ skills/ commands/ 2>&1
```

Expected: 0 matches in `agents/`, `skills/`, `commands/`.

(The CONTRIBUTING.md may legitimately mention framework names in its rule about NOT enumerating them — that's outside the plugin code globs, allowed.)

- [ ] **Step 3: Verify done criteria**

Manual checklist:
- [ ] `LICENSE` exists at repo root
- [ ] `CHANGELOG.md` exists with entries for v0.1.0 → v1.0.0
- [ ] `CONTRIBUTING.md` exists
- [ ] `plugin.json` has `homepage`, `repository`, `keywords`, `version: "1.0.0"`
- [ ] `README.md` opens with the public-facing pitch + install command
- [ ] Repo is public on GitHub (`gh repo view --json visibility` returns `PUBLIC`) — assuming Task 7 was completed
- [ ] `git tag --list` includes `v1.0.0`
- [ ] `gh release view v1.0.0` returns the release with curated notes
- [ ] `tests/lint.sh` reports `14 passed, 0 failed`
- [ ] Critical guardrail: no framework name references in `agents/`, `skills/`, `commands/`

---

## Done criteria for this plan

- [ ] All 10 tasks complete (Task 7 may be deferred if user holds off on public flip; rest still independently completable).
- [ ] `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md` all exist at repo root.
- [ ] `plugin.json` v1.0.0 with expanded metadata.
- [ ] `README.md` is public-ready (hero + install + use + revise + deploy + architecture + contributing + license).
- [ ] `git tag --list` shows `v1.0.0`.
- [ ] `gh release view v1.0.0` exists.
- [ ] `tests/lint.sh` passes.
- [ ] Critical guardrail clean.

## Out of scope for this plan (deferred to v1.x)

- Custom domain automation (v1.1)
- Multi-language site output (v1.1)
- Test framework setup
- AI-generated images
- Template marketplace
- Logo / brand assets / dedicated website
- Asciicast / video demo
- Plugin-registry submission beyond GitHub-based install (depends on Claude Code's roadmap)

## Risks and edge cases

- **Public flip is one-way (practically):** Task 7 is gated behind explicit user confirmation. If the user wants to keep the repo private and just tag v1.0.0 internally, that's fine — Tasks 8-9 work either way; the repo can be flipped later. Don't run Task 7 without explicit consent.
- **Install command may differ across Claude Code versions:** the documented `claude code plugin install <path|owner/repo>` is the most common form, but Claude Code may evolve the CLI. The README install snippet is a sensible default; users on different versions may need to consult their own docs.
- **plugin.json metadata fields:** the fields added (`homepage`, `repository`, `keywords`) are conventions from package managers (npm-style); Claude Code's plugin loader may ignore extras silently. Adding them is harmless and helps future tooling (search, discovery).
- **CHANGELOG link references at the bottom point at GitHub release URLs** — these only resolve once the corresponding tags are pushed and (for v1.0.0) the release is created. Acceptable; the references work as soon as Task 9 completes.
- **Smoke tests don't change in v1.0.0:** the plugin's behavior is identical to v0.5.0; we're only updating distribution metadata. No new tests needed in this plan.
- **No regressions expected:** Plan 6 is metadata + docs only; lint coverage stays at 14 files.
