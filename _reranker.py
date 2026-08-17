# WARNING: The reranker is TEMPORARILY initialized in this separate module so that
# SentenceTransformers/PyTorch loads before FAISS. This workaround is needed
# due to a FAISS/PyTorch compatibility issue on our Mac Intel environment.

from llama_index.core.postprocessor import SentenceTransformerRerank
from constants import RERANKER_MODEL, RERANKER_TOP_N

_reranker = SentenceTransformerRerank(
    model=RERANKER_MODEL,
    top_n=RERANKER_TOP_N,
)
