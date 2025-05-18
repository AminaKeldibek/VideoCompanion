import argparse
import json
from pathlib import Path

import cv2
from matplotlib import pyplot as plt
from moviepy import VideoFileClip
import numpy as np
import pandas as pd
from pytubefix import YouTube
from pytubefix.cli import on_progress


def download_audio_from_youtube_video(youtube_url: str, output_path: str = '.'):
    yt = YouTube(youtube_url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()

    audio_file = ys.download(output_path, mp3=True)
    print(f"Audio downloaded successfully as: {audio_file}")


def get_video_properties(cap: cv2.VideoCapture):
    properties = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'frame_height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    }

    return properties


def display_image(frame: np.ndarray):
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()


def extract_images_from_video(video_input_path: str, video_output_path: Path, video_id: str, frame_interval: int,
                              display_frames: bool = False):
    """ Extracts image frames from video and saves them as jpg files.
    Arguments:
        video_input_path: Path to the input video file.
        video_output_path: Path to the directory where output (frames, metadata) will be saved.
        video_id: An identifier for the video, used in naming output files.
        frame_interval: Interval at which frames are extracted (e.g., if 10, every 10th frame is saved).
        display_frames: if True, will display each frame saved
    """
    frames_path = Path(video_output_path / "frames/")
    frames_path.mkdir(parents=True, exist_ok=True)

    frame_ids = []
    frame_timestamp_ms = []
    write_status = []
    cap = cv2.VideoCapture(video_input_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file {video_input_path}")
        return

    properties = get_video_properties(cap)
    with open(Path(video_output_path / "video_metadata.json"), "w") as f:
        json.dump(properties, f, indent=4)

    frame_count = 0
    while frame_count < properties['total_frames']:
        is_read, frame = cap.read()
        if not is_read:
            print(f"Warning: Could not read frame at index {frame_count}. Stopping.")
            break

        if np.all(frame == frame[0, 0]):
            print(f"Skipping empty frame at index {frame_count} (all pixels have value {frame[0,0]}).")
            frame_count += 1
            continue

        if frame_count % frame_interval == 0:
            if display_frames:
                display_image(frame)
            img_id = f"{video_id}_{frame_count}.jpg"
            frame_ids.append(img_id)

            frame_timestamp_ms.append(int(cap.get(cv2.CAP_PROP_POS_MSEC)))

            is_done = cv2.imwrite(str(frames_path / img_id), frame)
            write_status.append(is_done)

        frame_count += 1

    frames_metadata = pd.DataFrame(data={
        'frame_id': frame_ids,
        'timestamp_ms': frame_timestamp_ms,
        'write_status': write_status
    })
    frames_metadata.to_csv(Path(video_output_path / "frames_metadata.csv"), index=False)


def extract_audio(video_input_path: str, video_output_path: Path):
    """ Extracts audio from video and saves it as wav. """
    video = VideoFileClip(video_input_path)
    video.audio.write_audiofile(Path(video_output_path / "audio.wav"))


def main():
    parser = argparse.ArgumentParser(
        prog='Youtube audio downloader',
        description='Downloads audio file from youtube video')
    parser.add_argument('youtube_url', help='youtube video url')
    parser.add_argument('-output_path', help='output path for audio file')

    args = parser.parse_args()

    download_audio_from_youtube_video(args.youtube_url, Path(args.output_path))


if __name__ == '__main__':
    main()
