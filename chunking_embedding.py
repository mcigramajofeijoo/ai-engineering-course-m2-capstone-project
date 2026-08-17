from dotenv import load_dotenv

load_dotenv()

from llama_index.core import Document, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from sonyflake import SonyFlake

from _embedding_model import _embedding_model
from constants import EMBEDDING_MODEL
from documentation import DOCUMENTATION
from paths import DOC_STORE_PATH
from utils import tokenize_words

CHUNK_SIZE = 100
CHUNK_OVERLAP = 30


splitter = SentenceSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    paragraph_separator="\n\n",
    secondary_chunking_regex=r"[^,.;。？！]+[,.;。？！]?",
    separator=" ",
    include_metadata=False,  # If True, the splitter calculatest the chunk_size as: metadata tokens + chunk text tokens
)

sonyflake = SonyFlake()


def build_documents():
    documents = []

    for article in DOCUMENTATION:
        article_meta = {
            "product": article["product"],
            "category": article["category"],
            "article_id": article["article_id"],
            "article_title": article["article_title"],
            "article_path": article["article_path"],
        }

        for section in article["sections"]:
            section_meta = {
                **article_meta,
                "section": section["section"],
                "section_anchor": section["section_anchor"],
            }

            # A section can contain its own text AND subsections.
            # We must preserve both.
            if section.get("text"):
                documents.append(
                    Document(
                        text=section["text"],
                        metadata={
                            **section_meta,
                            "subsection": None,
                            "subsection_anchor": None,
                        },
                    )
                )

            for subsection in section.get("subsections", []):
                documents.append(
                    Document(
                        text=subsection["text"],
                        metadata={
                            **section_meta,
                            "subsection": subsection.get("subsection"),
                            "subsection_anchor": subsection.get("subsection_anchor"),
                        },
                    )
                )

    return documents


def build_nodes():
    documents = build_documents()

    mtd = {document.doc_id: document.metadata.copy() for document in documents}

    for doc in documents:
        doc.metadata = {}

    nodes = splitter.get_nodes_from_documents(documents)

    for n in nodes:
        source_doc_id = n.ref_doc_id

        if source_doc_id not in mtd:
            raise ValueError(
                f"Could not find metadata for source document " f"{source_doc_id}"
            )

        n.metadata = mtd[source_doc_id].copy()

        int64_uid = (
            sonyflake.next_id()
        )  # FaissVectorStore requires integer IDs (int64) for .add_with_ids(), but LlamaIndex default node IDs are strings. This conversion ensures compatibility.

        n.id_ = str(int64_uid)
        n.metadata["deleted"] = False
        n.metadata["tokenized_text"] = tokenize_words(n.text)
        n.metadata["embedding_model"] = EMBEDDING_MODEL

    embeddings = _embedding_model.get_text_embedding_batch(
        [n.get_content() for n in nodes], show_progress=True
    )

    for node, embedding in zip(nodes, embeddings):
        node.embedding = embedding

    return nodes


def persist_nodes(nodes):
    # `exist_ok=True` ensures the directory is created if it is missing, but safely ignored without raising an error if it already exists.
    # LLAMA_INDEX_STORAGE_CONTEXT_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)

    storage_context = StorageContext.from_defaults(docstore=docstore)

    storage_context.docstore.persist(persist_path=str(DOC_STORE_PATH))


if __name__ == "__main__":
    nodes = build_nodes()
    persist_nodes(nodes)

    print(f"{len(nodes)} nodes created and persisted.")
