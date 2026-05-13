---
name: voice-config
description: Switch TTS voice or language for Claude's spoken output
---

# Voice Config Skill

Change the voice or language used for spoken output. Reads/writes `.claude/voice-config.json`.

## What you do

### Show current config (no arguments)
Read `.claude/voice-config.json` and tell the user what voice is currently set.

### Change voice (`/voice-config <voice-name>`)
Write the new voice name AND `lang` to `.claude/voice-config.json`. Derive `lang` from the voice prefix:
- `zh-CN-*` → `"lang": "zh"`
- `en-US-*` / `en-GB-*` → `"lang": "en"`
- `ja-JP-*` → `"lang": "ja"`
- `ko-KR-*` → `"lang": "ko"`
- Other → `"lang": "zh"` (default)

Example: `/voice-config en-US-JennyNeural` writes `{"voice": "en-US-JennyNeural", "lang": "en"}`

### List voices for a language (`/voice-config --list <language>`)
Run `python -m edge_tts --list-voices` and filter/grep for the language code. Show a short table of matching voices.

Common language codes: `zh-CN` `en-US` `en-GB` `ja-JP` `ko-KR`

## Popular voices

| Language | Female | Male |
|----------|--------|------|
| Chinese (Mainland) | zh-CN-XiaoxiaoNeural (warm) | zh-CN-YunyangNeural (professional) |
| Chinese (Mainland) | zh-CN-XiaoyiNeural (lively) | zh-CN-YunxiNeural (sunshine) |
| English (US) | en-US-JennyNeural | en-US-GuyNeural |
| English (UK) | en-GB-SoniaNeural | en-GB-RyanNeural |
| Japanese | ja-JP-NanamiNeural | ja-JP-KeitaNeural |
| Korean | ko-KR-SunHiNeural | ko-KR-InJoonNeural |

User can also pick any other voice from the full list.
