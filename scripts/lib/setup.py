#!/usr/bin/env python3
"""ai-daridev setup: machine setup. Idempotent, with timestamped backups.

- Engram, skills and commands are handled by scripts/install.sh.
- MCP entries are applied here (Engram always; Odoo only when a wrapper and its env file exist).
- The ai-daridev instruction block is written into the four agent instruction files.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
ENGRAM = HOME / ".local" / "bin" / "engram"
ODOO_WRAPPER = HOME / "tools" / "odoo-mcp-server" / "mcp.sh"
ODOO_ENV = HOME / ".config" / "odoo-mcp.env"
STAMP = time.strftime("%Y%m%d%H%M%S")

OPENCODE = HOME / ".config" / "opencode" / "opencode.json"
CODEX = HOME / ".codex" / "config.toml"
GEMINI = HOME / ".gemini" / "settings.json"
INSTRUCTIONS = [
    HOME / ".config" / "opencode" / "AGENTS.md",
    HOME / ".claude" / "CLAUDE.md",
    HOME / ".gemini" / "GEMINI.md",
    HOME / ".codex" / "AGENTS.md",
]

BLOCK = """<!-- ai-daridev -->
Work is tracked with the `ai-daridev` skills (installed globally, invoked manually):
backlog → story → pair → review → archive. In a repo whose `AGENTS.md` has a
`<!-- ai-daridev:start -->` block, run `ai-daridev preflight` first and use its JSON; if it exits
non-zero, print its errors and stop. Engram is required; Odoo is optional. Never move Odoo cards
between columns, never mark cards done or cancelled, never set assignees. Plan steps are validated
with `1_done` (dropped steps use `1_canceled`); structure changes ask once, state changes do not.
The Engram store is global (`~/.engram/engram.db`); exported chunks live in
`.engram/` and are committed at each checkpoint as `chore: memory — …`. `ai-daridev preflight`
imports pending chunks before every skill; never hand-edit a chunk.
<!-- ai-daridev -->"""


def run(cmd: list[str], dry: bool) -> int:
    print("+ " + " ".join(cmd))
    if dry:
        return 0
    return subprocess.call(cmd)


def backup(path: Path, dry: bool) -> Path | None:
    if not path.exists():
        return None
    dest = path.with_name(f"{path.name}.bak.{STAMP}")
    print(f"  backup {path} -> {dest.name}")
    if not dry:
        shutil.copy2(path, dest)
    return dest


def scan_object(text: str, open_idx: int) -> int:
    """Return the index of the brace closing the object that starts at open_idx."""
    depth, i, in_str, esc = 0, open_idx, False, False
    while i < len(text):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise ValueError("unbalanced JSON object")


def apply_opencode(dry: bool) -> str:
    if not OPENCODE.is_file():
        return "opencode: config not found — skipped"
    text = OPENCODE.read_text(encoding="utf-8")
    entries = {
        "engram": {"type": "local", "command": [str(ENGRAM), "mcp", "--tools=agent"], "disabled": False},
    }
    if ODOO_WRAPPER.is_file() and ODOO_ENV.is_file():
        entries["odoo"] = {"type": "local", "command": [str(ODOO_WRAPPER)], "disabled": False}

    m = re.search(r'"servers"\s*:\s*\{', text)
    if not m:
        return "opencode: no mcp.servers object — add the snippet manually"
    open_idx = text.index("{", m.start())
    close_idx = scan_object(text, open_idx)
    body = text[open_idx:close_idx]
    additions = []
    empty = not body.strip()
    for name, entry in entries.items():
        if re.search(rf'"{name}"\s*:', body):
            continue
        sep = "" if (empty and not additions) else ","
        additions.append(f'\n      "{name}": {json.dumps(entry)}{sep}')
        empty = False
    if not additions:
        return "opencode: engram already registered"
    backup(OPENCODE, dry)
    new = text[:open_idx + 1] + "".join(additions) + text[open_idx + 1:]
    if not dry:
        OPENCODE.write_text(new, encoding="utf-8")
    return "opencode: " + ", ".join(entries)


def apply_claude(dry: bool) -> str:
    if not shutil.which("claude"):
        return "claude: CLI not found — skipped"
    run(["claude", "mcp", "remove", "--scope", "user", "engram"], dry)
    run(["claude", "mcp", "add", "--scope", "user", "engram", "--",
         str(ENGRAM), "mcp", "--tools=agent"], dry)
    if ODOO_WRAPPER.is_file() and ODOO_ENV.is_file():
        run(["claude", "mcp", "remove", "--scope", "user", "odoo"], dry)
        run(["claude", "mcp", "add", "--scope", "user", "odoo", "--", str(ODOO_WRAPPER)], dry)
    return "claude: registered"


def apply_codex(dry: bool) -> str:
    if not CODEX.is_file():
        return "codex: config not found — skipped"
    text = CODEX.read_text(encoding="utf-8")
    blocks = {
        "engram": f'[mcp_servers.engram]\ncommand = "{ENGRAM}"\nargs = ["mcp", "--tools=agent"]\n',
    }
    if ODOO_WRAPPER.is_file() and ODOO_ENV.is_file():
        blocks["odoo"] = f'[mcp_servers.odoo]\ncommand = "{ODOO_WRAPPER}"\n'
    changed = False
    for name, block in blocks.items():
        pattern = re.compile(rf"^\[mcp_servers\.{name}\]\n(?:.*\n)*?(?=^\[|\Z)", re.M)
        if pattern.search(text):
            new = pattern.sub(block + "\n", text)
        else:
            new = text.rstrip() + "\n\n" + block
        if new != text:
            changed = True
            text = new
    if changed:
        backup(CODEX, dry)
        if not dry:
            CODEX.write_text(text, encoding="utf-8")
        return "codex: registered"
    return "codex: already registered"


def apply_gemini(dry: bool) -> str:
    if not GEMINI.is_file():
        return "gemini: settings not found — skipped"
    try:
        data = json.loads(GEMINI.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return "gemini: settings.json is not valid JSON — skipped"
    servers = data.setdefault("mcpServers", {})
    entry = {"command": str(ENGRAM), "args": ["mcp", "--tools=agent"]}
    if ODOO_WRAPPER.is_file() and ODOO_ENV.is_file():
        servers.setdefault("odoo", {"command": str(ODOO_WRAPPER)})
    if servers.get("engram") == entry:
        return "gemini: already registered"
    servers["engram"] = entry
    backup(GEMINI, dry)
    if not dry:
        GEMINI.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return "gemini: registered"


def apply_instructions(dry: bool) -> list[str]:
    done = []
    for path in INSTRUCTIONS:
        if not path.is_file():
            done.append(f"{path}: missing — skipped")
            continue
        text = path.read_text(encoding="utf-8")
        if "<!-- ai-daridev -->" in text and text.count("<!-- ai-daridev -->") >= 2:
            head, rest = text.split("<!-- ai-daridev -->", 1)
            _, tail = rest.split("<!-- ai-daridev -->", 1)
            new = head + BLOCK + tail
        else:
            new = text.rstrip() + "\n\n" + BLOCK + "\n"
        if new == text:
            done.append(f"{path}: up to date")
            continue
        backup(path, dry)
        if not dry:
            path.write_text(new, encoding="utf-8")
        done.append(f"{path}: block written")
    return done


def restore(dry: bool) -> int:
    targets = [OPENCODE, CODEX, GEMINI, *INSTRUCTIONS]
    restored = 0
    for path in targets:
        candidates = sorted(path.parent.glob(f"{path.name}.bak.*"))
        if not candidates:
            continue
        latest = candidates[-1]
        print(f"restore {path} <- {latest.name}")
        if not dry:
            shutil.copy2(latest, path)
        restored += 1
    if not restored:
        print("nothing to restore")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="ai-daridev setup")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--print", dest="print_only", action="store_true")
    ap.add_argument("--restore", action="store_true")
    args = ap.parse_args()

    if args.restore:
        return restore(args.dry_run)

    fork = Path(__file__).resolve().parents[2]
    if args.print_only:
        print(BLOCK)
        print(f"\nengram: {ENGRAM} mcp --tools=agent")
        return 0

    install = str(fork / "scripts" / "install.sh")
    if args.dry_run:
        print(f"+ {install} (skipped in dry-run)")
    elif subprocess.call([install]) != 0:
        print("error: install.sh failed", file=sys.stderr)
        return 1

    running = subprocess.run(["pgrep", "-x", "opencode"], capture_output=True, text=True).returncode == 0
    if running:
        print("warning: OpenCode is running — it may rewrite its config on exit; re-run setup after closing it")

    for fn in (apply_opencode, apply_claude, apply_codex, apply_gemini):
        print(fn(args.dry_run))
    for line in apply_instructions(args.dry_run):
        print(line)

    print("\nrestart the agents and run: ai-daridev doctor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
