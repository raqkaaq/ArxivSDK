"""Client for Semantic Scholar API."""
import requests
import time
import logging
from typing import Optional, List
from academic_sdk.models import Paper
from academic_sdk.errors import AcademicAPIError, AcademicNetworkError, AcademicParseError
from .models import SemanticScholarPaper

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """Client for Semantic Scholar Academic Graph API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None, user_agent: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        self.user_agent = user_agent or "SemanticScholarSDK/1.0"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})

    def _retry_request(self, request_func, max_retries=3):
        """Retry requests with exponential backoff."""
        backoff = 1
        for attempt in range(max_retries):
            try:
                return request_func()
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    logger.warning("Rate limited (429), retrying in %d seconds: %s", backoff, e)
                else:
                    logger.warning("Request failed, retrying in %d seconds: %s", backoff, e)
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
        raise AcademicNetworkError("Max retries exceeded")

    def search(self, query: str, limit: int = 10, offset: int = 0) -> List[Paper]:
        """Search for papers."""
        def request_func():
            url = f"{self.BASE_URL}/paper/search"
            params = {"query": query, "limit": limit, "offset": offset, "fields": "title,abstract,authors,year,venue"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            papers = []
            for item in data.get("data", []):
                paper = SemanticScholarPaper(
                    id=item["paperId"],
                    title=item["title"],
                    summary=item.get("abstract"),
                    authors=[{"name": a["name"]} for a in item.get("authors", [])],
                    year=item.get("year"),
                    venue=item.get("venue"),
                )
                papers.append(paper)
            return papers
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """Get paper by ID."""
        url = f"{self.BASE_URL}/paper/{paper_id}"
        params = {"fields": "title,abstract,authors,year,venue,references,citations"}
        try:
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            paper = SemanticScholarPaper(
                id=data["paperId"],
                title=data["title"],
                summary=data.get("abstract"),
                authors=[{"name": a["name"]} for a in data.get("authors", [])],
                year=data.get("year"),
                venue=data.get("venue"),
                references=[{"title": r.get("title"), "paperId": r["paperId"]} for r in data.get("references", [])],
                citations=[{"title": c.get("title"), "paperId": c["paperId"]} for c in data.get("citations", [])],
            )
            return paper
        except requests.RequestException as e:
            if resp.status_code == 404:
                return None
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    # Add more methods for other APIs as needed, like recommendations, datasets, etc.

    def close(self):
        self.session.close()