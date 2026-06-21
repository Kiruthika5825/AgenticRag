import logging
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain_core.documents.base import Blob

logger=logging.getLogger(__name__)
MIN_CHARS_PER_PAGE=30

def extract_from_pdf(file_path:str) -> str:
    try:
        docs = PyMuPDFLoader(file_path).load()
        text = "\n".join(d.page_content for d in docs).strip()
        num_pages=max(len(docs),1)

        if len(text)/num_pages >= MIN_CHARS_PER_PAGE:
            logger.info("Normal PDF: %d chars", len(text))
            return text
        logger.info("scanned PDF detected, switching to OCR")
        return _ocr_pdf(file_path)
    except Exception as e:
        logger.error("PDF extraction failed for %s:%s", file_path,e)
        return ""


def _ocr_pdf(file_path:str) -> str:
    try: 
        loader = PyPDFLoader(
            file_path,
            extract_images=True,
            images_parser = RapidOCRBlobParser(),
        )
        docs = loader.load()
        return "\n".join(d.page_content for d in docs).strip()
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return ""
    

def extract_from_image(file_path:str)-> str:
    try:
        blob = Blob.from_path(file_path)
        docs = RapidOCRBlobParser().parse(blob)
        text = "\n".join(d.page_content for d in docs).strip()
        logger.info("Images OCR: %d chars", len(text))
        return text
    except Exception as e:
        logger.error("Image extraction failed for %s: %s", file_path,e)
        return ""
                     
def extract_from_url(url:str) -> str:
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text,'html.parser')
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        lines = [line.strip() for line in soup.get_text(separator = "\n").splitlines() if line.strip()]
        text = "\n".join(lines)
        logger.info("URL scraped: %d chars", len(text))
        return text
    except Exception as e:
        logger.error("URL extraction failed for %s: %s", url, e)
        return ""

def extract(source:str, source_type: str) -> str:
    try:
        if source_type == "pdf":
            return extract_from_pdf(source)
        elif source_type =="image":
            return extract_from_image(source)
        elif source_type =="url":
            return extract_from_url(source)
        else:
            raise ValueError(f"Unsupported source_type:{source_type!r}")
    except ValueError:
        raise
    except Exception as e:
        logger.error("Extraction failed for %s : %s", source, e)
        return ""
    
             

