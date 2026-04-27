# web-builder

A Claude Code plugin that builds you a website end-to-end through guided Q&A. You describe what you want, the plugin asks a few quick questions, and you end up with a working site in a folder.

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

Answer 5 short questions. The plugin creates a subfolder with a working site and tells you how to view it.

For technical users who want to influence the stack pick (preference for Python on backend, "I want it as simple as possible", "I prioritize performance", etc.):

```
/web-builder-dev
```

Same flow but with preference questions added. The plugin still picks the framework — but informed by your preferences.

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

You can edit `brief.md` by hand — re-run `/web-builder` from inside the project folder and the plugin will detect the change (briefHash diff) and ask whether to regenerate the affected parts. `style-guide.md` and `content.md` can also be hand-edited; the next revision through the plugin will honor whatever's there.

## View your site

```bash
cd {project-name}
pnpm dev
# open http://localhost:4321
```

## Architecture (one-liner)

Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle the dialog. Worker agents (`ui-ux-designer`, `content-writer`, `frontend-expert`, `backend-engineer`, `deployer`) write the actual files in their own context. `frontend-expert` and `backend-engineer` are stack-agnostic — they pick the framework/language at runtime based on user preferences and current ecosystem knowledge, then record the choice in `state.json.chosenStack`.

See `docs/specs/2026-04-26-web-builder-plugin-design.md` for the full design.

## License

MIT
