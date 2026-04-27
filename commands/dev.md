---
description: Build a website end-to-end through guided Q&A — dev mode (asks technical preferences like interactivity level, performance priority, language preference; the plugin still picks the framework, but with your input).
---

You are entering the web-builder flow in **dev mode** — a slightly more technical Q&A. The user can express preferences (e.g., "I care about fast initial load", "I prefer Python on the backend", "let me write the JavaScript myself") and these inform the agent's framework choice. Plain language is still preferred.

Use the `Skill` tool to invoke the `web-builder-orchestrator` skill, passing `mode=dev`.

Detect the user's language from their first message and respond in that language throughout.

Do not output anything to the user before invoking the skill — the skill itself handles all dialog.
