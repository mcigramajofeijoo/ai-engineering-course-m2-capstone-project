import numpy as np

from llama_index.core.embeddings import BaseEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import time

# from utils import ingest_with_retry


# WARNING: We put it here because if not causes circular import, project structure needs to be improved.
def ingest_with_retry(faiss_index, embeddings, ids, max_retries: int = 5):
    retries = 0

    while retries <= max_retries:
        try:
            print("Calling FAISS '.add_with_ids'")
            faiss_index.add_with_ids(embeddings, ids)
            break
        except Exception as exc:
            sleep_time = 2**retries
            print(f"{type(exc).__name__}: Reintentando en {sleep_time}s...")
            time.sleep(sleep_time)
            retries += 1
    else:
        raise RuntimeError(
            f"No se pudo ingerir el batch tras {max_retries} reintentos."
        )


class RetryFaissVectorStore(FaissVectorStore):

    def add(self, nodes, **kwargs):
        embeddings = np.asarray(
            [node.get_embedding() for node in nodes], dtype=np.float32
        )

        # NOTE:
        # Node embeddings are stored unnormalized.
        # Normalize before insertion because the index uses inner product
        # to implement cosine similarity.
        faiss.normalize_L2(embeddings)

        _IDS = np.asarray([int(node.node_id) for node in nodes], dtype=np.int64)

        ingest_with_retry(self._faiss_index, embeddings, _IDS)

        return [node.node_id for node in nodes]

    def query(self, query, **kwargs):

        # INFO: Debug Logs (Make sure the query embedding is reaching FAISS normalized by the embedding model we provided to the VectorStoreIndex)
        query_embedding = np.asarray(
            query.query_embedding,
            dtype=np.float32,
        )

        print("Query norm BEFORE FAISS:", np.linalg.norm(query_embedding))
        print("FAISS metric:", self._faiss_index.metric_type)

        return super().query(query, **kwargs)


class NormalizedEmbeddingModel(BaseEmbedding):
    model: BaseEmbedding

    def __init__(self, model: BaseEmbedding, **kwargs):
        super().__init__(model=model, **kwargs)

    @staticmethod
    def _normalize_embedding(embedding):
        embedding = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(
            1, -1
        )  # WARNING: El reshape es únicamente una representación temporal para satisfacer la API de FAISS. Si usamos Numpy para normalizar, no necesitamos este reshape.

        norm = np.linalg.norm(embedding)

        if norm == 0:
            raise ValueError("Cannot normalize a zero-vector embedding.")

        faiss.normalize_L2(embedding)
        return embedding[0].tolist()

    def _get_query_embedding(self, query):
        # Se utiliza para representar la consulta del usuario.
        embedding = self.model.get_query_embedding(query)

        return self._normalize_embedding(embedding)

    def _get_text_embedding(self, text):
        # Se utiliza para representar documentos/textos que van a ser almacenados en el índice.
        embedding = self.model.get_text_embedding(text)

        return self._normalize_embedding(embedding)

    async def _aget_query_embedding(self, query):
        # Esto permite que LlamaIndex pueda ejecutar operaciones de embedding de manera concurrente cuando el pipeline utiliza asyncio.
        embedding = await self.model.aget_query_embedding(query)

        return self._normalize_embedding(embedding)

    async def _aget_text_embedding(self, text):
        embedding = await self.model.aget_text_embedding(text)

        return self._normalize_embedding(embedding)
