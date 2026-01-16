"""Base client for academic SDKs."""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Union
import os
import logging

from .models import Paper
from .errors import AcademicNetworkError, AcademicAPIError, AcademicParseError, AcademicDownloadError

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Abstract base client for academic APIs."""

    def __init__(self, base_url: str, user_agent: Optional[str] = None, rate_limit: float = 3.0, max_concurrent: int = 1):
        self.base_url = base_url
        self.user_agent = user_agent or "AcademicSDK/1.0"
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0.0

    async def _apply_rate_limit(self):
        """Apply rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self.last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self.last_request_time = asyncio.get_event_loop().time()

    async def _retry_request(self, request_func, max_retries=3):
        """Retry requests with backoff."""
        backoff = 1
        for attempt in range(max_retries):
            try:
                async with self.semaphore:
                    await self._apply_rate_limit()
                    return await request_func()
            except (Exception) as e:  # Broad exception for retries
                if attempt == max_retries - 1:
                    raise
                logger.warning("Request failed (attempt %d/3), retrying in %d seconds: %s", attempt + 1, backoff, e)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    @abstractmethod
    async def search(self, query: Union[str, object], start: int = 0, max_results: int = 10, timeout: float = 10.0):
        """Search for papers."""
        pass

    @abstractmethod
    async def get_by_id(self, paper_id: str, timeout: float = 10.0) -> Optional[Paper]:
        """Get paper by ID."""
        pass

    async def download_pdf(self, paper: Paper, dest_path: str, timeout: float = 20.0, overwrite: bool = False) -> str:
        """Download PDF for a paper."""
        # Shared logic for PDF downloads
        pdf_url = getattr(paper, 'pdf_url', None) or getattr(paper, 'open_access_pdf', {}).get('url')
        if not pdf_url:
            raise AcademicDownloadError('No PDF URL available for this paper')

        # Shared filename logic
        title_slug = self._slugify(getattr(paper, 'title', '') or '')
        arxiv_id = getattr(paper, 'id', '').split('/')[-1] if getattr(paper, 'id', '') else None
        if arxiv_id:
            final_name = f"{title_slug}-{arxiv_id}.pdf"
        else:
            final_name = f"{title_slug}.pdf"

        # Category logic (abstract)
        category_dir = self._get_category_dir(paper, dest_path)
        full = os.path.join(category_dir, final_name)
        if os.path.exists(full) and not overwrite:
            return full

        # Download logic (to be implemented in subclasses)
        return await self._download_file(pdf_url, full, timeout)

    def _slugify(self, text: str, maxlen: int = 80) -> str:
        """Slugify text for filenames."""
        if not text:
            return ''
        import unicodedata
        import re
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", '_', text)
        text = text.strip('_')
        if len(text) > maxlen:
            text = text[:maxlen].rstrip('_')
        return text or ''

    def _get_category_dir(self, paper: Paper, dest_path: str) -> str:
        """Get category directory (override in subclasses)."""
        cat = getattr(paper, 'primary_category', None) or getattr(paper, 'venue', None)
        if cat:
            try:
                cat_name = str(cat).replace('.', '_').upper()
                if not cat_name:
                    cat_name = 'UNKNOWN'
            except (AttributeError, TypeError):
                cat_name = 'UNKNOWN'
        else:
            cat_name = 'UNKNOWN'
        category_dir = os.path.join(dest_path, cat_name)
        os.makedirs(category_dir, exist_ok=True)
        return category_dir

    @abstractmethod
    async def _download_file(self, url: str, dest: str, timeout: float) -> str:
        """Download file implementation."""
        pass