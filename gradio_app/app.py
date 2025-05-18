import atexit
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

num_results = 3

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


def format_metadata(obj):
    return (
        f"\nSimilarity score: {obj.metadata.distance:.4f}"
        f"\nVideo ID: {obj.properties.get('video_id', 'N/A')}"
        f"\nTimestamp: {obj.properties.get('timestamp', 'N/A')}"
    )


def handle_input_change(text, image, audio, source):
    if source == "text" and text.strip():
        return (
            gr.update(interactive=True),
            gr.update(value=None, interactive=False),
            gr.update(value=None, interactive=False),
        )
    elif source == "image" and image:
        return (
            gr.update(value=None, interactive=False),
            gr.update(interactive=True),
            gr.update(value=None, interactive=False),
        )
    elif source == "audio" and audio is not None:
        return (
            gr.update(value=None, interactive=False),
            gr.update(value=None, interactive=False),
            gr.update(interactive=True),
        )
    else:
        # If cleared, re-enable all
        return (
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
        )


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

    text_results = []
    images = []
    image_metadata = []
    audios = []
    audio_metadata = []

    for i in range(num_results):
        r = response_text.objects[i]
        text_results.append(r.properties['text'] + format_metadata(r))

        images.append(decode_base64_to_pil(response_img.objects[i].properties['image']))
        image_metadata.append(format_metadata(response_img.objects[i]))

        audios.append(decode_base64_to_audio_file(response_audio.objects[i].properties['audio']))
        audio_metadata.append(format_metadata(response_audio.objects[i]))

    return text_results + images + image_metadata + audios + audio_metadata


with gr.Blocks() as demo:
    text_input = gr.Textbox(label="Text Input")
    image_input = gr.Image(type="pil", label="Image Input")
    audio_input = gr.Audio(type="numpy", label="Audio Input")

    text_input.change(
        fn=lambda text, image, audio: handle_input_change(text, image, audio, "text"),
        inputs=[text_input, image_input, audio_input],
        outputs=[text_input, image_input, audio_input]
    )

    image_input.change(
        fn=lambda text, image, audio: handle_input_change(text, image, audio, "image"),
        inputs=[text_input, image_input, audio_input],
        outputs=[text_input, image_input, audio_input]
    )

    audio_input.change(
        fn=lambda text, image, audio: handle_input_change(text, image, audio, "audio"),
        inputs=[text_input, image_input, audio_input],
        outputs=[text_input, image_input, audio_input]
    )

    btn = gr.Button("Search")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Text results")
            text_boxes = [gr.Textbox(label=f"Result {i+1}") for i in range(num_results)]

        with gr.Column():
            gr.Markdown("### Image results")
            img_outputs = [gr.Image(type="pil") for _ in range(num_results)]
            img_metas = [gr.Textbox(label=f"Metadata {i+1}", interactive=False) for i in range(num_results)]

        with gr.Column():
            gr.Markdown("### Audio results")
            audio_outputs = [gr.Audio(type="filepath") for _ in range(num_results)]
            audio_metas = [gr.Textbox(label=f"Metadata {i+1}", interactive=False) for i in range(num_results)]

    btn.click(
        fn=search_multimodal,
        inputs=[text_input, image_input, audio_input],
        outputs=text_boxes + img_outputs + img_metas + audio_outputs + audio_metas
    )

demo.launch()
atexit.register(vs.close_client)
