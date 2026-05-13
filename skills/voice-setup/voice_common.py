#!/usr/bin/env python3
"""Shared utilities for voice TTS scripts."""
import os, json, glob, time, subprocess, shutil, tempfile, uuid

def _find_project_root():
    # Prefer the Claude Code env var
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return env_dir
    # Fallback: walk up from this script's directory to find .claude/
    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(cur, ".claude")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.getcwd()

PROJECT_DIR = _find_project_root()
CONFIG_FILE = os.path.join(PROJECT_DIR, ".claude", "voice-config.json")
TMPDIR = tempfile.gettempdir()
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# All temp file patterns to clean
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
    """Detect language from config or voice name. Returns 'zh' or 'en'."""
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
    # Filepath is always UUID hex — safe for shell string interpolation.
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
