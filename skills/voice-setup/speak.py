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
