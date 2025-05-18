import base64
import json
import math
import os
import io
from pathlib import Path
from typing import Any, Dict, List

from pydub import AudioSegment
from langchain.docstore.document import Document
import pandas as pd


def concatenate_segments(segments: List[Dict['str', Any]], concat_size: int) -> List[Dict[str, Any]]:
    """Concatenates transcription segments into bigger text segments of concat_size."""
    concatenated_segments = []

    for i in range(math.ceil(len(segments) / concat_size)):
        output = {}

        start_idx = i * concat_size
        end_idx = min(start_idx + concat_size, len(segments))

        output['text'] = ' '.join([segment['text'] for segment in segments[start_idx: end_idx]])
        output['start'] = min([segment['start'] for segment in segments[start_idx: end_idx]])
        output['end'] = max([segment['end'] for segment in segments[start_idx: end_idx]])

        concatenated_segments.append(output)

    return concatenated_segments


def load_documents(segments: List[Dict['str', Any]]) -> List[Document]:
    """Creates list of Langchain Documents with text and corresponding metadata."""
    docs = []
    for segment in segments:
        docs.append(Document(
            page_content=segment["text"],
            metadata={
                "start_timestamp": segment["start"],
                "end_timestamp": segment["end"]
            })
        )

    return docs


def chunk_transcript(transcription_path: Path):
    with open(transcription_path, 'r') as fi:
        transcription = json.load(fi)

    concat_sizes = [3, 5, 20, 30]
    segments = []
    concat_segments = []

    for segment in transcription['segments']:
        segments.append({k: segment[k] for k in ('text', 'start', 'end')})

    for concat_size in concat_sizes:
        concat_segments += concatenate_segments(segments, concat_size=concat_size)

    return concat_segments


def create_documents(transcription_path: Path) -> List[Document]:
    docs = []
    chunks = chunk_transcript(transcription_path)
    for c in chunks:
        docs += load_documents(c)
    return docs


def format_text_chunks(chunks: List[Dict[str, Any]], video_id: str):
    chunks_formatted = []
    for chunk in chunks:
        d = {"path": '',
             "text": chunk['text'],
             "mediaType": "text",
             "video_id": video_id,
             "timestamp": int(chunk['start'] * 1000)}

        chunks_formatted.append(d)

    return chunks_formatted


def file_to_base64(path: str) -> str:
    """Helper function to convert a file to base64 representation."""
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def audiosegment_to_base64(audio_segment: AudioSegment) -> str:
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="wav")

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def collect_frames(video_output_path: Path, video_id: str):
    frames_path = Path(video_output_path / "frames/")
    frame_metadata_path = Path(video_output_path / "frames_metadata.csv")

    source = [f for f in os.listdir(frames_path) if f != '.DS_Store']
    items = list()
    frames_df = pd.read_csv(frame_metadata_path)

    for name in source:
        path = str(frames_path) + '/' + name

        items.append({
            "path": name,
            "image": file_to_base64(path),
            "mediaType": "image",
            "video_id": video_id,
            "timestamp": int(frames_df[frames_df['frame_id'] == name].timestamp_ms.values[0])
        })

    return items


def collect_audio_chunks(video_output_path: Path, video_id: str, chunk_duration_ms: int):
    audio = AudioSegment.from_wav(Path(video_output_path / "audio.wav"))
    audio_chunks = []

    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i+chunk_duration_ms]
        audio_chunks.append({
            "path": f"chunk_{i}_{chunk_duration_ms}",
            "audio": audiosegment_to_base64(chunk),
            "mediaType": "audio",
            "video_id": video_id,
            "timestamp": i,
        })

    return audio_chunks

