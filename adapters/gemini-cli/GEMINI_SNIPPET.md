# Skill Routing

- Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists.
- Use that routing file to decide whether a local skill, plugin skill, MCP-backed workflow, or manual tool workflow should be loaded.
- If one high-confidence route matches, read the corresponding `SKILL.md` or route notes before acting.
- If several complementary routes match, use the minimal useful set.
- If several routes are mutually exclusive, ask the user to choose from a short list.
- If a route points to a tool unavailable in Gemini CLI, explain the missing capability and use the closest available workflow.
- Treat the routing file as an index, not as the source of detailed instructions.

