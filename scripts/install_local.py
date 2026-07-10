#!/usr/bin/env python3
"""Install skill-routing adapters for Codex and other agent tools."""

from __future__ import annotations

import argparse
import dataclasses
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER_SKILL = ROOT / "skills" / "skill-router"
BUILD_SCRIPT = ROOT / "scripts" / "build_skill_routing.py"

SNIPPETS = {
    "codex": ROOT / "adapters" / "codex" / "AGENTS_SNIPPET.md",
    "claude-code": ROOT / "adapters" / "claude-code" / "CLAUDE_SNIPPET.md",
    "openclaw-agents": ROOT / "adapters" / "openclaw" / "AGENTS_SNIPPET.md",
    "openclaw-tools": ROOT / "adapters" / "openclaw" / "TOOLS_SNIPPET.md",
    "gemini-cli": ROOT / "adapters" / "gemini-cli" / "GEMINI_SNIPPET.md",
    "opencode": ROOT / "adapters" / "opencode" / "AGENTS_SNIPPET.md",
    "cline": ROOT / "adapters" / "cline" / "skill-routing.md",
    "roo-code": ROOT / "adapters" / "roo-code" / "skill-routing.md",
    "cursor": ROOT / "adapters" / "cursor" / "skill-routing.mdc",
    "continue": ROOT / "adapters" / "continue" / "skill-routing.md",
    "aider": ROOT / "adapters" / "aider" / "CONVENTIONS_SNIPPET.md",
    "windsurf": ROOT / "adapters" / "windsurf" / "WINDSURF_SNIPPET.md",
}


@dataclasses.dataclass(frozen=True)
class Adapter:
    name: str
    scope: str
    description: str
    detect: Callable[["InstallContext"], bool]
    install: Callable[["InstallContext"], None]
    skill_roots: Callable[["InstallContext"], list[Path]] = lambda _ctx: []


@dataclasses.dataclass(frozen=True)
class InstallContext:
    codex_home: Path
    claude_home: Path
    openclaw_home: Path
    openclaw_workspace: Path
    gemini_home: Path
    opencode_home: Path
    cline_rules_home: Path
    roo_home: Path
    project_root: Path | None
    explicit_project_root: bool


def main() -> None:
    args = parse_args()
    context = build_context(args)
    adapters = build_adapters()

    if args.list_agents:
        list_agents(adapters, context)
        return

    selected = select_adapters(args.agent, adapters, context)
    if not selected:
        print("No adapters selected. Use --agent codex, --agent auto, or --list-agents.")
        return

    for adapter in selected:
        adapter.install(context)

    if not args.skip_build:
        build_routing_index(context, selected)

    print("Selected adapters: " + ", ".join(adapter.name for adapter in selected))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        nargs="+",
        default=["auto"],
        choices=[
            "auto",
            "all",
            "all-known",
            "codex",
            "claude-code",
            "openclaw",
            "gemini-cli",
            "opencode",
            "cline",
            "cline-project",
            "roo-code",
            "roo-code-project",
            "cursor",
            "continue",
            "aider",
            "windsurf",
        ],
        help=(
            "Agent adapter(s) to install. Defaults to auto, which detects installed "
            "tools and existing project rule directories."
        ),
    )
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
    parser.add_argument("--claude-home", default=os.environ.get("CLAUDE_HOME", "~/.claude"))
    parser.add_argument("--openclaw-home", default=os.environ.get("OPENCLAW_HOME", "~/.openclaw"))
    parser.add_argument(
        "--openclaw-workspace",
        default=os.environ.get("OPENCLAW_WORKSPACE", "~/.openclaw/workspace"),
    )
    parser.add_argument("--gemini-home", default=os.environ.get("GEMINI_HOME", "~/.gemini"))
    parser.add_argument(
        "--opencode-home",
        default=os.environ.get("OPENCODE_HOME", "~/.config/opencode"),
    )
    parser.add_argument(
        "--cline-rules-home",
        default=os.environ.get("CLINE_RULES_HOME", "~/Documents/Cline/Rules"),
    )
    parser.add_argument("--roo-home", default=os.environ.get("ROO_HOME", "~/.roo"))
    parser.add_argument(
        "--project-root",
        help=(
            "Project root for project-scoped adapters such as Cursor, Continue, "
            "aider, Windsurf, Cline project rules, and Roo Code project rules."
        ),
    )
    parser.add_argument("--list-agents", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    return parser.parse_args()


def build_context(args: argparse.Namespace) -> InstallContext:
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()
    return InstallContext(
        codex_home=expand(args.codex_home),
        claude_home=expand(args.claude_home),
        openclaw_home=expand(args.openclaw_home),
        openclaw_workspace=expand(args.openclaw_workspace),
        gemini_home=expand(args.gemini_home),
        opencode_home=expand(args.opencode_home),
        cline_rules_home=expand(args.cline_rules_home),
        roo_home=expand(args.roo_home),
        project_root=project_root,
        explicit_project_root=bool(args.project_root),
    )


def expand(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_adapters() -> dict[str, Adapter]:
    adapters = [
        Adapter(
            name="codex",
            scope="global",
            description="Codex global AGENTS.md and ~/.codex/skills.",
            detect=lambda ctx: ctx.codex_home.exists() or command_exists("codex"),
            install=install_codex,
            skill_roots=lambda ctx: [ctx.codex_home / "skills"],
        ),
        Adapter(
            name="claude-code",
            scope="global",
            description="Claude Code ~/.claude/CLAUDE.md and ~/.claude/skills.",
            detect=lambda ctx: ctx.claude_home.exists() or command_exists("claude"),
            install=install_claude,
            skill_roots=lambda ctx: [ctx.claude_home / "skills"],
        ),
        Adapter(
            name="openclaw",
            scope="global",
            description="OpenClaw workspace AGENTS.md/TOOLS.md and personal skills.",
            detect=lambda ctx: (
                ctx.openclaw_home.exists()
                or ctx.openclaw_workspace.exists()
                or command_exists("openclaw")
            ),
            install=install_openclaw,
            skill_roots=lambda ctx: [
                ctx.openclaw_home / "skills",
                ctx.openclaw_workspace / "skills",
            ],
        ),
        Adapter(
            name="gemini-cli",
            scope="global",
            description="Gemini CLI ~/.gemini/GEMINI.md context.",
            detect=lambda ctx: ctx.gemini_home.exists() or command_exists("gemini"),
            install=install_gemini,
        ),
        Adapter(
            name="opencode",
            scope="global",
            description="OpenCode ~/.config/opencode/AGENTS.md and native skills.",
            detect=lambda ctx: ctx.opencode_home.exists() or command_exists("opencode"),
            install=install_opencode,
            skill_roots=lambda ctx: [ctx.opencode_home / "skills"],
        ),
        Adapter(
            name="cline",
            scope="global",
            description="Cline global rules directory.",
            detect=lambda ctx: ctx.cline_rules_home.exists() or command_exists("cline"),
            install=install_cline_global,
        ),
        Adapter(
            name="roo-code",
            scope="global",
            description="Roo Code global rules directory.",
            detect=lambda ctx: (
                ctx.roo_home.exists() or command_exists("roo") or command_exists("roo-code")
            ),
            install=install_roo_global,
        ),
        Adapter(
            name="cline-project",
            scope="project",
            description="Cline project .clinerules directory.",
            detect=lambda ctx: project_marker(ctx, ".clinerules"),
            install=install_cline_project,
        ),
        Adapter(
            name="roo-code-project",
            scope="project",
            description="Roo Code project .roo/rules directory.",
            detect=lambda ctx: project_marker(ctx, ".roo") or project_marker(ctx, ".roorules"),
            install=install_roo_project,
        ),
        Adapter(
            name="cursor",
            scope="project",
            description="Cursor project .cursor/rules directory.",
            detect=lambda ctx: project_marker(ctx, ".cursor") or project_marker(ctx, ".cursorrules"),
            install=install_cursor,
        ),
        Adapter(
            name="continue",
            scope="project",
            description="Continue project .continue/rules directory.",
            detect=lambda ctx: project_marker(ctx, ".continue"),
            install=install_continue,
        ),
        Adapter(
            name="aider",
            scope="project",
            description="aider project CONVENTIONS.md.",
            detect=lambda ctx: (
                project_marker(ctx, "CONVENTIONS.md") or project_marker(ctx, ".aider.conf.yml")
            ),
            install=install_aider,
        ),
        Adapter(
            name="windsurf",
            scope="project",
            description="Windsurf/Devin Cascade project rules.",
            detect=lambda ctx: (
                project_marker(ctx, ".devin")
                or project_marker(ctx, ".windsurf")
                or project_marker(ctx, ".windsurfrules")
            ),
            install=install_windsurf,
        ),
    ]
    return {adapter.name: adapter for adapter in adapters}


def select_adapters(
    requested: list[str],
    adapters: dict[str, Adapter],
    context: InstallContext,
) -> list[Adapter]:
    requested_set = set(requested)
    if "all" in requested_set:
        print("--agent all is kept as an alias for --agent all-known.")
        requested_set.add("all-known")

    if "auto" in requested_set:
        return [
            adapter
            for adapter in adapters.values()
            if adapter.detect(context) and project_scope_allowed(adapter, context, explicit=False)
        ]

    if "all-known" in requested_set:
        return [
            adapter
            for adapter in adapters.values()
            if adapter.scope != "project" or context.explicit_project_root
        ]

    selected: list[Adapter] = []
    for name in requested:
        if name in {"all", "all-known", "auto"}:
            continue
        adapter = adapters[name]
        if (
            adapter.scope == "project"
            and not context.explicit_project_root
            and not adapter.detect(context)
        ):
            raise SystemExit(
                f"{name} requires --project-root unless the current project already has its marker."
            )
        selected.append(adapter)
    return selected


def project_scope_allowed(adapter: Adapter, context: InstallContext, *, explicit: bool) -> bool:
    if adapter.scope != "project":
        return True
    return explicit or adapter.detect(context)


def list_agents(adapters: dict[str, Adapter], context: InstallContext) -> None:
    print("Supported adapters:")
    for adapter in adapters.values():
        detected = adapter.detect(context)
        marker = "yes" if detected else "no"
        print(f"- {adapter.name:17} scope={adapter.scope:7} detected={marker:3} {adapter.description}")


def build_routing_index(context: InstallContext, selected: list[Adapter]) -> None:
    build_cmd = [sys.executable, str(BUILD_SCRIPT), "--codex-home", str(context.codex_home)]
    seen: set[Path] = set()
    for adapter in selected:
        for root in adapter.skill_roots(context):
            if root in seen:
                continue
            seen.add(root)
            build_cmd.extend(["--skill-root", str(root)])
    subprocess.run(build_cmd, check=True)


def install_codex(context: InstallContext) -> None:
    install_skill(context.codex_home / "skills" / "skill-router")
    append_snippet(context.codex_home / "AGENTS.md", SNIPPETS["codex"], marker="# Skill Routing")
    print(f"Installed Codex adapter into {context.codex_home}")


def install_claude(context: InstallContext) -> None:
    install_skill(context.claude_home / "skills" / "skill-router")
    append_snippet(context.claude_home / "CLAUDE.md", SNIPPETS["claude-code"], marker="# Skill Routing")
    print(f"Installed Claude Code adapter into {context.claude_home}")


def install_openclaw(context: InstallContext) -> None:
    install_skill(context.openclaw_home / "skills" / "skill-router")
    append_snippet(
        context.openclaw_workspace / "AGENTS.md",
        SNIPPETS["openclaw-agents"],
        marker="# Skill Routing",
    )
    append_snippet(
        context.openclaw_workspace / "TOOLS.md",
        SNIPPETS["openclaw-tools"],
        marker="# Skill Routing Tools",
    )
    print(f"Installed OpenClaw adapter into {context.openclaw_workspace}")


def install_gemini(context: InstallContext) -> None:
    append_snippet(context.gemini_home / "GEMINI.md", SNIPPETS["gemini-cli"], marker="# Skill Routing")
    print(f"Installed Gemini CLI adapter into {context.gemini_home}")


def install_opencode(context: InstallContext) -> None:
    install_skill(context.opencode_home / "skills" / "skill-router")
    append_snippet(context.opencode_home / "AGENTS.md", SNIPPETS["opencode"], marker="# Skill Routing")
    print(f"Installed OpenCode adapter into {context.opencode_home}")


def install_cline_global(context: InstallContext) -> None:
    write_rule_file(
        context.cline_rules_home / "skill-routing.md",
        SNIPPETS["cline"],
        marker="# Skill Routing",
    )
    print(f"Installed Cline global adapter into {context.cline_rules_home}")


def install_roo_global(context: InstallContext) -> None:
    write_rule_file(
        context.roo_home / "rules" / "skill-routing.md",
        SNIPPETS["roo-code"],
        marker="# Skill Routing",
    )
    print(f"Installed Roo Code global adapter into {context.roo_home / 'rules'}")


def install_cline_project(context: InstallContext) -> None:
    project = require_project(context)
    write_rule_file(project / ".clinerules" / "00-skill-routing.md", SNIPPETS["cline"], marker="# Skill Routing")
    print(f"Installed Cline project adapter into {project}")


def install_roo_project(context: InstallContext) -> None:
    project = require_project(context)
    write_rule_file(
        project / ".roo" / "rules" / "00-skill-routing.md",
        SNIPPETS["roo-code"],
        marker="# Skill Routing",
    )
    print(f"Installed Roo Code project adapter into {project}")


def install_cursor(context: InstallContext) -> None:
    project = require_project(context)
    write_rule_file(
        project / ".cursor" / "rules" / "skill-routing.mdc",
        SNIPPETS["cursor"],
        marker="# Skill Routing",
    )
    print(f"Installed Cursor adapter into {project}")


def install_continue(context: InstallContext) -> None:
    project = require_project(context)
    write_rule_file(
        project / ".continue" / "rules" / "00-skill-routing.md",
        SNIPPETS["continue"],
        marker="# Skill Routing",
    )
    print(f"Installed Continue adapter into {project}")


def install_aider(context: InstallContext) -> None:
    project = require_project(context)
    append_snippet(project / "CONVENTIONS.md", SNIPPETS["aider"], marker="# Skill Routing")
    print(f"Installed aider adapter into {project}")


def install_windsurf(context: InstallContext) -> None:
    project = require_project(context)
    preferred = project / ".devin" / "rules"
    legacy = project / ".windsurf" / "rules"
    if preferred.exists() or not legacy.exists():
        write_rule_file(preferred / "00-skill-routing.md", SNIPPETS["windsurf"], marker="# Skill Routing")
        target = preferred
    else:
        write_rule_file(legacy / "00-skill-routing.md", SNIPPETS["windsurf"], marker="# Skill Routing")
        target = legacy
    print(f"Installed Windsurf adapter into {target}")


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


def write_rule_file(target_path: Path, snippet_path: Path, *, marker: str) -> None:
    snippet = snippet_path.read_text(encoding="utf-8").strip()
    existing = target_path.read_text(encoding="utf-8") if target_path.is_file() else ""
    if marker in existing:
        print(f"Rule already present in {target_path}")
        return
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if existing:
        append_snippet(target_path, snippet_path, marker=marker)
        return
    target_path.write_text(snippet + "\n", encoding="utf-8")
    print(f"Updated {target_path}")


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def project_marker(context: InstallContext, relative: str) -> bool:
    project = context.project_root
    return bool(project and (project / relative).exists())


def require_project(context: InstallContext) -> Path:
    if context.project_root is None:
        raise SystemExit("A project-scoped adapter requires --project-root.")
    return context.project_root


if __name__ == "__main__":
    main()
