# main.py
import argparse
import os
from api import DownloaderAPI


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_path = os.path.join(os.path.dirname(script_dir), 'gen')

    parser = argparse.ArgumentParser(description='Download video or audio from URL.')
    parser.add_argument('url', help='URL of the media to download')
    parser.add_argument('-a', '--audio', action='store_true', help='Download audio only (mp3)')
    parser.add_argument('-q', '--quality', type=int, choices=[0, 1, 2], default=0,
                        help='Video quality (0: best, 1: medium, 2: worst)')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-d', '--directory', default=default_output_path, help='Output directory')
    args = parser.parse_args()

    api = DownloaderAPI(args.directory)

    try:
        result = api.download_media(args.url, args.audio, args.quality, args.output)
        if result["success"]:
            print(f"Download completed: {result['filename']}")
        else:
            print(f"Download failed: {result['error']}")
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
