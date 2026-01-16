from __future__ import annotations
from typing import Optional, Union, List
import time
import os
import logging
from urllib.parse import urlparse, unquote
import importlib.metadata
import re
import unicodedata

import requests
import feedparser

from .models import ArxivPaper, ArxivResultSet
from .errors import ArxivAPIError, ArxivNetworkError, ArxivParseError, ArxivDownloadError

logger = logging.getLogger(__name__)


def _default_user_agent(app_name="ArxivSDK"):
    env = os.environ.get("ARXIV_SDK_USER_AGENT")
    if env:
        return env
    try:
        ver = importlib.metadata.version("ArxivSDK")
    except importlib.metadata.PackageNotFoundError:
        ver = "0.0"
    url = os.environ.get("ARXIV_SDK_HOMEPAGE", "https://example.invalid")
    email = os.environ.get("ARXIV_SDK_CONTACT", "")
    contact = f" (+{url}{'; mailto:'+email if email else ''})"
    return f"{app_name}/{ver}{contact}"


class ArxivClient:
    """Client for interacting with the arXiv Atom API.

    Provides methods to search for papers, retrieve by ID, and download PDFs.
    Handles retries, rate limiting, and error handling for stability.
    """
    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None, user_agent: Optional[str] = None, rate_limit: Optional[float] = None):
        """Initialize the client.

        Args:
            base_url: Custom base URL for the API.
            session: Custom requests session.
            user_agent: Custom user agent string.
            rate_limit: Delay in seconds between requests.
        """
        self.base_url = base_url or self.BASE_URL
        self.session = session or requests.Session()
        self.user_agent = user_agent or _default_user_agent()
        self.rate_limit = rate_limit

    def _apply_rate_limit(self):
        if self.rate_limit:
            time.sleep(self.rate_limit)

    def search(self, query: Union[str, object], start: int = 0, max_results: int = 10, timeout: float = 10.0) -> ArxivResultSet:
        if isinstance(query, str):
            if not query.strip():
                raise ValueError("query string cannot be empty")
            search_query = query
            sortBy = None
            sortOrder = None
        else:
            # QueryBuilder-like
            if not hasattr(query, 'build'):
                raise ValueError("query must be a QueryBuilder or string")
            search_query = query.build()
            sortBy = getattr(query, 'sortBy', None)
            sortOrder = getattr(query, 'sortOrder', None)

        if start < 0:
            raise ValueError("start must be >= 0")
        if max_results < 0:
            raise ValueError("max_results must be >= 0")
        if max_results > 2000:
            # respect recommended slice limit; allow but warn or cap — here we cap
            raise ValueError("max_results must be <= 2000 per request; page large sets in slices")

        params = {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
        }
        if sortBy:
            params['sortBy'] = sortBy
        if sortOrder:
            params['sortOrder'] = sortOrder

        headers = {"User-Agent": self.user_agent}

        self._apply_rate_limit()

        for attempt in range(3):
            try:
                resp = self.session.get(self.base_url, params=params, timeout=timeout, headers=headers)
                break
            except requests.RequestException as e:
                if attempt == 2:
                    raise ArxivNetworkError(e)
                backoff = 2 ** attempt
                logger.warning("Search request failed (attempt %d/3), retrying in %d seconds: %s", attempt + 1, backoff, e)
                time.sleep(backoff)

        if resp.status_code != 200:
            raise ArxivAPIError(resp.status_code, body=resp.text)

        feed = feedparser.parse(resp.text)
        if not hasattr(feed, 'entries'):
            raise ArxivParseError('No entries in feed')

        # OpenSearch metadata lives in feed.feed
        feed_meta = getattr(feed, 'feed', {})
        total = None
        start_index = None
        items_per_page = None
        try:
            total = int(feed_meta.get('opensearch_totalresults')) if feed_meta.get('opensearch_totalresults') is not None else None
        except (ValueError, TypeError):
            logger.warning("Failed to parse opensearch_totalresults: %s", feed_meta.get('opensearch_totalresults'))
            total = None
        try:
            start_index = int(feed_meta.get('opensearch_startindex')) if feed_meta.get('opensearch_startindex') is not None else None
        except (ValueError, TypeError):
            logger.warning("Failed to parse opensearch_startindex: %s", feed_meta.get('opensearch_startindex'))
            start_index = None
        try:
            items_per_page = int(feed_meta.get('opensearch_itemsperpage')) if feed_meta.get('opensearch_itemsperpage') is not None else None
        except (ValueError, TypeError):
            logger.warning("Failed to parse opensearch_itemsperpage: %s", feed_meta.get('opensearch_itemsperpage'))
            items_per_page = None

        papers: List[ArxivPaper] = []
        parse_errors = []
        for idx, entry in enumerate(feed.entries):
            # feedparser entries are dict-like
            try:
                # normalize entry fields for Pydantic; leave extra ignored
                papers.append(ArxivPaper.model_validate(entry))
            except (ValueError, TypeError) as e:
                # collect parse errors to surface a helpful message
                logger.warning("Failed to parse entry at index %d: %s", idx, e)
                parse_errors.append({'index': idx, 'error': str(e)})

        if parse_errors:
            # surface a clear parse error with a short summary
            first = parse_errors[0]
            raise ArxivParseError(f"{len(parse_errors)} entries failed to parse (first at index {first['index']}): {first['error']}")

        result = ArxivResultSet(entries=papers, total_results=total, start_index=start_index, items_per_page=items_per_page, query=search_query, sortBy=sortBy, sortOrder=sortOrder)
        return result

    def get_by_id(self, arxiv_id: str, timeout: float = 10.0) -> Optional[ArxivPaper]:
        if not re.match(r'\d{4}\.\d{5}(v\d+)?$', arxiv_id):
            raise ValueError("Invalid arXiv ID format")
        params = {"id_list": arxiv_id, "start": 0, "max_results": 1}
        headers = {"User-Agent": self.user_agent}
        self._apply_rate_limit()
        for attempt in range(3):
            try:
                resp = self.session.get(self.base_url, params=params, timeout=timeout, headers=headers)
                break
            except requests.RequestException as e:
                if attempt == 2:
                    raise ArxivNetworkError(e)
                backoff = 2 ** attempt
                logger.warning("Get by ID request failed (attempt %d/3), retrying in %d seconds: %s", attempt + 1, backoff, e)
                time.sleep(backoff)
        if resp.status_code != 200:
            raise ArxivAPIError(resp.status_code, body=resp.text)
        feed = feedparser.parse(resp.text)
        if not feed.entries:
            return None
        try:
            return ArxivPaper.model_validate(feed.entries[0])
        except Exception as e:
            raise ArxivParseError(e)

    def download_pdf(self, paper: ArxivPaper, dest_path: str, timeout: float = 20.0, overwrite: bool = False) -> str:
        url = paper.pdf_url
        if not url:
            raise ArxivDownloadError('No PDF URL available for this paper')
        self._apply_rate_limit()
        for attempt in range(3):
            try:
                with self.session.get(url, stream=True, timeout=timeout, headers={"User-Agent": self.user_agent}) as r:
                    r.raise_for_status()
                    # try content-disposition
                    filename = None
                    cd = r.headers.get('content-disposition')
                    if cd:
                        m = re.search(r'filename\*=UTF-8''(.+)|filename="?([^";]+)"?', cd)
                        if m:
                            filename = unquote(m.group(1) or m.group(2))
                    if not filename:
                        parsed = urlparse(r.url)
                        filename = os.path.basename(parsed.path)
                    # Build a readable, unique filename: title_slug-arxivid.pdf
                    # Extract arXiv id from paper.id if available
                    arxiv_id = None
                    try:
                        m_id = re.search(r"/abs/(.+)$", getattr(paper, 'id', '') or '')
                        if m_id:
                            arxiv_id = m_id.group(1)
                    except (TypeError, AttributeError) as e:
                        logger.warning("Failed to extract arxiv_id: %s", e)
                        arxiv_id = None

                    def _slugify(text: str, maxlen: int = 80) -> str:
                        if not text:
                            return ''
                        text = unicodedata.normalize('NFKD', text)
                        text = text.encode('ascii', 'ignore').decode('ascii')
                        text = text.lower()
                        text = re.sub(r"[^a-z0-9]+", '_', text)
                        text = text.strip('_')
                        if len(text) > maxlen:
                            text = text[:maxlen].rstrip('_')
                        return text or ''

                    title_slug = _slugify(getattr(paper, 'title', '') or '')
                    if not title_slug:
                        title_slug = os.path.splitext(filename)[0]

                    if arxiv_id:
                        final_name = f"{title_slug}-{arxiv_id}.pdf"
                    else:
                        final_name = f"{title_slug}.pdf"

                    # require the hub dest_path to already exist and be a directory
                    if not os.path.isdir(dest_path):
                        raise ArxivDownloadError(f"Destination path does not exist: {dest_path}")

                    # create a category subfolder under the hub (e.g. CS_LG)
                    cat = getattr(paper, 'primary_category', None)
                    if cat:
                        try:
                            cat_name = str(cat).replace('.', '_').upper()
                            if not cat_name:
                                cat_name = 'UNKNOWN'
                        except (AttributeError, TypeError) as e:
                            logger.warning("Failed to normalize category: %s", e)
                            cat_name = 'UNKNOWN'
                    else:
                        cat_name = 'UNKNOWN'

                    category_dir = os.path.join(dest_path, cat_name)
                    try:
                        os.makedirs(category_dir, exist_ok=True)
                    except OSError as e:
                        raise ArxivDownloadError(f"Failed to create category directory {category_dir}: {e}")

                    full = os.path.join(category_dir, final_name)
                    if os.path.exists(full) and not overwrite:
                        return full
                    try:
                        with open(full, 'wb') as fh:
                            bytes_written = 0
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    fh.write(chunk)
                                    bytes_written += len(chunk)
                        if bytes_written == 0:
                            os.remove(full)
                            raise ArxivDownloadError("Downloaded file is empty")

                        # Save paper metadata as JSON
                        json_path = full.replace('.pdf', '.json')
                        try:
                            with open(json_path, 'w', encoding='utf-8') as jf:
                                jf.write(paper.model_dump_json(indent=2))
                        except Exception as e:
                            logger.warning("Failed to save metadata JSON for %s: %s", full, e)
                            # Don't fail the download for this
                    except OSError as e:
                        if os.path.exists(full):
                            os.remove(full)
                        raise ArxivDownloadError(f"File system error during download: {e}")
                    return full
            except (requests.RequestException, OSError) as e:
                if attempt == 2:
                    raise ArxivDownloadError(e)
                backoff = 2 ** attempt
                logger.warning("Download request failed (attempt %d/3), retrying in %d seconds: %s", attempt + 1, backoff, e)
                time.sleep(backoff)
