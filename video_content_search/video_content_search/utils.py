from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


def display_image(frame: np.ndarray):
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()


def get_video_id_to_path(input_videos_path: Path, extracted_data_path: Path):
    files = [f for f in input_videos_path.iterdir() if f.is_file()]

    video_id_to_path = {}

    for i in range(len(files)):
        video_id = files[i].stem.lower()
        video_id_to_path[video_id] = Path(extracted_data_path / video_id)

    return video_id_to_path
