from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional


from video_content_search.search import retrieve_logic
from video_content_search.search.vector_store import MilvusVectorStore


app = FastAPI()
vector_store = MilvusVectorStore()

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "chrome-extension://eccpoojjhhiefghcpelkhckjilkifkfd"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    video_id: str = Field(..., description='youtube video id', example='123')
    query: str = Field(..., description='search query', example='where in the video they talk about pride')
    user_id: Optional[str] = Field(None, description='user_id', example='123abc')


def search_video_for_timestamp(video_id: str, query: str) -> float:
    try:
        result = retrieve_logic.search_timestamp(vector_store, query)
    except Exception as e:
        print("Couldn't query vector database")
        return None

    return result.get('timestamp')


@app.post("/search_video")
async def search_video(data: SearchRequest):
    timestamp = search_video_for_timestamp(data.video_id, data.query)

    if timestamp is None:
        raise HTTPException(status_code=404, detail='Timestamp not found for the given query')

    return {
        "video_id": data.video_id,
        "timestamp": timestamp
    }
