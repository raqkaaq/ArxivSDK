# ArxivSDK

A small, synchronous Python SDK for interacting with the arXiv Atom API. The SDK provides typed models, a fluent query builder, a simple HTTP client, a small category enum, and PDF download helpers.

**Quick overview**
- `ArxivClient` ([ArxivSDK/client.py](ArxivSDK/client.py)): main HTTP client. Methods: `search()`, `get_by_id()`, `download_pdf()`.
- `QueryBuilder` ([ArxivSDK/query.py](ArxivSDK/query.py)): fluent builder for arXiv `search_query` strings (title, author, abstract, category, boolean ops, date ranges, sorting).
- `models` ([ArxivSDK/models.py](ArxivSDK/models.py)): Pydantic v2 models `ArxivPaper`, `Author`, `Link`, and `ArxivResultSet`.
- `errors` ([ArxivSDK/errors.py](ArxivSDK/errors.py)): SDK-specific exceptions (`ArxivAPIError`, `ArxivNetworkError`, `ArxivParseError`, `ArxivDownloadError`).
- `categories` ([ArxivSDK/categories.py](ArxivSDK/categories.py)): small `Category` Enum and descriptions map for common arXiv category codes.

**Design principles**
- Synchronous by default (requests + feedparser). Easy to extend for async in future.
- Convert Atom feed entries into typed Pydantic models immediately for safe access.
- Keep behavior explicit and predictable (e.g., `download_pdf` requires an existing hub directory).

Usage examples
--------------
Search by title + author:

```python
from arxiv_sdk import ArxivClient
from arxiv_sdk.query import QueryBuilder

client = ArxivClient()
qb = QueryBuilder().title("deep learning").and_().author("Goodfellow")
results = client.search(qb, max_results=10)
for paper in results.entries:
    print(paper.title, paper.primary_category)
```

Get a single paper by id:

```python
paper = ArxivClient().get_by_id("2101.00001v2")
print(paper.title, paper.doi)
```

Download PDF (category-organized):

```python
client = ArxivClient()
# hub_dir must exist; the SDK will create a category subfolder inside it
path = client.download_pdf(paper, "./downloads", overwrite=False)
print("Saved to", path)
```

Filename & storage behavior
---------------------------
- Files are saved under a hub path you provide as `dest_path`.
- The SDK creates a category subfolder (derived from `paper.primary_category`, e.g. `cs.LG` -> `CS_LG`) under the hub.
- Files are named `{title_slug}-{arxiv_id}.pdf` where `title_slug` is a sanitized snake_case slug of the title and `arxiv_id` is the arXiv identifier (keeps filenames readable and unique).
- The hub directory (`dest_path`) must already exist; the SDK will create the category subfolder but will raise `ArxivDownloadError` if the hub does not exist.

QueryBuilder highlights
-----------------------
- Fielded searches: `title`, `author`, `abstract`, `comment`, `journal_ref`, `category`, `report_number`.
- Boolean operators: `and_()`, `or_()`, `andnot_()` and `group()` for parentheses.
- `date_range(start, end)` accepts many human-friendly date formats and normalizes to arXiv's `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]` format.

Testing
-------
- Unit tests live under `ArxivSDK/tests/`.
- Live integration tests that make real API calls are guarded by the environment variable `ARXIV_SDK_RUN_LIVE_TESTS=1` — set it to run live queries.
- Run unit tests for the SDK with:

```bash
export PYTHONPATH=$(pwd)
pip install -r ArxivSDK/requirements.txt
pytest ArxivSDK/tests -q
```

Extending categories
--------------------
The included `Category` enum is a compact, curated set of common codes. To support the full arXiv taxonomy you can either extend `ArxivSDK/categories.py` or generate it from the official taxonomy page.

Contributing
------------
- Follow PEP8 and keep changes focused. Tests should accompany behavior changes.
- For large changes (async API, extensive taxonomy generation) open an issue first to discuss design tradeoffs.

License & notes
---------------
This repository includes minimal dependencies (requests, feedparser, pydantic). The SDK is intended as an easy-to-use layer over the arXiv Atom API — follow arXiv API rules (rate limits and polite querying).
# ArxivSDK
