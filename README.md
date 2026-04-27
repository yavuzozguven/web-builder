# web-builder

A Claude Code plugin that builds you a website end-to-end through guided Q&A. You describe what you want, the plugin asks a few quick questions, and you end up with a working site in a folder.

## Status

**v0.2.0.** Multi-page static sites (Astro + Tailwind), sade mode, with preview and deploy.

- ✅ Generate multi-page static site from Q&A
- ✅ Preview locally (`npm run dev`) with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages
- ✅ Local-only output for self-hosting
- ✅ Auto git initialization in sade mode

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), revision flow, SEO/accessibility agents.

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
