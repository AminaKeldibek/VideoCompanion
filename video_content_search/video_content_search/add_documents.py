import argparse
import os

from video_content_search.search.vector_store import MilvusVectorStore
from video_content_search import preprocess
from pathlib import Path


def add_video_content_to_vectorstore(transcription_json_path):
    documents = preprocess.create_documents(Path(transcription_json_path))
    vector_store = MilvusVectorStore()

    vector_store.add_documents(documents)


def main():
    parser = argparse.ArgumentParser(
                        prog='Preprocesses transcription output and adds documents in vectorstore',
                        description='Downloads audio file from youtube video')
    parser.add_argument('transcription_json_path', help='path to transcription json file')

    args = parser.parse_args()
    add_video_content_to_vectorstore(os.path.expanduser(args.transcription_json_path))


if __name__ == '__main__':
    main()