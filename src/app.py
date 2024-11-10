# app.py

import json
import os
import queue
import subprocess
import sys
import threading
from datetime import datetime

import eel

from world import get_default_output_path, get_config_path

from api import DownloaderAPI


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
            'embed_thumbnail': False,

            # Additional Settings
            'segments': 4,
            'retries': 5,
            'buffer_size': '16M'
        }

        self.load_settings_from_file()

    def load_settings(self):
        return self.settings

    def add_to_queue(self, url, audio_only):
        if not url:
            eel.updateDownloadList("Please enter a URL.")
            return

        self.download_queue.put((url, audio_only))
        eel.updateDownloadList(f"Added to queue: {url}")

    def browse_output(self, output_type):
        def run_dialog():
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            initial_dir = self.settings.get(f'{output_type}_output_path', '')
            path = filedialog.askdirectory(initialdir=initial_dir)
            root.destroy()
            if path:
                self.settings[f'{output_type}_output_path'] = path
                self.save_settings_to_file()
                eel.set_browse_output(output_type, path)
            else:
                eel.set_browse_output(output_type, None)

        threading.Thread(target=run_dialog).start()

    def open_download_folder(self):
        output_path = self.settings['audio_output_path'] if getattr(self, 'current_audio_only', False) else \
        self.settings['video_output_path']
        try:
            if sys.platform.startswith('win'):
                os.startfile(output_path)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(["open", output_path])
            else:
                subprocess.Popen(["xdg-open", output_path])
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
                quality = None  # Not applicable for audio-only downloads
            else:
                output_path = self.settings['video_output_path']
                quality = self.settings['video_quality']

            self.api.set_output_path(output_path)
            self.api.set_formats(self.settings['video_format'], self.settings['audio_format'])
            self.api.set_options(
                proxy=self.settings['proxy'],
                sublangs=self.settings['sublangs'],
                write_thumbnail=self.settings['write_thumbnail'],
                embed_thumbnail=self.settings['embed_thumbnail'],
                segments=self.settings['segments'],
                retries=self.settings['retries'],
                buffer_size=self.settings['buffer_size']
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

    def set_segments(self, segments):
        self.settings['segments'] = segments
        self.save_settings_to_file()

    def set_retries(self, retries):
        self.settings['retries'] = retries
        self.save_settings_to_file()

    def set_buffer_size(self, buffer_size):
        self.settings['buffer_size'] = buffer_size if self.api.validate_buffer_size(buffer_size) else '1M'
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
            'embed_thumbnail': False,

            # Additional Settings
            'segments': 4,
            'retries': 5,
            'buffer_size': '16M'
        }
        self.save_settings_to_file()
        return self.settings

    def get_logs(self):
        return self.download_logs

    def save_logs(self):
        logs_dir = get_config_path() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_filename = logs_dir / f"O2-{timestamp}.log"
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(self.download_logs, f, ensure_ascii=False, indent=4)

    def load_settings_from_file(self):
        config_dir = get_config_path()
        settings_file = config_dir / "setting.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.save_settings_to_file()

    def save_settings_to_file(self):
        config_dir = get_config_path()
        settings_file = config_dir / "setting.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
