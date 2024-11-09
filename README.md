# Oxygen2

Oxygen2 is a powerful and user-friendly YouTube downloader built with Python and Electron (using Eel). 
It allows you to download videos and audio from Website.

## Features

- **Download Videos and Audio**: Download videos or extract audio only.
- **Flexible Format Selection**: Choose from various video formats (MP4, MOV, WebM) and audio formats (MP3, WAV, AAC).
- **Quality Settings**: Select the desired quality (Best, High, Medium, Low, Worst).
- **Proxy Support**: Configure a proxy server for your downloads.

## Prerequisites

- **Python 3.6+**
- **Node.js and npm (for Electron if needed)**
- **FFmpeg**: Ensure FFmpeg is installed and added to your system's PATH.

## Quick start

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/rxxuzi/oxygen2.git
   cd oxygen2
   ```

2. **Install Python Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**:

    - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html#build-windows) and add to PATH.
    - **macOS**: Use Homebrew `brew install ffmpeg`.
    - **Linux**: Install via package manager `sudo apt-get install ffmpeg`.

4. **Install Node.js and npm** (if planning to integrate with Electron):

   Download from [Node.js website](https://nodejs.org/).

## Usage

1. **Run the Application**:

   ```bash
   python src/main.py
   ```

2. **Using the Interface**:

    - **Main Tab**:
        - Enter the URL.
        - Check "Audio Only" if you want to download audio.
        - Select the desired quality.
        - Specify the output path or use the default.
        - Click "Download".
    - **Settings Tab**:
        - Choose video and audio formats.
        - Set additional options like proxy, subtitle languages, and yt-dlp flags.
    - **Logs Tab**:
        - View the download logs.
        - Save logs by clicking "Save Logs".

3. **Open Download Folder**:

    - Click the "Open Folder" button to open the output directory.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE)

## Acknowledgments

- **yt-dlp**: A youtube-dl fork with additional features and fixes.
- **Eel**: For bridging Python and JavaScript to create the desktop application.
