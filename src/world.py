# world.py
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def log_error(error_message: str):
    error_dir = get_config_path() / "error"
    error_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    error_filename = error_dir / f"O2-error-{timestamp}.log"
    with open(error_filename, 'w', encoding='utf-8') as f:
        json.dump({"error": error_message, "timestamp": timestamp}, f, ensure_ascii=False, indent=4)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, 'res', relative_path)


def get_default_output_path(for_audio=False):
    home = Path.home()
    if sys.platform == "win32":
        base_path = home / ("Music" if for_audio else "Videos")
    elif sys.platform == "darwin":
        base_path = home / ("Music" if for_audio else "Movies")
    else:
        base_path = home / ("Music" if for_audio else "Videos")
    output_path = base_path / "oxygen2"
    output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path)


def get_config_path():
    home = Path.home()
    config_dir = home / ".oxygen2"
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error(
            "FFmpeg is not installed or not in the system PATH. Please install FFmpeg and add it to your system PATH.")
        print(
            "FFmpeg is not installed or not in the system PATH. Please install FFmpeg and add it to your system PATH.")
        sys.exit(1)
