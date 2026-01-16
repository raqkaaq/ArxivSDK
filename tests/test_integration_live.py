import os
from datetime import datetime, timezone, timedelta
import pytest

from arxiv_sdk import ArxivClient
from arxiv_sdk.query import QueryBuilder


RUN_LIVE = os.environ.get("ARXIV_SDK_RUN_LIVE_TESTS", "0").lower() in ("1", "true", "yes")

@pytest.mark.skipif(not RUN_LIVE, reason="Set ARXIV_SDK_RUN_LIVE_TESTS=1 to run live arXiv API tests")
def test_date_range_live_recent_week():
    """Live integration test: query arXiv for papers submitted in the last 7 days.

    This test is intentionally guarded by an environment variable to avoid
    accidental network calls in CI or local runs.
    """
    now = datetime.now(timezone.utc)
    start_dt = now - timedelta(days=7)
    # normalize start to the beginning of the start day because the builder
    # accepts date-only inputs and normalizes them to 00:00 of that day
    start_day_start = datetime(start_dt.year, start_dt.month, start_dt.day, tzinfo=timezone.utc)
    # Format dates as YYYY-MM-DD (QueryBuilder will parse and normalize)
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = now.strftime("%Y-%m-%d")

    qb = QueryBuilder().date_range(start_str, end_str)
    client = ArxivClient()

    # keep results small to be polite to the API
    results = client.search(qb, max_results=5)

    assert results is not None
    assert isinstance(results.entries, list)
    # At least 0 results is acceptable; if there are results, verify date range
    if results.entries:
        for p in results.entries:
            assert p.published is not None
            # Normalize published to UTC-aware datetime
            pub = p.published
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            else:
                pub = pub.astimezone(timezone.utc)
            assert start_day_start <= pub <= now


@pytest.mark.skipif(not RUN_LIVE, reason="Set ARXIV_SDK_RUN_LIVE_TESTS=1 to run live arXiv API tests")
def test_date_range_live_specific_window():
    """Live test for a small historical window likely to have results.

    We pick a known month in the past to increase likelihood of results
    without returning huge sets. This is still a live network call and
    guarded by the env var.
    """
    # Example historical window: January 2020
    qb = QueryBuilder().date_range("2020-01-01", "2020-01-31")
    client = ArxivClient()
    results = client.search(qb, max_results=3)
    assert results is not None
    assert isinstance(results.entries, list)
    # If there are entries, ensure published dates fall in the window
    if results.entries:
        s = datetime(2020, 1, 1, tzinfo=timezone.utc)
        e = datetime(2020, 1, 31, 23, 59, tzinfo=timezone.utc)
        for p in results.entries:
            assert p.published is not None
            pub = p.published
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            else:
                pub = pub.astimezone(timezone.utc)
            assert s <= pub <= e
