# Agent Research

This file records the adapter targets checked for the router. The purpose is to turn "and similar tools" into a concrete, reviewable matching table.

## Global Or User-Level Adapters

| Agent | Rule location used by this project | Detection used by `auto` | Basis |
| --- | --- | --- | --- |
| Codex | `~/.codex/AGENTS.md` | `~/.codex` or `codex` command | Codex global instructions and local skills. |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude` or `claude` command | Claude Code documents `~/.claude/CLAUDE.md` as user instructions and says it reads `CLAUDE.md`, not `AGENTS.md`. |
| OpenClaw | `~/.openclaw/workspace/AGENTS.md`, `~/.openclaw/workspace/TOOLS.md`, `~/.openclaw/skills/skill-router/` | `~/.openclaw`, workspace, or `openclaw` command | Existing OpenClaw workspace convention. |
| Gemini CLI | `~/.gemini/GEMINI.md` | `~/.gemini` or `gemini` command | Gemini CLI defaults `contextFileName` to `GEMINI.md` and stores user settings in `~/.gemini/settings.json`. |
| OpenCode | `~/.config/opencode/AGENTS.md`, `~/.config/opencode/skills/skill-router/` | `~/.config/opencode` or `opencode` command | OpenCode supports global `AGENTS.md` and native `SKILL.md` discovery under `~/.config/opencode/skills/`. |
| Cline | `~/Documents/Cline/Rules/skill-routing.md` | Cline global rules directory or `cline` command | Cline documents a global rules directory at `~/Documents/Cline/Rules`. |
| Roo Code | `~/.roo/rules/skill-routing.md` | `~/.roo`, `roo`, or `roo-code` | Roo Code documents global rules under `~/.roo/rules/`. |

## Project-Level Adapters

Project adapters are installed in `auto` only when the current project already contains the relevant marker. Explicit `--agent <name> --project-root <path>` creates the target file. Explicit project adapters without `--project-root` are allowed only when the current project already has the matching marker.

| Agent | Rule location | Detection marker |
| --- | --- | --- |
| Cursor | `<project>/.cursor/rules/skill-routing.mdc` | `.cursor` or `.cursorrules` |
| Continue | `<project>/.continue/rules/00-skill-routing.md` | `.continue` |
| aider | `<project>/CONVENTIONS.md` | `CONVENTIONS.md` or `.aider.conf.yml` |
| Windsurf / Devin Cascade | `<project>/.devin/rules/00-skill-routing.md`, fallback `<project>/.windsurf/rules/00-skill-routing.md` | `.devin`, `.windsurf`, or `.windsurfrules` |
| Cline project rules | `<project>/.clinerules/00-skill-routing.md` | `.clinerules` |
| Roo Code project rules | `<project>/.roo/rules/00-skill-routing.md` | `.roo` or `.roorules` |

## Sources Checked

- Claude Code memory and rules: <https://docs.anthropic.com/en/docs/claude-code/memory>
- Claude Code skills: <https://docs.anthropic.com/en/docs/claude-code/skills>
- Gemini CLI configuration: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/configuration.md>
- Cursor rules: <https://cursor.com/docs/rules>
- Cline rules: <https://docs.cline.bot/customization/cline-rules>
- Roo Code custom instructions: <https://docs.roocode.com/features/custom-instructions>
- OpenCode rules: <https://opencode.ai/docs/rules/>
- OpenCode skills: <https://opencode.ai/docs/skills/>
- Continue rules: <https://docs.continue.dev/customize/rules>
- aider conventions: <https://aider.chat/docs/usage/conventions.html>
- Windsurf / Devin Cascade memories and rules: <https://docs.windsurf.com/windsurf/cascade/memories>
- Devin Desktop `AGENTS.md`: <https://docs.devin.ai/desktop/cascade/agents-md>

## Notes

- Some tools can read `AGENTS.md` directly. The router still writes native files when the tool documents a more specific convention.
- `auto` avoids creating project-scoped files in unrelated repositories. It only writes project adapters when an existing marker shows the project already uses that tool.
- `all-known` is intentionally explicit and should be used with `--project-root` when project-scoped adapters are desired.
