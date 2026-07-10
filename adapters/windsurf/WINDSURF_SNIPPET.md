---
trigger: always_on
description: Route non-trivial requests to installed skills, plugin skills, and tool-specific workflows.
---

# Skill Routing

- Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists.
- Use that file to decide whether a local skill, project rule, MCP-backed workflow, or manual tool workflow should be loaded.
- If one high-confidence route matches and the required tool is available in Windsurf, use it before acting.
- If several complementary routes match, use the minimal useful set.
- If several routes are mutually exclusive, ask the user to choose.
- If a route depends on a tool unavailable in Windsurf, explain the missing capability and use the closest available workflow.
