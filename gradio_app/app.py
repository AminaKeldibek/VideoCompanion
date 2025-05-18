import base64
import io
from PIL import Image
import soundfile as sf
import tempfile

import gradio as gr

import video_content_search.search.multimodal_vector_store as mvs


vs = mvs.WeviateMultimodal()
vs.connect_to_client()

collection_name = "youtube"
collection = vs.get_collection(collection_name)


def decode_base64_to_pil(b64_string: str) -> Image.Image:
    """Converts base64 image string to PIL.Image."""
    image_bytes = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_bytes))


def decode_base64_to_audio_file(b64_string: str) -> str:
    """Decode base64-encoded audio to a temp .wav file and return its path."""
    audio_bytes = base64.b64decode(b64_string)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        return f.name


def pil_to_base64(pil_img):
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return img_b64


def audio_tuple_to_base64(audio_tuple):
    sample_rate, data = audio_tuple
    buffer = io.BytesIO()
    sf.write(buffer, data, samplerate=sample_rate, format='WAV', subtype='PCM_16')
    wav_bytes = buffer.getvalue()

    return base64.b64encode(wav_bytes).decode('utf-8')


def search_multimodal(text, image, audio):
    search_query = None
    input_modality = None

    if audio:
        search_query = audio_tuple_to_base64(audio)
        input_modality = mvs.Modality.AUDIO
    elif text:
        search_query = text
        input_modality = mvs.Modality.TEXT
    elif image:
        search_query = pil_to_base64(image)
        input_modality = mvs.Modality.IMAGE
    else:
        raise ValueError("No input is provided!")

    response_text = vs.query_multimodal(
        collection,
        query=search_query,
        input_modality=input_modality,
        output_modality=mvs.Modality.TEXT
    )

    response_img = vs.query_multimodal(
        collection,
        query=search_query,
        input_modality=input_modality,
        output_modality=mvs.Modality.IMAGE
    )

    response_audio = vs.query_multimodal(
        collection,
        query=search_query,
        input_modality=input_modality,
        output_modality=mvs.Modality.AUDIO
    )

    i = 0
    return_text = "Result 1\n"
    return_text = response_text.objects[i].properties['text']
    return_text += f"\n similarity score: {response_text.objects[i].metadata.distance}"
    return_text += f"\n video_id: {response_text.objects[i].properties['video_id']}"
    return_text += f"\n timestamp: {response_text.objects[i].properties['timestamp']}"

    return_image = decode_base64_to_pil(response_img.objects[i].properties['image'])

    return_audio = decode_base64_to_audio_file(response_audio.objects[i].properties['audio'])

    return return_text, return_image, return_audio


demo = gr.Interface(
    fn=search_multimodal,
    inputs=["text", gr.Image(type="pil"), gr.Audio(type="numpy")],
    outputs=["text", gr.Image(type="pil"), gr.Audio(type="filepath")],
)

demo.launch()
