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
