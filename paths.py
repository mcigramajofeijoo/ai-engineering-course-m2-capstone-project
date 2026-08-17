from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

STORAGE_FOLDER = PROJECT_ROOT / "storage"

LLAMA_INDEX_STORAGE_CONTEXT_PERSIST_DIR = STORAGE_FOLDER / "llama_index"

DOC_STORE_PATH = LLAMA_INDEX_STORAGE_CONTEXT_PERSIST_DIR / "docstore.json"
INDEX_STORE_PATH = LLAMA_INDEX_STORAGE_CONTEXT_PERSIST_DIR / "index_store.json"
VECTOR_STORE_PATH = STORAGE_FOLDER / "faiss" / "vector_store.faiss"
