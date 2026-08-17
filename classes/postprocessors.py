from typing import Optional

import numpy as np
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
import re
import hashlib
from datasketch import MinHash, MinHashLSH
from semhash import SemHash
from _embedding_model import _embedding_model


class MetadataFilterPostprocessor(BaseNodePostprocessor):
    """
    Filters retrieved nodes according to metadata values.
    Only nodes matching ALL provided filters are kept.
    """

    # NOTE: La documentación de LlamaIndex muestra el mismo patrón: recibe nodes + QueryBundle y devuelve una lista de NodeWithScore.
    # Es decir, cada postprocessor recibe nodes y querybundle, y devuelve una lista de NodesWithScore.

    product: Optional[str] = None
    category: Optional[str] = None

    @classmethod
    def class_name(cls) -> str:
        return "MetadataFilterPostprocessor"

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:

        # print("Metadata filter query_bundle:", type(query_bundle), query_bundle)
        filtered_nodes = []

        for node_with_score in nodes:

            node = node_with_score.node
            metadata = node.metadata

            # Product filter
            if self.product is not None and metadata.get("product") != self.product:
                continue

            # Category filter
            if self.category is not None and metadata.get("category") != self.category:
                continue

            filtered_nodes.append(node_with_score)

        return filtered_nodes


class ExactDedupPostprocessor(BaseNodePostprocessor):
    """
    Removes exact duplicate texts.

    We normalize whitespace/case first, then compute SHA-256.
    This is deterministic and very cheap.
    """

    # INFO: This has some cool benefits, e.g: The program can check the name of the tool before wasting memory creating or loading the whole tool.
    @classmethod
    def class_name(cls) -> str:
        return "ExactDedupPostprocessor"

    # INFO: Remember that with double underscores ("__") Python treats the method as PRIVATE.
    @staticmethod
    def __normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @classmethod
    def __hash_text(cls, text: str) -> str:
        normalized = cls.__normalize_text(text)

        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def __score(node: NodeWithScore) -> float:
        return float(node.score or 0.0)

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:

        if len(nodes) <= 1:
            return nodes

        reranked_nodes = sorted(nodes, key=self.__score, reverse=True)

        seen = set()
        deduped_nodes = []

        for node_with_score in reranked_nodes:
            text = node_with_score.node.get_content()
            fingerprint = self.__hash_text(text)

            if fingerprint in seen:
                continue

            seen.add(fingerprint)
            deduped_nodes.append(node_with_score)

        return deduped_nodes


class NearDuplicatePostprocessor(BaseNodePostprocessor):
    """
    Detects lexical near-duplicates using MinHash + LSH.

    MinHash approximates Jaccard similarity over shingles.
    LSH is used to find candidate pairs efficiently.
    """

    threshold: float = 0.9
    num_perm: int = 128
    shingle_size: int = 5

    @classmethod
    def class_name(cls) -> str:
        return "NearDuplicatePostprocessor"

    @staticmethod
    def __score(node: NodeWithScore) -> float:
        return float(node.score or 0.0)

    @staticmethod
    def __normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def __build_minhash(self, text: str) -> MinHash:
        text = self.__normalize_text(text)
        tokens = text.split()

        if len(tokens) <= self.shingle_size:
            shingles = [" ".join(tokens)]
        else:
            shingles = [
                " ".join(tokens[i : i + self.shingle_size])
                for i in range(len(tokens) - self.shingle_size + 1)
            ]

        minhash = MinHash(
            # INFO: With more permutations, better Jaccard approximation, but more memory and computing.
            # Official documentation indicates that 128 is the default and by increasing it we get more precision
            # at the expense of resources. (https://ekzhu.com/datasketch/documentation.html?utm_source=chatgpt.com)
            num_perm=self.num_perm,
            gpu_mode="detect",
        )

        for shingle in shingles:
            minhash.update(shingle.encode("utf-8"))

        return minhash

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:

        if len(nodes) <= 1:
            return nodes

        ranked_nodes = sorted(
            nodes,
            key=self.__score,
            reverse=True,
        )

        # INFO: En datasketch, normalmente no necesitás especificarlos manualmente: con threshold y num_perm, LSH puede optimizar
        # automáticamente la combinación de bands/rows. También podés especificarlos explícitamente si necesitás controlar el comportamiento.
        lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)

        minhashes: dict[int, MinHash] = {}

        result = []

        for idx, node_with_score in enumerate(ranked_nodes):

            text = node_with_score.node.get_content()

            minhash = self.__build_minhash(text)
            minhashes[idx] = minhash

            # LSH performs a fast approximate search and returns
            # candidate near-duplicates.
            duplicate_candidates = lsh.query(minhash)

            is_duplicate = False

            for candidate_idx in duplicate_candidates:
                # NOTE: La propia documentación de datasketch recomienda ese segundo filtro porque LSH.query() es aproximado.
                # Confirm the candidate using the actual MinHash
                # Jaccard estimate instead of relying only on LSH.
                similarity = minhash.jaccard(minhashes[candidate_idx])

                if similarity >= self.threshold:
                    is_duplicate = True
                    break

            if is_duplicate:
                # A higher-scoring node was already accepted,
                # so this node is discarded.
                continue

            # No confirmed near-duplicate was found.
            # Keep this node and add it to the LSH index.
            lsh.insert(idx, minhash)

            result.append(node_with_score)

        return result


class SemanticDedupPostprocessor(BaseNodePostprocessor):

    threshold: float = 0.9

    @classmethod
    def class_name(cls) -> str:
        return "SemanticDedupPostprocessor"

    @staticmethod
    def __score(node: NodeWithScore) -> float:
        return float(node.score or 0.0)

    def _postprocess_nodes(
        self, nodes: list[NodeWithScore], query_bundle: Optional[QueryBundle] = None
    ) -> list[NodeWithScore]:

        reranked_nodes = sorted(nodes, key=self.__score, reverse=True)

        embeddings = []
        records = []

        for node_with_score in reranked_nodes:
            node = node_with_score.node

            if node.embedding is None:
                raise ValueError(
                    f"Node {node.node_id} does not contain an embedding. "
                    "SemanticDedupPostprocessor requires node embeddings."
                )

            records.append({"node_id": node.node_id})
            embeddings.append(node.embedding)

        embeddings = np.asarray(embeddings, dtype=np.float32)

        # We already computed the embeddings during retrieval/indexing,
        # so we don't need SemHash to embed the text again.
        semhash = SemHash.from_embeddings(
            embeddings=embeddings, 
            records=records, 
            columns=["node_id"],
            model=_embedding_model
        )

        results = semhash.self_deduplicate(threshold=self.threshold)

        ids = [record["node_id"] for record in results.selected]

        deduplicated_nodes_with_score = [
            node_with_score
            for node_with_score in reranked_nodes
            if node_with_score.node_id in ids
        ]

        return deduplicated_nodes_with_score


class RagPipelineDeduplicationPostprocessor(BaseNodePostprocessor):
    """
    RAG-specific deduplication pipeline.

    The individual deduplication strategies remain independent and can
    also be used separately. This wrapper controls which strategies are
    enabled for this RAG pipeline.
    """

    exact: bool = True
    near: bool = True
    semantic: bool = True

    @classmethod
    def class_name(cls) -> str:
        return "RagPipelineDeduplicationPostprocessor"

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:

        if len(nodes) <= 1:
            return nodes

        # Exact deduplication
        if self.exact:
            exact_dedup = ExactDedupPostprocessor()

            nodes = exact_dedup._postprocess_nodes(
                nodes,
                query_bundle=query_bundle,
            )

        # Lexical near-duplicate detection
        if self.near:
            near_dedup = NearDuplicatePostprocessor()

            nodes = near_dedup._postprocess_nodes(
                nodes,
                query_bundle=query_bundle,
            )

        # Semantic deduplication
        if self.semantic:
            semantic_dedup = SemanticDedupPostprocessor()

            nodes = semantic_dedup._postprocess_nodes(
                nodes,
                query_bundle=query_bundle,
            )

        return nodes
