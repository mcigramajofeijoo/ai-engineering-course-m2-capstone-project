from dotenv import load_dotenv

load_dotenv()
import os
from typing import Dict, Text

from llama_index.core import VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor

# from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever

# from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.schema import QueryBundle
from llama_index.llms.openrouter import OpenRouter

from _embedding_model import _embedding_model
from _reranker import _reranker
from classes.postprocessors import (
    MetadataFilterPostprocessor,
    RagPipelineDeduplicationPostprocessor,
)
from utils import get_storage_context_and_nodes

# ============================================================
# CONFIGURATION
# ============================================================
CANDIDATE_K = 50
RRF_RANK_C = 60
# RERANK_TOP_K = 5


# TODO: Apply QUERY EXPANSION ✅
# TODO: Apply DEDUPLICATION ✅
# TODO: Apply CACHING ✅
# TODO: Apply INFERENCE BATCHES – continous batching (vLLM)
# TODO: MICRO-BENCHMARKS: MEDIR Y ENTENDER LA DISTRIBUCIÓN DE LATENCIA (p50, p95)
# TODO: Apply MULTI-HOP


def get_index():
    # WARNING: WARNING: WARNING:
    # Un StorageContext puede contener varios IndexStruct. LlamaIndex lo soporta explícitamente; por ejemplo, podés tener distintos índices sobre el mismo DocStore.
    # Una aplicación puede tener varios índices si realmente los necesita. En ese caso, cada uno tiene su propio index_id, y al cargarlo tenés que especificar cuál querés.
    # Pero tu pipeline tiene un único índice vectorial FAISS, así que conceptualmente debería existir un único IndexStruct asociado a ese índice.

    storage_context, _ = get_storage_context_and_nodes()

    # NOTE: If we know we're going to have only one struct, we can run ".get_index_struct()"
    index_structs = storage_context.index_store.index_structs()

    if not index_structs:
        raise ValueError("No index structures found in IndexStore.")

    if len(index_structs) > 1:
        raise ValueError(
            f"Expected exactly one index structure, found {len(index_structs)}."
        )

    index_struct = index_structs[0]

    # Reconstruimos la abstracción VectorStoreIndex de LlamaIndex
    # alrededor de nuestro StorageContext ya cargado.
    index = VectorStoreIndex(
        nodes=[],
        index_struct=index_struct,
        storage_context=storage_context,
        embed_model=_embedding_model,
    )

    return index


def build_rrf_retriever(index):
    """
    Creates:
        Semantic Retriever
              +
        BM25 Retriever
              ↓
        Reciprocal Rank Fusion
    """
    semantic_retriever = index.as_retriever(
        similarity_top_k=CANDIDATE_K,  # Number of candidates returned by the vector search. Our FAISS index performs the actual semantic search.
    )

    bm25_retriever = BM25Retriever.from_defaults(
        # LlamaIndex obtains the Nodes from the DocStore and uses their text to build/search the BM25 corpus.
        # Conceptually this replaces our manual: corpus = ... / bm25 = BM25Okapi(corpus) / scores = bm25.get_scores(...)
        docstore=index.docstore,
        similarity_top_k=CANDIDATE_K,
    )

    retriever_base = {
        "retrievers": [
            semantic_retriever,
            bm25_retriever,
        ],
        "similarity_top_k": CANDIDATE_K,
        "mode": "relative_score",  # Applies Reciprocal Rank Fusion (RRF)
        "use_async": True,  # Runs the underlying retrievers asynchronously.
        "verbose": True,  # Prints information about the fusion process.
        "retriever_weights": [0.75, 0.25],
    }

    rrf_retriever = QueryFusionRetriever(**retriever_base, num_queries=1)

    rrf_retriever_with_query_expansion = QueryFusionRetriever(
        **retriever_base,
        num_queries=3,
        llm=OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")),
    )

    return rrf_retriever_with_query_expansion


def build_query_engine(index, filters):
    """
    Builds the complete retrieval pipeline:

        FAISS Semantic Search
                  +
             BM25 Search
                  ↓
                RRF
                  ↓
          Metadata Filtering
                  ↓
             CrossEncoder
                  ↓
               Top-K
    """
    print("Building retriever...")
    rrf_retriever = build_rrf_retriever(index)

    # # WARNING: We need to create a postprocessor class in order to add the filtering in the postprocessors,
    # # because it needs a callback manager (to know when retrieval begins, ends, reranking begins, ends, etc. – Observability)
    # # INFO: We need to add the filters to the postprocessors because FAISS doesn't support pre-filtering. If we were using Pinecone for example,
    # # we would pass these filters to the retriever.
    # metadata_filters = build_metadata_filters(filters)

    # print("Building metadata filters postprocessor...")
    metadata_filter = MetadataFilterPostprocessor(
        product=filters.get("product", None), category=filters.get("category", None)
    )

    # reranker = build_reranker()

    similarity_postprocessor = SimilarityPostprocessor(similarity_cutoff=0.6)
    deduplication_postprocessor = RagPipelineDeduplicationPostprocessor(
        exact=True, near=True, semantic=True
    )

    postprocessors = [
        metadata_filter,
        similarity_postprocessor,
        deduplication_postprocessor,
        _reranker,
    ]

    # print("Setting up the query engine...")
    query_engine = RetrieverQueryEngine(
        retriever=rrf_retriever,
        node_postprocessors=postprocessors,  # Postprocessors are executed after retrieval.
    )

    return query_engine


def RAG(query: str, filters: Dict[Text, Text] = {}):
    """
    Complete RAG retrieval pipeline.
    """
    print("Getting index")
    index = get_index()

    print("Building query engine")
    query_engine = build_query_engine(index, filters)

    """
    Executes:
    
    Query
      ↓
    FAISS + BM25
      ↓
    RRF
      ↓
    Reranker
      ↓
    Top 5
    """

    # INFO: Wrap the query in a QueryBundle because the postprocessors expect a QueryBundle,
    # but retrieve() was passing a plain string, causing an error in the filters/postprocessor.
    response = query_engine.retrieve(QueryBundle(query_str=query))

    return response


if __name__ == "__main__":

    # Setup
    query = "A client started a dispute and won, but is unfair, he's lying, what can I do? Can you recheck it please?"
    filters = {"category": "Disputes"}

    # RAG
    results = RAG(query=query, filters=filters)

    if results:

        print("\nTop results:\n")

        for rank, result in enumerate(results, start=1):

            print(f"--- Result {rank} ---")
            print(f"Score: {result.score}")
            print(f"Node ID: {result.node.node_id}")
            print(f"Text: {result.node.text}")
            print()

    else:
        print("No relevant documents found.")

    # ––– UNUSED –––
    # def build_metadata_filters(filters: Dict[Text, Text] = None):
    #     """
    #     WARNING: This would be used ONLY if the backend supports pre-filtering!

    #     Converts our application-level metadata filters into
    #     LlamaIndex MetadataFilters.
    #     """

    #     if not filters:
    #         return None

    #     converted_filters = []

    #     for k, v in filters.items():
    #         if k in METADATA_FILTERS_AVAILABLE:
    #             if v is not None:
    #                 converted_filters.append(MetadataFilter(key=k, value=v, operator="=="))

    #     if not converted_filters:
    #         return None

    #     return MetadataFilters(
    #         filters=converted_filters,
    #         condition="and",  # AND means that ALL supplied filters must match.
    #     )

    # def build_reranker():
    # WARNING: TEMPORARILY DISABLED due to a FAISS/PyTorch compatibility issue on Mac Intel.
    # PyTorch is limited to v2.2.2 in our environment, and SentenceTransformers
    # must initialize before FAISS. Since FAISS is imported by classes.py/utils.py,
    # the reranker cannot be initialized here. If the compatibility issue is
    # resolved (e.g. with newer versions), this can be initialized here again.
    # Creates the CrossEncoder-based reranker.

    """

    LlamaIndex handles:
        query + candidate text
            ↓
        relevance score
            ↓
        sorting
            ↓
        top N
    """

    # reranker = SentenceTransformerRerank(
    #     model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    #     top_n=RERANK_TOP_K,  # Number of candidates returned AFTER reranking.
    # )

    # return reranker
