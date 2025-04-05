import argparse
import json
import os
import whisper


def transcribe_russian(audio_path: str, output_path: str ='.'):
    """Creates transcription of an audio in russian language and records it in json."""
    model = whisper.load_model("small")

    result = model.transcribe(audio_path, language="ru")

    with open(output_path, 'w') as fi:
        json.dump(result, fi, indent=4)


def main():
    parser = argparse.ArgumentParser(
                        prog='',
                        description='Downloads audio file from youtube video')
    parser.add_argument('audio_path', help='path to audio file to transcribe')
    parser.add_argument('-output_path', help='output path for json transcription')

    args = parser.parse_args()

    transcribe_russian(os.path.expanduser(args.audio_path), os.path.expanduser(args.output_path))


if __name__ == '__main__':
    main()
