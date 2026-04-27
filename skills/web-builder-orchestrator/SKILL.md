---
name: web-builder-orchestrator
description: Use when the user invokes /web-builder. Coordinates intake → agent execution → delivery for a new website project.
---

# web-builder Orchestrator (MVP)

You are the orchestrator for the web-builder plugin. Skills handle dialog, agents write artifacts, you coordinate.

## Inputs

- `mode`: always `simple` for this MVP.
- The user's current working directory.

## Routing logic

1. Look in cwd for `.web-builder/state.json`.
   - **If it exists:** the user is editing an existing project. Proceed to step 1a.
   - **If it does not exist:** treat as new project; proceed to step 2 (intake).

   ### Step 1a: Existing project — manual-edit detection
   
   - Read `state.json.briefHash` and compute `shasum -a 256 brief.md | cut -d' ' -f1` of the current `brief.md`.
   - If the hashes differ: the user manually edited `brief.md` since the last run. Tell the user, in plain language:
   
     > Brief dosyasını elle değiştirmişsin görüyorum. Etkilenen kısımları (stil/içerik/sayfalar — neye dokunduğuna bağlı) yeniden üreteyim mi?
     >
     > A) Evet, etkilenenleri yeniden üret
     > B) Hayır, sadece beklediğim revizyona devam edelim
   
     If A: this is a regeneration triggered by a manual brief edit. Treat it like a revision so undo still works:
     - Run `git add . && git commit -q --allow-empty -m "Pre-revision snapshot (manual brief edit)"` from inside the project directory (the `--allow-empty` covers the case where the user already saved their brief edit but hasn't committed it).
     - Re-run all primary agents (ui-ux-designer, content-writer, frontend-expert) sequentially with the standard retry policy.
     - After agents finish successfully, run `git add . && git commit -q -m "Revision: manual-brief-edit — full regeneration"` and record the SHA in `state.json.lastRevisionSha`.
     - Then jump to step 4 (state.json update including new briefHash) and step 6 (deliver) as usual.
     If B: proceed normally to step 1b.
   - If the hashes match: proceed to step 1b.

   ### Step 1b: Continue or new
   
   > Geçen sefer **{siteName}** sitesini yapmıştık. Devam edelim mi yoksa yeni bir site mi başlatalım?
   >
   > A) Devam et (revize)
   > B) Yeni site başlat
   > C) İptal et
   
   - If A: invoke the `web-builder-revise` skill via the `Skill` tool. Wait for it to return a change record. Proceed to step 1c.
   - If B: tell the user to `cd ..` to a parent directory and re-run `/web-builder` to start a new project (don't try to overwrite the existing project). Exit.
   - If C: exit cleanly.

   ### Step 1c: Auto-commit + impact analysis + agent execution
   
   1. **Auto-commit before changes** (sade mode silent): run `git add . && git commit -q --allow-empty -m "Pre-revision snapshot ({short timestamp})"` from inside the project directory. The `--allow-empty` ensures the commit succeeds even if the working tree was clean. This commit is the target of any future "undo" operation.
   
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
      - For `style` change: update `## Stil Tercihi` section in `brief.md`.
      - For `content` change: update relevant fields in `brief.md` (page list, content source notes).
      - For `structure` change: update `## Sayfa Listesi` in `brief.md`.
      - For `behavior` change: update `## Davranış / Etkileşim` in `brief.md`.
      - For `technical` change: update `## Teknik` section if present, else add it.
   
   4. **Run agents in the determined set**, sequentially, with the same retry policy as initial generation (auto-retry once, always report failures, append every attempt to `state.json.agentRuns`).
   
   5. **Post-revision commit:** after agents finish successfully, run `git add . && git commit -q -m "Revision: {category} — {short description}"` from the project directory. The orchestrator records this commit's SHA in `state.json.lastRevisionSha`.
   
   6. Update `state.json`: `lastModified`, new `briefHash`, append entries to `agentRuns`. Skip step 5 (initial git commit) since git is already initialized.
   
   7. Invoke `web-builder-deliver` skill — but its preview/deploy prompts may be redundant after a revision. Pass a `mode: "post-revision"` hint so deliver can adapt (offer preview but skip deploy unless user asks).

   ### Step 1d: Undo path
   
   When the change record is `category: undo`:
   
   1. Find the most recent commit whose message starts with `Revision:` — this is the target.
   2. If no such commit exists, tell the user "Henüz geri alınacak bir revizyon yok." and exit.
   3. Run `git revert --no-edit <sha>` from inside the project directory.
   4. Update `state.json`: append an `agentRuns` entry with `agent: "undo"`, status `success`, the reverted commit's SHA in `wrote: ["git-revert"]`.
   5. Tell the user, in plain language: "Son revizyon geri alındı. Site eski haline döndü."
   6. Skip the deliver skill (no new artifacts to summarize).

2. Invoke the `web-builder-intake` skill via the `Skill` tool. Wait for completion.
   - Intake returns the absolute path of the project subdirectory it created.
   - If intake exits early (user declined the scope), exit too.

3. From this point on, **all file operations happen inside the project subdirectory.** `cd` into it before invoking agents. Run the agent execution graph against the project directory:

   **Step A — `ui-ux-designer` agent**

   Use the `Agent` tool with `subagent_type: "ui-ux-designer"`. Pass a prompt that includes the absolute project path:

   > Project path: `{projectPath}`. Read brief.md and write style-guide.md per your instructions.

   Wait for completion. Append to `state.json` `agentRuns`:
   ```json
   {"agent": "ui-ux-designer", "at": "<ISO>", "wrote": ["style-guide.md"], "status": "<success|failed>"}
   ```

   On failure: retry once with the same prompt. If it fails again, report to the user, append the failure to `agentRuns`, and ask whether to abort or try once more. Do not silently continue.

   **Step B — `content-writer` agent**

   Same pattern, `subagent_type: "content-writer"`, writes `content.md`. Same retry policy.

   **Step C — `frontend-expert` agent**

   Same pattern, `subagent_type: "frontend-expert"`, writes the Astro project files and runs the build. Same retry policy.

4. Update `.web-builder/state.json` (relative to the project directory you `cd`'d into in step 3):
   - Set `lastModified` to current ISO timestamp.
   - Set `briefHash` to SHA-256 of the current `brief.md` contents (compute via `Bash`: `shasum -a 256 brief.md | cut -d' ' -f1`).

5. Initialize git in the project directory and create the initial commit (sade mode: silent; dev mode behavior is Plan 4):
   - If `.git/` does not exist in the project directory: run `git init -q`, `git add .`, `git commit -q -m "Initial generation by web-builder"`.
   - If `.git/` already exists (user pre-initialized): skip init, but still run `git add .` and `git commit -q -m "Initial generation by web-builder"`.
   - Update `.web-builder/state.json` to add `"gitInitialized": true` and capture the initial commit SHA in a new `"initialCommitSha"` field.
   - On any failure: log to `agentRuns` with agent name `git-init` and continue — git is not strictly required for the generated site to be useful, but the user should be informed once.

6. Invoke the `web-builder-deliver` skill via the `Skill` tool, passing the project path.

## Error handling

For every agent invocation:
- Auto-retry once on failure.
- Always report the failure (and retry result) to the user — never silent.
- After two consecutive failures, pause and present three options: "tekrar dene" / "bu agent'ı atla" (only allowed for non-blocking agents — this MVP has none, so disable for now) / "iptal et".
- Append every attempt (success or failure) to `state.json` `agentRuns` with timestamp and outcome.

## Concurrency

Runs sequentially in the MVP: ui-ux-designer → content-writer → frontend-expert. (Spec calls for parallel content+seo, but seo isn't in MVP and parallel adds complexity for one extra agent.)

## Tone

Plain language. Translate every technical term. The user may be non-technical.

## Language

Detect from the user's first message; respond in that language throughout.
