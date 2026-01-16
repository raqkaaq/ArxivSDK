"""PDF processing utilities using PyMuPDF."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logger.warning("PyMuPDF not installed; PDF processing unavailable")


class ArxivPDFProcessor:
    """Processor for extracting content from arXiv PDFs using PyMuPDF."""

    def __init__(self):
        if fitz is None:
            raise ImportError("PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF")

    def get_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Get PDF metadata."""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            return dict(metadata)
        except Exception as e:
            logger.error("Failed to get metadata from %s: %s", pdf_path, e)
            raise

    def extract_first_page_text(self, pdf_path: str) -> str:
        """Extract text from the first page of the PDF."""
        try:
            doc = fitz.open(pdf_path)
            if doc.page_count > 0:
                text = doc[0].get_text()
            else:
                text = ""
            doc.close()
            return text
        except Exception as e:
            logger.error("Failed to extract first page text from %s: %s", pdf_path, e)
            raise

    def extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from the PDF as list of dicts."""
        try:
            doc = fitz.open(pdf_path)
            tables = []
            for page in doc:
                tabs = page.find_tables()
                for tab in tabs:
                    tables.append(tab.to_dict())  # Dict with headers, data
            doc.close()
            return tables
        except Exception as e:
            logger.error("Failed to extract tables from %s: %s", pdf_path, e)
            raise

    def get_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Get PDF metadata."""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            return dict(metadata)
        except Exception as e:
            logger.error("Failed to get metadata from %s: %s", pdf_path, e)
            raise

    def extract_text_with_layout(self, pdf_path: str) -> str:
        """Extract text preserving some layout (e.g., paragraphs)."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text += span["text"] + " "
                        text += "\n"
            doc.close()
            return text
        except Exception as e:
            logger.error("Failed to extract layout text from %s: %s", pdf_path, e)
            raise