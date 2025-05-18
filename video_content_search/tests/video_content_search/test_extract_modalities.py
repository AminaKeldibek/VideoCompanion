import pytest
import numpy as np
import cv2
from pathlib import Path
import pandas as pd
import json
import shutil
from video_content_search import extract_modalities
from tempfile import TemporaryDirectory


def create_test_video(path: Path, num_frames: int = 30, frame_size=(64, 64)):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(path), fourcc, 10.0, frame_size)

    for i in range(num_frames):
        frame = np.random.randint(0, 256, (frame_size[1], frame_size[0], 3), dtype=np.uint8)
        out.write(frame)

    out.release()


def test_extract_images_from_video():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        video_path = tmp_path / "test_video.mp4"
        output_path = tmp_path / "output"
        output_path.mkdir()

        create_test_video(video_path)

        extract_modalities.extract_images_from_video(
            video_input_path=str(video_path),
            video_output_path=output_path,
            video_id="testvideo",
            frame_interval=5,
        )

        # Check metadata file
        metadata_file = output_path / "video_metadata.json"
        assert metadata_file.exists()
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        assert "total_frames" in metadata

        # Check frame images
        frames_dir = output_path / "frames"
        frame_files = list(frames_dir.glob("*.jpg"))
        assert len(frame_files) > 0

        # Check frames metadata CSV
        frames_metadata_file = output_path / "frames_metadata.csv"
        assert frames_metadata_file.exists()
        df = pd.read_csv(frames_metadata_file)
        assert not df.empty
        assert all(df['write_status'])

        # Check frame filenames match expected pattern
        for fid in df['frame_id']:
            assert fid.startswith("testvideo_")
            assert (frames_dir / fid).exists()
