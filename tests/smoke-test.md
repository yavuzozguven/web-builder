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
4. Answer Q1: `Kadıköy'de küçük bir kafem var, kahve ve sandviç satıyorum, bir tanıtım sitesi istiyorum.`
5. Expected: plugin summarizes "çok sayfalı tanıtım sitesi" interpretation; presents A/B/C choice. Pick A.
6. Expected: plugin suggests 3 names + "kendin yaz" option. Pick the first suggestion (or type a custom name like `kadikoy-kahve`).
7. Expected: plugin asks content source (A/B). Pick B.
8. Expected: plugin asks style preset (A-E). Pick A (Minimalist).
9. Expected: plugin runs three agents sequentially (designer → content → frontend), reporting progress. Frontend agent runs `pnpm install` and `pnpm build`.
10. Expected: deliver skill summarizes the output and tells you how to view the site (`cd kadikoy-kahve && pnpm dev`).

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
