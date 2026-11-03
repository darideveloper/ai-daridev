#!/usr/bin/env bash
# ai-daridev installer (Linux / macOS).
# Engram is REQUIRED: the installer aborts if it cannot install or verify it.
# Skills and OpenCode commands are SYMLINKED, so a git pull updates them with no re-run.
# Usage: ./scripts/install.sh
#        AI_DARIDEV_FORK=/path/to/clone ./scripts/install.sh
set -eu

FORK="${AI_DARIDEV_FORK:-${HOLA_AI_FORK:-$(cd "$(dirname "$0")/.." && pwd)}}"
VER="${ENGRAM_VERSION:-3.6.1}"
LEGACY="backlog story pair archive review"
AGENT_DIRS="$HOME/.claude $HOME/.gemini $HOME/.continue $HOME/.codeium/windsurf $HOME/.kiro $HOME/.config/devin $HOME/.codex"
CMD_DIR="$HOME/.config/opencode/commands"

say() { printf '%s\n' "$*"; }
die() { printf '\nerror: %s\n' "$*" >&2; exit 1; }

# Skills come from the clone, never from a hardcoded list that can drift.
IDS=""
for dir in "$FORK"/skills/*/; do
  [ -d "$dir" ] || continue
  id="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || die "skill '$id' has no SKILL.md in $FORK"
  IDS="${IDS:+$IDS }$id"
done
[ -n "$IDS" ] || die "no skills found in $FORK/skills"

# --- 1. Engram (required) ---------------------------------------------------
engram_bin="$(command -v engram || true)"
[ -n "$engram_bin" ] || engram_bin="$HOME/.local/bin/engram"

installed=""
if [ -x "$engram_bin" ]; then
  installed="$("$engram_bin" version 2>/dev/null | awk '{print $2}')"
fi

if [ "$installed" = "$VER" ]; then
  say "engram: already installed ($installed)"
elif [ -n "$installed" ]; then
  say "engram: $installed found, installing $VER into $HOME/.local/bin"
fi

if [ "$installed" != "$VER" ]; then
  case "$(uname -s)" in
    Linux)  OS=linux ;;
    Darwin) OS=darwin ;;
    *) die "unsupported OS '$(uname -s)'. Install Engram manually: https://github.com/Gentleman-Programming/engram" ;;
  esac
  case "$(uname -m)" in
    x86_64|amd64)  ARCH=amd64 ;;
    arm64|aarch64) ARCH=arm64 ;;
    *) die "unsupported architecture '$(uname -m)'. Install Engram manually." ;;
  esac

  asset="engram_${VER}_${OS}_${ARCH}.tar.gz"
  base="https://github.com/Gentleman-Programming/engram/releases/download/v$VER"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  curl -fsSL -o "$tmp/$asset" "$base/$asset"      || die "could not download $asset"
  curl -fsSL -o "$tmp/checksums.txt" "$base/checksums.txt" || die "could not download checksums.txt"

  if command -v sha256sum >/dev/null 2>&1; then
    ( cd "$tmp" && grep "$asset" checksums.txt | sha256sum -c - ) || die "checksum failed for $asset"
  elif command -v shasum >/dev/null 2>&1; then
    ( cd "$tmp" && grep "$asset" checksums.txt | shasum -a 256 -c - ) || die "checksum failed for $asset"
  else
    say "warning: no sha256 tool found, skipping checksum verification"
  fi

  tar -xzf "$tmp/$asset" -C "$tmp" || die "could not extract $asset"
  [ -f "$tmp/engram" ] || die "engram binary not found inside $asset"
  mkdir -p "$HOME/.local/bin"
  # Write then rename: the old binary may still be executing as an MCP server.
  install -m755 "$tmp/engram" "$HOME/.local/bin/.engram.new" || die "could not stage engram in ~/.local/bin"
  mv -f "$HOME/.local/bin/.engram.new" "$HOME/.local/bin/engram" || die "could not install engram to ~/.local/bin"
  say "engram: installed $VER at $HOME/.local/bin/engram"
fi

# Engram is required: prove it works before touching anything else.
[ -n "$engram_bin" ] || engram_bin="$HOME/.local/bin/engram"
[ -x "$engram_bin" ] || die "engram not found on PATH and not at ~/.local/bin/engram"
"$engram_bin" version >/dev/null 2>&1 || die "engram is installed but not runnable ($engram_bin)"
if ! "$engram_bin" doctor >/dev/null 2>&1; then
  say "warning: 'engram doctor' reported findings — run it and review before relying on memory"
fi
say "engram: verified ($("$engram_bin" version 2>/dev/null))"

# --- 2. Remove shadowing copies --------------------------------------------
# OpenCode gives ~/.config/opencode/skills precedence over ~/.agents/skills, so an
# older copy silently wins over the linked skill.
for id in $IDS $LEGACY; do
  shadow="$HOME/.config/opencode/skills/$id"
  if [ -e "$shadow" ] || [ -L "$shadow" ]; then
    rm -rf "$shadow"
    say "removed shadowing copy: $shadow"
  fi
done

# --- 3. Skills: clone -> ~/.agents/skills -> each agent ---------------------
mkdir -p "$HOME/.agents/skills"
# remove links from the pre-prefix era so only the new names remain
for id in $LEGACY; do
  rm -rf "$HOME/.agents/skills/$id"
  for a in $AGENT_DIRS; do
    link="$a/skills/$id"
    if [ -L "$link" ] || [ -e "$link" ]; then rm -rf "$link"; fi
  done
  rm -f "$CMD_DIR/$id.md"
done

for id in $IDS; do
  ln -sfn "$FORK/skills/$id" "$HOME/.agents/skills/$id"
  for a in $AGENT_DIRS; do
    [ -d "$a/skills" ] && ln -sfn "$HOME/.agents/skills/$id" "$a/skills/$id"
  done
done
say "skills: linked $IDS into ~/.agents/skills and existing agent dirs"

# --- 4. OpenCode commands (symlinked) --------------------------------------
mkdir -p "$CMD_DIR"
for src in "$FORK"/commands/*.md; do
  [ -f "$src" ] || die "no commands found in $FORK/commands"
  name="$(basename "$src")"
  rm -f "$CMD_DIR/$name"
  ln -sfn "$src" "$CMD_DIR/$name"
done
# drop links whose source left the repo
for link in "$CMD_DIR"/*.md; do
  [ -L "$link" ] || continue
  [ -e "$link" ] || { rm -f "$link"; say "removed stale command link: $(basename "$link")"; }
done
say "commands: linked to $CMD_DIR"

# --- 5. MCP: print, never rewrite someone's config --------------------------
say ""
say "Engram is required — register it in every agent you use:"
say "  OpenCode -> ~/.config/opencode/opencode.json, under mcp.servers:"
say '    "engram": { "type": "local", "command": ["'"$HOME"'/.local/bin/engram", "mcp", "--tools=agent"], "disabled": false }'
say "  Claude Code -> claude mcp add --scope user engram -- $HOME/.local/bin/engram mcp --tools=agent"
say "  Codex -> ~/.codex/config.toml: [mcp_servers.engram] command = \"$HOME/.local/bin/engram\" / args = [\"mcp\", \"--tools=agent\"]"
say "  Gemini CLI -> ~/.gemini/settings.json, under mcpServers:"
say '    "engram": { "command": "'"$HOME"'/.local/bin/engram", "args": ["mcp", "--tools=agent"] }'
say ""
say "Odoo is optional. Without it the skills still remember decisions, they just create no cards."
say "Restart the agent afterwards, then verify by using a memory tool in a NEW session."
say "Run scripts/verify.sh in a project to check the wiring; skills and commands need no re-run after a pull."
