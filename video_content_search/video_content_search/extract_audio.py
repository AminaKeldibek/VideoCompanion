import argparse
from pathlib import Path
from pytubefix import YouTube
from pytubefix.cli import on_progress


def download_audio(youtube_url, output_path='.'):
    yt = YouTube(youtube_url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()

    audio_file = ys.download(output_path, mp3=True)
    print(f"Audio downloaded successfully as: {audio_file}")


def main():
    parser = argparse.ArgumentParser(
                        prog='Youtube audio downloader',
                        description='Downloads audio file from youtube video')
    parser.add_argument('youtube_url', help='youtube video url')
    parser.add_argument('-output_path', help='output path for audio file')

    args = parser.parse_args()

    download_audio(args.youtube_url, Path(args.output_path))


if __name__ == '__main__':
    main()
