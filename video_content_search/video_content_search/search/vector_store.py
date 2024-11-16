from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_milvus import Milvus
from abc import ABC, abstractmethod
from langchain_core.documents.base import Document
from typing import List, Tuple
from uuid import uuid4
import os


class VectorStore(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    def delete_vectors(self, ids: List[str]):
        pass

    @abstractmethod
    def delete_vector_store(self):
        pass

    @abstractmethod
    def search_similar(self, query: str) -> List[Tuple[Document, float]]:
        pass


class MilvusVectorStore(VectorStore):

    EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    URI = os.path.expanduser("~/Projects/video_companion/podcast_transcripts.db")

    def __init__(self):
        embedding_model = SentenceTransformerEmbeddings(model_name=self.EMBEDDING_MODEL_NAME)

        self.vector_store = Milvus(
            embedding_function=embedding_model,
            connection_args={"uri": self.URI},
        )

        self.retriever = self.vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 10, "fetch_k": 10}
        )

    def add_documents(self, documents: List[Document]):
        """Change this logic to make sure that ids are unique."""
        video_id = '111xyz'
        uuids = [f"{video_id}_{str(uuid4())}" for _ in range(len(documents))]

        try:
            self.vector_store.add_documents(documents=documents, ids=uuids)
            print("Documents added successfully.")
        except Exception as e:
            print(f"Error adding documents: {e}")

    def delete_vectors(self, ids: List[str]):
        self.vector_store.delete(ids=ids)

    def delete_vector_store(self):
        os.remove(self.URI)

    def search_similar(self, query: str) -> List[Tuple[Document, float]]:
        """Each result is a list of tuple:
        Document: contains page_content and metadata
        Similarity Score
        """
        return self.vector_store.similarity_search_with_score(query)

