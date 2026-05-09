# web-builder Plan 2: Preview & Deploy

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After the MVP generates a site, give the user a one-click way to preview it locally in their browser and to deploy it to one of four cloud targets (Cloudflare Pages, Vercel, Netlify, GitHub Pages), all in plain language, with auto git initialization in simple mode.

**Architecture:** Add one new `deployer` agent that owns all deployment operations (CLI auth checks + per-target deploy + state.json updates). Enrich the existing `web-builder-deliver` skill with two interactive choice flows (preview + deploy) that come after the initial summary. Update the orchestrator to do a silent initial `git init` + commit in simple mode after agents finish (precondition for any deploy and for Plan 3's undo).

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). Bash for CLI tool invocation. Node.js dev server (`npm run dev`) for preview.

**v0.2.0 scope (vs. spec):**
- 1 new agent: `deployer`
- Modified: orchestrator (initial git commit), deliver (preview + deploy flows)
- 4 deploy targets: Cloudflare Pages (default), Vercel, Netlify, GitHub Pages
- 5th deploy option: "local only — I'll upload myself"
- Preview: starts `npm run dev` in background, gives user the URL, kills server on user request
- All flows in simple-mode plain language; technical CLI errors are translated when surfaced

**Definition of done:** A user runs `/web-builder` end to end, gets the site generated as in v0.1.0, then is asked (a) "do you want to see it in your browser?" and (b) "do you want to publish it on the internet?" — answering yes triggers the actual preview/deploy. State persists in `state.json`. Smoke test passes.

**Out of scope (deferred):**
- Custom domain setup (v1.1)
- Revision flow (Plan 3)
- Other site scopes / dev mode (Plan 4)
- SEO + a11y agents (Plan 5)
- Public Claude Code plugin distribution (Plan 6 — already partially done: private GitHub repo exists)
- Backend deployment for full apps (Plan 4 brings full app scope)

---

## File Structure

```
web-builder/
├── plugin.json                                  # unchanged
├── README.md                                    # MODIFY: update status to v0.2.0
├── commands/
│   └── web-builder.md                           # unchanged
├── skills/
│   ├── web-builder-orchestrator/SKILL.md        # MODIFY: add initial git commit
│   ├── web-builder-intake/SKILL.md              # MODIFY: add gitInitialized to state.json schema docs
│   └── web-builder-deliver/SKILL.md             # MODIFY: add preview + deploy flows
├── agents/
│   ├── ui-ux-designer.md                        # unchanged
│   ├── content-writer.md                        # unchanged
│   ├── frontend-expert.md                       # unchanged
│   └── deployer.md                              # CREATE
├── tests/
│   ├── fixtures/
│   │   ├── sample-brief.md                      # unchanged
│   │   ├── sample-style-guide.md                # unchanged
│   │   ├── sample-content.md                    # unchanged
│   │   └── sample-state.json                    # CREATE (for deployer smoke test)
│   ├── lint.sh                                  # unchanged (still passes)
│   └── smoke-test.md                            # MODIFY: add preview + deploy test sections
└── docs/
    └── plans/
        └── 2026-04-26-plan-2-preview-and-deploy.md  # this file
```

**Responsibilities:**

| File | Owns |
|---|---|
| `agents/deployer.md` | All deployment operations: auth checks, per-target deploy commands, state.json `deployment` updates |
| `skills/web-builder-deliver/SKILL.md` | Final summary + interactive preview flow + interactive deploy flow → invokes deployer agent |
| `skills/web-builder-orchestrator/SKILL.md` | (existing) + simple-mode silent `git init` + initial commit after agents finish |

---

## Task 1: Initial Git Commit in Orchestrator (Sade Mode)

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md` (insert new step before existing step 5)

**Why:** Plan 3's "undo" feature relies on git history. Plan 2's GitHub Pages deployment needs a git repo. Initial commit must happen automatically in simple mode (the user shouldn't need to know `git` exists).

- [ ] **Step 1: Read the current orchestrator skill**

Run: `cat skills/web-builder-orchestrator/SKILL.md` and identify the line numbers of step 4 (state.json update) and step 5 (deliver invocation).

- [ ] **Step 2: Insert new step between current 4 and 5**

Use `Edit` to insert the following between current step 4 and current step 5. The current text of step 5 is `5. Invoke the \`web-builder-deliver\` skill via the \`Skill\` tool, passing the project path.` — the new step becomes step 5 and the deliver step becomes step 6.

New step body to insert:

```markdown
5. Initialize git in the project directory and create the initial commit (simple mode: silent; dev mode behavior is Plan 4):
   - If `.git/` does not exist in the project directory: run `git init -q`, `git add .`, `git commit -q -m "Initial generation by web-builder"`.
   - If `.git/` already exists (user pre-initialized): skip init, but still run `git add .` and `git commit -q -m "Initial generation by web-builder"`.
   - Update `.web-builder/state.json` to add `"gitInitialized": true` and capture the initial commit SHA in a new `"initialCommitSha"` field.
   - On any failure: log to `agentRuns` with agent name `git-init` and continue — git is not strictly required for the generated site to be useful, but the user should be informed once.
```

After insertion, renumber the existing step 5 (deliver) to step 6.

- [ ] **Step 3: Verify the file structure**

Run: `grep -nE "^[0-9]+\." skills/web-builder-orchestrator/SKILL.md` and confirm steps are numbered 1, 2, 3, 4, 5, 6 in that order, with the new step 5 about git init present.

Expected output (line numbers may vary):
```
17:1. Look in cwd for `.web-builder/state.json`.
21:2. Invoke the `web-builder-intake` skill via the `Skill` tool.
25:3. From this point on, **all file operations happen inside the project subdirectory.**
48:4. Update `.web-builder/state.json`...
54:5. Initialize git in the project directory...
60:6. Invoke the `web-builder-deliver` skill...
```

- [ ] **Step 4: Run lint to confirm nothing broke**

Run: `tests/lint.sh`
Expected: `8 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: orchestrator does initial git commit in simple mode"
```

---

## Task 2: Add `deployer` Agent

**Files:**
- Create: `agents/deployer.md`

The deployer is the largest new artifact in Plan 2. It owns all 5 deployment paths (4 cloud + 1 local). The agent runs in its own context, takes a deploy target as input, performs the work, and returns a result.

- [ ] **Step 1: Create `agents/deployer.md`**

Write the following content (preserve every code fence, every Turkish character, every URL exactly):

````markdown
---
name: deployer
description: Deploys a generated static site to one of Cloudflare Pages / Vercel / Netlify / GitHub Pages, or sets up a local-only "files ready to upload" state. Handles CLI auth checks; never asks the user for credentials directly.
tools: Read, Write, Edit, Bash
---

# deployer agent (MVP — static sites only)

You handle all deployment operations for the web-builder plugin. The orchestrator and deliver skill invoke you with a deploy target; you do the work and return.

## Inputs

You receive in the prompt:

- `projectPath`: absolute path to the project directory (contains `dist/`, `package.json`, `.web-builder/state.json`)
- `target`: one of `cloudflare-pages` | `vercel` | `netlify` | `github-pages` | `local`
- `siteName`: the kebab-case site name from `state.json`

## Pre-flight (for all cloud targets)

Before the per-target deploy, verify that `dist/` exists in the project directory. If missing, return:

```
status: failed
reason: dist-missing
human-readable: "There's no built version of the site yet. `npm run build` should have been run first — this is normally done by the frontend-expert agent."
```

The orchestrator should not invoke you if the build hasn't happened, but defensive check.

## Per-target behavior

### `local`

No CLI work. Compute the absolute path of `{projectPath}/dist/` and return:

```
status: success
target: local
artifact: {absolute path to dist/}
human-readable: "The ready files are in this folder: {path}. You can copy them anywhere you like (e.g., cPanel, FTP, your own server)."
```

Do NOT update `state.json` for local target — there's no remote URL to record.

### `cloudflare-pages`

1. Auth check: run `wrangler whoami` (Bash). If exit non-zero or output contains "not authenticated":

   ```
   status: needs-auth
   target: cloudflare-pages
   human-readable: "You're not connected to a Cloudflare account. Run this in your own terminal, then tell me 'ok':
   
   wrangler login
   
   If wrangler isn't installed: npm install -g wrangler"
   ```

   Return without proceeding. The orchestrator will re-invoke you after the user signals readiness.

2. Deploy: run from inside the project directory:

   ```bash
   wrangler pages deploy dist --project-name="{siteName}" --commit-dirty=true 2>&1
   ```

   Capture the output. The deploy URL appears in the output as a line containing `https://...pages.dev`. Extract it.

3. Update `.web-builder/state.json` `deployment` field:

   ```json
   {
     "type": "cloudflare-pages",
     "url": "https://{siteName}.pages.dev",
     "lastDeployAt": "<ISO timestamp>"
   }
   ```

4. Return:

   ```
   status: success
   target: cloudflare-pages
   url: https://{siteName}.pages.dev
   human-readable: "Site is live on Cloudflare! Address: {url}"
   ```

### `vercel`

1. Auth check: run `vercel whoami`. If non-zero or "not authenticated":

   ```
   status: needs-auth
   human-readable: "You're not connected to a Vercel account. Run this in your own terminal:
   
   vercel login
   
   If the vercel CLI isn't installed: npm install -g vercel"
   ```

2. Deploy from project directory:

   ```bash
   vercel deploy --prod --yes 2>&1
   ```

   The output's last line is the deployment URL. Capture it.

3. Update `state.json` `deployment` with `"type": "vercel"`, `"url": "<captured>"`, `"lastDeployAt"`.

4. Return success with URL and human-readable confirmation in the user's language.

### `netlify`

1. Auth check: run `netlify status`. If non-zero or "not logged in":

   ```
   status: needs-auth
   human-readable: "You're not connected to a Netlify account. Run this:
   
   netlify login
   
   If not installed: npm install -g netlify-cli"
   ```

2. First-time site link: if `.netlify/state.json` does not exist in the project directory:
   ```bash
   netlify sites:create --name="{siteName}" 2>&1
   netlify link --name="{siteName}" 2>&1
   ```

3. Deploy:
   ```bash
   netlify deploy --prod --dir=dist 2>&1
   ```

   Capture the "Website URL" from the output.

4. Update `state.json` `deployment`. Return success.

### `github-pages`

This target requires a GitHub repo for the project (separate from the plugin's own repo). Steps:

1. Auth check: run `gh auth status`. If non-zero or "not logged in":

   ```
   status: needs-auth
   human-readable: "You're not connected to a GitHub account. Run this:
   
   gh auth login
   
   If not installed: brew install gh"
   ```

2. Check if remote `origin` exists in the project directory: `git remote get-url origin 2>/dev/null`. If not:
   - Create a private repo: `gh repo create {siteName} --private --source=. --push 2>&1`
   - Read the URL from the output.

3. Enable Pages with GitHub Actions deploy workflow (Astro static):

   - Write `.github/workflows/deploy.yml` in the project directory with the standard Astro-to-Pages workflow (use the official Astro docs template — single workflow that builds and uploads to Pages).
   - Commit the workflow file: `git add .github && git commit -q -m "ci: add Pages deploy workflow"`
   - Push: `git push -q`
   - Enable Pages via API: `gh api -X POST repos/{owner}/{repo}/pages -f build_type=workflow 2>&1`

4. Wait for the first workflow run to start (`gh run list --workflow=deploy.yml --limit=1`). Tell the user the workflow will take ~1-2 minutes and they can watch progress at `https://github.com/{owner}/{repo}/actions`.

5. Update `state.json` `deployment`:
   ```json
   {
     "type": "github-pages",
     "url": "https://{owner}.github.io/{repo}/",
     "lastDeployAt": "<ISO>",
     "repoUrl": "https://github.com/{owner}/{repo}"
   }
   ```

6. Return:
   ```
   status: success
   target: github-pages
   url: https://{owner}.github.io/{repo}/
   human-readable: "Everything is set up for GitHub Pages. The site will be live at {url} in a few minutes. You can watch the build status at: {repoUrl}/actions"
   ```

## On any error

Capture the failed command's output. Return:

```
status: failed
target: <target>
reason: <one-word category: cli-error / network / auth / build-missing / unknown>
human-readable: "<plain-language explanation in user's language; if it's a CLI error, include the actual error text but prefix it with 'Details:'>"
```

The orchestrator will surface this to the user; do not try to recover automatically (deployment recovery requires user intent).

## Constraints

- Never prompt the user for credentials yourself. Always defer to the CLI's own login flow.
- Never store credentials in `state.json` or any plugin-managed file.
- Always update `state.json` `deployment` field on success (except `local`).
- Output a one-line summary at the end of your turn for the orchestrator: `deployer: target=<target> status=<status> [url=<url>]`.
````

- [ ] **Step 2: Verify file**

Run: `head -5 agents/deployer.md`
Expected: frontmatter with `name: deployer`, description, `tools: Read, Write, Edit, Bash`.

Run: `grep -c "^### " agents/deployer.md`
Expected: 5 (one h3 per target — local, cloudflare-pages, vercel, netlify, github-pages).

Run: `grep -c '^```' agents/deployer.md`
Expected: EVEN, around 14-18 (multiple inner code blocks for command examples and JSON snippets).

- [ ] **Step 3: Run lint**

Run: `tests/lint.sh`
Expected: `9 passed, 0 failed.` (one more than before — the new agent file).

- [ ] **Step 4: Commit**

```bash
git add agents/deployer.md
git commit -m "feat: add deployer agent (cloudflare-pages, vercel, netlify, github-pages, local)"
```

---

## Task 3: Enrich `web-builder-deliver` Skill — Preview Flow

**Files:**
- Modify: `skills/web-builder-deliver/SKILL.md`

The current deliver skill ends after listing files and telling the user how to view the site. We add an interactive question: "do you want me to actually open it for you?" — and if yes, run `npm run dev` in the background.

- [ ] **Step 1: Read current deliver skill**

Run: `cat skills/web-builder-deliver/SKILL.md`. Note the current structure: frontmatter, h1 title, `## Inputs`, `## Behavior` (4 numbered items), `## Tone`.

- [ ] **Step 2: Replace `## Behavior` with the enriched version**

Use `Edit` to replace the entire `## Behavior` section (everything from `## Behavior` up to but not including `## Tone`) with:

````markdown
## Behavior

1. List the top-level files in `projectPath` (Bash: `ls {projectPath}`).
2. Open `{projectPath}/.web-builder/state.json` to read the site name and language.
3. Output a friendly summary in the user's language. The summary must include:
   - Confirmation that the site is ready
   - The absolute path of the project directory
   - A 1-sentence explanation of what each top-level markdown file is (`brief.md`, `style-guide.md`, `content.md`) and that the user can edit them by hand
   - A note that revision flow is coming in a later version of the plugin

4. **Preview prompt.** Ask the user (in their language):

   > Want to open the site in your browser now?
   >
   > A) Yes, open it
   > B) No, skip

   If user picks **A**:
   - Use `Bash` with `run_in_background: true` to start `npm run dev` from inside the project directory. Capture the bash shell ID.
   - Wait ~3 seconds (use a Bash sleep or just monitor the bash output briefly until you see "Local" or "ready").
   - Tell the user, in plain language:

     > Ready! Open this address in your browser: http://localhost:4321
     >
     > Take as long as you like. When you're done, just say **"stop"** and I'll shut down the dev server.

   - Save the shell ID in your context. When the user later says "stop" / "close" (in any language), use `KillShell` to terminate the bash process and confirm: "Dev server stopped."

   If user picks **B**: print a quick reminder of how they can preview later (the existing instructions about `npm run dev`), and proceed to step 5.

5. **Deploy prompt.** Ask the user (in their language):

   > Do you want to publish the site online? A few free options:
   >
   > A) Cloudflare Pages (recommended — most generous free plan, easy custom domains)
   > B) Vercel (most natural for Next.js, also fine for static)
   > C) Netlify (classic, simple setup)
   > D) GitHub Pages (you own the repo, build runs on GitHub)
   > E) Not now / Just the files — I'll upload them myself

   For each cloud option (A-D), before invoking the deployer agent, briefly explain in plain language what will happen:

   - For **A**: "Cloudflare needs a CLI tool called `wrangler`. If you're not logged in I'll show you how. Then we'll push the site and get a URL."
   - For **B**: similar phrasing for `vercel` CLI.
   - For **C**: similar phrasing for `netlify` CLI.
   - For **D**: "We'll create a GitHub repo and push the files. Then GitHub will build and publish on its own servers. You'll need the `gh` tool installed in your terminal."
   - For **E**: invoke deployer agent with `target=local`, surface the result, end.

   Get user confirmation ("Should we proceed?") for cloud options, then:

6. **Invoke deployer agent.** Use the `Agent` tool with `subagent_type: "deployer"`. Pass the project path, target, and siteName in the prompt:

   > Project path: `{projectPath}`. Target: `{cloudflare-pages|vercel|netlify|github-pages|local}`. Site name: `{siteName}`. Deploy per your instructions.

7. **Handle deployer result:**

   - If `status: success`: announce the URL with a friendly message. For `local`, point at the dist/ folder.
   - If `status: needs-auth`: surface the deployer's `human-readable` message (it's already plain-language). Wait for the user to say they've authenticated, then re-invoke the deployer agent with the same target.
   - If `status: failed`: surface the failure plainly, ask if they want to try a different target or skip deployment.

8. After deployment is done (or skipped), output a final closing message that includes:
   - The project path
   - The deployment URL (if any)
   - A reminder that they can re-run `/web-builder` from any other folder to start a new project (revision flow will come in a later version)

9. Do NOT start a dev server unless the user explicitly opts in via the preview prompt.
````

- [ ] **Step 3: Verify the deliver skill structure**

Run: `grep -nE "^## " skills/web-builder-deliver/SKILL.md`
Expected: lines for `## Inputs`, `## Behavior`, `## Tone`.

Run: `grep -c "^[0-9]\." skills/web-builder-deliver/SKILL.md`
Expected: 9 (the 9 numbered items in the new Behavior section).

Run: `grep -c "subagent_type" skills/web-builder-deliver/SKILL.md`
Expected: 1 (the deployer invocation).

- [ ] **Step 4: Run lint**

Run: `tests/lint.sh`
Expected: `9 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-deliver/SKILL.md
git commit -m "feat: enrich deliver skill with interactive preview + deploy flows"
```

---

## Task 4: Update `state.json` Schema References

**Files:**
- Modify: `skills/web-builder-intake/SKILL.md`

The intake skill writes the initial `state.json`. The schema reference there does not yet mention the new `gitInitialized`, `initialCommitSha`, or `deployment` fields that Tasks 1 and 2 introduce. Update the docs so future readers see the full schema in one place.

- [ ] **Step 1: Locate the state.json fields list in intake skill**

Run: `grep -nA 12 "Write \`{projectPath}/.web-builder/state.json\`" skills/web-builder-intake/SKILL.md`

Find the section that says "with initial state (see schema in design spec §6.2). Set `mode: \"simple\"`...". You will append additional notes there.

- [ ] **Step 2: Edit the side-effects step**

Use `Edit` to find the line that ends with `empty agentRuns: []` (or similar — the bullet describing initial state.json fields) and append a new line right after:

```
   - Note: subsequent steps (orchestrator git init, deployer) will add `gitInitialized`, `initialCommitSha`, and `deployment` fields. Intake itself does not need to set these — they default to absent.
```

- [ ] **Step 3: Verify the edit**

Run: `grep -A 1 "agentRuns: \[\]" skills/web-builder-intake/SKILL.md`
Expected: the new note line about gitInitialized/initialCommitSha/deployment is present right after.

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `9 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-intake/SKILL.md
git commit -m "docs: note state.json fields added by orchestrator and deployer"
```

---

## Task 5: Add Sample State Fixture for Smoke Test

**Files:**
- Create: `tests/fixtures/sample-state.json`

The Plan 1 fixtures cover the 3 markdown artifacts but not the state.json. To smoke-test the deployer agent (which reads state.json for siteName), we need a fixture state.

- [ ] **Step 1: Write the fixture**

Create `tests/fixtures/sample-state.json`:

```json
{
  "version": "1",
  "mode": "simple",
  "language": "tr",
  "scope": "multi-page-static",
  "stack": "astro+tailwind",
  "siteName": "test-cafe",
  "siteLanguage": "tr",
  "createdAt": "2026-04-26T12:00:00Z",
  "lastModified": "2026-04-26T12:00:00Z",
  "briefHash": "sha256:placeholder",
  "agentRuns": [
    {"agent": "ui-ux-designer", "at": "2026-04-26T12:01:00Z", "wrote": ["style-guide.md"], "status": "success"},
    {"agent": "content-writer", "at": "2026-04-26T12:02:00Z", "wrote": ["content.md"], "status": "success"},
    {"agent": "frontend-expert", "at": "2026-04-26T12:03:00Z", "wrote": ["src/", "package.json", "..."], "status": "success"}
  ],
  "gitInitialized": true,
  "initialCommitSha": "abc123def456"
}
```

- [ ] **Step 2: Verify it's valid JSON**

Run: `python3 -c "import json; d=json.load(open('tests/fixtures/sample-state.json')); print('OK', d['siteName'])"`
Expected: `OK test-cafe`

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/sample-state.json
git commit -m "test: add sample state.json fixture for deployer smoke test"
```

---

## Task 6: Update Smoke Test Procedure

**Files:**
- Modify: `tests/smoke-test.md`

Add new test sections covering the preview and local-deploy flows, since they're new in v0.2.0.

- [ ] **Step 1: Append new test sections to the smoke test doc**

Use `Edit` to add the following just before the existing `## Pass criteria` section:

````markdown
## Test 3: Preview flow (after Test 1 generation)

After Test 1 completes and the deliver skill prompts you with "Want to open the site in your browser now?":

1. Pick **A) Yes, open it**.
2. Expected: plugin runs `npm run dev` in the background, waits ~3s, then tells you to open http://localhost:4321 and that you can say "kapat" to stop.
3. Open http://localhost:4321 in a browser.
4. Expected: site renders correctly (4 pages, Turkish content, Tailwind styles).
5. Tell the plugin: "kapat".
6. Expected: plugin kills the background dev server and confirms.

Pass: dev server stops cleanly, no leftover process on port 4321.

## Test 4: Local deploy (E option)

After preview is closed (or you skipped it), the deploy prompt appears.

1. Pick **E) Just the files — I'll upload them myself**.
2. Expected: plugin invokes deployer with `target=local`, then surfaces a message like "The ready files are in this folder: /tmp/.../test-cafe/dist/".
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
````

- [ ] **Step 2: Verify the smoke test doc**

Run: `grep -nE "^## Test [0-9]" tests/smoke-test.md`
Expected: at least 6 test sections (Test 1 + Test 2 from Plan 1, Test 3-6 from Plan 2).

- [ ] **Step 3: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: add smoke tests for preview and deploy flows"
```

---

## Task 7: Update README

**Files:**
- Modify: `README.md`

Update the Status section to reflect v0.2.0 features and remove preview/deploy from the "not yet supported" list.

- [ ] **Step 1: Read current README status section**

Run: `grep -nA 5 "## Status" README.md`

The current status reads:
```
## Status

**v0.1.0 — MVP.** Multi-page static sites only (Astro + Tailwind). Simple mode only.

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), preview/deploy, revision flow, SEO/accessibility agents.
```

- [ ] **Step 2: Replace the Status section**

Use `Edit` to replace the Status section with:

```markdown
## Status

**v0.2.0.** Multi-page static sites (Astro + Tailwind), simple mode, with preview and deploy.

- ✅ Generate multi-page static site from Q&A
- ✅ Preview locally (`npm run dev`) with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages
- ✅ Local-only output for self-hosting
- ✅ Auto git initialization in simple mode

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), revision flow, SEO/accessibility agents.
```

- [ ] **Step 3: Verify**

Run: `grep -A 9 "## Status" README.md`
Expected: the new content with v0.2.0 and the bullet list.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README status to v0.2.0 (preview + deploy)"
```

---

## Task 8: Final Lint, Structural Smoke Test, Tag v0.2.0

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `9 passed, 0 failed.` (8 from Plan 1 + 1 new agent file).

- [ ] **Step 2: Structural smoke test of deployer (local target)**

Set up a temp test directory with a built site (re-use Plan 1's smoke test artifact pattern):

```bash
rm -rf /tmp/web-builder-smoke-p2
mkdir -p /tmp/web-builder-smoke-p2/test-cafe
cp -r tests/fixtures/sample-brief.md /tmp/web-builder-smoke-p2/test-cafe/brief.md
cp tests/fixtures/sample-style-guide.md /tmp/web-builder-smoke-p2/test-cafe/style-guide.md
cp tests/fixtures/sample-content.md /tmp/web-builder-smoke-p2/test-cafe/content.md
mkdir -p /tmp/web-builder-smoke-p2/test-cafe/.web-builder
cp tests/fixtures/sample-state.json /tmp/web-builder-smoke-p2/test-cafe/.web-builder/state.json
mkdir -p /tmp/web-builder-smoke-p2/test-cafe/dist
echo "<!DOCTYPE html><html><body>Stub built site</body></html>" > /tmp/web-builder-smoke-p2/test-cafe/dist/index.html
```

Then dispatch a subagent with the deployer agent's instructions (inline as in Plan 1's smoke test) and target=local. Verify the agent returns a success result with the dist/ path.

Expected agent summary line: `deployer: target=local status=success`

- [ ] **Step 3: Optional — full end-to-end re-run of Plan 1 smoke**

Re-run the Plan 1 structural smoke test (regenerate the test-cafe site from sample-brief.md via 3-agent dispatches) to confirm Plan 2's orchestrator/deliver/intake changes did not break the generation pipeline. Same expected outcomes as Plan 1.

If you want to skip this and trust the per-task lints, that's acceptable — Plan 2 didn't touch the agent prompts or generation logic.

- [ ] **Step 4: Tag v0.2.0**

```bash
git tag -a v0.2.0 -m "v0.2.0: preview + deploy + initial git commit

- New deployer agent (Cloudflare Pages, Vercel, Netlify, GitHub Pages, local)
- Deliver skill: interactive preview + deploy flows
- Orchestrator: silent git init + initial commit in simple mode
- Smoke test: covers preview and local-deploy paths
"
```

- [ ] **Step 5: Push to GitHub**

```bash
git push origin <branch>
git push --tags
```

(Replace `<branch>` with the actual branch you've been working on, e.g., `plan-2-preview-and-deploy`.)

---

## Done criteria for this plan

- [ ] All 8 tasks complete with lint passing.
- [ ] Deployer agent file exists with all 5 target sections.
- [ ] Deliver skill includes both preview prompt and deploy prompt with all 5 deploy options.
- [ ] Orchestrator does silent `git init` + initial commit in simple mode.
- [ ] Structural smoke test of `local` target passes.
- [ ] `git tag --list` shows `v0.2.0`.
- [ ] No `TBD` / `TODO` strings in any active plugin file.

## Out of scope for this plan (deferred)

- Custom domain automation → v1.1
- Backend deployment (full app scope) → comes implicitly with Plan 4 (full-app scope)
- Revision flow → Plan 3
- Other site scopes + dev mode → Plan 4
- SEO + a11y agents → Plan 5
- Public Claude Code plugin distribution → Plan 6 (the GitHub repo already exists privately)
