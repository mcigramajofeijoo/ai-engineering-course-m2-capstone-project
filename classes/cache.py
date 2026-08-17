from dotenv import load_dotenv
load_dotenv()

import os
import redis
import json
import hashlib
from my_types.rag import RagPipelineMetadataFiltersType
from dataclasses import dataclass

@dataclass(frozen=True)
class CacheContext():
    """
    Contains everything that defines the execution context of
    a cached RAG response.
    """
    metadata_filters: RagPipelineMetadataFiltersType | None = None
    rag_pipeline_version: str = "v1" # INFO: For simplicity this encapsulates index, system prompt, LLM, embedding/reranker, etc. So each time we change these, it would be a new RAG pipeline version.
    tenant_id: str = "default"


class RagExactCache():

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_RAG_TTL_SECONDS = int(os.getenv("CACHE_RAG_TTL_SECONDS", "3600"))
    CACHE_RAG_KEY_PREFIX = os.getenv("CACHE_RAG_KEY_PREFIX", "rag:v1")

    def __init__(self):
        self.redis = redis.Redis.from_url(
            self.REDIS_URL,
            decode=True # means Redis returns stringsinstead of raw bytes.
        )

    @staticmethod
    def __normalize_query(query) -> str:
        """
        Minimal normalization for exact caching.

        We intentionally DO NOT do semantic normalization here.
        This cache only matches equivalent normalized strings.
        """
        return "".join(query.strip().lower().split())

    @staticmethod
    def __canonicalize_filters(metadata_filters: RagPipelineMetadataFiltersType) -> RagPipelineMetadataFiltersType:
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

    @classmethod
    def __build_cache_key(
        self,
        query: str,
        context: CacheContext
    ):
        """
        Builds a deterministic cache fingerprint.

        Every value that can change the final RAG answer should be
        represented here.
        """
        payload = {
            "query": self.__normalize_query(query),
            "metadata_filters": self.__canonicalize_filters(context.metadata_filters),
            "tenant_id": context.tenant_id,
            "model_version": context.model_version,
            "index_version": context.index_version,
            "prompt_version": context.prompt_version,
        }

        canonical_payload = json.dumps(
            payload,
            sort_keys=True, # INFO: In Python, setting sort_keys=True in json.dumps() tells the encoder to recursively sort all dictionary keys alphabetically, including any keys nested deep inside the structure.
            separators=(",", ":")
        )

        digest = hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

        return f"{self.CACHE_RAG_KEY_PREFIX}:{digest}"

    @classmethod
    def get(
        self,
        query: str,
        context: CacheContext
    ):
        """
        Returns the cached response or None on a miss.
        """
        cache_key = self.__build_cache_key(
            query=query,
            context=context
        )

        return self.redis.get(cache_key)

    @classmethod
    def set(
        self,
        query: str,
        response: str,
        context: CacheContext
    ):
        """
        Stores a response with a TTL.
        """
        key = self.__build_cache_key(
            query=query,
            context=context
        )

        return self.redis.set(key, response, ex=self.CACHE_RAG_TTL_SECONDS)

    def delete(
        self,
        query: str,
        context: CacheContext
    ) -> None:
        """
        Explicitly invalidates one cached response.
        """

        key = self._build_cache_key(
            query=query,
            context=context
        )

        self.redis.delete(key)

    def ping(self) -> bool:
        """Checks Redis connectivity."""
        return bool(self.redis.ping())
