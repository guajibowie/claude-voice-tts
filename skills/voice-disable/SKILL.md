---
name: voice-disable
description: Remove voice output configuration from the current project
---

# Voice Disable Skill

Remove the voice output system from the current project.

## What you do

1. Remove the `hooks.Stop` entry from `.claude/settings.json` that references `hook_speak.py`.
2. Remove the "Voice Output" section from `CLAUDE.md`.
3. Optionally delete `.claude/skills/voice-setup/` directory (ask user first).
4. Tell the user to restart Claude Code.
