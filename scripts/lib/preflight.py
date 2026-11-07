#!/usr/bin/env python3
"""ai-daridev preflight: resolve and validate the repo configuration.

Emits the JSON contract consumed by the five skills. Exits non-zero on any inconsistency.
Only reads project.project, project.task.type and project.tags from Odoo.
"""
from __future__ import annotations

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

ENV_FILE = Path.home() / ".config" / "odoo-mcp.env"
PERSONAL_DIR = Path.home() / ".config" / "ai-daridev" / "repos"
TIMEOUT = 5


def slug(path: Path) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", path.name.lower()).strip("-")


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".engram" / "config.json").is_file():
            return p
    raise SystemExit(
        "error: not inside the repository that holds .engram/config.json\n"
        "       open the agent in that directory (or run 'engram init <project>' first)"
    )


def read_env(path: Path) -> dict:
    env: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def engram_version(binary: str) -> str:
    out = subprocess.run([binary, "version"], capture_output=True, text=True, timeout=TIMEOUT)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "engram version failed")
    return out.stdout.strip()


def odoo_resolve(cfg: dict, warnings: list) -> dict | None:
    if not cfg["odoo"]:
        return None
    if not ENV_FILE.is_file():
        warnings.append(
            "no Odoo credentials at ~/.config/odoo-mcp.env — card writes are disabled")
        return None
    env = read_env(ENV_FILE)
    for key in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD"):
        if not env.get(key):
            raise RuntimeError(f"{ENV_FILE} is missing {key}")

    socket.setdefaulttimeout(TIMEOUT)
    url, db, user, password = env["ODOO_URL"].rstrip("/"), env["ODOO_DB"], env["ODOO_USER"], env["ODOO_PASSWORD"]
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid_auth = common.authenticate(db, user, password, {})
        if not uid_auth:
            raise RuntimeError(
                f"Odoo authentication failed for {user} (credentials present but rejected)")
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

        def call(model, method, *args, **kwargs):
            return models.execute_kw(db, uid_auth, password, model, method, list(args), kwargs)

        name = cfg["odoo"]["project"]
        found = call("project.project", "search_read", [["name", "=", name]], fields=["id", "name"])
        if not found:
            raise RuntimeError(f"project '{name}' not found (exact match)")
        if len(found) > 1:
            raise RuntimeError(
                f"project '{name}' is ambiguous: " + ", ".join(f"{p['name']} ({p['id']})" for p in found))
        project = found[0]

        stages = call(
            "project.task.type", "search_read",
            [["project_ids", "in", [project["id"]]]],
            fields=["id", "name", "sequence"], order="sequence asc")
        by_name = {s["name"]: s["id"] for s in stages}
        resolved = {}
        for role, value in cfg["odoo"]["stages"].items():
            if value is None:
                resolved[role] = None
            elif role == "active":
                missing = [n for n in value if n not in by_name]
                if missing:
                    raise RuntimeError(
                        f"stage(s) {missing} not in project '{name}'; real stages: "
                        + ", ".join(s["name"] for s in stages))
                resolved[role] = [by_name[n] for n in value]
            else:
                if value not in by_name:
                    raise RuntimeError(
                        f"stage '{value}' not in project '{name}'; real stages: "
                        + ", ".join(s["name"] for s in stages))
                resolved[role] = by_name[value]

        wanted = cfg["odoo"]["tags"]
        tags = call("project.tags", "search_read", [["name", "in", wanted]], fields=["id", "name"])
        tag_map = {t["name"]: t["id"] for t in tags}
        missing = [t for t in wanted if t not in tag_map]
        if missing:
            raise RuntimeError(f"missing tag(s) {missing}; create them in Odoo first")

        return {"project": project, "stages": resolved, "tags": tag_map}
    except (socket.timeout, TimeoutError):
        warnings.append(f"Odoo did not answer within {TIMEOUT}s — card writes disabled for this run")
        return None
    except xmlrpc.client.Fault as e:
        raise RuntimeError(f"Odoo fault: {e.faultString}")
    except OSError as e:
        warnings.append(f"cannot reach Odoo ({e}) — card writes disabled for this run")
        return None


def main() -> int:
    cwd = Path.cwd()
    root = repo_root(cwd)
    errors: list[str] = []
    warnings: list[str] = []

    result: dict = {
        "ok": False,
        "repo": str(root),
        "config": {"path": str(root / "AGENTS.md"), "version": None},
        "project": None,
        "stages": None,
        "tags": None,
        "uid": None,
        "engram": {"project": None, "match": False},
        "listing": {"limit": 20, "mine_only": False},
        "plan_steps": {"min": 5, "max": 20},
        "markers": {"min": 2, "max": 4},
        "assignees": False,
        "errors": errors,
        "warnings": warnings,
    }

    try:
        cfg = block_mod.load(root / "AGENTS.md")
    except (block_mod.BlockError, FileNotFoundError) as e:
        errors.append(str(e))
        print(json.dumps(result, indent=2))
        return 1

    result["config"]["version"] = cfg["version"]
    result["listing"]["limit"] = cfg["listing_limit"]
    result["plan_steps"] = cfg["plan_steps"]
    # deprecated: kept one release so old skills/blocks keep working
    result["markers"] = cfg["markers"]
    result["assignees"] = cfg["assignees"]

    # memory project
    try:
        engram_cfg = json.loads((root / ".engram" / "config.json").read_text())
        project_name = engram_cfg.get("project_name")
    except Exception as e:  # noqa: BLE001
        errors.append(f"cannot read .engram/config.json: {e}")
        project_name = None
    result["engram"]["project"] = project_name
    result["engram"]["match"] = bool(project_name) and project_name == cfg["engram_project"]
    if project_name and not result["engram"]["match"]:
        errors.append(
            f"engram project is '{project_name}' but AGENTS.md says '{cfg['engram_project']}'")

    # engram binary
    binary = os.environ.get("ENGRAM_BIN") or str(Path.home() / ".local/bin/engram")
    try:
        result["engram"]["version"] = engram_version(binary)
    except Exception as e:  # noqa: BLE001
        errors.append(f"engram is not runnable at {binary}: {e}")

    # Import pending chunks (best effort) and detect a stale export.
    if result["engram"]["version"]:
        try:
            subprocess.run([binary, "sync", "--import"], cwd=root, capture_output=True,
                           text=True, timeout=20, check=False)
        except Exception as e:  # noqa: BLE001
            warnings.append(f"could not import memory chunks: {e}")
        manifest = root / ".engram" / "manifest.json"
        if not manifest.is_file():
            try:
                st = subprocess.run([binary, "sync", "--status"], cwd=root, capture_output=True,
                                    text=True, timeout=20, check=False)
                m = re.search(r"Local chunks:\s*(\d+)", st.stdout)
                if m and int(m.group(1)) > 0:
                    warnings.append(
                        f"{m.group(1)} chunks recorded but .engram/ is empty — run 'engram sync'")
            except Exception:  # noqa: BLE001
                pass

    # personal uid
    personal = PERSONAL_DIR / f"{slug(root)}.json"
    if personal.is_file():
        try:
            data = json.loads(personal.read_text())
            uid = data.get("odoo_uid")
            if uid is not None and not isinstance(uid, int):
                errors.append(f"{personal}: odoo_uid must be an integer")
            else:
                result["uid"] = uid
        except Exception as e:  # noqa: BLE001
            errors.append(f"cannot read {personal}: {e}")
    if result["uid"] is None:
        warnings.append("no personal odoo_uid — 'mine' is not marked in listings (ai-daridev uid <n>)")

    # odoo
    try:
        resolved = odoo_resolve(cfg, warnings)
        if resolved:
            result["project"] = resolved["project"]
            result["stages"] = resolved["stages"]
            result["tags"] = resolved["tags"]
    except RuntimeError as e:
        errors.append(str(e))

    result["ok"] = not errors
    print(json.dumps(result, indent=2))
    if errors:
        print("\npreflight failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("  fix the configuration (ai-daridev init) and run preflight again", file=sys.stderr)
    else:
        summary = [f"repo {root.name}"]
        if result["project"]:
            summary.append(f"project {result['project']['name']} ({result['project']['id']})")
            summary.append("stages ok")
        if result["uid"] is not None:
            summary.append(f"uid {result['uid']}")
        print(" · ".join(summary), file=sys.stderr)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
