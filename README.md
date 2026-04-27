# web-builder

A Claude Code plugin that builds you a website end-to-end through guided Q&A. You describe what you want, the plugin asks a few quick questions, and you end up with a working site in a folder.

## Status

**v0.5.0.** Full quality pass: per-page SEO and accessibility review run as part of every generation. All 4 site scopes supported, sade and dev modes, stack-agnostic agents.

- ✅ Generate any of 4 scope types from Q&A
- ✅ Sade mode + dev mode (`/web-builder-dev`)
- ✅ Stack-agnostic plugin: agents pick framework/language at runtime
- ✅ Stack pick recorded in `state.json.chosenStack`
- ✅ Preview locally + deploy to Cloudflare Pages / Vercel / Netlify / GitHub Pages
- ✅ Auto git initialization in sade mode
- ✅ Revise existing projects: structured Q&A + impact analysis + undo + preferences-change + a11y recheck
- ✅ Per-page SEO: every site gets `seo.md` with titles, descriptions, og policy, sitemap, robots
- ✅ Accessibility review: every generated frontend gets a pass for missing alt text, labels, semantic HTML, color contrast; auto-fixes inline + `a11y-report.md`

Not yet supported (coming in later versions): public Claude Code plugin distribution, custom domain automation, multi-language site output, Schema.org structured data, automated Lighthouse / Pa11y runs.

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

Skills (`web-builder-orchestrator`, `web-builder-intake`, `web-builder-revise`, `web-builder-deliver`) handle the dialog. Worker agents (`ui-ux-designer`, `content-writer`, `seo-expert`, `frontend-expert`, `backend-engineer`, `accessibility-reviewer`, `deployer`) write the actual files in their own context. The pipeline runs: designer → [content-writer + seo-expert parallel] → [frontend-expert + backend-engineer parallel for full-app] → accessibility-reviewer (final pass). All agents stack-agnostic.

See `docs/specs/2026-04-26-web-builder-plugin-design.md` for the full design.

## License

MIT
