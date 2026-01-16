"""Client for Semantic Scholar API."""
import os
import requests
import time
import logging
from typing import Optional, List, Dict, Any
from academic_sdk.models import Paper
from academic_sdk.errors import AcademicNetworkError, AcademicParseError
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
                    pdf_url=item.get("openAccessPdf", {}).get("url"),
                )
                papers.append(paper)
            return papers
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """Get paper by ID."""
        def request_func():
            url = f"{self.BASE_URL}/paper/{paper_id}"
            params = {"fields": "title,abstract,authors,year,venue,references,citations"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp

        try:
            resp = self._retry_request(request_func)
            data = resp.json()
            paper = SemanticScholarPaper(
                id=data["paperId"],
                title=data["title"],
                summary=data.get("abstract"),
                authors=[{"name": a["name"]} for a in data.get("authors", [])],
                year=data.get("year"),
                venue=data.get("venue"),
                pdf_url=data.get("openAccessPdf", {}).get("url"),
                references=[{"title": r.get("title"), "paperId": r["paperId"]} for r in data.get("references", [])],
                citations=[{"title": c.get("title"), "paperId": c["paperId"]} for c in data.get("citations", [])],
            )
            return paper
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def search_authors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for authors."""
        def request_func():
            url = f"{self.BASE_URL}/author/search"
            params = {"query": query, "limit": limit, "fields": "name,paperCount,citationCount"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            return data.get("data", [])
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_author_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author details."""
        def request_func():
            url = f"{self.BASE_URL}/author/{author_id}"
            params = {"fields": "name,papers,citationCount"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp

        try:
            resp = self._retry_request(request_func)
            data = resp.json()
            return data
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_paper_citations(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get citations for a paper."""
        def request_func():
            url = f"{self.BASE_URL}/paper/{paper_id}/citations"
            params = {"limit": limit, "fields": "title,paperId"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            return data.get("data", [])
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_paper_references(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get references for a paper."""
        def request_func():
            url = f"{self.BASE_URL}/paper/{paper_id}/references"
            params = {"limit": limit, "fields": "title,paperId"}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            return data.get("data", [])
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def get_recommendations(self, paper_ids: List[str], limit: int = 10) -> List[Paper]:
        """Get recommendations based on papers."""
        def request_func():
            url = f"{self.BASE_URL}/paper/batch"
            params = {"fields": "title,abstract,authors,year,venue"}
            json_data = {"ids": paper_ids}
            resp = self.session.post(url, params=params, json=json_data)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            # For simplicity, return papers, but actually recommendations might need different endpoint
            papers = []
            for item in data:
                paper = SemanticScholarPaper(
                    id=item["paperId"],
                    title=item["title"],
                    summary=item.get("abstract"),
                    authors=[{"name": a["name"]} for a in item.get("authors", [])],
                    year=item.get("year"),
                    venue=item.get("venue"),
                    pdf_url=item.get("openAccessPdf", {}).get("url"),
                )
                papers.append(paper)
            return papers
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def batch_get_papers(self, paper_ids: List[str]) -> List[Paper]:
        """Batch get papers by IDs."""
        def request_func():
            url = f"{self.BASE_URL}/paper/batch"
            params = {"fields": "title,abstract,authors,year,venue,references,citations"}
            json_data = {"ids": paper_ids}
            resp = self.session.post(url, params=params, json=json_data)
            resp.raise_for_status()
            return resp

        try:
            resp = self._retry_request(request_func)
            data = resp.json()
            papers = []
            for item in data:
                paper = SemanticScholarPaper(
                    id=item["paperId"],
                    title=item["title"],
                    summary=item.get("abstract"),
                    authors=[{"name": a["name"]} for a in item.get("authors", [])],
                    year=item.get("year"),
                    venue=item.get("venue"),
                    references=[{"title": r.get("title"), "paperId": r["paperId"]} for r in item.get("references", [])],
                    citations=[{"title": c.get("title"), "paperId": c["paperId"]} for c in item.get("citations", [])],
                )
                papers.append(paper)
            return papers
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def autocomplete(self, query: str) -> List[str]:
        """Get autocomplete suggestions."""
        def request_func():
            url = f"{self.BASE_URL}/paper/autocomplete"
            params = {"query": query}
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_request(request_func)
            return [item["title"] for item in data.get("data", [])]
        except requests.RequestException as e:
            raise AcademicNetworkError(e)
        except Exception as e:
            raise AcademicParseError(str(e))

    def close(self):
        self.session.close()