#!/usr/bin/env bash
# Lint the plugin: validate plugin.json + every md file's frontmatter.
set -euo pipefail

cd "$(dirname "$0")/.."

ok=0
fail=0

# --- plugin.json (canonical location: .claude-plugin/plugin.json) ---
echo -n ".claude-plugin/plugin.json valid JSON: "
if python3 -c "import json,sys; d=json.load(open('.claude-plugin/plugin.json')); assert 'name' in d and 'version' in d and 'description' in d" 2>/dev/null; then
  echo "OK"; ok=$((ok+1))
else
  echo "FAIL"; fail=$((fail+1))
fi

# --- marketplace.json (single-plugin marketplace at .claude-plugin/marketplace.json) ---
echo -n ".claude-plugin/marketplace.json valid JSON: "
if python3 -c "import json,sys; d=json.load(open('.claude-plugin/marketplace.json')); assert 'name' in d and 'owner' in d and 'plugins' in d and isinstance(d['plugins'], list) and len(d['plugins']) >= 1" 2>/dev/null; then
  echo "OK"; ok=$((ok+1))
else
  echo "FAIL"; fail=$((fail+1))
fi

# --- frontmatter check ---
check_frontmatter() {
  local file="$1"
  local needs_name="$2"   # "yes" for skills/agents, "no" for commands
  local first_line
  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    echo "FAIL ($file: missing frontmatter opening)"; return 1
  fi
  if ! grep -q "^description:" "$file"; then
    echo "FAIL ($file: missing description)"; return 1
  fi
  if [[ "$needs_name" == "yes" ]] && ! grep -q "^name:" "$file"; then
    echo "FAIL ($file: missing name)"; return 1
  fi
  echo "OK ($file)"; return 0
}

# Commands: name not required (filename is the command name).
for f in commands/*.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "no"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

# Skills: name required.
for f in skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "yes"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

# Agents: name required.
for f in agents/*.md; do
  [ -f "$f" ] || continue
  echo -n "frontmatter $f: "
  if check_frontmatter "$f" "yes"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

echo
echo "Summary: ${ok} passed, ${fail} failed."
[[ $fail -eq 0 ]]
