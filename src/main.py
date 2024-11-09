import os
import sys
import queue
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import json

import eel

# Include DownloaderAPI class directly in main.py
import yt_dlp
from typing import Dict, Any, Callable


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


class DownloaderAPI:
    def __init__(self):
        self.output_path = None
        self.video_format = "auto"  # 'auto', 'mp4', 'mov', 'webm', etc.
        self.audio_format = "auto"  # 'auto', 'mp3', 'wav', 'aac', etc.
        self.options = {
            'proxy': None,
            'sublangs': None,
            'write_thumbnail': False,
            'embed_thumbnail': False
        }

    def set_output_path(self, path):
        self.output_path = path

    def set_formats(self, video_format: str, audio_format: str):
        self.video_format = video_format
        self.audio_format = audio_format

    def set_options(self, proxy=None, sublangs=None, write_thumbnail=False, embed_thumbnail=False):
        self.options['proxy'] = proxy
        self.options['sublangs'] = sublangs
        self.options['write_thumbnail'] = write_thumbnail
        self.options['embed_thumbnail'] = embed_thumbnail

    def download_media(
            self,
            url: str,
            audio_only: bool = False,
            quality: str = 'Best',
            output_filename: str = None,
            progress_callback: Callable[[float, str], None] = None
    ) -> Dict[str, Any]:
        quality_map = {
            'Best': '',
            'High': '[height<=1080]',
            'Medium': '[height<=720]',
            'Low': '[height<=480]',
            'Worst': 'worst'
        }

        # Build format specification
        if audio_only:
            if self.audio_format == 'auto':
                format_spec = 'bestaudio/best'
            else:
                format_spec = f'bestaudio[ext={self.audio_format}]/bestaudio/best'
        else:
            if self.video_format == 'auto':
                format_spec = f'bestvideo{quality_map.get(quality, "")}+bestaudio/best[ext=m4a]/best'
            else:
                # Prefer formats with the selected video extension
                format_spec = f'bestvideo{quality_map.get(quality, "")}[ext={self.video_format}]+bestaudio/best[ext=m4a]/best[ext={self.video_format}]/best'
                if quality == 'Worst':
                    format_spec = f'worstvideo[ext={self.video_format}]+worstaudio/worst'

        # Adjust output template
        outtmpl = os.path.join(self.output_path, '%(title)s.%(ext)s')

        if output_filename:
            outtmpl = os.path.join(self.output_path, output_filename)

        def progress_hook(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                progress = downloaded_bytes / total_bytes if total_bytes else 0
                filename = d.get('filename', 'Unknown')
                if progress_callback:
                    progress_callback(progress, filename)

        ydl_opts = {
            'format': format_spec,
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'proxy': self.options['proxy'],
            'writesubtitles': bool(self.options['sublangs']),
            'subtitleslangs': self.options['sublangs'].split(',') if self.options['sublangs'] else None,
            'writethumbnail': self.options['write_thumbnail'],
            'embedthumbnail': self.options['embed_thumbnail'],
            'merge_output_format': self.video_format if not audio_only and self.video_format != 'auto' else None,
        }

        # Add postprocessors for video if necessary
        if not audio_only and self.options['embed_thumbnail']:
            ydl_opts.setdefault('postprocessors', [])
            ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return {"success": True, "filename": filename, "info": info}
        except Exception as e:
            # Remove partial file if exists
            if 'filename' in locals():
                partial_file = filename
                if partial_file and os.path.exists(partial_file):
                    os.remove(partial_file)
            return {"success": False, "error": str(e)}


class App:
    def __init__(self):
        self.api = DownloaderAPI()

        self.download_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.download_worker, daemon=True)
        self.worker_thread.start()

        self.download_logs = []

        self.settings = {
            # Video Settings
            'video_quality': 'Best',
            'video_format': 'auto',
            'video_output_path': get_default_output_path(for_audio=False),

            # Audio Settings
            'audio_format': 'auto',
            'audio_output_path': get_default_output_path(for_audio=True),

            # Other Settings
            'proxy': None,
            'sublangs': None,
            'write_thumbnail': False,
            'embed_thumbnail': False
        }

        self.load_settings_from_file()

    def add_to_queue(self, url, audio_only):
        if not url:
            eel.updateDownloadList("Please enter a URL.")
            return

        self.download_queue.put((url, audio_only))
        eel.updateDownloadList(f"Added to queue: {url}")

    def browse_output(output_type):
        import threading

        def run_dialog():
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            initial_dir = app.settings.get(f'{output_type}_output_path', '')
            path = filedialog.askdirectory(initialdir=initial_dir)
            root.destroy()
            if path:
                app.settings[f'{output_type}_output_path'] = path
                app.save_settings_to_file()
                eel.set_browse_output(output_type, path)
            else:
                eel.set_browse_output(output_type, None)

        threading.Thread(target=run_dialog).start()

    def open_download_folder(self):
        output_path = app.settings['audio_output_path'] if getattr(app, 'current_audio_only', False) else app.settings[
            'video_output_path']
        try:
            if sys.platform.startswith('win'):
                os.startfile(output_path)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(["open", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            eel.updateDownloadList(f"Failed to open folder: {e}")

    def open_logs_folder(self):
        logs_dir = get_config_path() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform.startswith('win'):
                os.startfile(str(logs_dir))
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(["open", str(logs_dir)])
            else:
                subprocess.Popen(["xdg-open", str(logs_dir)])
        except Exception as e:
            eel.updateDownloadList(f"Failed to open logs folder: {e}")

    def save_logs(self):
        config_dir = get_config_path()
        logs_dir = config_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_filename = logs_dir / f"O2-{timestamp}.log"
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(self.download_logs, f, ensure_ascii=False, indent=4)

    def load_logs(self):
        logs_dir = get_config_path() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_files = sorted(logs_dir.glob("O2-*.log"), reverse=True)
        if not log_files:
            eel.updateDownloadList("No logs found.")
            return
        self.download_logs = []
        eel.clearLogsTable()
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                self.download_logs.extend(logs)
                for log_entry in logs:
                    eel.updateLogsTable(log_entry)
        eel.updateDownloadList(f"Loaded logs from {len(log_files)} file(s).")

    def download_worker(self):
        while True:
            url, audio_only = self.download_queue.get()
            self.current_audio_only = audio_only
            eel.updateDownloadList(f"Downloading: {url}")
            eel.setProgressBar(0.0)

            if audio_only:
                output_path = self.settings['audio_output_path']
                format = self.settings['audio_format']
                quality = None  # Not applicable for audio-only downloads
            else:
                output_path = self.settings['video_output_path']
                format = self.settings['video_format']
                quality = self.settings['video_quality']

            self.api.set_output_path(output_path)
            self.api.set_formats(self.settings['video_format'], self.settings['audio_format'])
            self.api.set_options(
                proxy=self.settings['proxy'],
                sublangs=self.settings['sublangs'],
                write_thumbnail=self.settings['write_thumbnail'],
                embed_thumbnail=self.settings['embed_thumbnail']
            )

            def progress_callback(progress, filename):
                eel.updateDownloadList(f"Progress for {os.path.basename(filename)}: {progress:.2%}")
                eel.setProgressBar(progress)

            result = self.api.download_media(url, audio_only, quality, progress_callback=progress_callback)

            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if result["success"]:
                filename = os.path.basename(result['filename'])
                eel.updateDownloadList(f"Download completed: {filename}")
                log_entry = {
                    "result": "Success",
                    "date": date_str,
                    "url": url,
                    "folder": output_path
                }
            else:
                eel.updateDownloadList(f"Download failed: {result['error']}")
                log_entry = {
                    "result": "Failed",
                    "date": date_str,
                    "url": url,
                    "folder": output_path
                }
            eel.setProgressBar(0.0)
            self.download_logs.append(log_entry)
            self.save_logs()  # Save logs automatically
            eel.updateLogsTable(log_entry)
            eel.resetDownloadState()  # Reset the download state in the frontend

            self.download_queue.task_done()

    # Methods for handling settings
    def set_video_quality(self, quality):
        self.settings['video_quality'] = quality
        self.save_settings_to_file()

    def set_video_format(self, video_format):
        self.settings['video_format'] = video_format
        self.save_settings_to_file()

    def set_video_output_path(self, path):
        self.settings['video_output_path'] = path
        self.save_settings_to_file()

    def set_audio_format(self, audio_format):
        self.settings['audio_format'] = audio_format
        self.save_settings_to_file()

    def set_audio_output_path(self, path):
        self.settings['audio_output_path'] = path
        self.save_settings_to_file()

    def set_proxy(self, proxy):
        self.settings['proxy'] = proxy
        self.save_settings_to_file()

    def set_sublangs(self, sublangs):
        self.settings['sublangs'] = sublangs
        self.save_settings_to_file()

    def set_write_thumbnail(self, write_thumbnail):
        self.settings['write_thumbnail'] = write_thumbnail
        self.save_settings_to_file()

    def set_embed_thumbnail(self, embed_thumbnail):
        self.settings['embed_thumbnail'] = embed_thumbnail
        self.save_settings_to_file()

    def reset_settings(self):
        self.settings = {
            # Video Settings
            'video_quality': 'Best',
            'video_format': 'auto',
            'video_output_path': get_default_output_path(for_audio=False),

            # Audio Settings
            'audio_format': 'auto',
            'audio_output_path': get_default_output_path(for_audio=True),

            # Other Settings
            'proxy': None,
            'sublangs': None,
            'write_thumbnail': False,
            'embed_thumbnail': False
        }
        self.save_settings_to_file()
        return self.settings

    def get_logs(self):
        return self.download_logs

    def load_settings(self):
        return self.settings

    def save_settings_to_file(self):
        config_dir = get_config_path()
        settings_file = config_dir / "setting.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def load_settings_from_file(self):
        config_dir = get_config_path()
        settings_file = config_dir / "setting.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.save_settings_to_file()


app = None


# Expose top-level functions via @eel.expose to avoid naming collisions
@eel.expose
def add_to_queue(url, audio_only):
    global app
    app.add_to_queue(url, audio_only)


@eel.expose
def browse_output(output_type):
    global app
    app.browse_output(output_type)


@eel.expose
def set_browse_output(output_type, path):
    # This function is called from Python to JavaScript
    pass  # Handled in JavaScript


@eel.expose
def open_download_folder():
    global app
    app.open_download_folder()


@eel.expose
def open_logs_folder():
    global app
    app.open_logs_folder()


@eel.expose
def load_logs():
    global app
    app.load_logs()


@eel.expose
def load_settings():
    global app
    return app.load_settings()


@eel.expose
def reset_settings():
    global app
    settings = app.reset_settings()
    return settings


@eel.expose
def set_video_quality(quality):
    global app
    app.set_video_quality(quality)


@eel.expose
def set_video_format(video_format):
    global app
    app.set_video_format(video_format)


@eel.expose
def set_video_output_path(path):
    global app
    app.set_video_output_path(path)


@eel.expose
def set_audio_output_path(path):
    global app
    app.set_audio_output_path(path)


@eel.expose
def set_audio_format(audio_format):
    global app
    app.set_audio_format(audio_format)


@eel.expose
def set_proxy(proxy):
    global app
    app.set_proxy(proxy)


@eel.expose
def set_sublangs(sublangs):
    global app
    app.set_sublangs(sublangs)


@eel.expose
def set_write_thumbnail(write_thumbnail):
    global app
    app.set_write_thumbnail(write_thumbnail)


@eel.expose
def set_embed_thumbnail(embed_thumbnail):
    global app
    app.set_embed_thumbnail(embed_thumbnail)


@eel.expose
def resetDownloadState():
    # This function can be empty; it's called from Python to JavaScript
    pass


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "FFmpeg is not installed or not in the system PATH. Please install FFmpeg and add it to your system PATH.")
        sys.exit(1)


def on_close(page, sockets):
    print("Closing application...")
    sys.exit()

if __name__ == "__main__":
    check_ffmpeg()
    app = App()
    eel.init('web')
    eel.start('index.html', size=(1000, 800), close_callback=on_close)
