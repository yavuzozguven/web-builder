# Product Hunt submission copy — web-builder

Project: https://github.com/yavuzozguven/web-builder
Landing: https://yavuzozguven.github.io/web-builder/
License: MIT
Maker: Yavuz Ozguven

---

## 1. Tagline variants (PH limit: 60 chars)

| # | Angle | Tagline | Chars |
|---|---|---|---|
| 1 | No framework choice | `The agents pick the framework. You describe the site.` | 53 |
| 2 | Describe → deploy speed | `Describe a website, get a deployable project back.` | 50 |
| 3 | Stack-agnostic | `One prompt. Any stack. A real project you own.` | 46 |
| 4 | Claude Code plugin | `A Claude Code plugin that builds real websites.` | 47 |
| 5 | Creative / unexpected | `Stop choosing frameworks. Start shipping sites.` | 47 |

**Recommendation:** #2 `Describe a website, get a deployable project back.` (50 chars) **(RECOMMENDED)** — it states the input and the output in one breath, no jargon, no hype.

---

## 2. Short description (PH limit: 260 chars)

**Variant A (229 chars) (RECOMMENDED)**
`A Claude Code plugin that turns a short Q&A into a working website — pages, content, SEO, accessibility pass, one-command deploy. The agents pick the stack at runtime. You get real source files you can edit, commit, and own. MIT.`

**Variant B (239 chars)**
`Describe what you want. web-builder asks 5-10 plain questions, picks the framework, writes a complete project (not a starter template), and deploys to Cloudflare, Vercel, Netlify, or GitHub Pages. Runs inside Claude Code. Open source, MIT.`

**Recommendation:** Variant A — leads with what it is, ends with ownership and license, which is the differentiator vs sandboxed builders.

---

## 3. Long pitch (180 words)

web-builder is a Claude Code plugin for developers who want to skip the "which framework, which CSS approach, which deploy target" loop and just describe the site they need.

You run `/web-builder:start` in an empty directory. It asks 5–10 plain-language questions (what kind of site, how many pages, visual style, content source, deploy target). Worker agents then run in sequence — designer, content writer, SEO, frontend, accessibility reviewer — and produce a complete project on disk: pages, real content, SEO metadata, sitemap, a clean accessibility pass, and an editable `brief.md` you can hand-revise.

The agents choose the stack at runtime based on the brief — a one-page CV gets vanilla HTML, a content site gets an SSG, a full app gets a frontend plus backend chosen together — and record the rationale in `state.json`.

Unlike v0, Lovable, or Bolt — which generate code in their own sandboxes — web-builder writes plain files into your local repo. You commit them, edit them, re-run, deploy from your own machine.

Requires a Claude Code subscription. Alpha-quality v1.0.0, built solo, open source under MIT.

---

## 4. First maker comment (170 words)

Hi PH — Yavuz here, maker of web-builder.

I work as an engineer at Insider and kept hitting the same wall on side projects: I'd open a terminal to spin up a small marketing page or a quick tool, and lose forty minutes deciding between Next, Astro, SvelteKit, plain HTML, Tailwind vs not, Vercel vs Cloudflare. The decision fatigue killed more side projects than the actual work ever did.

So I built this for myself. The premise: I describe the goal, the plugin's agents decide the stack, and I get a real project on disk — not a sandboxed preview I can't own.

What I learned building it: keeping the agents stack-agnostic (zero hardcoded framework names in the plugin code) was harder than expected but pays back every time the JS ecosystem moves.

Next on the roadmap: custom domain automation, AI-generated images instead of Unsplash placeholders, and a test framework setup pass.

It needs a Claude Code subscription to run. Source is MIT.

Happy to answer questions — would love feedback on the revision flow specifically.

---

## 5. Suggested categories (pick 3)

1. **Developer Tools** — primary fit; this is a CLI plugin for devs who already live in Claude Code.
2. **Artificial Intelligence** — the generation flow is fully agent-driven; this is where AI-curious devs browse.
3. **Productivity** — the value proposition is removing setup decisions, not building a novel framework, so productivity is honest framing.

(Skipping No-Code — the target user reads diffs and edits source files; calling it no-code would mislead.)

---

## 6. Suggested topics / tags

- Open Source
- Developer Tools
- Artificial Intelligence
- CLI
- Web Development
- GitHub
- SaaS Tools
- Claude

---

## 7. Hunter outreach DM template (≤500 chars)

> Hi [Name] — I'm launching **web-builder** on Product Hunt soon: a Claude Code plugin that takes a plain-language brief and outputs a complete, deployable website project (agents pick the stack, you own the source files). Open source, MIT, v1.0.0.
>
> Repo: github.com/yavuzozguven/web-builder
>
> Given your work on [their thing], I thought this might fit what you hunt. Would you be open to hunting it? Happy to share a draft of the listing and answer anything. Thanks either way.

(Char count: ~485)

---

## 8. Launch-day comment thread starters

1. Which stack would you want web-builder to pick for a one-page founder portfolio — vanilla HTML, Astro, or something else? Tell me your reasoning.
2. What's the most decision-fatiguing part of starting a small web project for you — framework, CSS, deploy target, or naming the repo?
3. If you've used v0 / Lovable / Bolt, what made you stop using them (or stick with them)? I'm specifically curious about the "I want to own the files" point.

---

## 9. Risks & honest disclosures

**Material risk to disclose:** web-builder runs as a Claude Code plugin, which means using it requires an active Claude Code subscription (paid product from Anthropic). The plugin itself is free and MIT-licensed, but it cannot function standalone.

**Where to mention it in the listing:** in the **long pitch (Section 3)**, second-to-last paragraph, as a single plain sentence: *"Requires a Claude Code subscription."* This places the disclosure inline with the technical setup info rather than buried at the bottom or hidden in the FAQ. It also belongs in the first maker comment (already included above) so the top-pinned comment thread surfaces it for skimmers.

**Other honest framings already in the copy:**
- "Alpha-quality v1.0.0" — not pretending it's battle-tested.
- "Built solo" — not pretending there's a team.
- No fabricated metrics, no testimonials, no "trusted by".
- No claims about output quality beyond what the README documents (SEO meta, a11y pass, build succeeds).

---

## Submit-time recommendation

**Tagline:** `Describe a website, get a deployable project back.` (50 chars)
**Description:** Variant A.
**Category primary:** Developer Tools.
