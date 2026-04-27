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

## Test 7: Revision — style change

After Test 1 generation succeeds:

1. Without leaving the parent folder, run `/web-builder` again from the same parent.
2. Plugin should detect the existing `.web-builder/state.json` (manual-edit check passes since brief.md unchanged).
3. Plugin asks: "Geçen sefer kadikoy-kahve sitesini yapmıştık. Devam edelim mi yoksa yeni bir site mi?"
4. Pick **A) Devam et (revize)**.
5. Plugin invokes revise skill, asks "Neyi değiştirmek istersin?" — pick **A) Görsel stil**.
6. Sub-question: pick **A) Renk paletini değiştir**.
7. Tell the plugin: "Daha sıcak olsun, kahverengi ağırlıklı."
8. Plugin confirms summary, you say "Evet, uygula".
9. Plugin runs `ui-ux-designer` + `frontend-expert` (skipping `content-writer`).
10. Plugin auto-commits before agents (look for "Pre-revision snapshot" commit) and after (look for "Revision: style — ..." commit).
11. Plugin invokes deliver skill in post-revision mode.

Pass:
- `git log --oneline | head -5` shows pre-revision and post-revision commits with correct messages.
- `state.json.agentRuns` has new entries for `ui-ux-designer` and `frontend-expert` (NOT `content-writer`).
- `style-guide.md` palette section now reflects warmer/brown tones.
- `dist/` was rebuilt by `frontend-expert`.

## Test 8: Revision — content change (single page)

Following Test 7's project state:

1. Run `/web-builder` again from the parent.
2. Pick **A) Devam et (revize)**, then **B) İçerik**, then **A) Belirli bir sayfanın metnini değiştir**.
3. Plugin asks which page; say "Hakkımızda".
4. Plugin asks what to change; say "Daha samimi bir tone, kafenin kuruluş hikayesi de eklensin."
5. Confirm and continue.
6. Plugin runs `content-writer` + `frontend-expert` (NOT `ui-ux-designer`).

Pass:
- `state.json.agentRuns` has new `content-writer` + `frontend-expert` entries (and no new `ui-ux-designer` entry).
- `content.md` "Page: Hakkımızda" section has updated text reflecting the new tone.
- Dist rebuilt.

## Test 9: Undo

Following Test 8's project state:

1. Run `/web-builder` again.
2. Pick **A) Devam et (revize)**, then **G) Son değişikliği geri al**.
3. Plugin runs `git revert --no-edit <sha>` on Test 8's revision commit.
4. Plugin tells the user "Son revizyon geri alındı."

Pass:
- `git log --oneline` shows a new "Revert ..." commit at HEAD.
- `content.md` "Page: Hakkımızda" section reverted to its Test 1 (or Test 7's pre-content-change) state.
- `state.json.agentRuns` has a new entry with `agent: "undo"`.
- Re-running undo is allowed but only reverts the most recent revision commit each time (each call is a separate revert).

## Test 10: Manual brief.md edit detection (optional)

1. After Test 1, manually edit `brief.md` — change "minimalist" to "playful" in the Stil Tercihi section.
2. Save the file.
3. Run `/web-builder` again from the parent.
4. Plugin detects the briefHash mismatch and asks "Brief dosyasını elle değiştirmişsin görüyorum. Etkilenen kısımları yeniden üreteyim mi?"
5. Pick **A) Evet**.
6. Plugin runs all 3 agents (designer, content, frontend) since the brief is the source of truth.

Pass:
- All 3 agents re-ran (verified via `state.json.agentRuns`).
- New `style-guide.md` reflects "playful" preset (saturated colors instead of minimalist neutrals).
- `briefHash` in `state.json` updated.

## Test 11: Single-page scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At the scope question, pick A (tek sayfa).
3. Continue with default content + minimalist style.
4. Plugin generates a project. The agent picks whatever it deems best for "tek sayfa" — could be vanilla HTML/CSS/JS, could be a tiny static site framework, depending on Claude's current view.
5. Verify: the project builds (or runs without a build, if vanilla); `state.json.chosenStack.frontend` is populated; `state.json.chosenStack.rationale` is non-empty.

Pass:
- `state.json.chosenStack.frontend` is non-null and reasonable for single-page (the rationale should explain "why this stack for a one-pager")
- The project either has no build step (vanilla case) or `npm run build` (or equivalent) succeeds
- Generated files reflect content.md (site title, sections) and style-guide.md (palette in CSS)

## Test 12: Full-app scope (sade mode)

1. Run `/web-builder` in a clean dir.
2. At scope question, pick D (üye girişi / sipariş / veri kaydı).
3. Use the takim-takip example from sample-brief-full-app.md as inspiration for your answers (or any small CRUD app description).
4. Plugin runs frontend-expert AND backend-engineer (state.json.agentRuns has both, with status=success).
5. Both agents populate state.json.chosenStack (frontend, backend, database, rationale).

Pass:
- `state.json.chosenStack.frontend`, `chosenStack.backend`, `chosenStack.database` are all non-null
- The build/install commands run successfully (whatever they are for the picked stacks)
- The project has at least: a way to run the frontend (dev or preview command), a way to run the backend, a database file or migration script
- An `/api/health` endpoint or equivalent exists

## Test 13: Dev mode with backend language preference

1. Run `/web-builder-dev` in a clean dir.
2. At scope, pick D (full-app).
3. At preference questions, set `backendLang` to `python` (option C).
4. Plugin generates the project; backend-engineer's pick should be a Python framework (whatever it considers best for full-app + Python today).

Pass:
- `state.json.preferences.backendLang` is `python`
- `state.json.chosenStack.backend` is a Python-based framework (rationale mentions Python)
- The backend directory has Python project files (`pyproject.toml` or `requirements.txt`, `.py` source files)

## Test 14: Revise — change preferences (re-pick stack)

1. After Test 11 generation succeeds, run `/web-builder` again.
2. Pick A (devam et / revize), then E (technical), then E (Tercihlerimi değiştir).
3. Walk through the preference questions; change `priority` from `simple` to `feature-richness`.
4. Plugin regenerates; the frontend-expert may pick a different stack (richer framework) and update `state.json.chosenStack.frontend`.

Pass:
- `state.json.preferences.priority` is updated to `feature-richness`
- A `Pre-revision snapshot` commit precedes the change
- A `Revision: technical — preferences-change` commit follows
- `state.json.chosenStack.frontend` may differ from before; rationale updated

## Test 15: SEO smoke (seo-expert agent)

After Test 1 generation succeeds:

1. Run `/web-builder` again from the parent (or look at the existing `kadikoy-kahve/` project).
2. Plugin runs the full pipeline; verify `seo.md` exists in the project directory.
3. Open `seo.md` and verify it has:
   - Site-wide section with default site name, description, keywords, og policy
   - Per-page sections — one ### Page block per page in brief.md
   - Sitemap section listing all pages with priority + changefreq
   - robots.txt section with User-agent + Allow + Sitemap line

Pass:
- `seo.md` exists at `{projectPath}/seo.md`
- Site title is in the user's language (Turkish for Test 1, English for Test 2)
- All page slugs (e.g., /, /menu, /hakkimizda, /iletisim) appear in both Per-page SEO and Sitemap sections
- `state.json.agentRuns` has an entry for `seo-expert` with `wrote: ["seo.md"]` and `status: success`

## Test 16: A11y smoke (accessibility-reviewer agent)

After Test 1 generation succeeds:

1. Verify `a11y-report.md` exists in the project directory.
2. Open `a11y-report.md` and verify it has:
   - Summary section (files scanned, issues fixed, issues reported)
   - Auto-fixed issues section (or "no auto-fixes needed" if the generated code was already clean)
   - Issues reported section (or empty if everything passed)
   - Notes section (skip-to-content link, page language)
3. Spot-check the generated frontend code for a11y basics:
   - At least one `<img>` has a non-empty `alt` attribute
   - The root `<html>` has `lang="..."` matching state.json.siteLanguage
   - At least one form input (if present) has an associated `<label>` or aria-label

Pass:
- `a11y-report.md` exists at `{projectPath}/a11y-report.md`
- The summary numbers add up correctly (scanned ≥ 1, fixed + reported = total issues found)
- Spot-checks pass: no `<img>` without alt, `<html lang="...">` set
- `state.json.agentRuns` has an entry for `accessibility-reviewer`

## Test 17: A11y recheck via revise (optional)

1. After Test 1 + Test 16, manually edit a frontend file to introduce an a11y issue (e.g., remove an alt attribute from an `<img>`).
2. Run `/web-builder` and pick A (revize) → E (technical) → G (a11y recheck).
3. Plugin re-runs only `accessibility-reviewer`.
4. Verify the missing alt was auto-fixed and `a11y-report.md` lists it under "Auto-fixed issues".

Pass:
- Only `accessibility-reviewer` ran (state.json.agentRuns has new entry; no new entries for content-writer / frontend-expert / etc.)
- The `<img>` you broke has an alt again
- `a11y-report.md` mentions the fix

## Pass criteria

- Both tests complete without manual intervention beyond answering questions.
- Both generated sites build successfully (`pnpm build` exits 0).
- Both sites render in the browser without console errors.
- `state.json` is well-formed in both runs.

## If a test fails

Log the failure: which task's output broke things, what error was reported, what files were/weren't written. File a follow-up bug for the broken task.
