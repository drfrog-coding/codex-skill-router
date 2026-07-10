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
        project = Path(tmp) / "project"
        project.mkdir()
        subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--list-agents",
                "--codex-home",
                str(home),
                "--claude-home",
                str(Path(tmp) / ".claude"),
                "--openclaw-home",
                str(Path(tmp) / ".openclaw"),
                "--openclaw-workspace",
                str(Path(tmp) / ".openclaw" / "workspace"),
                "--gemini-home",
                str(Path(tmp) / ".gemini"),
                "--opencode-home",
                str(Path(tmp) / ".config" / "opencode"),
                "--cline-rules-home",
                str(Path(tmp) / "Documents" / "Cline" / "Rules"),
                "--roo-home",
                str(Path(tmp) / ".roo"),
                "--project-root",
                str(project),
                "--skip-build",
            ],
            check=True,
            cwd=ROOT,
        )
        project_adapter_without_marker = subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--agent",
                "cursor",
                "--skip-build",
            ],
            cwd=project,
            text=True,
            capture_output=True,
        )
        assert project_adapter_without_marker.returncode != 0
        assert "requires --project-root" in (
            project_adapter_without_marker.stdout + project_adapter_without_marker.stderr
        )
        subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--agent",
                "all-known",
                "--codex-home",
                str(home),
                "--claude-home",
                str(Path(tmp) / ".claude"),
                "--openclaw-home",
                str(Path(tmp) / ".openclaw"),
                "--openclaw-workspace",
                str(Path(tmp) / ".openclaw" / "workspace"),
                "--gemini-home",
                str(Path(tmp) / ".gemini"),
                "--opencode-home",
                str(Path(tmp) / ".config" / "opencode"),
                "--cline-rules-home",
                str(Path(tmp) / "Documents" / "Cline" / "Rules"),
                "--roo-home",
                str(Path(tmp) / ".roo"),
                "--project-root",
                str(project),
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
        assert (Path(tmp) / ".gemini" / "GEMINI.md").is_file()
        assert (Path(tmp) / ".config" / "opencode" / "AGENTS.md").is_file()
        assert (Path(tmp) / ".config" / "opencode" / "skills" / "skill-router" / "SKILL.md").is_file()
        assert (Path(tmp) / "Documents" / "Cline" / "Rules" / "skill-routing.md").is_file()
        assert (Path(tmp) / ".roo" / "rules" / "skill-routing.md").is_file()
        assert (project / ".clinerules" / "00-skill-routing.md").is_file()
        assert (project / ".roo" / "rules" / "00-skill-routing.md").is_file()
        assert (project / ".cursor" / "rules" / "skill-routing.mdc").is_file()
        assert (project / ".continue" / "rules" / "00-skill-routing.md").is_file()
        assert (project / "CONVENTIONS.md").is_file()
        assert (project / ".devin" / "rules" / "00-skill-routing.md").is_file()
    print("ok")


if __name__ == "__main__":
    main()
