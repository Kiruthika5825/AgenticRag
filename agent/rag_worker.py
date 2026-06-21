from core.vector_store import search, SIMILARITY_THRESHOLD
import logging

logger = logging.getLogger(__name__)

def retrieve(query: str) -> dict:
    try:
        results = search(query)
        if not results or results[0]["score"] < SIMILARITY_THRESHOLD:
            return {
                "hit": False,
                "context": "",
                "score": results[0]["score"] if results else 0,
                "chunks": []
            }
        context = "\n\n---\n\n".join([r["chunk_text"] for r in results])
        return {
            "hit": True,
            "context": context,
            "score": results[0]["score"],
            "chunks": results
        }
    except Exception as e:
        logger.error("Retrieval failed: %s", e)
        raise

def build_rag_prompt(query: str, context: str) -> str:
    return f"""
You are a helpful product intelligence assistant.
Answer the question using ONLY the context provided.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {query}
Answer:
""".strip()