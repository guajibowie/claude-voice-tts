#!/usr/bin/env python3
"""PermissionRequest hook: speaks what permission is being requested."""
import sys, json, asyncio, os, tempfile, uuid
from voice_common import cleanup_old_temps, load_voice, load_lang, play_audio

# Messages keyed by language code
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
