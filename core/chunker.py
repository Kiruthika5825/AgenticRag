from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len
    )
    chunks = splitter.split_text(text)
    logger.info("Created %d chunks", len(chunks))
    return chunks