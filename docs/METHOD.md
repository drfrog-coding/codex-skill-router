# Method

## Problem

Codex can miss useful skills when the user does not explicitly name them. The issue is structural: a skill's full instructions usually stay outside the active context until the agent decides to load it. If the short skill description is vague, or several skills overlap, the agent may choose the wrong tool or skip the tool entirely.

## Approach

Create a compact routing index outside the conversation:

1. Scan installed skills and plugin skills.
2. Read only metadata and usage sections from each `SKILL.md`.
3. Generate a short Markdown file with `use_when`, `avoid_when`, `ask_user_when`, priority, and source type.
4. Add an AGENTS rule that tells Codex to consult the routing file before non-trivial work.
5. Keep detailed execution steps inside each skill. The router only decides which skill to load.

## Decision Rules

- One clear match: load the skill directly.
- Complementary matches: load the minimal useful set.
- Mutually exclusive matches: ask the user to choose from a short list.
- Low confidence: continue with normal reasoning or ask one targeted question.
- External upload, paid action, credential change, or system configuration: state the side effect before use unless the user already requested it.

## Why Markdown

Markdown is easy for Codex to read, easy for users to edit, and easy to publish. It does not require a local service, database, or embedding index. A future version can add semantic search, but the first useful layer is a stable, human-readable routing document.

## Privacy

The generator avoids full skill bodies and absolute paths by default. It extracts short descriptions and bullets, then applies simple redaction for token-like values. Users can add manual overrides without publishing their local routing file.

