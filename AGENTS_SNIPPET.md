# Skill Routing

- Before starting a non-trivial task, check `~/.codex/skill-routing.md` when it exists.
- Match the user's request against `use_when`, `avoid_when`, and `ask_user_when`.
- If exactly one high-confidence skill matches, load that skill before acting.
- If several complementary skills match, load the minimal useful set.
- If several mutually exclusive skills match, show a short list and ask the user to choose.
- If a matched route involves uploads, external APIs, paid services, credential changes, or system configuration, state that effect before using it unless the user already requested that action.
- After selecting a route, open the matched `SKILL.md` and follow the skill's own instructions. The routing file is only an index.

