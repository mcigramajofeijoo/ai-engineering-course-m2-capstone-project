# NOTE: Both values are linked, meaning, the embedding dimensions are the dimensions produced by the local embededing model.
# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# Reranker
RERANKER_TOP_N = 5
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"
