from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import re
import logging
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from academic_sdk.models import Paper, Author, Link

logger = logging.getLogger(__name__)


class ArxivPaper(Paper):
    # Inherit from academic_sdk.models.Paper
    # Add arXiv specific fields
    categories: Optional[List[str]] = None  # arXiv categories
    arxiv_comment: Optional[str] = None
    journal_ref: Optional[str] = None

    model_config = {"extra": "ignore"}

    @field_validator("title", mode="before")
    def strip_title(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("summary", mode="before")
    def strip_summary(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("primary_category", mode="before")
    def normalize_primary_category(cls, v):
        # feedparser may provide a dict like {'term': 'cs.LG'}; accept that and extract term
        if v is None:
            return None
        if isinstance(v, str):
            return v
        # dict-like
        try:
            if isinstance(v, dict):
                # common keys: 'term', 'scheme', 'label'
                return v.get('term') or v.get('label') or v.get('scheme')
        except Exception:
            pass
        # Fallback to string conversion
        return str(v)

    @property
    def pdf_url(self) -> Optional[str]:
        for l in self.links:
            if l.type == "application/pdf":
                href = l.href
                if href:
                    parsed = urlparse(href)
                    if parsed.scheme not in ('http', 'https'):
                        logger.warning("Invalid PDF URL scheme: %s", href)
                        continue
                    # ensure URL ends with .pdf; some feeds provide a PDF-like URL
                    # that lacks the .pdf suffix (e.g. /pdf/2101.00001v2). Normalize
                    # by appending .pdf when appropriate.
                    if not href.lower().endswith('.pdf'):
                        # only append when URL path contains '/pdf/' or matches arXiv patterns
                        path = parsed.path.rstrip('/')
                        last_part = path.split('/')[-1]
                        if ('/pdf/' in href or last_part.startswith('20') or last_part.startswith('arXiv') or
                            last_part.startswith('v') or re.search(r'\d{4}\.\d{5}', last_part)):
                            href += '.pdf'
                    return href
            # sometimes rel/title indicate pdf
            if (l.rel and l.rel.lower() == "related") and l.href:
                href = l.href
                parsed = urlparse(href)
                if parsed.scheme not in ('http', 'https'):
                    logger.warning("Invalid related PDF URL scheme: %s", href)
                    continue
                if href.lower().endswith('.pdf'):
                    return href
                if '/pdf/' in href:
                    return href + '.pdf'
        # fallback: try to construct from id if possible
        if self.id:
            # id often like http://arxiv.org/abs/XXXX -> pdf URL at /pdf/XXXX
            m = re.search(r"/abs/(.+)$", self.id)
            if m:
                pdf_url = f"https://arxiv.org/pdf/{m.group(1)}.pdf"
                # Validate the constructed URL
                if urlparse(pdf_url).scheme == 'https':
                    return pdf_url
                else:
                    logger.warning("Constructed invalid PDF URL: %s", pdf_url)
        return None

    @property
    def version(self) -> Optional[int]:
        m = re.search(r"v(\d+)$", self.id)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
        return None


class ArxivResultSet(BaseModel):
    entries: List[ArxivPaper] = []
    total_results: Optional[int] = None
    start_index: Optional[int] = None
    items_per_page: Optional[int] = None
    query: Optional[str] = None
    sortBy: Optional[str] = None
    sortOrder: Optional[str] = None

    model_config = {"extra": "ignore"}
