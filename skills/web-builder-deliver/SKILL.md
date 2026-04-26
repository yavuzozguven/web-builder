---
name: web-builder-deliver
description: Use after a successful web-builder generation to summarize what was created and tell the user how to view it, in plain language.
---

# web-builder Deliver (MVP)

You wrap up the generation by summarizing what's on disk and telling the user how to see the site.

## Inputs

- `projectPath`: absolute path to the generated project directory.

## Behavior

1. List the top-level files in `projectPath` (Bash: `ls {projectPath}`).
2. Open `{projectPath}/state.json` to read the site name and language.
3. Output a friendly summary in the user's language. The summary must include:
   - Confirmation that the site is ready
   - The absolute path of the project directory
   - A 1-sentence explanation of what each top-level markdown file is (`brief.md`, `style-guide.md`, `content.md`) and that the user can edit them by hand
   - Instructions to view the site, in plain language. **Do not say "run the dev server"** — say something like:

     > Siteyi tarayıcında görmek için: bu klasöre git ve şu komutları çalıştır:
     >
     > ```
     > cd {projectPath}
     > pnpm dev
     > ```
     >
     > Sonra tarayıcıda [http://localhost:4321](http://localhost:4321) adresini aç.

   - A note that preview, deploy, and revision features are coming in the next versions of the plugin.

4. Do not start a dev server yourself. (That's a Plan 2 feature.)

## Tone

Warm, plain language, no jargon. If the user has been technical, you can be slightly less verbose with explanations.
