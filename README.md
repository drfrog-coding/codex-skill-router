# Codex Skill Router

Codex skills and plugins are useful, but agents may miss them when the user does not explicitly name a skill. Claude Code, OpenClaw, and similar agent tools have the same problem when skills must be invoked manually. This project adds a small routing layer:

- scan installed `SKILL.md` files and plugin skills
- extract trigger scenarios from skill descriptions and usage sections
- generate a compact `skill-routing.md`
- add a short agent-specific rule that asks the agent to check that routing file before starting work

The generated routing file is an index, not a replacement for skills. After a route matches, the agent should still open the matched `SKILL.md` and follow its instructions.

## Files

- `scripts/build_skill_routing.py`: build `~/.codex/skill-routing.md`
- `scripts/test_build_skill_routing.py`: lightweight tests
- `AGENTS_SNIPPET.md`: legacy Codex rules to paste into `~/.codex/AGENTS.md`
- `adapters/`: snippets for Codex, Claude Code, and OpenClaw
- `examples/skill-routing-overrides.example.json`: optional manual routing overrides
- `skills/skill-router/SKILL.md`: optional skill that formalizes the routing behavior
- `docs/METHOD.md`: method and design notes
- `docs/ADAPTERS.md`: per-agent installation notes

## Install

Clone the repo, then run:

```bash
python3 scripts/install_local.py
```

That command installs the Codex adapter by default. To install multiple adapters:

```bash
python3 scripts/install_local.py --agent all
```

Supported adapters:

- `codex`
- `claude-code`
- `openclaw`

The install command copies the optional `skill-router` skill, appends the relevant agent rule if needed, and generates `~/.codex/skill-routing.md`.

To only generate the routing file:

```bash
python3 scripts/build_skill_routing.py
```

By default this reads:

- `~/.codex/skills`
- `~/.codex/plugins/cache`

and writes:

- `~/.codex/skill-routing.md`

To include local source paths for debugging:

```bash
python3 scripts/build_skill_routing.py --include-paths
```

To use overrides:

```bash
cp examples/skill-routing-overrides.example.json ~/.codex/skill-routing-overrides.json
python3 scripts/build_skill_routing.py
```

To scan skills from other agent workspaces:

```bash
python3 scripts/build_skill_routing.py \
  --skill-root ~/.claude/skills \
  --skill-root ~/.openclaw/skills \
  --skill-root ~/.openclaw/workspace/skills
```

## Add To Agent Instructions

`scripts/install_local.py` does this automatically. To do it manually, use the snippets in `adapters/`.

The short rule is:

```md
## Skill Routing

Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists. If one high-confidence skill matches the user's intent, load that skill. If several mutually exclusive skills match, present a short choice list. If several complementary skills match, use them together.
```

## Update After Installing Skills Or Plugins

Run this after installing or updating skills/plugins:

```bash
python3 scripts/build_skill_routing.py
```

New MCP tools and plugin-provided skills may still require a new Codex conversation or app restart before they are available in the active session.

## Safety

The generator does not copy full skill bodies. It extracts short descriptions and bullet-like usage hints. It also redacts common token-like strings. By default it does not include absolute local paths.
