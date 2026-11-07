#!/usr/bin/env python3
"""ai-daridev init: write the shared AGENTS.md block and the personal uid file.

Owner-only: detecting stages and tags needs Odoo credentials. Teammates inherit the committed
block and only need `ai-daridev uid <n>`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import block as block_mod  # noqa: E402
import preflight as pf  # noqa: E402

DEFAULT_TAGS = ["frontend", "backend", "script", "workflow"]


def call_models(env: dict):
    socket.setdefaulttimeout(pf.TIMEOUT)
    url, db = env["ODOO_URL"].rstrip("/"), env["ODOO_DB"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, env["ODOO_USER"], env["ODOO_PASSWORD"], {})
    if not uid:
        raise SystemExit("error: Odoo authentication failed; check ~/.config/odoo-mcp.env")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

    def call(model, method, *args, **kwargs):
        return models.execute_kw(db, uid, env["ODOO_PASSWORD"], model, method, list(args), kwargs)

    return call


def pick_stages(stages: list) -> dict:
    names = [s["name"] for s in stages]

    def find(patterns, default):
        for s in stages:
            if any(p in s["name"].lower() for p in patterns):
                return s["name"]
        return default

    backlog = find(["backlog"], names[0])
    done = find(["complete", "done", "closed"], names[-1])
    cancelled = find(["cancel"], None)
    order = [s["name"] for s in stages]
    i_backlog, i_done = order.index(backlog), order.index(done)
    active = order[i_backlog + 1:i_done] or [order[i_done]] if len(order) > 1 else [backlog]
    return {"backlog": backlog, "active": active, "done": done, "cancelled": cancelled}


def render_block(cfg: dict) -> str:
    lines = [block_mod.START, "## Workflow config", "- version: 1"]
    if cfg["odoo"]:
        o = cfg["odoo"]
        lines += [
            f"- odoo_project: {o['project']}",
            f"- odoo_stage_backlog: {o['stages']['backlog']}",
            f"- odoo_stage_active: {', '.join(o['stages']['active'])}",
            f"- odoo_stage_done: {o['stages']['done']}",
        ]
        if o["stages"].get("cancelled"):
            lines.append(f"- odoo_stage_cancelled: {o['stages']['cancelled']}")
        lines += [
            f"- odoo_assignees: {'true' if o.get('assignees') else 'false'}",
            f"- card_tag: {o['tag_default']}",
            f"- card_tags: {', '.join(o['tags'])}",
        ]
    lines += [
        f"- engram_project: {cfg['engram_project']}",
        f"- decisions_dir: {cfg['decisions_dir']}",
        f"- plan_steps: {cfg['plan_steps']['min']}-{cfg['plan_steps']['max']}",
        f"- listing_limit: {cfg['listing_limit']}",
        block_mod.END,
    ]
    return "\n".join(lines)


def write_block(agents: Path, rendered: str, force: bool) -> bool:
    text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    if block_mod.START in text and block_mod.END in text:
        new = text.split(block_mod.START)[0] + rendered + text.split(block_mod.END, 1)[1]
    elif "## Workflow config" in text:
        # migrate the pre-marker section written by an earlier version
        head, rest = text.split("## Workflow config", 1)
        m = re.search(r"\n## ", rest)
        tail = rest[m.start():] if m else ""
        new = head.rstrip() + "\n\n" + rendered + "\n" + tail
    else:
        new = (text.rstrip() + "\n\n" if text.strip() else "") + rendered + "\n"
    if new == text:
        print("AGENTS.md: already up to date")
        return False
    if agents.is_file() and block_mod.START in text and not force:
        import difflib
        diff = "".join(difflib.unified_diff(
            text.splitlines(True), new.splitlines(True), "AGENTS.md (current)", "AGENTS.md (proposed)"))
        print(diff)
        print("\nrefusing to overwrite an existing block without --force", file=sys.stderr)
        raise SystemExit(2)
    agents.write_text(new, encoding="utf-8")
    print(f"AGENTS.md: block written ({agents})")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(prog="ai-daridev init")
    ap.add_argument("--project")
    ap.add_argument("--uid", type=int)
    ap.add_argument("--no-odoo", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pf.repo_root(Path.cwd())
    agents = root / "AGENTS.md"
    cfg: dict = {
        "version": 1, "odoo": None,
        "engram_project": None, "decisions_dir": "docs/decisions",
        "listing_limit": 20, "plan_steps": {"min": 5, "max": 20}, "assignees": False,
    }

    # memory project
    engram_cfg = root / ".engram" / "config.json"
    if engram_cfg.is_file():
        cfg["engram_project"] = json.loads(engram_cfg.read_text()).get("project_name")
    else:
        print("error: no .engram/config.json; run 'engram init <project>' first", file=sys.stderr)
        return 1

    if not args.no_odoo:
        if not pf.ENV_FILE.is_file():
            return _fail("init needs Odoo credentials (owner-only). Teammates: ai-daridev uid <n>")
        env = pf.read_env(pf.ENV_FILE)
        call = call_models(env)
        project_name = args.project
        if not project_name:
            project_name = input("Odoo project name (blank to skip Odoo): ").strip()
        if project_name:
            found = call("project.project", "search_read", [["name", "=", project_name]], fields=["id", "name"])
            if not found:
                return _fail(f"project '{project_name}' not found (exact match)")
            if len(found) > 1:
                return _fail("ambiguous project: " + ", ".join(p["name"] for p in found))
            stages = call("project.task.type", "search_read",
                          [["project_ids", "in", [found[0]["id"]]]],
                          fields=["id", "name", "sequence"], order="sequence asc")
            picked = pick_stages(stages)
            tags = call("project.tags", "search_read", [["name", "in", DEFAULT_TAGS]], fields=["id", "name"])
            have = {t["name"] for t in tags}
            missing = [t for t in DEFAULT_TAGS if t not in have]
            if missing:
                print(f"warning: missing global tags {missing}; create them in Odoo or preflight will fail")
            tag_default = args.tag or ("workflow" if "workflow" in have else "backend")
            cfg["odoo"] = {
                "project": project_name,
                "stages": picked,
                "tag_default": tag_default,
                "tags": [t for t in DEFAULT_TAGS if t in have] or DEFAULT_TAGS,
                "assignees": False,
            }

    rendered = render_block(cfg)
    if args.dry_run:
        print(rendered)
        return 0
    changed = write_block(agents, rendered, args.force)
    if changed:
        print("next: ai-daridev preflight")

    # personal uid
    uid = args.uid
    if uid is None and not args.no_odoo:
        raw = input("Your Odoo uid (blank = unassigned): ").strip()
        uid = int(raw) if raw.isdigit() else None
    if uid is not None:
        pf.PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
        personal = pf.PERSONAL_DIR / f"{pf.slug(root)}.json"
        personal.write_text(json.dumps({"repo": str(root), "odoo_uid": uid}, indent=2) + "\n")
        os.chmod(personal, 0o600)
        print(f"personal: {personal} (odoo_uid {uid})")

    (root / cfg["decisions_dir"]).mkdir(parents=True, exist_ok=True)
    return 0


def _fail(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
