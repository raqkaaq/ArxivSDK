# ArxivSDK

A small Python SDK for interacting with the arXiv Atom API. The SDK provides typed models, a fluent query builder, synchronous and asynchronous HTTP clients, an expanded category taxonomy, PDF processing, advanced query options, and an interactive TUI.

**Quick overview**
- `ArxivClient` ([ArxivSDK/client.py](ArxivSDK/client.py)): synchronous HTTP client. Methods: `search()`, `get_by_id()`, `download_pdf()`.
- `AsyncArxivClient` ([ArxivSDK/async_client.py](ArxivSDK/async_client.py)): asynchronous HTTP client with rate limiting (1 req/3 sec).
- `QueryBuilder` ([ArxivSDK/query.py](ArxivSDK/query.py)): fluent builder for arXiv `search_query` strings (title, author, abstract, comment, journal_ref, report_number, doi, category, boolean ops, date ranges, sorting).
- `models` ([ArxivSDK/models.py](ArxivSDK/models.py)): Pydantic v2 models `ArxivPaper`, `Author`, `Link`, and `ArxivResultSet`.
- `errors` ([ArxivSDK/errors.py](ArxivSDK/errors.py)): SDK-specific exceptions (`ArxivAPIError`, `ArxivNetworkError`, `ArxivParseError`, `ArxivDownloadError`).
- `categories` ([ArxivSDK/categories.py](ArxivSDK/categories.py)): expanded `Category` Enum with full arXiv taxonomy, search helpers, and descriptions.
- `ArxivPDFProcessor` ([ArxivSDK/pdf_processor.py](ArxivSDK/pdf_processor.py)): PDF text/table extraction and metadata using PyMuPDF.

**Design principles**
- Synchronous by default (requests + feedparser). Async support available via AsyncArxivClient.
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

Async usage:

```python
import asyncio
from arxiv_sdk.async_client import AsyncArxivClient

async def main():
    client = AsyncArxivClient()
    try:
        qb = QueryBuilder().title("deep learning").and_().author("Goodfellow")
        results = await client.search(qb, max_results=10)
        for paper in results.entries:
            print(paper.title)
    finally:
        await client.close()

asyncio.run(main())
```

Category search:

```python
from arxiv_sdk.categories import search_categories
results = search_categories("machine learning")
print(results)  # List of (code, description)
```

PDF processing:

```python
from arxiv_sdk.pdf_processor import ArxivPDFProcessor
processor = ArxivPDFProcessor()
text = processor.extract_text("path/to/paper.pdf")
tables = processor.extract_tables("path/to/paper.pdf")
```

Advanced queries:

```python
qb = QueryBuilder().title("quantum").comment("review").doi("10.1234/example").date_range("last week", "today")
```

TUI (Interactive Terminal UI):

```bash
pip install arxiv-tui  # Installs TUI package (requires arxiv-sdk)
arxiv-tui --downloads ./data  # Launches TUI
```

Or from source:
```bash
pip install ./arxiv_tui  # Install TUI
python main.py --downloads ./data
```

Navigate with keyboard: Search papers, browse results, view details, download PDFs, manage downloads.

Filename & storage behavior
---------------------------
- Files are saved under a hub path you provide as `dest_path`.
- The SDK creates a category subfolder (derived from `paper.primary_category`, e.g. `cs.LG` -> `CS_LG`) under the hub.
- Files are named `{title_slug}-{arxiv_id}.pdf` where `title_slug` is a sanitized snake_case slug of the title and `arxiv_id` is the arXiv identifier (keeps filenames readable and unique).
- The hub directory (`dest_path`) must already exist; the SDK will create the category subfolder but will raise `ArxivDownloadError` if the hub does not exist.

QueryBuilder highlights
-----------------------
- Fielded searches: `title`, `author`, `abstract`, `comment`, `journal_ref`, `report_number`, `doi`, `category`.
- Boolean operators: `and_()`, `or_()`, `andnot_()` and `group()` for parentheses.
- `date_range(start, end)` accepts many human-friendly date formats (including relative like 'last week', 'today') and normalizes to arXiv's `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]` format.

Testing
-------
- Unit tests live under `ArxivSDK/tests/`.
- Live integration tests that make real API calls are guarded by the environment variable `ARXIV_SDK_RUN_LIVE_TESTS=1` — set it to run live queries.
- Async tests require `pytest-asyncio`.
- Run unit tests for the SDK with:

```bash
export PYTHONPATH=$(pwd)
pip install -e .  # Install SDK
pip install aiohttp PyMuPDF  # for optional features
pytest tests -q
```

For TUI tests:
```bash
pip install ./arxiv_tui
pytest arxiv_tui/tests  # If added
```

Extending categories
--------------------
The `Category` enum includes the full arXiv taxonomy (150+ codes) with search helpers. Use `search_categories()` to find categories by keyword or description.

Contributing
------------
- Follow PEP8 and keep changes focused. Tests should accompany behavior changes.
- For large changes (extensive taxonomy generation) open an issue first to discuss design tradeoffs.

License & notes
---------------
This repository includes minimal dependencies (requests, feedparser, pydantic). Optional dependencies: aiohttp for async, PyMuPDF for PDF processing. The SDK is intended as an easy-to-use layer over the arXiv Atom API — follow arXiv API rules (rate limits and polite querying).

v0.2.0 Changes
---------------
- Added AsyncArxivClient with rate limiting (1 req/3 sec) and retries.
- Expanded Category enum to full arXiv taxonomy (150+ codes) with search helpers.
- Introduced ArxivPDFProcessor for PDF text/table extraction and metadata using PyMuPDF.
- Extended QueryBuilder with doi(), improved date parsing (relative dates), and validation.
- Enhanced error handling, logging, and testing throughout.

# ArxivSDK
