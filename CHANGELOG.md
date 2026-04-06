# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-04-06

### Added

- **SKILL.md** — Core agent definition with full workflow, agent cluster roles, and verification checklists
- **SETUP_WIZARD.md** — First-time setup guide with step-by-step configuration
- **CLAUDE.md** — Claude Code native entry point
- **workspace-template/** — Complete template suite:
  - `world_template.md` (full example)
  - `characters/protagonist_template.md`
  - `characters/antagonist_template.md`
  - `characters/supporting_template.md`
  - `outline/structure_template.md` (full example)
  - `beats/tracking_template.md`
  - `style_guide_template.md`
- **frameworks/** — Three narrative frameworks:
  - 三段式_engine.md (Three-act structure)
  - 起承转合.md (Traditional Chinese structure)
  - 事件驱动.md (Event-driven)
- **scripts/** — Four validation/generation tools:
  - `consistency_check.py` — Detect character/equipment/timeline contradictions
  - `beat_tracker.py` — Track foreshadowing, warn on overdue beats
  - `context_compressor.py` — Compress old chapters to prevent context overflow
  - `outline_generator.py` — Generate volume/chapter outlines from framework templates
- **docs/** — Platform-specific installation guides:
  - `INSTALL.md` — General installation
  - `INSTALL_OPENCLAW.md`
  - `INSTALL_CLAUDE_CODE.md`
  - `INSTALL_CODEX.md`
  - `INSTALL_GENERIC.md` — Works with any LLM API
  - `COMPATIBILITY.md` — Platform comparison
  - `EXAMPLES.md` — Full walkthrough with sample novel
- **LICENSE** — MIT license

### Supported Platforms

- OpenClaw ✅
- Claude Code ✅
- Codex / Cursor / Windsurf ✅
- Any LLM API (OpenAI, Anthropic, DeepSeek, Doubao, etc.) ✅
- DeerFlow (ByteDance) ✅
- Coze / 扣子 ✅
