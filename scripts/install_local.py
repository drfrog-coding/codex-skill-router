#!/usr/bin/env python3
"""Install the skill router helper into a local Codex home."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNIPPET = ROOT / "AGENTS_SNIPPET.md"
ROUTER_SKILL = ROOT / "skills" / "skill-router"
BUILD_SCRIPT = ROOT / "scripts" / "build_skill_routing.py"


def main() -> None:
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    install_skill(codex_home)
    install_agents_snippet(codex_home)
    subprocess.run([sys.executable, str(BUILD_SCRIPT), "--codex-home", str(codex_home)], check=True)
    print(f"Installed skill router into {codex_home}")


def install_skill(codex_home: Path) -> None:
    target = codex_home / "skills" / "skill-router"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROUTER_SKILL, target)
    print(f"Installed {target}")


def install_agents_snippet(codex_home: Path) -> None:
    agents_path = codex_home / "AGENTS.md"
    snippet = SNIPPET.read_text(encoding="utf-8").strip()
    existing = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
    if "# Skill Routing" in existing:
        print(f"AGENTS snippet already present in {agents_path}")
        return
    agents_path.parent.mkdir(parents=True, exist_ok=True)
    with agents_path.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n"):
            handle.write("\n")
        if existing:
            handle.write("\n")
        handle.write(snippet)
        handle.write("\n")
    print(f"Updated {agents_path}")


if __name__ == "__main__":
    main()

