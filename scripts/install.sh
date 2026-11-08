#!/usr/bin/env bash
# ai-daridev installer: link the skills and the OpenCode commands, migrate the global block.
# Usage: ./scripts/install.sh [--check]
set -euo pipefail

FORK="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.agents/skills"
CMD_DIR="$HOME/.config/opencode/commands"
AGENT_HOMES=(
  "$HOME/.claude"
  "$HOME/.codex"
  "$HOME/.gemini"
  "$HOME/.continue"
  "$HOME/.codeium/windsurf"
  "$HOME/.kiro"
  "$HOME/.config/devin"
)
INSTRUCTIONS=(
  "$HOME/.config/opencode/AGENTS.md"
  "$HOME/.claude/CLAUDE.md"
  "$HOME/.gemini/GEMINI.md"
  "$HOME/.codex/AGENTS.md"
)
RETIRED=(ai-daridev-check-plan)
BLOCK='<!-- ai-daridev -->
Work is tracked with the `ai-daridev` skills, invoked manually: backlog → story → pair → review →
archive. The repo root is the nearest `AGENTS.md` holding an `ai-daridev:start` block; read it
before writing. Never move an Odoo card between stages, never mark a card done or cancelled, never
assign. Repo memory lives in `docs/ai-daridev/` and is committed by a human.
<!-- ai-daridev -->'

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -d "$FORK/skills" ] || die "no skills/ in $FORK"
IDS=()
for d in "$FORK"/skills/*/; do
  [ -d "$d" ] && IDS+=("$(basename "$d")")
done
[ "${#IDS[@]}" -gt 0 ] || die "no skills found in $FORK/skills"

targets=("$SKILLS_DIR")
for a in "${AGENT_HOMES[@]}"; do
  [ -d "$a" ] && targets+=("$a/skills")
done

migrate_block() {
  local file="$1" tmp n
  [ -f "$file" ] || return 0
  n="$(grep -c '<!-- ai-daridev -->' "$file" || true)"
  if [ "$n" -eq 0 ]; then return 0; fi
  if [ "$n" -lt 2 ]; then say "skip $file (single marker)"; return 0; fi
  tmp="$(mktemp)"
  awk -v block="$BLOCK" '
    /<!-- ai-daridev -->/ {
      n++
      if (n == 1) { print block; skip = 1 }
      else if (n == 2) { skip = 0 }
      next
    }
    skip { next }
    { print }
  ' "$file" > "$tmp"
  if cmp -s "$file" "$tmp"; then
    rm -f "$tmp"
    say "ok    $file"
    return 0
  fi
  cp -p "$file" "$file.bak.$(date +%Y%m%d%H%M%S)"
  mv "$tmp" "$file"
  say "block $file"
}

check() {
  local rc=0 t id f n
  for t in "${targets[@]}"; do
    for id in "${IDS[@]}"; do
      if [ -e "$t/$id/SKILL.md" ]; then say "ok    $t/$id"; else say "MISS  $t/$id"; rc=1; fi
    done
  done
  for f in "$FORK"/commands/*.md; do
    n="$(basename "$f")"
    if [ -e "$CMD_DIR/$n" ]; then say "ok    $CMD_DIR/$n"; else say "MISS  $CMD_DIR/$n"; rc=1; fi
  done
  for t in "${targets[@]}" "$HOME/.config/opencode/skills"; do
    for id in "${RETIRED[@]}"; do
      if [ -e "$t/$id" ]; then say "STALE $t/$id"; rc=1; fi
    done
  done
  if [ -e "$CMD_DIR/ai-daridev-check-plan.md" ]; then
    say "STALE $CMD_DIR/ai-daridev-check-plan.md"
    rc=1
  fi
  for f in "${INSTRUCTIONS[@]}"; do
    [ -f "$f" ] || continue
    n="$(grep -c '<!-- ai-daridev -->' "$f" || true)"
    if [ "$n" -lt 2 ]; then
      say "skip  block $f (no marker pair)"
      continue
    fi
    if grep -q 'Repo memory lives in' "$f" && ! grep -q 'ai-daridev preflight' "$f"; then
      say "ok    block $f"
    else
      say "STALE block $f"
      rc=1
    fi
  done
  return $rc
}

if [ "${1:-}" = "--check" ]; then
  check
  exit $?
fi

# 1. skills into ~/.agents/skills and every installed agent
for t in "${targets[@]}"; do mkdir -p "$t"; done
for id in "${IDS[@]}"; do
  for t in "${targets[@]}"; do
    dst="$t/$id"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then rm -rf "$dst"; fi
    ln -sfn "$FORK/skills/$id" "$dst"
  done
done
say "skills: linked ${#IDS[@]} into ${#targets[@]} directories"

# 2. OpenCode prefers ~/.config/opencode/skills, so a copy there would shadow the link
for id in "${IDS[@]}" "${RETIRED[@]}"; do
  if [ -e "$HOME/.config/opencode/skills/$id" ] || [ -L "$HOME/.config/opencode/skills/$id" ]; then
    rm -rf "$HOME/.config/opencode/skills/$id"
    say "removed shadowing copy: ~/.config/opencode/skills/$id"
  fi
done

# 3. retired skills
for t in "${targets[@]}"; do
  for id in "${RETIRED[@]}"; do
    if [ -e "$t/$id" ] || [ -L "$t/$id" ]; then
      rm -rf "$t/$id"
      say "removed retired skill: $t/$id"
    fi
  done
done

# 4. OpenCode commands (Claude Code and Codex invoke the skills directly)
mkdir -p "$CMD_DIR"
for src in "$FORK"/commands/*.md; do
  ln -sfn "$src" "$CMD_DIR/$(basename "$src")"
done
for link in "$CMD_DIR"/*.md; do
  [ -L "$link" ] || continue
  if [ ! -e "$link" ]; then rm -f "$link"; say "removed stale link: $link"; fi
done
say "commands: linked to $CMD_DIR"

# 5. global instruction block
for f in "${INSTRUCTIONS[@]}"; do migrate_block "$f"; done

# 6. MCP
say ""
say "Odoo is optional. To enable cards, register the MCP in the agent you use:"
say "  OpenCode  ~/.config/opencode/opencode.json, under mcp.servers:"
say '    "odoo": { "type": "local", "command": ["<path>/mcp.sh"], "disabled": false }'
say "  Claude    claude mcp add --scope user odoo -- <path>/mcp.sh"
say '  Codex     ~/.codex/config.toml: [mcp_servers.odoo] command = "<path>/mcp.sh"'
say ""
say "Then run: $FORK/scripts/install.sh --check"
