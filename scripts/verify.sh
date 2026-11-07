#!/usr/bin/env bash
# Checks that the skills are installed and that this repository is wired for the workflow.
# Read-only: it prints findings and suggests fixes, it changes nothing.
set -u

FORK="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_DIRS="$HOME/.claude $HOME/.gemini $HOME/.continue $HOME/.codeium/windsurf $HOME/.kiro $HOME/.config/devin $HOME/.codex"
CMD_DIR="$HOME/.config/opencode/commands"
fails=0
warn=0

ok()   { printf '  ok    %s\n' "$*"; }
bad()  { printf '  FAIL  %s\n' "$*"; fails=$((fails+1)); }
note() { printf '  warn  %s\n' "$*"; warn=$((warn+1)); }

IDS=""
for dir in "$FORK"/skills/*/; do
  [ -d "$dir" ] || continue
  IDS="${IDS:+$IDS }$(basename "$dir")"
done
[ -n "$IDS" ] || bad "no skills found in $FORK/skills"

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

echo "agents"
for a in $AGENT_DIRS; do
  [ -d "$a/skills" ] || continue
  name="${a#$HOME/}"
  missing=""
  for id in $IDS; do
    [ -e "$a/skills/$id/SKILL.md" ] || missing="$missing $id"
  done
  if [ -n "$missing" ]; then note "$name is missing:$missing (re-run the installer)"; else ok "$name"; fi
done

echo "commands (OpenCode)"
for f in "$FORK"/commands/*.md; do
  name="$(basename "$f")"
  dst="$CMD_DIR/$name"
  if [ -L "$dst" ] && [ -e "$dst" ]; then ok "$name (symlink)"
  elif [ -f "$dst" ]; then note "$name is a copy, not a symlink (re-run the installer)"
  else bad "$name missing (run: $FORK/scripts/install.sh)"; fi
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

cfg() { grep -m1 "^[[:space:]]*[-*][[:space:]]*$1:" AGENTS.md 2>/dev/null | sed "s/.*$1:[[:space:]]*//"; }

ENGRAM_PROJECT="$(cfg engram_project)"
if [ -n "${ENGRAM_PROJECT:-}" ] && [ -f .engram/config.json ] && [ "$ENGRAM_PROJECT" != "$(sed -n 's/.*"project_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' .engram/config.json)" ]; then
  bad "AGENTS.md says engram_project=$ENGRAM_PROJECT but .engram/config.json disagrees"
fi

TAG="$(cfg card_tag)"
case "$TAG" in
  frontend|backend|script|workflow) ok "card_tag: $TAG" ;;
  "") note "AGENTS.md has no card_tag (defaults to backend)" ;;
  *) bad "card_tag '$TAG' is not one of frontend|backend|script|workflow" ;;
esac

if cfg odoo_uid >/dev/null 2>&1 && [ -n "$(cfg odoo_uid)" ]; then
  bad "odoo_uid is in AGENTS.md — it is personal; move it with 'ai-daridev uid <n>'"
else
  ok "AGENTS.md has no odoo_uid (personal file, as designed)"
fi

REPO_SLUG="$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g')"
PERSONAL="$HOME/.config/ai-daridev/repos/$REPO_SLUG.json"
if [ -f "$PERSONAL" ]; then
  ok "personal uid: $PERSONAL"
else
  note "no personal uid — 'mine' is not marked (ai-daridev uid <n>)"
fi

if command -v ai-daridev >/dev/null 2>&1; then
  if ai-daridev preflight >/dev/null 2>&1; then ok "preflight: ok"; else bad "preflight failed (run: ai-daridev preflight)"; fi
else
  bad "ai-daridev CLI not on PATH (run: ./scripts/setup.sh)"
fi

GITIGNORE=".gitignore"
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "${GIT_ROOT:-}" ] && [ "$GIT_ROOT" != "$(pwd)" ]; then GITIGNORE="$GIT_ROOT/.gitignore"; fi
if [ -f "$GITIGNORE" ] && grep -qE '^\.engram/(engram\.db|tmp)|\*\*/\.engram/(engram\.db|tmp)' "$GITIGNORE" 2>/dev/null; then
  ok ".gitignore covers .engram/engram.db* and .engram/tmp/ ($GITIGNORE)"
else
  note "add '.engram/engram.db*' and '.engram/tmp/' to $GITIGNORE"
fi

echo "memory"
if [ -f .engram/config.json ]; then
  if [ -n "$(git status --porcelain -- .engram 2>/dev/null)" ]; then
    note ".engram/ has uncommitted changes (checkpoint commits use: git commit --only -- .engram/)"
  else
    ok ".engram/ is clean"
  fi
else
  note "no .engram/config.json here — memory checks skipped"
fi

echo
if [ "$fails" -gt 0 ]; then
  echo "$fails problem(s), $warn warning(s). Fix the FAIL lines first."
  exit 1
fi
echo "no failures, $warn warning(s)."
echo "Engram is required: if the MCP is missing, the skills stop. Odoo is optional."
echo "Next: open the agent in this directory, then use a memory tool in a NEW session to confirm the MCP."
