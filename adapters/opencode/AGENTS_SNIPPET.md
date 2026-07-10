# Skill Routing

- Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists.
- Match the request against route fields such as `use_when`, `avoid_when`, `ask_user_when`, and `combine_with`.
- If one high-confidence route matches and its tool is available in OpenCode, use it before acting.
- If a route points to a Codex-only plugin or MCP server that is unavailable here, explain the missing capability and use the closest available local workflow.
- Ask the user to choose when several matching routes are mutually exclusive.
- State external uploads, paid APIs, credential changes, or system configuration effects before using the matched capability unless the user already requested that action.

