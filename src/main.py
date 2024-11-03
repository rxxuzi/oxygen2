# main.py

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox, filedialog

from api import DownloaderAPI


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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Oxygen2")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Custom theme setup
        ctk.set_appearance_mode("dark")  # Options: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # Icon setup
        icon_path = resource_path("oxygen2.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
                print(f"Icon set successfully from: {icon_path}")
            except Exception as e:
                print(f"Failed to set icon from {icon_path}: {e}")
        else:
            print("Warning: Icon file not found.")

        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabview.add("Main")
        self.tabview.add("Settings")
        self.tabview.set("Main")

        # Setup tabs
        self.setup_main_tab()
        self.setup_settings_tab()

        # Initialize DownloaderAPI
        self.api = DownloaderAPI(self.output_path)

        # Initialize download queue and worker thread
        self.download_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.download_worker, daemon=True)
        self.worker_thread.start()

    def setup_main_tab(self):
        main_tab = self.tabview.tab("Main")
        main_tab.grid_columnconfigure(0, weight=1)
        main_tab.grid_rowconfigure(0, weight=1)

        # メインフレーム
        main_frame = ctk.CTkFrame(main_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # URL入力セクション
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", pady=(0, 10))

        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Enter YouTube URL",
            font=("Helvetica", 14)
        )
        self.url_entry.pack(fill="x")

        # オプションセクション
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        self.audio_var = ctk.BooleanVar()
        self.audio_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Audio Only",
            variable=self.audio_var,
            command=self.update_output_path,
            font=("Helvetica", 12)
        )
        self.audio_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["Best", "High", "Medium", "Low", "Worst"],
            variable=self.quality_var,
            dropdown_font=("Helvetica", 12)
        )
        self.quality_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        options_frame.grid_columnconfigure(1, weight=1)

        # 出力パスセクション
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="x", pady=(0, 10))

        self.output_path = get_default_output_path()
        self.output_entry = ctk.CTkEntry(
            output_frame,
            font=("Helvetica", 14)
        )
        self.output_entry.insert(0, self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_button = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.browse_output,
            font=("Helvetica", 12)
        )
        self.browse_button.pack(side="right")

        # ダウンロードボタン
        self.download_button = ctk.CTkButton(
            main_frame,
            text="Download",
            command=self.add_to_queue,
            font=("Helvetica", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.download_button.pack(fill="x", pady=(0, 10))

        # プログレスバー
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)

        # ダウンロードリスト
        self.download_list = ctk.CTkTextbox(
            main_frame,
            state="disabled",
            font=("Helvetica", 12)
        )
        self.download_list.pack(fill="both", expand=True, pady=(0, 10))

        # アクションボタンセクション
        actions_frame = ctk.CTkFrame(main_frame)
        actions_frame.pack(fill="x")

        self.clear_console_button = ctk.CTkButton(
            actions_frame,
            text="Clear Console",
            command=self.clear_console,
            font=("Helvetica", 12),
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        self.clear_console_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.open_folder_button = ctk.CTkButton(
            actions_frame,
            text="Open Folder",
            command=self.open_download_folder,
            font=("Helvetica", 12),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.open_folder_button.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def setup_settings_tab(self):
        settings_tab = self.tabview.tab("Settings")
        settings_tab.grid_columnconfigure(0, weight=1)
        settings_tab.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(settings_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Download Format Label
        format_label = ctk.CTkLabel(
            frame,
            text="Select Download Format:",
            anchor="w",
            font=("Helvetica", 16)
        )
        format_label.pack(fill="x", pady=(0, 10))

        # Tabview for Video and Audio Formats
        format_tabview = ctk.CTkTabview(frame)
        format_tabview.pack(fill="both", expand=True)
        format_tabview.add("Video")
        format_tabview.add("Audio")
        format_tabview.set("Video")

        # Video Format Tab
        video_tab = format_tabview.tab("Video")
        video_tab.grid_columnconfigure(0, weight=1)
        video_tab.grid_rowconfigure(0, weight=1)

        video_frame = ctk.CTkFrame(video_tab)
        video_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.video_format_var = ctk.StringVar(value="auto")
        video_formats = ["auto", "mp4", "webm"]
        self.video_format_menu = ctk.CTkOptionMenu(
            video_frame,
            values=video_formats,
            variable=self.video_format_var,
            dropdown_font=("Helvetica", 12)
        )
        self.video_format_menu.pack(fill="x", pady=10)

        # Audio Format Tab
        audio_tab = format_tabview.tab("Audio")
        audio_tab.grid_columnconfigure(0, weight=1)
        audio_tab.grid_rowconfigure(0, weight=1)

        audio_frame = ctk.CTkFrame(audio_tab)
        audio_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.audio_format_var = ctk.StringVar(value="auto")
        audio_formats = ["auto", "mp3", "wav"]
        self.audio_format_menu = ctk.CTkOptionMenu(
            audio_frame,
            values=audio_formats,
            variable=self.audio_format_var,
            dropdown_font=("Helvetica", 12)
        )
        self.audio_format_menu.pack(fill="x", pady=10)

    def update_output_path(self):
        new_path = get_default_output_path(self.audio_var.get())
        self.output_path = new_path
        self.output_entry.delete(0, ctk.END)
        self.output_entry.insert(0, self.output_path)
        self.api.output_path = self.output_path

    def browse_output(self):
        new_path = filedialog.askdirectory(initialdir=self.output_path)
        if new_path:
            self.output_path = new_path
            self.output_entry.delete(0, ctk.END)
            self.output_entry.insert(0, self.output_path)
            self.api.output_path = self.output_path

    def add_to_queue(self):
        url = self.url_entry.get()
        audio_only = self.audio_var.get()
        quality = ["Best", "High", "Medium", "Low", "Worst"].index(self.quality_var.get())

        if audio_only:
            download_format = self.audio_format_var.get()
            format_type = "audio"
        else:
            download_format = self.video_format_var.get()
            format_type = "video"

        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL.")
            return

        self.download_queue.put((url, audio_only, quality, download_format, format_type))
        self.update_download_list(f"Added to queue: {url}")
        self.url_entry.delete(0, 'end')

    def download_worker(self):
        while True:
            url, audio_only, quality, download_format, format_type = self.download_queue.get()
            self.update_download_list(f"Downloading: {url}")

            # プログレスバーをリセット
            self.progress_bar.set(0)

            # Set format in API
            self.api.set_format(download_format, format_type)

            def progress_callback(progress, filename):
                self.update_download_list(f"Progress for {os.path.basename(filename)}: {progress:.2%}")
                self.progress_bar.set(progress)

            result = self.api.download_media(url, audio_only, quality, progress_callback=progress_callback)

            if result["success"]:
                self.update_download_list(f"Download completed: {os.path.basename(result['filename'])}")
            else:
                self.update_download_list(f"Download failed: {result['error']}")

            self.download_queue.task_done()

    def update_download_list(self, message):
        def update():
            self.download_list.configure(state="normal")
            self.download_list.insert("end", message + "\n")
            self.download_list.see("end")
            self.download_list.configure(state="disabled")

        self.after(0, update)

    def clear_console(self):
        self.download_list.configure(state="normal")
        self.download_list.delete("1.0", ctk.END)
        self.download_list.configure(state="disabled")

    def open_download_folder(self):
        if sys.platform == "win32":
            os.startfile(self.output_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.output_path])
        else:
            subprocess.Popen(["xdg-open", self.output_path])


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror(
            "Error",
            "FFmpeg is not installed or not in the system PATH. Please install FFmpeg "
            "and add it to your system PATH."
        )
        sys.exit(1)


if __name__ == "__main__":
    check_ffmpeg()
    app = App()
    app.mainloop()
