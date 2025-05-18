import argparse
import json
import os
from pathlib import Path

import whisper


def transcribe_audio(audio_path: str, output_path: str = '.', language: str = None):
    """Creates transcription of an audio in language passed or detected and records it in json."""
    model = whisper.load_model("small")
    if not language:
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)

        language = max(probs, key=probs.get)
        print (f"Detected language {language}")

    result = model.transcribe(audio_path, language=language)

    with open(Path(output_path / "transcription.json"), 'w') as fi:
        json.dump(result, fi, indent=4)


def main():
    parser = argparse.ArgumentParser(
                        prog='',
                        description='Downloads audio file from youtube video')
    parser.add_argument('audio_path', help='path to audio file to transcribe')
    parser.add_argument('-output_path', help='output path for json transcription')
    parser.add_argument('-language', help='audio language')

    args = parser.parse_args()

    transcribe_audio(os.path.expanduser(args.audio_path), os.path.expanduser(args.output_path), args.language)


if __name__ == '__main__':
    main()
