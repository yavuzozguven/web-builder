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
