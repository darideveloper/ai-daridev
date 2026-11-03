#!/usr/bin/env python3
"""ai-daridev uid: set your personal Odoo uid for this repo (never committed)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight as pf  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].lstrip("-").isdigit():
        print("usage: ai-daridev uid <n>", file=sys.stderr)
        return 2
    root = pf.repo_root(Path.cwd())
    pf.PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
    path = pf.PERSONAL_DIR / f"{pf.slug(root)}.json"
    data = {"repo": str(root), "odoo_uid": int(sys.argv[1])}
    path.write_text(json.dumps(data, indent=2) + "\n")
    os.chmod(path, 0o600)
    print(f"{path}: odoo_uid {data['odoo_uid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
