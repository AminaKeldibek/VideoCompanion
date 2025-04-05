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
        """Adds documents in vector database."""
        pass

    @abstractmethod
    def delete_vectors(self, ids: List[str]):
        """Delete vectors from vector store by ids."""
        pass

    @abstractmethod
    def delete_vector_store(self):
        """Delete entire instance of vector database."""
        pass

    @abstractmethod
    def search_similar(self, query: str) -> List[Tuple[Document, float]]:
        """Returns similar vectors for input query.Each result is a list of tuple:
            Document: contains page_content and metadata
            Similarity Score
        """
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

    def add_documents(self, documents: List[Document]):
        """Adds documents in vector database.
        TODO: store ids separately."""
        video_id = "abc_123"
        uuids = [f"{video_id}_{str(uuid4())}" for _ in range(len(documents))]

        try:
            self.vector_store.add_documents(documents=documents, ids=uuids)
            print("Documents are added successfully!")
        except Exception as e:
            print("Failed to add documents: {e}")

    def delete_vectors(self, ids: List[str]):
        """Delete vectors from vector store by ids."""
        self.vector_store.delete(ids=ids)

    def delete_vector_store(self):
        """Delete entire instance of vector database."""
        os.remove(self.URI)
        print("Database is deleted successfully!")

    def search_similar(self, query: str) -> List[Tuple[Document, float]]:
        """Returns similar vectors for input query.Each result is a list of tuple:
            Document: contains page_content and metadata
            Similarity Score
        """
        return self.vector_store.similarity_search_with_score(query)

