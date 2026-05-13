---
name: voice-setup
description: Configure Claude Code to speak responses aloud via edge-tts
---

# Voice Setup Skill

Configure the current project so Claude speaks a short spoken summary after each response, using Microsoft Edge TTS (edge-tts).

## What you do

1. Verify edge-tts is installed (`pip show edge-tts`). If missing, tell user to run `pip install edge-tts`.
2. Create `.claude/voice-config.json` with default voice.
3. Create `speak.py`, `hook_speak.py`, and `permission_speak.py` in the project `.claude/skills/voice-setup/` directory.
4. Create `.claude/skills/voice-config/SKILL.md` for the `/voice-config` command.
5. Update `.claude/settings.json` to add Stop and PermissionRequest hooks.
6. Create or update `CLAUDE.md` to add the Voice Output section.
7. Test: write a test sentence to `last_response.txt`, then run `python hook_speak.py` to verify audio.

## Reliability note

The hook and TTS code are 100% reliable. The weak point: Claude must remember to call the Write tool for `last_response.txt`. With CLAUDE.md as a prominent reminder, this works ~80-90% of the time. If Claude forgets, just say "你没说话" and it will write the file on the next turn.

## voice-config.json

Create `<project>/.claude/voice-config.json`:

```json
{
  "voice": "zh-CN-XiaoxiaoNeural",
  "lang": "zh"
}
```

All TTS scripts read this file on every run. The `lang` field controls permission prompt language. Users can change voice via `/voice-config` command (requires the voice-config skill below).

## voice-config skill

Create `<project>/.claude/skills/voice-config/SKILL.md`:

```markdown
---
name: voice-config
description: Switch TTS voice or language for Claude's spoken output
---

# Voice Config Skill

Change the voice or language used for spoken output. Reads/writes `.claude/voice-config.json`.

## What you do

### Show current config (no arguments)
Read `.claude/voice-config.json` and tell the user what voice is set.

### Change voice (`/voice-config <voice-name>`)
Write the new voice to `.claude/voice-config.json`.

### List voices (`/voice-config --list <language>`)
Run `python -m edge_tts --list-voices` and filter for the language code.

Common codes: `zh-CN` `en-US` `en-GB` `ja-JP` `ko-KR`

| Language | Female | Male |
|----------|--------|------|
| Chinese | zh-CN-XiaoxiaoNeural | zh-CN-YunyangNeural |
| English (US) | en-US-JennyNeural | en-US-GuyNeural |
| English (UK) | en-GB-SoniaNeural | en-GB-RyanNeural |
| Japanese | ja-JP-NanamiNeural | ja-JP-KeitaNeural |
```

## File templates

All scripts import from `voice_common.py` (shared utilities). Create this file first.

### voice_common.py
Shared module: config loading, cleanup, audio playback. Place at `<project>/.claude/skills/voice-setup/voice_common.py`.

```python
#!/usr/bin/env python3
"""Shared utilities for voice TTS scripts."""
import os, json, glob, time, subprocess, shutil, tempfile

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", ".")
CONFIG_FILE = os.path.join(PROJECT_DIR, ".claude", "voice-config.json")
TMPDIR = tempfile.gettempdir()
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
TEMP_PATTERNS = ["tts_hook_*.mp3", "tts_perm_*.mp3", "tts_*.mp3"]


def load_voice():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("voice", DEFAULT_VOICE)
    except Exception:
        pass
    return DEFAULT_VOICE


def load_lang():
    try:
        if os.path.exists(CONFIG_FILE):
            cfg = json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
            if "lang" in cfg:
                return cfg["lang"]
            voice = cfg.get("voice", "")
            if voice.startswith("en-"):
                return "en"
            if voice.startswith("ja-"):
                return "ja"
    except Exception:
        pass
    return "zh"


def cleanup_old_temps():
    try:
        now = time.time()
        for pattern in TEMP_PATTERNS:
            for f in glob.glob(os.path.join(TMPDIR, pattern)):
                if now - os.path.getmtime(f) > 600:
                    try:
                        os.unlink(f)
                    except OSError:
                        pass
    except Exception:
        pass


def play_audio(filepath: str):
    if shutil.which("mpv"):
        subprocess.Popen(
            f'mpv --really-quiet "{filepath}" && rm -f "{filepath}"',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    elif shutil.which("ffplay"):
        subprocess.Popen(
            f'ffplay -nodisp -autoexit -loglevel quiet "{filepath}" && rm -f "{filepath}"',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        ps_cmd = (
            'Add-Type -AssemblyName PresentationCore; '
            '$p = New-Object System.Windows.Media.MediaPlayer; '
            f"$p.Open('{filepath}'); "
            '$p.Play(); '
            'Start-Sleep -Milliseconds 500; '
            '$dur = $p.NaturalDuration.TimeSpan.TotalMilliseconds; '
            'if ($dur -gt 0) { Start-Sleep -Milliseconds ($dur + 200) } '
            'else { Start-Sleep -Seconds 10 }; '
            '$p.Close(); '
            f"Remove-Item '{filepath}' -ErrorAction SilentlyContinue"
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
```

### speak.py
Core TTS utility: reads text from stdin, speaks via edge-tts. Place at `<project>/.claude/skills/voice-setup/speak.py`.

```python
#!/usr/bin/env python3
"""edge-tts wrapper: reads text from stdin and speaks it aloud."""
import sys, asyncio, os, tempfile, uuid
from voice_common import cleanup_old_temps, load_voice, play_audio


async def speak_async(text: str, voice: str):
    tmp_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex[:8]}.mp3")
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)
        play_audio(tmp_path)
    except Exception as e:
        print(f"Speak error: {e}", file=sys.stderr)


def main():
    cleanup_old_temps()
    text = sys.stdin.buffer.read().decode("utf-8").strip()
    if not text:
        return
    asyncio.run(speak_async(text, load_voice()))


if __name__ == "__main__":
    main()
```

### hook_speak.py
Stop hook handler: reads `last_response.txt` and speaks it. Place at `<project>/.claude/skills/voice-setup/hook_speak.py`.

```python
#!/usr/bin/env python3
"""Stop hook: reads last_response.txt and speaks it aloud via edge-tts."""
import sys, asyncio, os, tempfile, uuid
from voice_common import cleanup_old_temps, load_voice, play_audio, PROJECT_DIR

RESPONSE_FILE = os.path.join(PROJECT_DIR, "last_response.txt")


async def speak(text: str, voice: str):
    if not text:
        return
    tmp_path = os.path.join(tempfile.gettempdir(), f"tts_hook_{uuid.uuid4().hex[:8]}.mp3")
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)
        play_audio(tmp_path)
    except Exception:
        pass


def main():
    cleanup_old_temps()
    text = ""
    if os.path.exists(RESPONSE_FILE):
        try:
            with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                text = content
            os.remove(RESPONSE_FILE)
        except Exception:
            pass
    asyncio.run(speak(text, load_voice()))


if __name__ == "__main__":
    main()
```

### permission_speak.py
Bilingual permission hook (auto-detects language from voice config). Place at `<project>/.claude/skills/voice-setup/permission_speak.py`.

```python
#!/usr/bin/env python3
"""PermissionRequest hook: speaks what permission is being requested."""
import sys, json, asyncio, os, tempfile, uuid
from voice_common import cleanup_old_temps, load_voice, load_lang, play_audio

MSG = {
    "Bash": {"zh": "需要请求命令执行权限", "en": "Permission needed to run a command"},
    "Write": {"zh": "需要请求写入文件权限", "en": "Permission needed to write a file"},
    "Edit": {"zh": "需要请求编辑文件权限", "en": "Permission needed to edit a file"},
    "Read": {"zh": "需要请求读取文件权限", "en": "Permission needed to read a file"},
    "WebFetch": {"zh": "需要请求访问网页权限", "en": "Permission needed to access a webpage"},
    "WebSearch": {"zh": "需要请求网络搜索权限", "en": "Permission needed to search the web"},
    "Grep": {"zh": "需要请求搜索代码权限", "en": "Permission needed to search code"},
    "Glob": {"zh": "需要请求查找文件权限", "en": "Permission needed to find files"},
}
_FALLBACK = {"zh": "需要请求权限", "en": "Permission required"}


def _build_message(data: dict, lang: str) -> str:
    tool = data.get("tool_name", "") or data.get("tool", "")
    if tool in MSG:
        return MSG[tool].get(lang, MSG[tool]["zh"])
    if tool:
        label = _FALLBACK.get(lang, _FALLBACK["zh"])
        return f"{label}: {tool}"
    return _FALLBACK.get(lang, _FALLBACK["zh"])


async def speak(text: str, voice: str):
    if not text:
        return
    tmp_path = os.path.join(tempfile.gettempdir(), f"tts_perm_{uuid.uuid4().hex[:8]}.mp3")
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)
        play_audio(tmp_path)
    except Exception:
        pass


def main():
    cleanup_old_temps()
    try:
        raw = sys.stdin.buffer.read()
        data = json.loads(raw.decode("utf-8")) if raw else {}
    except Exception:
        data = {}
    lang = load_lang()
    asyncio.run(speak(_build_message(data, lang), load_voice()))


if __name__ == "__main__":
    main()
```

### settings.json hook entry

Add or merge into `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python <project>/.claude/skills/voice-setup/hook_speak.py"
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python <project>/.claude/skills/voice-setup/permission_speak.py"
          }
        ]
      }
    ]
  }
}
```

Replace `<project>` with the actual project directory path.

### CLAUDE.md section

Create or append to `CLAUDE.md`:

```markdown
## Voice Output

After each conversational response (not after tool-only turns), write a short spoken summary to `<project>/last_response.txt` using the Write tool. The Stop hook reads this file aloud via edge-tts.

This is NOT the full response — it's a 1-3 sentence spoken summary. Rules:
- Pure natural spoken Chinese, like you're talking to someone
- No markdown, no code, no table data, no file paths, no symbols
- Skip details the user can read on screen (code, tables, lists)
- Just tell them the key takeaway in plain speech
- If the response was purely operational (tool output, file read), still write a one-line summary

Write ONLY the text to be spoken — no prefixes, no labels.
```

Replace `<project>` with the actual project directory path.

## Post-setup

Tell the user to restart Claude Code. After restart, the Stop hook will read `last_response.txt` and speak its contents.
