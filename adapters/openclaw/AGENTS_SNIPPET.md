# Skill Routing

- Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists.
- Match the request against route fields such as `use_when`, `avoid_when`, `ask_user_when`, and `combine_with`.
- If a matching skill exists in the OpenClaw workspace, load and follow that skill's `SKILL.md`.
- If a route points to a Codex-only plugin or MCP server that is unavailable here, use `TOOLS.md` notes or ask the user before substituting a workflow.
- Ask the user to choose when several matching skills are mutually exclusive.
- State external uploads, paid APIs, credential changes, or system configuration effects before using the matched capability unless the user already requested that action.

