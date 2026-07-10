# Agent Adapters

The router generates a neutral `skill-routing.md` index. Agent adapters place a short rule where each tool already looks for persistent instructions.

## Selection Modes

```bash
python3 scripts/install_local.py --list-agents
python3 scripts/install_local.py --agent auto
python3 scripts/install_local.py --agent all-known --project-root /path/to/project
```

- `auto`: install only adapters detected from commands, home/config directories, or existing project rule markers.
- `all-known`: install all supported global adapters. Project adapters are included when `--project-root` is supplied.
- explicit names: install the requested adapter. Project adapters require `--project-root` unless the current project already has the matching marker.
- `all`: deprecated compatibility alias for `all-known`.

## Global Or User-Level Adapters

| Adapter | Target | Skill copied |
| --- | --- | --- |
| `codex` | `~/.codex/AGENTS.md` | `~/.codex/skills/skill-router/SKILL.md` |
| `claude-code` | `~/.claude/CLAUDE.md` | `~/.claude/skills/skill-router/SKILL.md` |
| `openclaw` | `~/.openclaw/workspace/AGENTS.md`, `~/.openclaw/workspace/TOOLS.md` | `~/.openclaw/skills/skill-router/SKILL.md` |
| `gemini-cli` | `~/.gemini/GEMINI.md` | none |
| `opencode` | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/skills/skill-router/SKILL.md` |
| `cline` | `~/Documents/Cline/Rules/skill-routing.md` | none |
| `roo-code` | `~/.roo/rules/skill-routing.md` | none |

## Project Adapters

| Adapter | Target |
| --- | --- |
| `cursor` | `<project>/.cursor/rules/skill-routing.mdc` |
| `continue` | `<project>/.continue/rules/00-skill-routing.md` |
| `aider` | `<project>/CONVENTIONS.md` |
| `windsurf` | `<project>/.devin/rules/00-skill-routing.md`, falling back to `<project>/.windsurf/rules/00-skill-routing.md` |
| `cline-project` | `<project>/.clinerules/00-skill-routing.md` |
| `roo-code-project` | `<project>/.roo/rules/00-skill-routing.md` |

## Custom Skill Roots

The generator can scan extra skill directories:

```bash
python3 scripts/build_skill_routing.py \
  --skill-root ~/.claude/skills \
  --skill-root ~/.openclaw/skills \
  --skill-root ~/.openclaw/workspace/skills \
  --skill-root ~/.config/opencode/skills
```

`install_local.py` adds relevant skill roots automatically for adapters that use `SKILL.md`.
