# app.py

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

import customtkinter as ctk

from api import DownloaderAPI


def get_default_output_path(for_audio=False):
    home = Path.home()
    if sys.platform == "win32":
        base_path = home / ("Music" if for_audio else "Videos")
    elif sys.platform == "darwin":
        base_path = home / ("Music" if for_audio else "Movies")
    else:  # Linux and other Unix-like OS
        base_path = home / ("Music" if for_audio else "Videos")

    output_path = base_path / "oxygen2"
    output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Oxygen2")
        self.geometry("800x600")

        # アイコンの設定
        icon_paths = [
            os.path.join(os.path.dirname(__file__), "..", "res", "oxygen2.ico"),
            os.path.join(os.path.dirname(__file__), "res", "oxygen2.ico"),
            "res/oxygen2.ico",
            "oxygen2.ico"
        ]

        icon_set = False
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.iconbitmap(icon_path)
                    print(f"Icon set successfully from: {icon_path}")
                    icon_set = True
                    break
                except Exception as e:
                    print(f"Failed to set icon from {icon_path}: {e}")

        if not icon_set:
            print("Warning: Failed to set any icon.")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter URL")
        self.url_entry.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")

        self.audio_var = ctk.BooleanVar()
        self.audio_checkbox = ctk.CTkCheckBox(self, text="Audio Only", variable=self.audio_var,
                                              command=self.update_output_path)
        self.audio_checkbox.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkOptionMenu(self, values=["Best", "High", "Medium", "Low", "Worst"],
                                              variable=self.quality_var)
        self.quality_menu.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        self.output_path = get_default_output_path()
        self.output_entry = ctk.CTkEntry(self)
        self.output_entry.insert(0, self.output_path)
        self.output_entry.grid(row=3, column=0, columnspan=2, padx=(20, 10), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_output)
        self.browse_button.grid(row=3, column=2, padx=(0, 20), pady=10)

        self.download_button = ctk.CTkButton(self, text="Download", command=self.add_to_queue)
        self.download_button.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        self.download_list = ctk.CTkTextbox(self, state="disabled")
        self.download_list.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        self.clear_console_button = ctk.CTkButton(self, text="Clear Console", command=self.clear_console)
        self.clear_console_button.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.open_folder_button = ctk.CTkButton(self, text="Open Folder", command=self.open_download_folder)
        self.open_folder_button.grid(row=6, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        self.api = DownloaderAPI(self.output_path)

        self.download_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.download_worker, daemon=True)
        self.worker_thread.start()

    def update_output_path(self):
        new_path = get_default_output_path(self.audio_var.get())
        self.output_path = new_path
        self.output_entry.delete(0, ctk.END)
        self.output_entry.insert(0, self.output_path)
        self.api.output_path = self.output_path

    def browse_output(self):
        new_path = ctk.filedialog.askdirectory(initialdir=self.output_path)
        if new_path:
            self.output_path = new_path
            self.output_entry.delete(0, ctk.END)
            self.output_entry.insert(0, self.output_path)
            self.api.output_path = self.output_path

    def add_to_queue(self):
        url = self.url_entry.get()
        audio_only = self.audio_var.get()
        quality = ["Best", "High", "Medium", "Low", "Worst"].index(self.quality_var.get())

        if url:
            self.download_queue.put((url, audio_only, quality))
            self.update_download_list(f"Added to queue: {url}")
            self.url_entry.delete(0, 'end')

    def download_worker(self):
        while True:
            url, audio_only, quality = self.download_queue.get()
            self.update_download_list(f"Downloading: {url}")

            def progress_callback(progress, filename):
                self.update_download_list(f"Progress for {os.path.basename(filename)}: {progress:.2%}")

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
        ctk.messagebox.showerror("Error", "FFmpeg is not installed or not in the system PATH. Please install FFmpeg "
                                          "and add it to your system PATH.")
        sys.exit(1)


if __name__ == "__main__":
    check_ffmpeg()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
