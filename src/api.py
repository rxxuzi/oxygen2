# src/api.py

import os
import yt_dlp
from typing import Dict, Any, Callable


class DownloaderAPI:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.format = "auto"       # 'auto', 'mp4', 'webm', 'mp3', 'wav'
        self.format_type = "video"  # 'video' or 'audio'

    def set_format(self, download_format: str, format_type: str):
        self.format = download_format
        self.format_type = format_type

    def download_media(
            self,
            url: str,
            audio_only: bool = False,
            quality: int = 0,
            output_filename: str = None,
            progress_callback: Callable[[float, str], None] = None
    ) -> Dict[str, Any]:
        quality_map = {
            0: 'bestvideo+bestaudio/best',
            1: 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            2: 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            3: 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            4: 'worstvideo+worstaudio/worst'
        }
        format_spec = quality_map.get(quality, 'best')

        if audio_only or self.format_type == "audio":
            format_spec = 'bestaudio/best'

        # Adjust output template based on format
        if self.format == "auto":
            outtmpl = os.path.join(self.output_path, '%(title)s.%(ext)s')
        else:
            outtmpl = os.path.join(self.output_path, f'%(title)s.{self.format}')

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
        }

        # Postprocessors for audio formats
        if audio_only or self.format_type == "audio":
            if self.format in ["mp3", "wav"]:
                preferred_codec = self.format
            else:
                preferred_codec = 'mp3'  # Default to mp3
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': preferred_codec,
                'preferredquality': '192',
            }]

        # Postprocessors for video formats
        if self.format in ["mp4", "webm"]:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': self.format,
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Update filename based on format
                if self.format in ["mp4", "webm", "mp3", "wav"]:
                    filename = os.path.splitext(filename)[0] + f".{self.format}"
                return {"success": True, "filename": filename, "info": info}
            except Exception as e:
                # Remove partial file if exists
                if "total_bytes" in str(e):
                    partial_file = ydl.prepare_filename(info) if 'info' in locals() else None
                    if partial_file and os.path.exists(partial_file):
                        os.remove(partial_file)
                return {"success": False, "error": str(e)}
