# api.py

import os
import yt_dlp
from typing import Dict, Any, Callable

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
                format_spec = f'bestvideo{quality_map.get(quality, "")}+bestaudio/best'
            else:
                # Prefer formats with the selected video extension
                format_spec = f'bestvideo{quality_map.get(quality, "")}[ext={self.video_format}]+bestaudio/best[ext=m4a]/best[ext={self.video_format}]/best'
                if quality == 'Worst':
                    format_spec = f'worst[ext={self.video_format}]/worst'

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

        # For audio-only downloads, handle format conversion
        if audio_only and self.audio_format != 'auto':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
                'preferredquality': '192',
            }]
            if self.options['embed_thumbnail']:
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
