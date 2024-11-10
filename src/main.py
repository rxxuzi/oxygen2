# main.py

import sys
import eel
from app import App
from world import check_ffmpeg, log_error

app = None

# Expose top-level functions via @eel.expose to avoid naming collisions
@eel.expose
def add_to_queue(url, audio_only):
    try:
        global app
        app.add_to_queue(url, audio_only)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error adding to queue: {e}")


@eel.expose
def browse_output(output_type):
    try:
        global app
        app.browse_output(output_type)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error browsing output: {e}")


@eel.expose
def set_browse_output(output_type, path):
    # This function is called from Python to JavaScript
    pass  # Handled in JavaScript


@eel.expose
def open_download_folder():
    try:
        global app
        app.open_download_folder()
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error opening download folder: {e}")


@eel.expose
def open_logs_folder():
    try:
        global app
        app.open_logs_folder()
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error opening logs folder: {e}")


@eel.expose
def load_logs():
    try:
        global app
        app.load_logs()
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error loading logs: {e}")


@eel.expose
def load_settings():
    try:
        global app
        return app.load_settings()
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error loading settings: {e}")
        return {}


@eel.expose
def reset_settings():
    try:
        global app
        settings = app.reset_settings()
        return settings
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error resetting settings: {e}")
        return {}


@eel.expose
def set_video_quality(quality):
    try:
        global app
        app.set_video_quality(quality)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting video quality: {e}")


@eel.expose
def set_video_format(video_format):
    try:
        global app
        app.set_video_format(video_format)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting video format: {e}")


@eel.expose
def set_video_output_path(path):
    try:
        global app
        app.set_video_output_path(path)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting video output path: {e}")


@eel.expose
def set_audio_format(audio_format):
    try:
        global app
        app.set_audio_format(audio_format)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting audio format: {e}")


@eel.expose
def set_audio_output_path(path):
    try:
        global app
        app.set_audio_output_path(path)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting audio output path: {e}")


@eel.expose
def set_proxy(proxy):
    try:
        global app
        app.set_proxy(proxy)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting proxy: {e}")


@eel.expose
def set_sublangs(sublangs):
    try:
        global app
        app.set_sublangs(sublangs)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting subtitle languages: {e}")


@eel.expose
def set_write_thumbnail(write_thumbnail):
    try:
        global app
        app.set_write_thumbnail(write_thumbnail)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting write_thumbnail: {e}")


@eel.expose
def set_embed_thumbnail(embed_thumbnail):
    try:
        global app
        app.set_embed_thumbnail(embed_thumbnail)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting embed_thumbnail: {e}")


@eel.expose
def set_segments(segments):
    try:
        global app
        app.set_segments(segments)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting segments: {e}")


@eel.expose
def set_retries(retries):
    try:
        global app
        app.set_retries(retries)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting retries: {e}")


@eel.expose
def set_buffer_size(buffer_size):
    try:
        global app
        app.set_buffer_size(buffer_size)
    except Exception as e:
        log_error(str(e))
        eel.updateDownloadList(f"Error setting buffer size: {e}")


@eel.expose
def resetDownloadState():
    # This function is called from Python to JavaScript to reset download state
    pass  # The frontend handles the reset


def on_close(page, sockets):
    print("Closing application...")
    sys.exit()


if __name__ == "__main__":
    check_ffmpeg()
    app = App()
    eel.init('web')
    eel.start('index.html', size=(1000, 800), close_callback=on_close)
