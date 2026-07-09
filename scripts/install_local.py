#!/usr/bin/env python3
"""Install the skill router helper for Codex, Claude Code, and OpenClaw."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_SNIPPET = ROOT / "adapters" / "codex" / "AGENTS_SNIPPET.md"
CLAUDE_SNIPPET = ROOT / "adapters" / "claude-code" / "CLAUDE_SNIPPET.md"
OPENCLAW_AGENTS_SNIPPET = ROOT / "adapters" / "openclaw" / "AGENTS_SNIPPET.md"
OPENCLAW_TOOLS_SNIPPET = ROOT / "adapters" / "openclaw" / "TOOLS_SNIPPET.md"
ROUTER_SKILL = ROOT / "skills" / "skill-router"
BUILD_SCRIPT = ROOT / "scripts" / "build_skill_routing.py"


def main() -> None:
    args = parse_args()
    agents = expand_agents(args.agent)
    codex_home = Path(args.codex_home).expanduser().resolve()
    claude_home = Path(args.claude_home).expanduser().resolve()
    openclaw_home = Path(args.openclaw_home).expanduser().resolve()
    openclaw_workspace = Path(args.openclaw_workspace).expanduser().resolve()

    if not args.skip_build:
        build_cmd = [sys.executable, str(BUILD_SCRIPT), "--codex-home", str(codex_home)]
        if "openclaw" in agents:
            build_cmd.extend(["--skill-root", str(openclaw_home / "skills")])
            build_cmd.extend(["--skill-root", str(openclaw_workspace / "skills")])
        if "claude-code" in agents:
            build_cmd.extend(["--skill-root", str(claude_home / "skills")])
        subprocess.run(build_cmd, check=True)

    if "codex" in agents:
        install_skill(codex_home / "skills" / "skill-router")
        append_snippet(codex_home / "AGENTS.md", CODEX_SNIPPET, marker="# Skill Routing")
        print(f"Installed Codex adapter into {codex_home}")

    if "claude-code" in agents:
        install_skill(claude_home / "skills" / "skill-router")
        append_snippet(claude_home / "CLAUDE.md", CLAUDE_SNIPPET, marker="# Skill Routing")
        print(f"Installed Claude Code adapter into {claude_home}")

    if "openclaw" in agents:
        install_skill(openclaw_home / "skills" / "skill-router")
        append_snippet(openclaw_workspace / "AGENTS.md", OPENCLAW_AGENTS_SNIPPET, marker="# Skill Routing")
        append_snippet(openclaw_workspace / "TOOLS.md", OPENCLAW_TOOLS_SNIPPET, marker="# Skill Routing Tools")
        print(f"Installed OpenClaw adapter into {openclaw_workspace}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        nargs="+",
        default=["codex"],
        choices=["codex", "claude-code", "openclaw", "all"],
        help="Agent adapter(s) to install. Defaults to codex.",
    )
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
    parser.add_argument("--claude-home", default=os.environ.get("CLAUDE_HOME", "~/.claude"))
    parser.add_argument("--openclaw-home", default=os.environ.get("OPENCLAW_HOME", "~/.openclaw"))
    parser.add_argument(
        "--openclaw-workspace",
        default=os.environ.get("OPENCLAW_WORKSPACE", "~/.openclaw/workspace"),
    )
    parser.add_argument("--skip-build", action="store_true")
    return parser.parse_args()


def expand_agents(values: list[str]) -> set[str]:
    if "all" in values:
        return {"codex", "claude-code", "openclaw"}
    return set(values)


def install_skill(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROUTER_SKILL, target)
    print(f"Installed {target}")


def append_snippet(target_path: Path, snippet_path: Path, *, marker: str) -> None:
    snippet = snippet_path.read_text(encoding="utf-8").strip()
    existing = target_path.read_text(encoding="utf-8") if target_path.is_file() else ""
    if marker in existing:
        print(f"Snippet already present in {target_path}")
        return
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n"):
            handle.write("\n")
        if existing:
            handle.write("\n")
        handle.write(snippet)
        handle.write("\n")
    print(f"Updated {target_path}")


if __name__ == "__main__":
    main()
