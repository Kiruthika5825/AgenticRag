from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

embedder = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

def embed(texts: list) -> list:
    try:
        embeddings = embedder.embed_documents(texts)
        logger.info("Embedded %d chunks", len(texts))
        return embeddings
    except Exception as e:
        logger.error("Embedding failed: %s", e)
        return []

def embed_query(query: str) -> list:
    try:
        embedding = embedder.embed_query(query)
        return embedding
    except Exception as e:
        logger.error("Query embedding failed: %s", e)
        return []