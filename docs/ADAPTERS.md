# Agent Adapters

The router generates a neutral `skill-routing.md` index. Agent adapters decide where to place the short instruction that tells an agent to consult that index.

## Codex

Codex uses `AGENTS.md` project and global instructions. The adapter appends the routing rule to:

```text
~/.codex/AGENTS.md
```

It also installs the helper skill at:

```text
~/.codex/skills/skill-router/SKILL.md
```

Install:

```bash
python3 scripts/install_local.py --agent codex
```

## Claude Code

Claude Code uses `CLAUDE.md` memory files. Anthropic documents that `CLAUDE.md` files are loaded in full at session start, while `MEMORY.md` has a startup size limit.

The adapter appends the routing rule to:

```text
~/.claude/CLAUDE.md
```

It also copies the helper skill into:

```text
~/.claude/skills/skill-router/SKILL.md
```

Install:

```bash
python3 scripts/install_local.py --agent claude-code
```

## OpenClaw

OpenClaw workspace conventions use files such as `AGENTS.md` and `TOOLS.md`. The default OpenClaw AGENTS reference says tools live in skills and agents should follow each skill's `SKILL.md` when needed.

The adapter appends routing instructions to:

```text
~/.openclaw/workspace/AGENTS.md
~/.openclaw/workspace/TOOLS.md
```

It also copies the helper skill into the OpenClaw personal skill directory:

```text
~/.openclaw/skills/skill-router/SKILL.md
```

Install:

```bash
python3 scripts/install_local.py --agent openclaw
```

## All Adapters

```bash
python3 scripts/install_local.py --agent all
```

## Custom Skill Roots

The generator can scan extra skill directories:

```bash
python3 scripts/build_skill_routing.py \
  --skill-root ~/.claude/skills \
  --skill-root ~/.openclaw/skills \
  --skill-root ~/.openclaw/workspace/skills
```

Use this when an agent has skills outside Codex's `~/.codex/skills` and `~/.codex/plugins/cache` conventions.
