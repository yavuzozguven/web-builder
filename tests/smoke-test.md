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

## Test 3: Preview flow (after Test 1 generation)

After Test 1 completes and the deliver skill prompts you with "Şimdi siteyi tarayıcında açıp görmek ister misin?":

1. Pick **A) Evet, aç**.
2. Expected: plugin runs `npm run dev` in the background, waits ~3s, then tells you to open http://localhost:4321 and that you can say "kapat" to stop.
3. Open http://localhost:4321 in a browser.
4. Expected: site renders correctly (4 pages, Turkish content, Tailwind styles).
5. Tell the plugin: "kapat".
6. Expected: plugin kills the background dev server and confirms.

Pass: dev server stops cleanly, no leftover process on port 4321.

## Test 4: Local deploy (E option)

After preview is closed (or you skipped it), the deploy prompt appears.

1. Pick **E) Sadece dosyalar — kendim yüklerim**.
2. Expected: plugin invokes deployer with `target=local`, then surfaces a message like "Hazır dosyalar şu klasörde: /tmp/.../test-cafe/dist/".
3. Verify the path exists and contains the built `index.html`, `menu/`, etc.

Pass: path printed correctly, dist/ contents intact.

## Test 5: Cloudflare Pages deploy (optional, requires wrangler auth)

Run only if you have Cloudflare account + wrangler CLI installed and authenticated.

1. After preview, pick **A) Cloudflare Pages**.
2. Expected: plugin explains in plain language what will happen, asks for confirmation, then invokes deployer.
3. Deployer runs `wrangler pages deploy dist --project-name=test-cafe`.
4. Expected: a `https://test-cafe.pages.dev` URL is printed, and `state.json` `deployment` field is updated.
5. Open the URL in a browser.
6. Expected: live site is accessible.

Pass: site is live at returned URL, state.json `deployment.type=cloudflare-pages`.

## Test 6: Cloudflare Pages auth-needed path (optional)

To test the auth-needed flow without actually deploying:

1. Run `wrangler logout` first.
2. Run `/web-builder` end to end as in Test 1.
3. At deploy prompt, pick **A) Cloudflare Pages**.
4. Expected: plugin surfaces `needs-auth` message in plain language, telling you to run `wrangler login`.
5. Without running login, tell the plugin "tamam" anyway.
6. Expected: plugin re-invokes deployer, which fails the auth check again, and surfaces the same message. (No auto-login attempt; respects user's choice.)
7. Run `wrangler login` in another terminal.
8. Tell the plugin "tamam" again.
9. Expected: this time deploy succeeds.

Pass: no silent failures; auth handoff is clean and respects user agency.

## Pass criteria

- Both tests complete without manual intervention beyond answering questions.
- Both generated sites build successfully (`pnpm build` exits 0).
- Both sites render in the browser without console errors.
- `state.json` is well-formed in both runs.

## If a test fails

Log the failure: which task's output broke things, what error was reported, what files were/weren't written. File a follow-up bug for the broken task.
