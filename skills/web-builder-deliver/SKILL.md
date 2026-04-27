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
   - A 1-sentence explanation of what each top-level markdown file is (`brief.md`, `style-guide.md`, `content.md`) and that the user can edit them by hand
   - A note that revision flow is coming in a later version of the plugin

4. **Preview prompt.** Ask the user (in their language):

   > Şimdi siteyi tarayıcında açıp görmek ister misin?
   >
   > A) Evet, aç
   > B) Hayır, geçelim

   If user picks **A**:
   - Use `Bash` with `run_in_background: true` to start `npm run dev` from inside the project directory. Capture the bash shell ID.
   - Wait ~3 seconds (use a Bash sleep or just monitor the bash output briefly until you see "Local" or "ready").
   - Tell the user, in plain language:

     > Hazır! Tarayıcıda şu adresi aç: http://localhost:4321
     >
     > Görmek istediğin kadar baksın. Bittikten sonra bana **"kapat"** dersen, dev server'ı durdururum.

   - Save the shell ID in your context. When the user later says "kapat" / "stop" / "close" (in either language), use `KillShell` to terminate the bash process and confirm: "Dev server kapatıldı."

   If user picks **B**: print a quick reminder of how they can preview later (the existing instructions about `npm run dev`), and proceed to step 5.

5. **Deploy prompt.** Ask the user (in their language):

   > Siteyi internet'te yayınlamak ister misin? Birkaç ücretsiz seçenek var:
   >
   > A) Cloudflare Pages (önerilen — en cömert ücretsiz plan, custom domain kolay)
   > B) Vercel (Next.js için en doğal, statik için de iyi)
   > C) Netlify (klasik, basit setup)
   > D) GitHub Pages (kendi repo'na sahip olursun, build GitHub'da yapılır)
   > E) Hayır şimdilik / Sadece dosyalar — kendim yüklerim

   For each cloud option (A-D), before invoking the deployer agent, briefly explain in plain language what will happen:

   - For **A**: "Cloudflare için `wrangler` adında bir komut satırı aracı gerek. Eğer giriş yapmamışsan sana göstereceğim. Sonra siteyi gönderip bir adres alacağız."
   - For **B**: similar phrasing for `vercel` CLI.
   - For **C**: similar phrasing for `netlify` CLI.
   - For **D**: "GitHub'a bir repo açıp dosyaları göndereceğiz. Sonra GitHub kendi sunucularında build edip yayınlayacak. Senin terminalinde `gh` aracı yüklü olmalı."
   - For **E**: invoke deployer agent with `target=local`, surface the result, end.

   Get user confirmation ("Devam edelim mi?" / "Should we proceed?") for cloud options, then:

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

## Tone

Warm, plain language, no jargon. If the user has been technical, you can be slightly less verbose with explanations.
