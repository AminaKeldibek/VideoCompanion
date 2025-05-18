# 🎥🔍 video_content_search

**video_content_search** is a multimodal search library that enables searching inside video content using **text**, **image**, or **audio** queries — and returns semantically relevant results from the transcript, screenshots, and soundbites of the video.

It includes:
- Data pipeline for prepare video modalities (images, text, audio) for inserting to vector store
- A vector database interface for Weaviate (`WeviateMultimodal`)
- Support for multimodal similarity search across text, image, and audio
- A Gradio-powered web app for demoing and exploring the search results

---

## ✨ Features

- 🔤 Text-based semantic search across video transcripts
- 🖼️ Image-based search for matching video frames
- 🔊 Audio-based search for retrieving soundbites
- ⏱️ Returns video ID and timestamp for all results
- 🧠 Multimodal embedding and retrieval using Weaviate vector DB

---

## 🚀 Demo App

### 🔧 Prerequisites

- Python 3.9+
- Weaviate running locally or remotely with multimodal objects loaded
- Poetry

### Run the App

```
cd gradio_app
poetry run python app.py
```

This launches a Gradio web UI where you can:

1. Enter text
2. Upload an image
3. Record or upload audio and
4. get matching text/image/audio chunks from the video with their video_id and timestamp.


🧠 How It Works
When a user submits a query:

* The app encodes it based on its modality (text/image/audio)
* Queries Weaviate for top-k similar results across all 3 modalities
* Decodes results (e.g., base64 images, audio bytes)
* Displays them in Gradio, along with their metadata

Each result includes:
- Semantic similarity score 
- Video ID 
- Timestamp in the video



