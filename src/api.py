# api.py

import os
import yt_dlp
from typing import Dict, Any, Callable


class DownloaderAPI:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def download_media(self, url: str, audio_only: bool = False, quality: int = 0, output_filename: str = None,
                       progress_callback: Callable[[float, str], None] = None) -> Dict[str, Any]:
        quality_map = {
            0: 'bestvideo+bestaudio/best',
            1: 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            2: 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            3: 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            4: 'worstvideo+worstaudio/worst'
        }
        format_spec = quality_map[quality]

        if audio_only:
            format_spec = 'bestaudio/best'

        if output_filename:
            outtmpl = os.path.join(self.output_path, output_filename)
        else:
            outtmpl = os.path.join(self.output_path, '%(title)s.%(ext)s')

        def progress_hook(d):
            if d['status'] == 'downloading':
                progress = d['downloaded_bytes'] / d['total_bytes'] if d['total_bytes'] else 0
                if progress_callback:
                    progress_callback(progress, d['filename'])

        ydl_opts = {
            'format': format_spec,
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }

        if audio_only:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return {"success": True, "filename": filename, "info": info}
            except Exception as e:
                if "total_bytes" in str(e):
                    partial_file = ydl.prepare_filename(info) if 'info' in locals() else None
                    if partial_file and os.path.exists(partial_file):
                        os.remove(partial_file)
                return {"success": False, "error": str(e)}
