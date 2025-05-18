from enum import Enum
import requests
from typing import List

import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import (
    Property,
    DataType,
    Configure,
    Tokenization,
    VectorDistances,
    VectorFilterStrategy
)
from weaviate.collections.collection.sync import Collection
from weaviate.classes.query import Filter

from video_content_search import logging_utils

imagebind_url = "http://localhost:8081/vectorize"  # adjust if needed


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class WeviateMultimodal:
    def __init__(self):
        self.return_properties = ["mediaType", "video_id", "timestamp", *[m.value for m in Modality]]
        self.return_metadata = ["distance", "certainty"]
        self.limit = 10

    def connect_to_client(self):
        self.client = weaviate.connect_to_local()
        logging_utils.logger.info(f"is_read: {self.client.is_ready()}")
        logging_utils.logger.info(f"metadata: {self.client.get_meta()}")

    def close_client(self):
        if self.client:
            self.client.close()

    def create_collection(self, collection_name: str):
        if self.client.collections.exists(collection_name):
            logging_utils.logger.info(f"Collection {collection_name} already exists")
            return

        self.client.collections.create(
            name=collection_name,

            vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
                audio_fields=[Modality.AUDIO.value],
                image_fields=[Modality.IMAGE.value],
                text_fields=[Modality.TEXT.value],
            ),

            properties=[
                Property(
                    name="path",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,  # Don't vectorize this property
                    description="Path to file, can be null",
                ),
                Property(
                    name=Modality.TEXT.value,
                    data_type=DataType.TEXT,
                    vectorize_property_name=False,  # Use "title" as part of the value to vectorize
                    tokenization=Tokenization.WORD  # Use "whitespace" tokenization
                ),
                Property(
                    name=Modality.IMAGE.value,
                    data_type=DataType.BLOB,
                    vectorize_property_name=False,  # Use "title" as part of the value to vectorize
                ),
                Property(
                    name=Modality.AUDIO.value,
                    data_type=DataType.BLOB,
                    vectorize_property_name=False,  # Use "title" as part of the value to vectorize
                ),
                Property(
                    name="media_type",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,  # Don't vectorize this property
                ),
                Property(
                    name="video_id",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,  # Don't vectorize this property
                ),

                Property(
                    name="timestamp",
                    data_type=DataType.INT,
                    skip_vectorization=True,  # Don't vectorize this property
                ),
            ],

            # Additional configuration not shown
            vector_index_config=Configure.VectorIndex.hnsw(
                # quantizer=Configure.VectorIndex.Quantizer.bq(),
                ef_construction=300,
                distance_metric=VectorDistances.COSINE,
                filter_strategy=VectorFilterStrategy.SWEEPING  # or ACORN (Available from Weaviate v1.27.0)
            ),
        )

    def get_collection(self, collection_name: str) -> object | None:
        if self.client.collections.exists(collection_name):
            return self.client.collections.get(collection_name)
        logging_utils.logger.warning(f"Collection {collection_name} is not found.")

        return None

    def delete_collection(self, collection_name: str):
        if self.client.collections.exists(collection_name):
            self.client.collections.delete(collection_name)
            logging_utils.logger.info(f"Successfully deleted collection {collection_name}")

    def batch_insert_items(self, items: List[dict], collection: object, batch_size: int = 10):
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            try:
                collection.data.insert_many(batch)
                print(f"✅ Inserted batch {i // batch_size + 1} ({len(batch)} items)")
            except Exception as e:
                logging_utils.logger.error(f"❌ Failed to insert batch {i // batch_size + 1}: {e}")

    def get_near_function(self, collection: Collection, input_modality: Modality):
        try:
            if input_modality == Modality.AUDIO:
                return collection.query.near_vector
            return getattr(collection.query, f"near_{input_modality.value}")
        except AttributeError:
            raise ValueError(f"Unsupported modality: {input_modality.value}")

    def query_multimodal(self, collection: Collection, query: str, input_modality: Modality,
                         output_modality: Modality | None = None) -> List[dict]:
        """
        Run a multimodal query on the collection.

        Args:
            collection: Weaviate collection object.
            query: Input query (string or vector depending on modality).
            input_modality: Modality of the input query (e.g., Modality.TEXT).
            output_modality: If provided, restricts results to a specific media type.

        Returns:
            A list of query results with metadata and return properties.
        """
        modality_filter = None
        if output_modality:
            modality_filter = Filter.by_property('mediaType').like(output_modality.value)

        if input_modality == Modality.AUDIO:
            imagebind_response = requests.post(imagebind_url, json={Modality.AUDIO.value: [query]})
            if imagebind_response.status_code != 200:
                raise RuntimeError(f"ImageBind service failed: {imagebind_response.text}")
            query = imagebind_response.json()['audioVectors'][0]

        near_func = self.get_near_function(collection, input_modality)

        return near_func(
            query,
            filters=modality_filter,
            return_properties=self.return_properties,
            limit=self.limit,
            return_metadata=self.return_metadata,
        )
