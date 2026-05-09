# web-builder Plan 3: Revision Flow

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When the user re-invokes `/web-builder` inside an existing project directory, walk them through a structured mini-Q&A to revise the site, run only the agents whose artifacts are affected, auto-commit before changes (so "undo" works), and detect manual `brief.md` edits.

**Architecture:** A new `web-builder-revise` skill owns the revision Q&A. The orchestrator's routing logic gains real "existing project" handling — including manual-edit detection (briefHash diff), an impact-analysis function that maps a structured change record to the minimum set of agents to re-run, an auto-commit step before agent execution, and an "undo" path that runs `git revert` of the last revision commit. The deliver skill's closing message gains a one-liner telling the user how to come back and revise.

**Tech Stack:** Markdown + YAML frontmatter (Claude Code plugin format). Bash for git operations and SHA-256 computation.

**v0.3.0 scope (vs. spec):**
- New skill: `web-builder-revise` with 7-option Q&A (style / content / structure / behavior / technical / free-form / undo)
- Orchestrator: structured "existing project" branch with manual-edit detection, impact analysis, auto-commit
- Deliver skill: closing message gains a "to revise, run /web-builder again" reminder
- Smoke test: 3 new tests (style change → designer+frontend re-run, content change → content-writer+frontend re-run, undo → git revert verified)

**Definition of done:** A user can run `/web-builder` in an already-generated project directory and: (a) be asked whether to continue or start fresh, (b) if continuing, pick one of 7 revision categories, (c) see only the affected agents re-run (verified by `state.json.agentRuns`), (d) the change is git-committed automatically, (e) the user can pick "undo" later to revert. Manual `brief.md` edits are detected via hash comparison and surfaced before agents run.

**Out of scope (deferred):**
- Other site scopes (single page, full app) → Plan 4
- Dev mode + stack override → Plan 4
- SEO + accessibility agents → Plan 5
- Plan 5 will mean SEO/a11y artifacts also enter impact analysis; Plan 3's analysis logic should accept "unknown agent" gracefully (skip) so Plan 5 only adds entries
- Public Claude Code plugin distribution → Plan 6

---

## File Structure

```
web-builder/
├── plugin.json                                  # MODIFY: bump version to 0.3.0
├── README.md                                    # MODIFY: status to v0.3.0
├── commands/
│   └── web-builder.md                           # unchanged
├── skills/
│   ├── web-builder-orchestrator/SKILL.md        # MODIFY: real "existing project" routing + impact analysis + auto-commit
│   ├── web-builder-intake/SKILL.md              # unchanged
│   ├── web-builder-deliver/SKILL.md             # MODIFY: closing message mentions revision flow
│   └── web-builder-revise/SKILL.md              # CREATE: 7-option revision Q&A
├── agents/
│   ├── ui-ux-designer.md                        # unchanged
│   ├── content-writer.md                        # unchanged
│   ├── frontend-expert.md                       # unchanged
│   └── deployer.md                              # unchanged
├── tests/
│   ├── fixtures/                                # unchanged
│   ├── lint.sh                                  # unchanged (auto-picks up new skill via glob)
│   └── smoke-test.md                            # MODIFY: add Tests 7-9 for revision
└── docs/
    └── plans/
        ├── 2026-04-26-plan-2-preview-and-deploy.md
        └── 2026-04-27-plan-3-revision-flow.md   # this file
```

**Responsibilities:**

| File | Owns |
|---|---|
| `skills/web-builder-revise/SKILL.md` | Revision Q&A flow; normalizes user intent into a structured change record; passes record to orchestrator |
| `skills/web-builder-orchestrator/SKILL.md` (modified) | Existing-project routing, briefHash diff detection, impact analysis (change record → agent set), auto-commit before/after revision, undo execution |
| `skills/web-builder-deliver/SKILL.md` (modified) | Closing message updated to point at the revision path |

---

## Task 1: Create `web-builder-revise` Skill

**Files:**
- Create: `skills/web-builder-revise/SKILL.md`

This skill is invoked by the orchestrator when the user opts to continue editing an existing project. It conducts the structured Q&A, normalizes the user's intent, and returns a structured change record that the orchestrator's impact analysis consumes.

- [ ] **Step 1: Write the revise skill**

Create `skills/web-builder-revise/SKILL.md` with this exact content:

````markdown
---
name: web-builder-revise
description: Use when the user is editing an existing web-builder project. Conducts a structured mini-Q&A to capture what to change, normalizes the intent, and returns a change record for the orchestrator to act on.
---

# web-builder Revise (MVP)

You guide the user through a small, focused Q&A to figure out what they want to change. You do not modify any files yourself — your job is to elicit a structured change record and return it.

## Inputs

- `projectPath`: absolute path of the existing project directory.
- The orchestrator has already confirmed the user wants to continue editing this project.

## Q&A flow

Ask one question at a time. Wait for the user's answer before proceeding.

### Q1: Top-level category

> OK, back to the **{siteName}** project. What do you want to change?
>
> A) Visual style (colors, font, layout)
> B) Content (text, menu, contact info)
> C) Structure / add-remove pages (new page, new section, delete page)
> D) Behavior (add form, add animation, change interaction)
> E) Technical (deploy setting, performance, SEO meta)
> F) None of those — let me describe it freely
> G) Undo last change

Read `siteName` from `{projectPath}/.web-builder/state.json`.

### If user picks G (undo)

Return the change record:

```
category: undo
detail: revert-last-revision
```

The orchestrator will run `git revert` on the most recent revision commit. No further questions needed.

### If user picks F (free-form)

> Tell me — what should we change?

After the user describes the change, infer which structured category (A-E) it falls into and confirm:

> From what I understand this is a "{inferred category}" change — is that right?
>
> A) Yes
> B) No, a different category

If A: proceed to that category's follow-up questions.
If B: ask which category and proceed.

### If user picks A (style)

Ask one of these follow-ups (your choice based on user's likely intent):

> What should we change about the style?
>
> A) Change the color palette
> B) Change the font
> C) Change the overall vibe
> D) Style of a specific section (only header, only the cards, etc.)

Then ask for the actual change:

> Right now: {current palette / font / vibe — read briefly from style-guide.md}. What would you like?

Capture user's answer. Return:

```
category: style
detail: <one of: palette / typography / vibe / specific-section>
description: <user's verbatim answer>
```

### If user picks B (content)

> What about the content?
>
> A) Change the text on a specific page
> B) Kontakt bilgileri (adres, telefon, e-posta)
> C) Change an image
> D) Add new content (new section, new item — not a new page)

Then for each: ask the specific change. Capture the user's verbatim answer.

Return:

```
category: content
detail: <one of: page-text / contact / images / new-section>
description: <user's verbatim answer>
target-page: <if applicable, e.g. "Menu" or "About">
```

### If user picks C (structure)

> What about the structure?
>
> A) Yeni sayfa ekle
> B) Sayfa sil
> C) Change the page order
> D) Add a new section (to an existing page)

Capture the change. Return:

```
category: structure
detail: <one of: add-page / remove-page / reorder / add-section>
description: <user's verbatim answer>
```

### If user picks D (behavior)

> What about behavior?
>
> A) Add a contact form
> B) Animasyon ekle
> C) Galeri / slider ekle
> D) Some other interaction

Capture. Return:

```
category: behavior
detail: <user's choice>
description: <user's verbatim answer>
```

### If user picks E (technical)

> Teknik konularda?
>
> A) Change the deploy target (e.g. Cloudflare → Vercel)
> B) Change the site name / URL slug
> C) Change SEO meta (title, description)
> D) Performance / cache settings

For category E, note: SEO meta and performance are partially Plan 5 (SEO/a11y agents). For now, surface a friendly note: "Full SEO and performance support is coming in the next version. For now I can apply simple changes."

Capture. Return:

```
category: technical
detail: <user's choice>
description: <user's verbatim answer>
```

## Confirmation before returning

Before returning the change record to the orchestrator, summarize what you understood and confirm:

> Got it. {summary of the change}. Should I go ahead?
>
> A) Yes, uygula
> B) No, let's change something else
> C) Cancel

If A: return the change record.
If B: go back to Q1.
If C: return `{category: cancel}` and the orchestrator exits cleanly.

## Constraints

- Do not modify any files yourself. Your output is a change record passed to the orchestrator.
- Keep questions short and concrete. Plain language; no technical jargon.
- Match the user's language (Turkish or English).
- Output the final change record as a JSON-style block at the end of your turn for the orchestrator to parse.
````

- [ ] **Step 2: Verify the file**

Run: `head -5 skills/web-builder-revise/SKILL.md`
Expected: frontmatter with `name: web-builder-revise`.

Run: `grep -nE "^### " skills/web-builder-revise/SKILL.md`
Expected: list of 7+ h3 sections (Q1, A, B, C, D, E, F, G branches plus optional sub-sections).

Run: `grep -c '^```' skills/web-builder-revise/SKILL.md`
Expected: EVEN, around 14-18 (one fenced JSON-style block per category return + a few example fences).

- [ ] **Step 3: Lint**

Run: `tests/lint.sh`
Expected: `10 passed, 0 failed.` (one more than v0.2.0 because of the new skill).

- [ ] **Step 4: Commit**

```bash
git add skills/web-builder-revise/SKILL.md
git commit -m "feat: add web-builder-revise skill (7-option revision Q&A)"
```

---

## Task 2: Orchestrator — Real Existing-Project Routing

**Files:**
- Modify: `skills/web-builder-orchestrator/SKILL.md`

The current orchestrator step 1 has a placeholder: "since this is the MVP I can't edit an existing project". Replace with the real branching logic.

- [ ] **Step 1: Read current orchestrator**

Run: `cat skills/web-builder-orchestrator/SKILL.md`. Locate step 1 (the cwd state.json check) and the bullet that contains the MVP placeholder text.

- [ ] **Step 2: Replace step 1 with real routing**

Use Edit to replace step 1 entirely. The new step 1:

````markdown
1. Look in cwd for `.web-builder/state.json`.
   - **If it exists:** the user is editing an existing project. Proceed to step 1a.
   - **If it does not exist:** treat as new project; proceed to step 2 (intake).

   ### Step 1a: Existing project — manual-edit detection
   
   - Read `state.json.briefHash` and compute `shasum -a 256 brief.md | cut -d' ' -f1` of the current `brief.md`.
   - If the hashes differ: the user manually edited `brief.md` since the last run. Tell the user, in plain language:
   
     > I see you edited the brief file by hand. Should I regenerate the affected parts (style/content/pages — depending on what you touched)?
     >
     > A) Yes, regenerate the affected parts
     > B) No, just continue with the revision I was expecting
   
     If A: skip the revise skill and re-run all agents (ui-ux-designer, content-writer, frontend-expert) — the brief is the source of truth and a manual edit invalidates everything downstream. After re-run, jump to step 4 (state.json update including new briefHash).
     If B: proceed normally to step 1b.
   - If the hashes match: proceed to step 1b.

   ### Step 1b: Continue or new
   
   > Last time we built the **{siteName}** site. Do you want to continue, or start a new site?
   >
   > A) Continue (revise)
   > B) Start a new site
   > C) Cancel
   
   - If A: invoke the `web-builder-revise` skill via the `Skill` tool. Wait for it to return a change record. Proceed to step 1c.
   - If B: tell the user to `cd ..` to a parent directory and re-run `/web-builder` to start a new project (don't try to overwrite the existing project). Exit.
   - If C: exit cleanly.

   ### Step 1c: Auto-commit + impact analysis + agent execution
   
   1. **Auto-commit before changes** (simple mode silent): run `git add . && git commit -q -m "Pre-revision snapshot ({short timestamp})"` from inside the project directory. This commit is the target of any future "undo" operation.
   
   2. **Impact analysis** — given the change record's `category`, determine which agents to re-run:
   
      | Change category | Agents to re-run (in order) |
      |---|---|
      | `style` | `ui-ux-designer`, `frontend-expert` |
      | `content` | `content-writer`, `frontend-expert` |
      | `structure` | `ui-ux-designer` (if layout shifts), `content-writer`, `frontend-expert` |
      | `behavior` | `frontend-expert` |
      | `technical` | `frontend-expert` (for performance/cache); for deploy changes, route to deliver skill's deploy flow instead |
      | `undo` | (no agents — see step 1d below) |
      | `cancel` | exit cleanly |
   
   3. **Update brief.md and supporting docs** — based on the change record, edit `brief.md` (and any sub-document like `style-guide.md` description if relevant) to reflect the new intent BEFORE invoking agents. The agents will then read the updated brief and produce updated artifacts.
      - For `style` change: update `## Style Preference` section in `brief.md`.
      - For `content` change: update relevant fields in `brief.md` (page list, content source notes).
      - For `structure` change: update `## Pages` in `brief.md`.
      - For `behavior` change: update `## Behavior / Interaction` in `brief.md`.
      - For `technical` change: update `## Teknik` section if present, else add it.
   
   4. **Run agents in the determined set**, sequentially, with the same retry policy as initial generation (auto-retry once, always report failures, append every attempt to `state.json.agentRuns`).
   
   5. **Post-revision commit:** after agents finish successfully, run `git add . && git commit -q -m "Revision: {category} — {short description}"` from the project directory. The orchestrator records this commit's SHA in `state.json.lastRevisionSha`.
   
   6. Update `state.json`: `lastModified`, new `briefHash`, append entries to `agentRuns`. Skip step 5 (initial git commit) since git is already initialized.
   
   7. Invoke `web-builder-deliver` skill — but its preview/deploy prompts may be redundant after a revision. Pass a `mode: "post-revision"` hint so deliver can adapt (offer preview but skip deploy unless user asks).

   ### Step 1d: Undo path
   
   When the change record is `category: undo`:
   
   1. Find the most recent commit whose message starts with `Revision:` — this is the target.
   2. If no such commit exists, tell the user "There's no revision to undo yet." and exit.
   3. Run `git revert --no-edit <sha>` from inside the project directory.
   4. Update `state.json`: append an `agentRuns` entry with `agent: "undo"`, status `success`, the reverted commit's SHA in `wrote: ["git-revert"]`.
   5. Tell the user, in plain language: "The last revision has been undone. The site is back to its previous state."
   6. Skip the deliver skill (no new artifacts to summarize).
````

After this insertion, the existing steps 2-6 remain — but step 1 is now much larger. The deliver invocation (current step 6) stays as-is and only fires for new-project flows; revision flow's step 1c.7 invokes deliver inline.

- [ ] **Step 3: Verify orchestrator structure**

Run: `grep -nE "^[0-9]+\." skills/web-builder-orchestrator/SKILL.md`
Expected: top-level steps 1, 2, 3, 4, 5, 6 (current scheme preserved).

Run: `grep -nE "^### Step 1" skills/web-builder-orchestrator/SKILL.md`
Expected: 4 sub-steps — `### Step 1a:`, `### Step 1b:`, `### Step 1c:`, `### Step 1d:`.

Run: `grep -c "Impact analysis" skills/web-builder-orchestrator/SKILL.md`
Expected: at least 1.

Run: `grep -c "git revert" skills/web-builder-orchestrator/SKILL.md`
Expected: at least 1 (in step 1d).

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `10 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-orchestrator/SKILL.md
git commit -m "feat: orchestrator handles existing-project revision flow"
```

---

## Task 3: Update Deliver Skill — Closing Message

**Files:**
- Modify: `skills/web-builder-deliver/SKILL.md`

Step 8 (closing message) currently says "they can re-run `/web-builder` from any other folder to start a new project (revision flow will come in a later version)". Replace with revision-aware wording.

- [ ] **Step 1: Read current deliver skill**

Run: `cat skills/web-builder-deliver/SKILL.md`. Locate the step 8 closing message text.

- [ ] **Step 2: Replace the closing message**

Use Edit to replace the line:

```
   - A reminder that they can re-run `/web-builder` from any other folder to start a new project (revision flow will come in a later version)
```

with:

```
   - A reminder that the user can come back to this project anytime: re-run `/web-builder` from inside this project folder (`{projectPath}`) and pick "Continue (revise)" to make changes — style, content, structure, behavior, deploy target, or undo the last change.
```

- [ ] **Step 3: Verify**

Run: `grep -A 1 "come back to this project" skills/web-builder-deliver/SKILL.md`
Expected: the new line is present.

Run: `grep -c "revision flow will come" skills/web-builder-deliver/SKILL.md`
Expected: 0 (old wording removed).

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `10 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add skills/web-builder-deliver/SKILL.md
git commit -m "docs: deliver skill closing message points users at revision flow"
```

---

## Task 4: Smoke Test — Revision Flow

**Files:**
- Modify: `tests/smoke-test.md`

Append three new tests covering revision (style change), revision (content change), and undo. These come after Test 6 (Cloudflare auth-needed) and before `## Pass criteria`.

- [ ] **Step 1: Append new tests**

Use Edit to insert the following just before `## Pass criteria`:

````markdown
## Test 7: Revision — style change

After Test 1 generation succeeds:

1. Without leaving the parent folder, run `/web-builder` again from the same parent.
2. Plugin should detect the existing `.web-builder/state.json` (manual-edit check passes since brief.md unchanged).
3. Plugin asks: "Last time we built the brooklyn-coffee site. Do you want to continue, or start a new site?"
4. Pick **A) Continue (revise)**.
5. Plugin invokes revise skill, asks "What do you want to change?" — pick **A) Visual style**.
6. Sub-question: pick **A) Change the color palette**.
7. Tell the plugin: "Make it warmer, more brown-leaning."
8. Plugin confirms summary, you say "Yes, apply".
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
2. Pick **A) Continue (revise)**, then **B) Content**, then **A) Change the text on a specific page**.
3. Plugin asks which page; say "About".
4. Plugin asks what to change; say "More personal tone, include the cafe's founding story."
5. Confirm and continue.
6. Plugin runs `content-writer` + `frontend-expert` (NOT `ui-ux-designer`).

Pass:
- `state.json.agentRuns` has new `content-writer` + `frontend-expert` entries (and no new `ui-ux-designer` entry).
- `content.md` "Page: About" section has updated text reflecting the new tone.
- Dist rebuilt.

## Test 9: Undo

Following Test 8's project state:

1. Run `/web-builder` again.
2. Pick **A) Continue (revise)**, then **G) Undo last change**.
3. Plugin runs `git revert --no-edit <sha>` on Test 8's revision commit.
4. Plugin tells the user "The last revision has been undone."

Pass:
- `git log --oneline` shows a new "Revert ..." commit at HEAD.
- `content.md` "Page: About" section reverted to its Test 1 (or Test 7's pre-content-change) state.
- `state.json.agentRuns` has a new entry with `agent: "undo"`.
- Re-running undo is allowed but only reverts the most recent revision commit each time (each call is a separate revert).

## Test 10: Manual brief.md edit detection (optional)

1. After Test 1, manually edit `brief.md` — change "minimalist" to "playful" in the Style Preference section.
2. Save the file.
3. Run `/web-builder` again from the parent.
4. Plugin detects the briefHash mismatch and asks "I see you edited the brief file by hand. Should I regenerate the affected parts?"
5. Pick **A) Yes**.
6. Plugin runs all 3 agents (designer, content, frontend) since the brief is the source of truth.

Pass:
- All 3 agents re-ran (verified via `state.json.agentRuns`).
- New `style-guide.md` reflects "playful" preset (saturated colors instead of minimalist neutrals).
- `briefHash` in `state.json` updated.
````

- [ ] **Step 2: Verify**

Run: `grep -nE "^## Test [0-9]+:" tests/smoke-test.md`
Expected: 10 tests listed (Tests 1-10).

- [ ] **Step 3: Commit**

```bash
git add tests/smoke-test.md
git commit -m "test: add revision flow smoke tests (style, content, undo, manual brief edit)"
```

---

## Task 5: Update README to v0.3.0

**Files:**
- Modify: `README.md`

Add revision flow to the supported list; remove from "not yet supported".

- [ ] **Step 1: Replace Status section**

Use Edit to replace the entire Status section. The current version (post-Plan 2):

```
## Status

**v0.2.0.** Multi-page static sites (Astro + Tailwind), simple mode, with preview and deploy.

- ✅ Generate multi-page static site from Q&A
- ✅ Preview locally (`npm run dev`) with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages
- ✅ Local-only output for self-hosting
- ✅ Auto git initialization in simple mode

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), revision flow, SEO/accessibility agents.
```

The new version:

```
## Status

**v0.3.0.** Multi-page static sites (Astro + Tailwind), simple mode, full preview/deploy/revision loop.

- ✅ Generate multi-page static site from Q&A
- ✅ Preview locally (`npm run dev`) with one click
- ✅ Deploy to Cloudflare Pages, Vercel, Netlify, or GitHub Pages
- ✅ Local-only output for self-hosting
- ✅ Auto git initialization in simple mode
- ✅ Revise existing projects: structured Q&A, impact-aware re-runs, undo, manual brief.md edit detection

Not yet supported (coming in later versions): tek-sayfa sites, full web apps, dev mode (technical stack overrides), SEO/accessibility agents.
```

- [ ] **Step 2: Verify**

Run: `grep -A 11 "^## Status" README.md`
Expected: new content with 6 ✅ items and v0.3.0.

Run: `grep -c "v0.3.0" README.md`
Expected: at least 1.

Run: `grep -c "revision flow" README.md`
Expected: 0 (removed from "not yet supported").

- [ ] **Step 3: Bump plugin.json version**

Edit `plugin.json` to change `"version": "0.2.0"` to `"version": "0.3.0"`.

Run: `python3 -c "import json; print(json.load(open('plugin.json'))['version'])"`
Expected: `0.3.0`.

- [ ] **Step 4: Lint**

Run: `tests/lint.sh`
Expected: `10 passed, 0 failed.`

- [ ] **Step 5: Commit**

```bash
git add README.md plugin.json
git commit -m "docs: bump to v0.3.0 (revision flow shipped)"
```

---

## Task 6: Final Lint, Structural Smoke Test, Tag v0.3.0

- [ ] **Step 1: Run lint**

Run: `tests/lint.sh`
Expected: `10 passed, 0 failed.`

- [ ] **Step 2: Structural smoke test of the impact analysis logic**

Since the revision flow's correctness is mostly about the orchestrator's prompt + the revise skill's structured output, a true behavioral test requires interactive Claude Code. We can do a structural check:

1. Read `skills/web-builder-orchestrator/SKILL.md` and confirm the impact analysis table maps each category to the correct agent set.
2. Read `skills/web-builder-revise/SKILL.md` and confirm each Q&A branch returns a JSON-style change record matching the orchestrator's expectations (category names align: `style`, `content`, `structure`, `behavior`, `technical`, `undo`, `cancel`).
3. Dispatch a subagent acting as `web-builder-revise` against the existing test-cafe project (re-using Plan 1's smoke fixture) and verify it returns a well-formed change record for a "change style" scenario.

If the orchestrator's category names match the revise skill's output names, ship it. The actual git revert and agent re-run logic is exercised by the manual smoke tests (Tests 7-10) when the user runs them.

- [ ] **Step 3: Tag v0.3.0**

```bash
git tag -a v0.3.0 -m "v0.3.0: revision flow

- New web-builder-revise skill (7-option Q&A: style/content/structure/behavior/technical/free-form/undo)
- Orchestrator: real existing-project routing with manual-edit detection,
  impact analysis (change category → minimum agent set), auto-commit
  before/after revisions, undo path via git revert
- Deliver skill: closing message points users at revision flow
- Smoke test: 4 new tests (Tests 7-10) for revision and brief-edit detection
"
```

- [ ] **Step 4: Push and merge**

```bash
git push origin <feature-branch>
git push --tags
git checkout main
git merge --ff-only <feature-branch>
git push origin main
git branch -d <feature-branch>
```

(Replace `<feature-branch>` with the actual branch name, e.g., `plan-3-revision-flow`.)

---

## Done criteria for this plan

- [ ] All 6 tasks complete with lint passing (`10 passed, 0 failed`).
- [ ] `web-builder-revise` skill exists with 7 Q&A categories (A-G).
- [ ] Orchestrator has the 4-substep existing-project branch (1a manual-edit detection, 1b continue/new, 1c revision agent execution, 1d undo).
- [ ] Impact analysis table in orchestrator maps categories to agents.
- [ ] Deliver closing message points at revision flow.
- [ ] `git tag --list` shows `v0.3.0`.
- [ ] No `TBD` / `TODO` strings in any active plugin file.

## Out of scope for this plan (deferred)

- Other site scopes (single page / full app) → Plan 4
- Dev mode + stack override → Plan 4
- SEO + a11y agents (whose output also enters impact analysis) → Plan 5; Plan 3's analysis is forward-compatible (unknown agent names just don't trigger re-runs)
- Custom domain automation → v1.1
- Multi-revision rollback (`git revert HEAD~3`) — only single-step undo in v0.3.0
- Branch-based revisions / "try this and revert if I don't like it" — v1.x feature, not needed yet

## Risks and edge cases

- **Conflicting manual edits + plugin revisions:** if the user edits both `brief.md` AND asks the plugin for a revision, the plugin re-runs all 3 agents (full regeneration). Documented in step 1a.
- **Empty git history:** if `git revert` fails because there's no revision commit yet, the orchestrator surfaces "There's no revision to undo yet." Documented in step 1d.
- **Multiple undos in a row:** each undo is its own revert. The user can keep undoing until reaching the initial commit. After that, further undo attempts find no `Revision:` commit and exit cleanly.
- **Agent re-run failures during revision:** orchestrator uses the same retry policy as initial generation (one auto-retry, always report). The pre-revision auto-commit ensures the user can always recover via undo even if agents fail.
