---
name: web-builder-intake
description: Use to collect the user's requirements for a new website project via short, plain-language Q&A. Writes brief.md and returns the project path.
---

# web-builder Intake (MVP)

You collect what the user wants to build through a short Q&A and write the result to `brief.md`.

## Constraints

- **Simple mode (this skill is invoked from `/web-builder`):** ask scope (Q2 below); do NOT ask about frameworks or languages; the worker agents will pick automatically.
- **Dev mode (invoked from `/web-builder-dev`):** ask scope, then ask preferences (interactivity / performance / preferred language) — the plugin uses these to inform agent choices but **never names specific frameworks** in the dialog. The agent picks at runtime.
- Image strategy: contextual Unsplash placeholders for both modes.
- The orchestrator passes you a `mode` parameter (`simple` or `dev`); branch on it.
- **Do not enumerate specific frameworks anywhere in user-facing dialog.** Ask user-facing intent ("simple vs feature-rich", "Python vs Node vs compiled language"); the agents decide on concrete frameworks at generation time.

## Q&A flow

Ask one question at a time. Wait for the user's answer before asking the next.

### Q1: Free-form intro

> Hi! I'll help you out. First, tell me a bit: what is this site for, and who is it for? A couple of sentences is enough.

Capture the answer as `goal`.

### Q2: Site scope

> What kind of site are we making?
>
> A) Single page (short intro, one-pager)
> B) Multi-page promo site (home + about + contact, light or no interaction)
> C) Multi-page + a bit of interaction (form, gallery, small JS features)
> D) Full app with sign-in / orders / data persistence

Map the answer:
- A → `single-page`
- B → `multi-page-static`
- C → `interactive-static`
- D → `full-app`

Capture as `scope`.

In **dev mode only**, after scope, also ask the preference questions below. In **simple mode**, skip them entirely — the agents will pick reasonable defaults based on scope alone.

### Q2-dev-prefs: Dev mode preferences (only if mode == dev)

#### Q2-dev-prefs-1: Performance vs simplicity

> What matters more for this site?
>
> A) As simple and quick to set up as possible (no build step if you want)
> B) Modern, fast (small bundle, fast page loads)
> C) Content/feature heavy (build complexity is fine, but should be maintainable)
> D) Doesn't matter, you pick

Capture as `preferences.priority` (one of `simple`, `performance`, `feature-richness`, `claude-decides`).

#### Q2-dev-prefs-2: Interactivity (only ask for `interactive-static` or `full-app`)

> How much JS-based interaction will the site have?
>
> A) Little (just a couple of small interactions)
> B) Medium (forms, small UI components, a bit of dynamic content)
> C) A lot (a real app — persistent state, complex flows)
> D) Doesn't matter, you pick

Capture as `preferences.interactivity` (one of `low`, `medium`, `high`, `claude-decides`).

#### Q2-dev-prefs-3: Backend language (only ask for `full-app`)

> Any preference for the backend language/ecosystem?
>
> A) Same package as the frontend (a single node project)
> B) A separate Node service
> C) I'd like to use Python
> D) Go / Rust / another compiled language
> E) Java / .NET ecosystem
> F) Doesn't matter, you pick

Capture as `preferences.backendLang` (one of `same-as-frontend`, `node-separate`, `python`, `compiled`, `enterprise-jvm`, `claude-decides`).

The plugin does NOT enumerate specific frameworks. The agent picks within whichever language/ecosystem bucket the user chose.

#### Q2-dev-prefs-4: Database (only ask for `full-app`)

> Database preference?
>
> A) Simplest (file-based, zero setup — you pick)
> B) Classic SQL (Postgres or similar — you pick)
> C) Document DB (MongoDB or similar — you pick)
> D) None / I'll handle it myself
> E) Doesn't matter, you pick

Capture as `preferences.dbStyle` (one of `simple`, `sql`, `document`, `none`, `claude-decides`).

#### Q2-dev-prefs-5: TypeScript

> Should we use TypeScript?
>
> A) Yes
> B) No
> C) You pick (whichever fits the scope)

Capture as `preferences.typescript` (one of `true`, `false`, `claude-decides`).

The whole point is: dev mode collects user-facing intent ("I want fast", "I prefer Python") — never specific tool names. The agent's job is to translate intent into the most appropriate tool **right now**.

### Q3: Project name

Suggest **3 names** based on the goal description from Q1 — make them concrete (mention location/topic if mentioned), short (kebab-case, ≤20 chars), and distinct. Add a "write your own" option.

Example:

> Here are a few names I came up with — pick one you like, or write your own:
>
> • brooklyn-coffee
> • blue-door-cafe
> • corner-coffee
> • [or write your own]

Validate the chosen name: must be kebab-case, no spaces, no special characters except `-`. If invalid, ask again.

### Q4: Content source

> For the content (name, menu, photos, about text, etc.):
>
> A) I'll provide it
> B) You generate sample content, I'll edit later

If A: ask follow-ups in a focused way — collect the specific content the user has (name, contact info, page-specific text) in 1-3 follow-up questions, then move on. Don't drag this out.
If B: note in the brief that placeholders will be used.

### Q5: Style preset

> Pick a visual style:
>
> A) Minimalist (clean, white/black, few colors)
> B) Playful (colorful, fun, rounded shapes)
> C) Corporate (serious, blue/gray, classic)
> D) Vintage (warm tones, retro fonts)
> E) Dark/Modern (dark background, accent colors)

Capture the choice as `stylePreset`.

## Side effects

After all 5 questions are answered:

1. Compute project subdirectory path: `{cwd}/{siteName}/`. If it already exists, ask the user to pick another name.
2. Create the subdirectory: `mkdir -p {projectPath}`.
3. Create `{projectPath}/.web-builder/` directory.
4. Write `{projectPath}/brief.md` using the template below.
5. Write `{projectPath}/.web-builder/state.json` with initial state. Set the following fields:
   - `mode: "simple"` or `"dev"` (as passed by orchestrator)
   - `scope: <captured value from Q2>` (one of `single-page`, `multi-page-static`, `interactive-static`, `full-app`)
   - `siteName: <captured>`
   - `siteLanguage: <detected from user's language>`
   - `createdAt: <ISO timestamp>`
   - `lastModified: <ISO timestamp>`
   - `agentRuns: []` (empty array)
   - `preferences: <only in dev mode; simple mode sets to null or empty {}>`:
     - `priority: <captured from Q2-dev-prefs-1 | null>`
     - `interactivity: <captured from Q2-dev-prefs-2 | null>`
     - `backendLang: <captured from Q2-dev-prefs-3 | null>`
     - `dbStyle: <captured from Q2-dev-prefs-4 | null>`
     - `typescript: <captured from Q2-dev-prefs-5 | null>`
   - `chosenStack: { frontend: null, backend: null, database: null, rationale: null }` (agents populate these on first run)
   - Note: subsequent steps (orchestrator git init, deployer) will add `gitInitialized`, `initialCommitSha`, and `deployment` fields. Intake itself does not need to set these — they default to absent.

## brief.md template

```markdown
# Site Brief: {siteName}

## Scope
{scope value: single-page | multi-page-static | interactive-static | full-app}

## Goal
{goal verbatim from Q1}

## Audience
{infer 1-2 lines from goal; if unsure, write "Not specified"}

## Pages
- Home
- About
- {plus 1-3 more pages inferred from goal: e.g., "Menu", "Services", "Contact"}

## Content Source
{"User-provided" or "Plugin will generate sample content (user will edit it later)"}

{If user provided specific content in Q4-A, append a "## User-Provided Content" section listing the items.}

## Style Preference
Preset style: {stylePreset name}

## Behavior / Interaction
- Static site, no forms.

## Preferences (only populated in dev mode)
- Priority: {simple | performance | feature-richness | claude-decides | null}
- Interactivity: {low | medium | high | claude-decides | null}
- Backend language: {same-as-frontend | node-separate | python | compiled | enterprise-jvm | claude-decides | null}
- Database style: {simple | sql | document | none | claude-decides | null}
- TypeScript: {true | false | claude-decides | null}
```

If the user is writing in another language, translate the headings accordingly: `Scope`, `Goal`, `Audience`, `Pages`, `Content Source`, `Style`, `Interactivity`, `Preferences`.

## Return value

Return the absolute path of the project subdirectory to the orchestrator.
