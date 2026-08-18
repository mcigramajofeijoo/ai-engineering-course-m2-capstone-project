from dotenv import load_dotenv

load_dotenv()

import os
import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import json
import hashlib
from my_types.rag import RagPipelineMetadataFiltersType
from dataclasses import dataclass
from constants import EMBEDDING_DIMENSIONS
from _embedding_model import _embedding_model
import numpy as np
from pydantic import BaseModel
from clients.openrouter_client import openrouter_client
import faiss

REDIS_URL = os.getenv("REDIS_URL")


@dataclass(frozen=True)
class CacheContext:
    """
    Contains everything that defines the execution context of
    a cached RAG response.
    """

    metadata_filters: RagPipelineMetadataFiltersType | None = None
    rag_pipeline_version: str = (
        "v1"  # INFO: For simplicity this encapsulates index, system prompt, LLM, embedding/reranker, etc. So each time we change these, it would be a new RAG pipeline version.
    )
    tenant_id: str = "default"


class RagExactCache:

    def __init__(self):
        self.redis = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,  # means Redis returns stringsinstead of raw bytes. We won't have to manually call .decode("utf-8") on any data you retrieve from self.redis.get().
        )
        self.ttl_seconds = 3600
        self.key_prefix = "exact_cache:"

    @staticmethod
    def __normalize_query(query) -> str:
        """
        Minimal normalization for exact caching.

        We intentionally DO NOT do semantic normalization here.
        This cache only matches equivalent normalized strings.
        """
        return "".join(query.strip().lower().split())

    @staticmethod
    def __canonicalize_filters(
        metadata_filters: RagPipelineMetadataFiltersType,
    ) -> RagPipelineMetadataFiltersType:
        """
        Sort keys so logically identical dictionaries produce
        the same cache key.
        """
        if not metadata_filters:
            return {}

        return {
            key: metadata_filters[key]
            for key in sorted(metadata_filters)
            if key is not None
        }

    def __build_cache_key(self, query: str, context: CacheContext):
        """
        Builds a deterministic cache fingerprint.

        Every value that can change the final RAG answer should be
        represented here.
        """
        payload = {
            "query": self.__normalize_query(query),
            "metadata_filters": self.__canonicalize_filters(context.metadata_filters),
            "rag_pipeline_version": context.rag_pipeline_version,
            "tenant_id": context.tenant_id,
        }

        canonical_payload = json.dumps(
            payload,
            sort_keys=True,  # INFO: In Python, setting sort_keys=True in json.dumps() tells the encoder to recursively sort all dictionary keys alphabetically, including any keys nested deep inside the structure.
            separators=(",", ":"),
        )

        digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        return f"{self.key_prefix}{digest}"

    def get(self, query: str, context: CacheContext):
        """
        Returns the cached response or None on a miss.
        """
        cache_key = self.__build_cache_key(query=query, context=context)

        return self.redis.get(cache_key)

    def set(self, query: str, response: str, context: CacheContext):
        """
        Stores a response with a TTL.
        """
        key = self.__build_cache_key(query=query, context=context)

        return self.redis.set(key, response, ex=self.ttl_seconds)

    def delete(self, query: str, context: CacheContext) -> None:
        """
        Explicitly invalidates one cached response.
        """

        key = self.__build_cache_key(query=query, context=context)

        self.redis.delete(key)

    def ping(self):
        return bool(self.redis.ping())


# Semantic Cache Config
@dataclass(frozen=True)
class SemanticCacheConfig:
    index_name: str = "idx:semantic_cache"
    key_prefix: str = "semantic_cache:"

    embedding_dimension: int = EMBEDDING_DIMENSIONS
    distance_metric: str = (
        "IP"  # Since we're normalizing the embedding in `__embed_query`, this is equal to COSINE, just like in our RAG pipeline.
    )

    hnsw_m: int = (
        32  # This is big M, not m (number of subvectors if we're applying Product Quantization)
    )
    hnsw_ef_construction: int = 200
    hnsw_ef_runtime: int = 32

    candidate_k: int = 3
    similarity_threshold: float = 0.9

    ttl_seconds: int = 3600


# Semantic Cache
class RagSemanticCache:

    def __init__(self):
        self.redis = redis.Redis.from_url(REDIS_URL, decode_responses=False)
        self.embedding_model = _embedding_model
        self.config = SemanticCacheConfig()

        self.__create_index()

    def __create_index(self):
        try:
            self.redis.ft(self.config.index_name).info()
            return  # NOTE: If we don't return, it will fail since we will try to create an index that already exists
        except redis.exceptions.ResponseError:
            pass

        schema = (
            TagField("metadata_filters"),
            TagField("rag_pipeline_version"),
            TagField("tenant_id"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.config.embedding_dimension,
                    "DISTANCE_METRIC": self.config.distance_metric,
                    "M": self.config.hnsw_m,
                    "EF_CONSTRUCTION": self.config.hnsw_ef_construction,
                    "EF_RUNTIME": self.config.hnsw_ef_runtime,
                },
            ),
        )

        self.redis.ft(self.config.index_name).create_index(
            schema,
            definition=IndexDefinition(
                prefix=[self.config.key_prefix],
                index_type=IndexType.HASH,
            ),
        )

    def __build_cache_key(self, query: str, context: CacheContext) -> str:
        normalized_query = "".join(query.strip().lower().split())

        canonical_filters = json.dumps(
            context.metadata_filters, sort_keys=True, separators=(",", ":")
        )

        raw_key = (
            f"{canonical_filters}:"
            f"{context.rag_pipeline_version}:"
            f"{context.tenant_id}:"
            f"{normalized_query}"
        )

        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        return f"{self.config.key_prefix}{digest}"

    def __embed_query(self, query: str) -> np.ndarray:
        embedding = self.embedding_model._get_query_embedding(query)

        embedding = np.asarray(embedding, dtype=np.float32).reshape(1, -1)

        faiss.normalize_L2(embedding)

        return embedding

    @staticmethod
    def __canonicalize_filters(filters):
        canonical_filters = json.dumps(filters, sort_keys=True, separators=(",", ":"))

        digest = hashlib.sha256(canonical_filters.encode("utf-8")).hexdigest()

        return digest

    def set(self, query: str, response: str, context: CacheContext) -> None:

        key = self.__build_cache_key(query, context)

        embedding = self.__embed_query(query)

        canonical_filters = self.__canonicalize_filters(context.metadata_filters)

        self.redis.hset(
            key,
            mapping={
                "query": query,
                "response": response,
                "embedding": embedding.tobytes(),
                "metadata_filters": canonical_filters,
                "rag_pipeline_version": context.rag_pipeline_version,
                "tenant_id": context.tenant_id,
            },
        )

        self.redis.expire(key, self.config.ttl_seconds)

    def get(self, query: str, context: CacheContext) -> dict | None:
        query_embedding = self.__embed_query(query)
        query_vector = query_embedding.tobytes()

        canonical_filters = self.__canonicalize_filters(context.metadata_filters)

        redis_query = (
            f"(@metadata_filters:{{{canonical_filters}}} "
            f"@rag_pipeline_version:{{{context.rag_pipeline_version}}} "
            f"@tenant_id:{{{context.tenant_id}}}) "
            f"=>[KNN {self.config.candidate_k} "
            f"@embedding $query_vector "
            f"AS vector_score]"
        )

        query = (
            Query(redis_query)
            .sort_by("vector_score")
            .return_fields(
                "query",
                "response",
                "vector_score",
                "metadata_filters",
                "rag_pipeline_version",
                "tenant_id",
            )
            .dialect(2)
        )

        results = self.redis.ft(self.config.index_name).search(
            query, query_params={"query_vector": query_vector}
        )

        if not results.docs:
            return None

        candidate = results.docs[0]

        distance = float(candidate.vector_score)

        similarity = 1.0 - distance

        if similarity < self.config.similarity_threshold:
            return None

        return {
            "query": candidate.query,
            "response": candidate.response,
            "similarity": similarity,
        }

    def delete(self, query: str, context: CacheContext) -> None:

        key = self.__build_cache_key(query=query, context=context)

        self.redis.delete(key)


class SemanticCacheQueryMatch(BaseModel):
    match: bool
    reason: str


# Wrapper
class RagCache:
    """
    Orchestrates exact and semantic caching.

    Lookup order:
        1. Exact cache
        2. Semantic cache
        3. Full RAG pipeline

    On semantic hit:
        - backfill exact cache

    On full miss:
        - write to both caches
    """

    def __init__(self):
        self.exact_cache = RagExactCache()
        self.semantic_cache = RagSemanticCache()

    def __judge_semantic_candidate(
        self, query: str, cached_query: str
    ) -> SemanticCacheQueryMatch:

        # TODO: Improve the System Prompt
        SYSTEM_PROMPT = f"""
        ROLE

        You are a semantic cache query equivalence judge.

        Your purpose is to determine whether two user queries express the same request and can therefore safely reuse the same cached response.

        CONTEXT

        You will receive:

        - QUERY_A: the current user query.
        - QUERY_B: a query retrieved from the semantic cache because it is semantically similar to QUERY_A.

        The queries may use different wording, grammar, structure, verbosity, or paraphrasing.

        Evaluate ONLY the information explicitly expressed in the queries.

        Do NOT infer:
        - events that are not explicitly stated;
        - previous interactions or actions;
        - hidden context;
        - unstated user intentions;
        - unstated temporal information;
        - assumptions about what happened before the query.

        If two queries can reasonably be interpreted as expressing the same request based on their explicit content, they are a match.

        TASK

        Return match=true when the two queries express the same request, even when they use different wording or paraphrasing.

        Return match=false when there is an explicit semantic difference, such as:

        - one query asks for additional information;
        - one query asks for a different action;
        - one query refers to a different entity;
        - one query introduces a different constraint;
        - one query has a different explicit scope;
        - one query explicitly requires a different answer.

        When deciding, prefer the most direct interpretation supported by the text.

        Do NOT mark queries as different merely because one wording could imply additional context that is not explicitly stated.


        EXAMPLES

        Example 1 — Paraphrasing

        Query A:
        What is the capital of Argentina?

        Query B:
        Which city is Argentina's capital?

        Result:
        match = true


        Example 2 — Additional information

        Query A:
        What is the capital of Argentina?

        Query B:
        What is the capital of Argentina and what time is it there?

        Result:
        match = false

        Reason:
        Query B additionally asks for the current time.


        Example 3 — Different constraint

        Query A:
        How can I cancel my subscription?

        Query B:
        How can I cancel my subscription and get a refund?

        Result:
        match = false

        Reason:
        Query B additionally asks about obtaining a refund.

        OUTPUT

        Return a valid JSON object matching the provided response schema.

        - match must be true when both queries express the same request.
        - match must be false when they express different requests.
        - reason must briefly explain the semantic difference when match is false.
        - When match is true, reason should briefly explain why the queries are equivalent.
        """

        response = openrouter_client.chat.completions.create(
            model="google/gemma-4-26b-a4b-it:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (f"Query A:\n{query}\n\n" f"Query B:\n{cached_query}"),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "semantic_cache_query_match",
                    "strict": True,
                    "schema": SemanticCacheQueryMatch.model_json_schema(),
                },
            },
            temperature=0,
            max_tokens=100,
        )

        return SemanticCacheQueryMatch.model_validate_json(
            response.choices[0].message.content
        )

    def get(self, query: str, context: CacheContext) -> None:

        exact_response = self.exact_cache.get(query=query, context=context)
        if exact_response is not None:
            print("EXACT CACHE HIT")
            return exact_response

        print("EXACT CACHE MISS")

        semantic_candidate = self.semantic_cache.get(query=query, context=context)
        if semantic_candidate is not None:
            print("SEMANTIC CACHE HIT", semantic_candidate)
            response = semantic_candidate["response"]

            judge = self.__judge_semantic_candidate(
                query=query,
                cached_query=semantic_candidate["query"],
            )

            print("JUDGE", judge)

            if judge.match:
                # Backfill to exact cache
                self.exact_cache.set(
                    query=query,
                    response=response,
                    context=context,
                )

                return response

        # Both Cache Layers Missed
        print("SEMANTIC CACHE MISS")
        return None

    def set(self, query: str, response: str, context: CacheContext) -> None:
        # Store the same final response in both cache layers.
        self.exact_cache.set(query=query, response=response, context=context)
        self.semantic_cache.set(query=query, response=response, context=context)

    def delete(self, query: str, context: CacheContext) -> None:

        self.exact_cache.delete(query, context)
        self.semantic_cache.delete(query, context)

    def ping(self):
        return bool(self.exact_cache.ping())
