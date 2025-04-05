import json
import math
from typing import Any, Dict, List
from langchain.docstore.document import Document
from pathlib import Path


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


def create_documents(transcript_file: Path) -> List[Document]:
    with open(transcript_file, 'r') as fi:
        transcription = json.load(fi)

    segments = []
    docs = []
    concat_sizes = [3, 5, 20, 50]

    for segment in transcription['segments']:
        segments.append({k: segment[k] for k in ('text', 'start', 'end')})

    for concat_size in concat_sizes:
        docs += load_documents(concatenate_segments(segments, concat_size=concat_size))

    return docs
