---
name: skill-router
description: Route user requests to installed Codex skills and plugin skills by consulting a generated skill-routing.md index before work begins.
---

# Skill Router

Use this skill when a task may match an installed Codex skill or plugin skill, especially when the user did not explicitly name the skill.

## Routing Steps

1. Check `~/.codex/skill-routing.md` if it exists.
2. Match the user's request against `use_when`, `avoid_when`, and `ask_user_when`.
3. If one high-confidence skill matches, load that skill.
4. If complementary skills match, load the minimal useful set.
5. If mutually exclusive skills match, ask the user to choose from a short list.
6. After choosing a route, open the matched `SKILL.md` and follow its instructions.

## Regenerate The Index

When skills or plugins are installed or updated, run:

```bash
python3 scripts/build_skill_routing.py
```

If using this skill outside the repository, resolve the script path to the cloned `codex-skill-router` project.

