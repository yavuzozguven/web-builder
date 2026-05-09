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
> B) Contact info (address, phone, email)
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
> A) Add a new page
> B) Delete a page
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
> B) Add an animation
> C) Add a gallery / slider
> D) Some other interaction

Capture. Return:

```
category: behavior
detail: <user's choice>
description: <user's verbatim answer>
```

### If user picks E (technical)

> On the technical side?
>
> A) Change the deploy target (e.g. Cloudflare → Vercel)
> B) Change the site name / URL slug
> C) Change SEO meta (title, description, og policy)
> D) Performance / cache settings
> E) Change my preferences (interactivity, performance, language preference, etc. — the agent will re-pick the stack)
> F) Change scope (e.g. single page → multi-page — big change, the site is regenerated)
> G) Re-run accessibility (a11y) check / apply improvements

For category E, note: SEO meta and performance are partially Plan 5 (SEO/a11y agents). For now, surface a friendly note: "Full SEO and performance support is coming in the next version. For now I can apply simple changes."

Capture. Return:

```
category: technical
detail: <user's choice>
description: <user's verbatim answer>
```

For E (preferences-change): walk the user through dev-mode preference questions again (priority, interactivity, backendLang, dbStyle, typescript). Capture the new values. Return:

```
category: technical
detail: preferences-change
description: <one-line summary of what changed>
new-preferences: <object with the new preference values>
```

For F (scope-change): confirm the new scope with the user (warn it's a big change), capture new scope value. Return:

```
category: technical
detail: scope-change
new-scope: <single-page | multi-page-static | interactive-static | full-app>
```

The orchestrator will re-run all agents for both E and F (they may pick different stacks).

For G (a11y-recheck): no further questions needed. Return:

```
category: technical
detail: a11y-recheck
description: User asked to re-run accessibility review
```

The orchestrator on receiving `detail: a11y-recheck` runs ONLY the `accessibility-reviewer` agent (not the full pipeline) and refreshes `a11y-report.md`.

## Confirmation before returning

Before returning the change record to the orchestrator, summarize what you understood and confirm:

> Got it. {summary of the change}. Should I go ahead?
>
> A) Yes, apply it
> B) No, let's change something else
> C) Cancel

If A: return the change record.
If B: go back to Q1.
If C: return `{category: cancel}` and the orchestrator exits cleanly.

## Constraints

- Do not modify any files yourself. Your output is a change record passed to the orchestrator.
- Keep questions short and concrete. Plain language; no technical jargon.
- Match the user's language.
- Output the final change record as a JSON-style block at the end of your turn for the orchestrator to parse.
