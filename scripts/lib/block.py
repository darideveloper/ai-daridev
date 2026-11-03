#!/usr/bin/env python3
"""Strict parser for the ai-daridev block in AGENTS.md.

The block is the only configuration. It never contains IDs, never contains personal data,
and a malformed block is an error, never a guess.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

START = "<!-- ai-daridev:start -->"
END = "<!-- ai-daridev:end -->"

REQUIRED = {"version", "engram_project"}
KNOWN = {
    "version", "odoo_project",
    "odoo_stage_backlog", "odoo_stage_active", "odoo_stage_done", "odoo_stage_cancelled",
    "odoo_assignees", "card_tag", "card_tags",
    "engram_project", "decisions_dir", "markers", "listing_limit",
}
ODOO_REQUIRED = {"odoo_stage_backlog", "odoo_stage_active", "odoo_stage_done", "card_tag"}
PLACEHOLDER = re.compile(r"<[^>]*>|one of\b", re.I)
DEFAULT_TAGS = ["frontend", "backend", "script", "workflow"]


class BlockError(Exception):
    def __init__(self, message: str, line: int | None = None):
        self.line = line
        self.message = message
        super().__init__(f"AGENTS.md line {line}: {message}" if line else message)


def find_block(text: str) -> str:
    if START not in text or END not in text:
        raise BlockError(f"missing '{START}' … '{END}' block")
    body = text.split(START, 1)[1].split(END, 1)[0]
    return body


def parse(text: str) -> dict:
    body = find_block(text)
    raw: dict[str, str] = {}
    for idx, line in enumerate(body.splitlines(), start=1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^-?\s*([a-z_]+)\s*:\s*(.*)$", s)
        if not m:
            raise BlockError(f"cannot parse '{s}' (expected '- key: value')", idx)
        key, value = m.group(1), m.group(2).strip()
        if key in raw:
            raise BlockError(f"duplicate key '{key}'", idx)
        if key == "odoo_uid":
            raise BlockError(
                "odoo_uid is personal and must not be committed; "
                f"run 'ai-daridev uid <n>' (stored in ~/.config/ai-daridev/repos/)", idx)
        if key not in KNOWN:
            raise BlockError(f"unknown key '{key}'", idx)
        if PLACEHOLDER.search(value):
            raise BlockError(f"'{key}' still contains a placeholder: {value!r}", idx)
        raw[key] = value

    missing = REQUIRED - raw.keys()
    if missing:
        raise BlockError("missing required key(s): " + ", ".join(sorted(missing)))

    if raw["version"] != "1":
        raise BlockError(f"unsupported version {raw['version']!r} (expected 1)")

    odoo = bool(raw.get("odoo_project"))
    if odoo:
        missing = ODOO_REQUIRED - raw.keys()
        if missing:
            raise BlockError("odoo_project is set but missing: " + ", ".join(sorted(missing)))

    cfg: dict = {
        "version": 1,
        "odoo": None,
        "engram_project": raw["engram_project"],
        "decisions_dir": raw.get("decisions_dir", "docs/decisions"),
        "listing_limit": 20,
        "markers": {"min": 2, "max": 4},
        "assignees": False,
    }

    if "listing_limit" in raw:
        try:
            cfg["listing_limit"] = int(raw["listing_limit"])
        except ValueError:
            raise BlockError(f"listing_limit must be an integer, got {raw['listing_limit']!r}")
        if cfg["listing_limit"] <= 0:
            raise BlockError("listing_limit must be > 0")

    if "markers" in raw:
        m = re.fullmatch(r"(\d+)-(\d+)", raw["markers"])
        if not m:
            raise BlockError(f"markers must look like 2-4, got {raw['markers']!r}")
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo < 1 or hi < lo:
            raise BlockError(f"markers range is invalid: {raw['markers']!r}")
        cfg["markers"] = {"min": lo, "max": hi}

    if odoo:
        tags = [t.strip() for t in raw.get("card_tags", ",".join(DEFAULT_TAGS)).split(",") if t.strip()]
        if not tags:
            raise BlockError("card_tags cannot be empty")
        if raw["card_tag"] not in tags:
            raise BlockError(f"card_tag {raw['card_tag']!r} is not in card_tags {tags}")
        active = [s.strip() for s in raw["odoo_stage_active"].split(",") if s.strip()]
        if not active:
            raise BlockError("odoo_stage_active cannot be empty")
        assignees = raw.get("odoo_assignees", "false").strip().lower()
        if assignees not in {"true", "false"}:
            raise BlockError(f"odoo_assignees must be true or false, got {raw['odoo_assignees']!r}")
        cfg["assignees"] = assignees == "true"
        cfg["odoo"] = {
            "project": raw["odoo_project"],
            "stages": {
                "backlog": raw["odoo_stage_backlog"],
                "active": active,
                "done": raw["odoo_stage_done"],
                "cancelled": raw.get("odoo_stage_cancelled"),
            },
            "tag_default": raw["card_tag"],
            "tags": tags,
        }
    return cfg


def load(path: Path) -> dict:
    return parse(path.read_text(encoding="utf-8"))


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("AGENTS.md")
    try:
        print(json.dumps(load(path), indent=2))
        return 0
    except (BlockError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
