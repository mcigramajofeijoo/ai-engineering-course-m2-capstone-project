# WARNING: Read `_reranker.py`

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from classes.llama_idx import NormalizedEmbeddingModel
from constants import EMBEDDING_MODEL

hf_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

_embedding_model = NormalizedEmbeddingModel(model=hf_model)
