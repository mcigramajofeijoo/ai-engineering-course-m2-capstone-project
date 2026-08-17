from dotenv import load_dotenv

load_dotenv()

from llama_index.core import VectorStoreIndex
from llama_index.core.storage.storage_context import DEFAULT_VECTOR_STORE

from constants import EMBEDDING_DIMENSIONS
from paths import INDEX_STORE_PATH, VECTOR_STORE_PATH
from utils import get_storage_context_and_nodes, prepare_embeddings
import faiss
from classes.llama_idx import RetryFaissVectorStore

# WARNING: Dummy values, not optimized
NLIST = 50  # NOTE: En datasets grandes, FAISS recomienda calcular la cantidad de NLIST de la siguiente manera: 2/4/16 * sqrt(num_nodes), el resultado de la multiplicacion por "2" siendo el minimo.
PQ_M = 32
PQ_NBITS = 1
NPROBE = 5


def build_ivfpq_index(active_nodes):

    # 1. Get embeddings
    embeddings = prepare_embeddings(active_nodes, EMBEDDING_DIMENSIONS)

    # print(type(embeddings), embeddings[0][:100])

    # 2. Revalidate dimensions
    dimensions = embeddings.shape[1]
    if dimensions != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Embedding dimension is {dimensions}, "
            f"but expected {EMBEDDING_DIMENSIONS}."
        )

    # 3. Normalize embeddings (to use cosine similarity)
    faiss.normalize_L2(embeddings)

    # 4. Create quantizer (this is going to search for NLIST centroids)
    coerce_quantizer = faiss.IndexFlatIP(dimensions)

    # 5. Validate embeddings dimensions is divisible by PQ_M
    if (dimensions % PQ_M) != 0:
        raise ValueError(
            f"Embedding dimension ({dimensions}) must be divisible "
            f"by PQ_M ({PQ_M})."
        )

    # 6. Create Index
    index = faiss.IndexIVFPQ(
        coerce_quantizer, dimensions, NLIST, PQ_M, PQ_NBITS, faiss.METRIC_INNER_PRODUCT
    )

    # 7. Train Index
    train_embeddings = embeddings

    index.train(train_embeddings)

    if not index.is_trained:
        raise RuntimeError("FAISS IVF-PQ index was not successfully trained.")

    # INFO: Addition is being made through Llama Index (VectorStoreIndex) when persisting the index.

    # 8. Configure Index
    if NPROBE > NLIST:
        raise ValueError(f"NPROBE ({NPROBE}) cannot be greater than NLIST ({NLIST}).")

    index.nprobe = NPROBE

    # 9. Return Index
    return index


def build_index(storage_context, nodes):
    if not nodes:
        raise ValueError("No nodes received.")

    active_nodes = [node for node in nodes if not node.metadata.get("deleted", False)]

    if not active_nodes:
        raise ValueError("No active nodes.")

    # 1. Create IVFPQ Index
    faiss_index = build_ivfpq_index(active_nodes)

    # 2. Persist in Llama Index
    vector_store = RetryFaissVectorStore(faiss_index=faiss_index)

    storage_context.vector_stores[DEFAULT_VECTOR_STORE] = vector_store

    print("Calling VectorStoreIndex")

    index = VectorStoreIndex(
        nodes=active_nodes,
        storage_context=storage_context,
        insert_batch_size=100,  # Default is 2048
        show_progress=True,
    )

    print("VectorStoreIndex created")

    vector_store.persist(persist_path=str(VECTOR_STORE_PATH))

    storage_context.index_store.persist(persist_path=str(INDEX_STORE_PATH))


if __name__ == "__main__":
    storage_context, nodes = get_storage_context_and_nodes()

    index = build_index(storage_context, nodes)

    print("Index created.")
