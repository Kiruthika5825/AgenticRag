import warnings
warnings.filterwarnings("ignore")
from pymilvus import Collection, connections, utility, FieldSchema, CollectionSchema, DataType
from core.embedder import embed, embed_query
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "productmind_kb"
EMBEDDING_DIM = 384
SIMILARITY_THRESHOLD = 0.4

def connect():
    connections.connect(host="localhost", port="19530")

def ensure_collection():
    connect()
    if utility.has_collection(COLLECTION_NAME):
        return Collection(COLLECTION_NAME)
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
    ]
    schema = CollectionSchema(fields, description="ProductMind Knowledge Base")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    logger.info("Collection and index created.")
    return collection

def insert_chunks(chunks: list, embeddings: list, source: str):
    collection = ensure_collection()
    try:
        data = [chunks, embeddings, [source]*len(chunks)]
        collection.insert(data)
        collection.flush()
        logger.info("Inserted %d chunks from %s", len(chunks), source)
    except Exception as e:
        logger.error("Insert failed: %s", e)
        raise

def search(query: str, top_k: int = 5) -> list:
    query_embedding = embed_query(query)
    collection = ensure_collection()
    try:
        collection.load()
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["chunk_text", "source"]
        )
        hits = []
        for hit in results[0]:
            hits.append({
                "chunk_text": hit.entity.get("chunk_text"),
                "source": hit.entity.get("source"),
                "score": hit.score
            })
        return hits
    except Exception as e:
        logger.error("Search failed: %s", e)
        raise