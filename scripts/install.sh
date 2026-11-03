#!/usr/bin/env bash
# hola-ai + engram installer (Linux / macOS).
# Usage: ./scripts/install.sh
#        HOLA_AI_FORK=/path/to/clone ./scripts/install.sh
set -eu

FORK="${HOLA_AI_FORK:-$(cd "$(dirname "$0")/.." && pwd)}"
VER="${ENGRAM_VERSION:-3.6.0}"
IDS="backlog story pair archive"
AGENT_DIRS="$HOME/.claude $HOME/.gemini $HOME/.continue $HOME/.codeium/windsurf $HOME/.kiro $HOME/.config/devin"

say() { printf '%s\n' "$*"; }

# --- 1. Engram binary -------------------------------------------------------
if command -v engram >/dev/null 2>&1; then
  say "engram: already installed ($(engram version 2>/dev/null || echo unknown))"
else
  say "engram: installing $VER"
  mkdir -p "$HOME/.local/bin"
  tmp="$(mktemp -d)"
  case "$(uname -s)" in
    Linux)  asset="engram_${VER}_linux_amd64.tar.gz" ;;
    Darwin) asset="engram_${VER}_darwin_arm64.tar.gz" ;;
    *) say "engram: unsupported platform, install manually"; asset="" ;;
  esac
  if [ -n "$asset" ]; then
    base="https://github.com/Gentleman-Programming/engram/releases/download/v$VER"
    curl -fsSL -o "$tmp/$asset" "$base/$asset"
    curl -fsSL -o "$tmp/checksums.txt" "$base/checksums.txt"
    ( cd "$tmp" && grep "$asset" checksums.txt | sha256sum -c - )
    tar -xzf "$tmp/$asset" -C "$tmp"
    install -m755 "$tmp/engram" "$HOME/.local/bin/engram"
    say "engram: installed at $HOME/.local/bin/engram"
  fi
  rm -rf "$tmp"
fi

# --- 2. Skills: clone -> ~/.agents/skills -> each agent ---------------------
mkdir -p "$HOME/.agents/skills"
for id in $IDS; do
  [ -d "$FORK/skills/$id" ] || { say "skill $id missing in $FORK"; exit 1; }
  ln -sfn "$FORK/skills/$id" "$HOME/.agents/skills/$id"
  for a in $AGENT_DIRS; do
    [ -d "$a/skills" ] && ln -sfn "$HOME/.agents/skills/$id" "$a/skills/$id"
  done
done
say "skills: linked $IDS into ~/.agents/skills and existing agent dirs"

# --- 3. OpenCode commands --------------------------------------------------
mkdir -p "$HOME/.config/opencode/commands"
cp "$FORK/commands/"*.md "$HOME/.config/opencode/commands/"
say "commands: copied to ~/.config/opencode/commands"

# --- 4. MCP: print, never rewrite someone's config --------------------------
say ""
say "MCP servers (add these once per agent):"
say "  OpenCode -> ~/.config/opencode/opencode.json, under mcp.servers:"
say '    "engram": { "type": "local", "command": ["'"$HOME"'/.local/bin/engram", "mcp", "--tools=agent"], "disabled": false }'
say '    "odoo":   { "type": "local", "command": ["'"$HOME"'/tools/odoo-mcp-server/mcp.sh"], "disabled": false }'
say "  Claude Code -> claude mcp add --scope user engram -- $HOME/.local/bin/engram mcp --tools=agent"
say "  Codex -> ~/.codex/config.toml: [mcp_servers.engram] command = \"$HOME/.local/bin/engram\" / args = [\"mcp\", \"--tools=agent\"]"
say ""
say "Restart the agent afterwards. Verify by using a tool in a NEW session, not by listing servers."
say "Engram sharing: git pull -> engram sync --import ; before pushing -> engram sync"
