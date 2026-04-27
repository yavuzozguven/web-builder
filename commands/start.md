---
description: Build a website end-to-end through guided Q&A.
---

You are entering the web-builder flow in **sade mode** (plain language, no jargon — the plugin asks plain-language questions about the kind of site you want, and the framework/language choice is made automatically by the agent at generation time).

Use the `Skill` tool to invoke the `web-builder-orchestrator` skill, passing `mode=simple`.

Detect the user's language from their first message and respond in that language throughout.

Do not output anything to the user before invoking the skill — the skill itself handles all dialog.
