#!/usr/bin/env python3
"""Smoke tests for build_skill_routing.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_skill_routing.py"
INSTALL_SCRIPT = ROOT / "scripts" / "install_local.py"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / ".codex"
        skill = home / "skills" / "mineru-test"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            """---
name: mineru-test
description: Parse PDFs and images into Markdown.
---

# MinerU Test

## Use When

- User provides a PDF or image file.
- User asks to extract text.

## Ask User When

- The file contains private data and upload is required.
""",
            encoding="utf-8",
        )
        plugin_skill = home / "plugins" / "cache" / "personal" / "demo" / "0.1.0" / "skills" / "demo-skill"
        plugin_skill.mkdir(parents=True)
        (plugin_skill / "SKILL.md").write_text(
            """---
name: demo-skill
description: Demo plugin skill.
---

# Demo

## When To Use

- User asks for demo plugin behavior.
""",
            encoding="utf-8",
        )
        output = Path(tmp) / "routing.md"
        subprocess.run(
            [sys.executable, str(SCRIPT), "--codex-home", str(home), "--output", str(output)],
            check=True,
            cwd=ROOT,
        )
        text = output.read_text(encoding="utf-8")
        assert "### mineru-test" in text
        assert "User provides a PDF or image file." in text
        assert "### demo:demo-skill" in text
        assert str(tmp) not in text
        subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--agent",
                "all",
                "--codex-home",
                str(home),
                "--claude-home",
                str(Path(tmp) / ".claude"),
                "--openclaw-home",
                str(Path(tmp) / ".openclaw"),
                "--openclaw-workspace",
                str(Path(tmp) / ".openclaw" / "workspace"),
                "--skip-build",
            ],
            check=True,
            cwd=ROOT,
        )
        assert (home / "AGENTS.md").is_file()
        assert (Path(tmp) / ".claude" / "CLAUDE.md").is_file()
        assert (Path(tmp) / ".openclaw" / "skills" / "skill-router" / "SKILL.md").is_file()
        assert (Path(tmp) / ".openclaw" / "workspace" / "AGENTS.md").is_file()
        assert (Path(tmp) / ".openclaw" / "workspace" / "TOOLS.md").is_file()
    print("ok")


if __name__ == "__main__":
    main()
