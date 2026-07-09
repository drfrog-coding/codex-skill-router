#!/usr/bin/env python3
"""Build a compact routing index for installed Codex skills."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Iterable


SECTION_USE = {
    "use when",
    "when to use",
    "triggers",
    "trigger rules",
    "routing",
    "适用",
    "适用场景",
    "使用场景",
    "何时使用",
}
SECTION_AVOID = {
    "avoid when",
    "do not use",
    "when not to use",
    "不适用",
    "不要使用",
}
SECTION_ASK = {
    "ask user when",
    "clarify when",
    "requires confirmation",
    "需要确认",
    "何时询问",
}
SECTION_COMBINE = {
    "combine with",
    "related skills",
    "配合",
    "组合使用",
}

TOKEN_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|bearer)\s*[:=]\s*[A-Za-z0-9._~+/=-]{16,}"
)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")
HEX_SECRET_RE = re.compile(r"\b[a-f0-9]{40,}\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$")


@dataclasses.dataclass
class SkillRoute:
    name: str
    source: str
    description: str = ""
    use_when: list[str] = dataclasses.field(default_factory=list)
    avoid_when: list[str] = dataclasses.field(default_factory=list)
    ask_user_when: list[str] = dataclasses.field(default_factory=list)
    combine_with: list[str] = dataclasses.field(default_factory=list)
    priority: str = "medium"
    path: str | None = None


def parse_args() -> argparse.Namespace:
    default_codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    return argparse.ArgumentParser(description=__doc__).parse_args()


def build_parser() -> argparse.ArgumentParser:
    default_codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=str(default_codex_home))
    parser.add_argument("--output")
    parser.add_argument("--overrides")
    parser.add_argument("--include-paths", action="store_true")
    parser.add_argument("--no-plugins", action="store_true")
    parser.add_argument("--max-items", type=int, default=8)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    codex_home = Path(args.codex_home).expanduser().resolve()
    output = Path(args.output).expanduser().resolve() if args.output else codex_home / "skill-routing.md"
    overrides_path = (
        Path(args.overrides).expanduser().resolve()
        if args.overrides
        else codex_home / "skill-routing-overrides.json"
    )

    routes = collect_routes(codex_home, include_plugins=not args.no_plugins, max_items=args.max_items)
    overrides = load_overrides(overrides_path)
    routes = merge_overrides(routes, overrides)
    markdown = render_markdown(routes, include_paths=args.include_paths)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Routes: {len(routes)}")


def collect_routes(codex_home: Path, *, include_plugins: bool, max_items: int) -> list[SkillRoute]:
    skill_files = list(find_local_skill_files(codex_home / "skills"))
    if include_plugins:
        skill_files.extend(find_plugin_skill_files(codex_home / "plugins" / "cache"))

    seen: set[tuple[str, str]] = set()
    routes: list[SkillRoute] = []
    for path in sorted(skill_files):
        source = route_source(codex_home, path)
        metadata, body = read_skill(path)
        name = skill_name(codex_home, path, metadata, source)
        key = (name, source)
        if key in seen:
            continue
        seen.add(key)
        route = SkillRoute(
            name=name,
            source=source,
            description=clean_text(metadata.get("description", "")),
            path=str(path),
        )
        extracted = extract_usage(body, max_items=max_items)
        route.use_when = extracted["use_when"]
        route.avoid_when = extracted["avoid_when"]
        route.ask_user_when = extracted["ask_user_when"]
        route.combine_with = extracted["combine_with"]
        if not route.use_when and route.description:
            route.use_when = [route.description]
        route.priority = infer_priority(route)
        routes.append(route)
    return sorted(routes, key=lambda item: item.name.lower())


def find_local_skill_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return []
    return root.rglob("SKILL.md")


def find_plugin_skill_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return []
    return root.glob("*/*/*/skills/*/SKILL.md")


def route_source(codex_home: Path, path: Path) -> str:
    plugin_cache = codex_home / "plugins" / "cache"
    try:
        path.relative_to(plugin_cache)
        return "plugin"
    except ValueError:
        return "local"


def read_skill(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata: dict[str, str] = {}
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            lines = parts[1].splitlines()
            index = 0
            while index < len(lines):
                line = lines[index]
                if ":" not in line:
                    index += 1
                    continue
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value.startswith((">", "|")):
                    folded: list[str] = []
                    index += 1
                    while index < len(lines):
                        next_line = lines[index]
                        if next_line and not next_line.startswith((" ", "\t")):
                            index -= 1
                            break
                        stripped = next_line.strip()
                        if stripped:
                            folded.append(stripped)
                        index += 1
                    value = " ".join(folded)
                metadata[key] = value
                index += 1
            return metadata, parts[2]
    return metadata, text


def skill_name(codex_home: Path, path: Path, metadata: dict[str, str], source: str) -> str:
    raw_name = metadata.get("name") or path.parent.name
    if source != "plugin":
        return raw_name
    try:
        rel = path.relative_to(codex_home / "plugins" / "cache")
    except ValueError:
        return raw_name
    parts = rel.parts
    if len(parts) >= 5:
        plugin_name = parts[1]
        return f"{plugin_name}:{raw_name}"
    return raw_name


def extract_usage(body: str, *, max_items: int) -> dict[str, list[str]]:
    sections = {
        "use_when": [],
        "avoid_when": [],
        "ask_user_when": [],
        "combine_with": [],
    }
    current: str | None = None
    for line in body.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            title = normalize_heading(heading.group(2))
            current = classify_heading(title)
            continue
        if current is None:
            continue
        bullet = BULLET_RE.match(line)
        if not bullet:
            continue
        value = clean_text(bullet.group(1))
        if not value:
            continue
        if len(sections[current]) < max_items:
            sections[current].append(value)
    return sections


def normalize_heading(value: str) -> str:
    value = re.sub(r"[`*_#：:]+", " ", value)
    return re.sub(r"\s+", " ", value.strip().lower())


def classify_heading(title: str) -> str | None:
    if title in SECTION_USE or any(marker in title for marker in SECTION_USE):
        return "use_when"
    if title in SECTION_AVOID or any(marker in title for marker in SECTION_AVOID):
        return "avoid_when"
    if title in SECTION_ASK or any(marker in title for marker in SECTION_ASK):
        return "ask_user_when"
    if title in SECTION_COMBINE or any(marker in title for marker in SECTION_COMBINE):
        return "combine_with"
    return None


def clean_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    value = redact(value)
    return value


def redact(value: str) -> str:
    value = TOKEN_RE.sub(r"\1=[REDACTED]", value)
    value = JWT_RE.sub("[REDACTED_JWT]", value)
    value = HEX_SECRET_RE.sub("[REDACTED_HEX]", value)
    return value


def infer_priority(route: SkillRoute) -> str:
    text = " ".join([route.name, route.description, *route.use_when]).lower()
    high_markers = [
        "must",
        "mandatory",
        "immediately",
        "pdf",
        "file",
        "mcp",
        "github",
        "deploy",
        "freecad",
        "ocr",
        "parse",
        "润色",
        "论文",
    ]
    if any(marker in text for marker in high_markers):
        return "high"
    return "medium"


def load_overrides(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def merge_overrides(routes: list[SkillRoute], overrides: dict) -> list[SkillRoute]:
    by_name = {route.name: route for route in routes}
    for name, payload in overrides.get("skills", {}).items():
        route = by_name.get(name)
        if route is None:
            route = SkillRoute(name=name, source=payload.get("source", "manual"))
            routes.append(route)
            by_name[name] = route
        for field in ("description", "priority"):
            if field in payload:
                setattr(route, field, clean_text(str(payload[field])))
        for field in ("use_when", "avoid_when", "ask_user_when", "combine_with"):
            if field in payload:
                setattr(route, field, [clean_text(str(item)) for item in payload[field]])
    return sorted(routes, key=lambda item: item.name.lower())


def render_markdown(routes: list[SkillRoute], *, include_paths: bool) -> str:
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Codex Skill Routing Rules",
        "",
        f"Generated: {generated}",
        "",
        "## Router Protocol",
        "",
        "- Check this file before starting a non-trivial task.",
        "- Load one high-confidence skill directly.",
        "- Use complementary skills together when they cover different parts of the same request.",
        "- Ask the user to choose when matched skills are mutually exclusive.",
        "- State uploads, paid actions, credential changes, or system configuration effects before use unless already requested.",
        "- Treat this file as an index. After selecting a skill, read its `SKILL.md`.",
        "",
        "## Routes",
        "",
    ]
    for route in routes:
        lines.extend(render_route(route, include_paths=include_paths))
    return "\n".join(lines).rstrip() + "\n"


def render_route(route: SkillRoute, *, include_paths: bool) -> list[str]:
    lines = [
        f"### {route.name}",
        "",
        f"- Source: {route.source}",
        f"- Priority: {route.priority}",
    ]
    if include_paths and route.path:
        lines.append(f"- Path: `{redact(route.path)}`")
    if route.description:
        lines.extend(["", f"Description: {route.description}"])
    append_list(lines, "Use when", route.use_when)
    append_list(lines, "Avoid when", route.avoid_when)
    append_list(lines, "Ask user when", route.ask_user_when)
    append_list(lines, "Combine with", route.combine_with)
    lines.append("")
    return lines


def append_list(lines: list[str], title: str, values: list[str]) -> None:
    if not values:
        return
    lines.extend(["", f"{title}:"])
    lines.append("")
    for value in values:
        lines.append(f"- {value}")


if __name__ == "__main__":
    main()
