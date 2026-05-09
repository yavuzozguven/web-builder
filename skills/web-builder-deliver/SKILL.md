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
2. Open `{projectPath}/.web-builder/state.json` to read the site name and language.
3. Output a friendly summary in the user's language. The summary must include:
   - Confirmation that the site is ready
   - The absolute path of the project directory
   - A 1-sentence explanation of what each top-level markdown file is (`brief.md`, `style-guide.md`, `content.md`, `seo.md`) and that the user can edit them by hand
   - A note that the user can re-run `/web-builder` later to revise this site (style, content, structure, behavior, deploy target, or undo the last change)

3a. **A11y report surfacing.** Read `{projectPath}/a11y-report.md` if it exists.
   - In **simple mode** (`state.json.mode === "simple"`): append a 1-line summary like "Accessibility check: {N} automatic fixes applied, {M} findings need attention (see a11y-report.md for details)." (translate to the user's language as needed). Mention the report file by name so the user knows where to look for details.
   - In **dev mode** (`state.json.mode === "dev"`): surface the full Auto-fixed and Issues reported sections from a11y-report.md inline.
   - If `a11y-report.md` doesn't exist: skip silently (accessibility-reviewer may have been skipped if frontend wasn't generated).

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
     > Take as long as you like. When you're done, just say **"stop"** and I'll shut down the preview.

   - Save the shell ID in your context. When the user later says "stop" / "close" (in any language), use `KillShell` to terminate the bash process and confirm: "Preview stopped."

   If user picks **B**: print a quick reminder of how they can preview later (the existing instructions about `npm run dev`), and proceed to step 5.

5. **Deploy prompt.** Ask the user (in their language):

   > Do you want to publish the site online? A few free options:
   >
   > A) Cloudflare Pages ({"recommended — most generous free plan, easy custom domains" if scope is static, otherwise "good static option"})
   > B) Vercel ({"recommended — most natural for modern full-apps" if scope is full-app, otherwise "best for full-app, also fine for static"})
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
   - A reminder that the user can come back to this project anytime: re-run `/web-builder` from inside this project folder (`{projectPath}`) and pick "Continue (revise)" to make changes — style, content, structure, behavior, deploy target, or undo the last change.

9. Do NOT start a dev server unless the user explicitly opts in via the preview prompt.

## Tone

Warm, plain language, no jargon. If the user has been technical, you can be slightly less verbose with explanations.
