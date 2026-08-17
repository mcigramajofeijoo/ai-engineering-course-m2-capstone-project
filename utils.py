import time

import nltk
import numpy as np
from llama_index.core import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.storage.storage_context import DEFAULT_VECTOR_STORE
from nltk import word_tokenize

from classes.llama_idx import RetryFaissVectorStore
from paths import DOC_STORE_PATH, INDEX_STORE_PATH, VECTOR_STORE_PATH


def tokenize_words(text):
    try:
        # Safely check if the files already exist on your hard drive
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        # This block ONLY runs the very first time you ever trigger the function
        print("Downloading required NLTK dependency (one-time setup)...")
        nltk.download("punkt_tab", quiet=True)

    # Tokenize instantly from local disk cache
    return word_tokenize(text)


def prepare_embeddings(nodes, expected_dim):

    for idx, node in enumerate(nodes):
        embedding = node.embedding

        if embedding is None:
            raise ValueError(
                f"Node at index {idx} has no embedding. " f"Node ID: {node.node_id}"
            )

        embedding_dim = len(embedding)

        if embedding_dim != expected_dim:
            raise ValueError(
                f"Invalid embedding dimension at node {idx}. "
                f"Node ID: {node.node_id}. "
                f"Expected {expected_dim} dimensions, "
                f"but got {embedding_dim}."
            )

    # INFO: np.asarray() intenta evitar una copia innecesaria si el objeto que recibe ya es un ndarray compatible, mientras que np.array() por defecto puede crear una copia.
    embeddings = np.asarray([node.embedding for node in nodes], dtype=np.float32)

    # ––– Safety Net –––

    if embeddings.ndim != 2:
        # FAISS expects (n, D)
        raise ValueError(
            f"Expected embeddings with shape (n, d), " f"got {embeddings.shape}."
        )

    if embeddings.shape[1] != expected_dim:
        raise ValueError(
            f"Expected embedding dimension {expected_dim}, "
            f"got {embeddings.shape[1]}."
        )

    # Return
    return embeddings


# def ingest_with_retry(faiss_index, embeddings, ids, max_retries: int = 5):
#     retries = 0

#     while retries <= max_retries:
#         try:
#             print("Calling FAISS '.add_with_ids'")
#             faiss_index.add_with_ids(embeddings, ids)
#             break
#         except Exception as exc:
#             sleep_time = 2**retries
#             print(f"{type(exc).__name__}: Reintentando en {sleep_time}s...")
#             time.sleep(sleep_time)
#             retries += 1
#     else:
#         raise RuntimeError(
#             f"No se pudo ingerir el batch tras {max_retries} reintentos."
#         )


def get_storage_context_and_nodes():

    docstore = SimpleDocumentStore.from_persist_path(persist_path=str(DOC_STORE_PATH))

    if INDEX_STORE_PATH.exists():
        index_store = SimpleIndexStore.from_persist_path(
            persist_path=str(INDEX_STORE_PATH)
        )
    else:
        index_store = SimpleIndexStore()

    storage_context = StorageContext.from_defaults(
        docstore=docstore, index_store=index_store
    )

    if VECTOR_STORE_PATH.exists():
        vector_store = RetryFaissVectorStore.from_persist_path(
            persist_path=str(VECTOR_STORE_PATH)
        )

        storage_context.vector_stores[DEFAULT_VECTOR_STORE] = vector_store

    nodes = list(storage_context.docstore.docs.values())

    if not nodes:
        raise ValueError("No nodes found in persisted docstore.")

    return storage_context, nodes
