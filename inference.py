from rag_rrf import RAG
from classes.cache import RagExactCache, CacheContext
from my_types.rag import RagPipelineMetadataFiltersType

EXACT_CACHE = RagExactCache()

def inference(query: str, filters: RagPipelineMetadataFiltersType):
    # ––– CACHE Layer –––
    # Check if Redis is connected
    if not EXACT_CACHE.ping():
        raise RuntimeError(
            "Could not connect to Redis"
        )

    # Create CacheContext
    cache_context = CacheContext(query=query, filters=filters)

    # Get cached response
    cached_response = EXACT_CACHE.get(query, cache_context)

    # If we hit the cache, return the cached response
    if cached_response is not None:
        return cached_response

    # ––– RAG Layer –––
    # NOTE: If cache missed, perform RAG
    retrieved_context = RAG(query, filters)

    augmented_prompt = (
        f"<context>\n{retrieved_context}\n</context>\n\n"
        f"<user_query>\n{query}\n</user_query>"
    )

    messages = [
        {"role": "system", "content": "[MY SYSTEM PROMPT]"},
        {"role": "user", "content": augmented_prompt}
    ]

    # LLM/vLLM Call
    # INFO: Still doing research on vLLM to integrate it here!