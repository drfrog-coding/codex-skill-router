# Skill Routing Tools

- Skill route index: `~/.codex/skill-routing.md`
- Regenerate from the cloned router repository:

```bash
python3 scripts/build_skill_routing.py
```

- If OpenClaw workspace skills live outside Codex, include them explicitly:

```bash
python3 scripts/build_skill_routing.py \
  --skill-root ~/.openclaw/skills \
  --skill-root ~/.openclaw/workspace/skills \
  --output ~/.codex/skill-routing.md
```

- The route index may mention Codex-only MCP servers or plugins. Use only tools available in the current OpenClaw runtime, or ask the user before switching tools.
