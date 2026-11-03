#!/usr/bin/env bash
# Checks that the skills are installed and that this repository is wired for the workflow.
# Read-only: it prints findings and suggests fixes, it changes nothing.
set -u

FORK="$(cd "$(dirname "$0")/.." && pwd)"
IDS="ai-daridev-backlog ai-daridev-story ai-daridev-pair ai-daridev-archive ai-daridev-review"
fails=0
warn=0

ok()   { printf '  ok    %s\n' "$*"; }
bad()  { printf '  FAIL  %s\n' "$*"; fails=$((fails+1)); }
note() { printf '  warn  %s\n' "$*"; warn=$((warn+1)); }

echo "engram"
if command -v engram >/dev/null 2>&1; then
  ok "binary: $(command -v engram) ($(engram version 2>/dev/null || echo unknown))"
  if engram doctor >/dev/null 2>&1; then ok "doctor: clean"; else bad "doctor reported findings (run: engram doctor)"; fi
else
  bad "engram not on PATH"
fi

echo "skills"
for id in $IDS; do
  link="$HOME/.agents/skills/$id"
  if [ -L "$link" ] && [ -e "$link" ]; then ok "$id -> $(readlink "$link")"
  elif [ -e "$link" ]; then note "$id exists but is not a symlink (may drift)"
  else bad "$id missing (run: $FORK/scripts/install.sh)"; fi
done

echo "commands (OpenCode)"
for id in $IDS; do
  f="$HOME/.config/opencode/commands/$id.md"
  [ -f "$f" ] && ok "$id.md" || bad "$id.md missing"
done

echo "this repository"
if [ -f .engram/config.json ]; then
  project="$(sed -n 's/.*"project_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' .engram/config.json)"
  ok "engram project: $project"
else
  note "no .engram/config.json here — run: engram init <name>"
fi

if [ -f AGENTS.md ] && grep -q "Workflow config" AGENTS.md 2>/dev/null; then
  ok "AGENTS.md has a Workflow config section"
else
  note "AGENTS.md without a Workflow config section (see AGENTS.template.md)"
fi

PROJECT=$(grep -m1 'engram_project:' AGENTS.md 2>/dev/null | sed 's/.*engram_project:[[:space:]]*//')
if [ -n "${PROJECT:-}" ] && [ -f .engram/config.json ] && [ "$PROJECT" != "$(sed -n 's/.*"project_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' .engram/config.json)" ]; then
  bad "AGENTS.md says engram_project=$PROJECT but .engram/config.json disagrees"
fi

echo
if [ "$fails" -gt 0 ]; then
  echo "$fails problem(s), $warn warning(s). Fix the FAIL lines first."
  exit 1
fi
echo "no failures, $warn warning(s)."
echo "Engram is required: if the MCP is missing, the skills stop. Odoo is optional."
echo "Next: open the agent in this directory, then use a memory tool in a NEW session to confirm the MCP."
