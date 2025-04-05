from video_content_search import preprocess

def test_concatenate_segments():
    segments = [
        {'text': 'Hello', 'start': 0, 'end': 1},
        {'text': 'world', 'start': 2, 'end': 3},
        {'text': 'This', 'start': 4, 'end': 5},
        {'text': 'is GPT', 'start': 6, 'end': 7},
        {'text': 'Nice to meet you!', 'start': 8, 'end': 10},
    ]

    output = [
        {'text': 'Hello world', 'start': 0, 'end': 3},
        {'text': 'This is GPT', 'start': 4, 'end': 7},
        {'text': 'Nice to meet you!', 'start': 8, 'end': 10}
    ]

    assert preprocess.concatenate_segments(segments, concat_size=2) == output

