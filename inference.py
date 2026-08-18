from rag_rrf import RAG
from classes.cache import RagCache, CacheContext
from my_types.rag import RagPipelineMetadataFiltersType


CACHE = RagCache()


def inference(
    query: str,
    filters: RagPipelineMetadataFiltersType,
):

    cache_context = CacheContext(
        metadata_filters=filters,
    )

    # --------------------------------------------------------
    # Cache lookup
    # --------------------------------------------------------
    cached_response = CACHE.get(
        query=query,
        context=cache_context,
    )

    if cached_response is not None:
        return cached_response

    # --------------------------------------------------------
    # Full RAG pipeline
    # --------------------------------------------------------
    retrieved_context = RAG(
        query=query,
        filters=filters,
    )

    # --------------------------------------------------------
    # LLM generation
    # --------------------------------------------------------

    # augmented_prompt = (
    #     f"<context>\n{retrieved_context}\n</context>\n\n"
    #     f"<user_query>\n{query}\n</user_query>"
    # )

    # response = LLM(...)

    response = "This is a fake response."

    # --------------------------------------------------------
    # Populate both cache layers
    # --------------------------------------------------------
    CACHE.set(
        query=query,
        response=response,
        context=cache_context,
    )

    return response


if __name__ == "__main__":
    query = "A client won me a dispute, could you double check it?"
    filters = {"category": "Disputes"}

    result = inference(query, filters)
    print(result)
