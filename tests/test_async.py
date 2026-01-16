"""Tests for async client."""
import pytest
from arxiv_sdk.async_client import AsyncArxivClient
from arxiv_sdk.query import QueryBuilder


@pytest.mark.asyncio
async def test_async_search():
    client = AsyncArxivClient()
    try:
        qb = QueryBuilder().title("test")
        results = await client.search(qb, max_results=1)
        assert results is not None
        assert len(results.entries) <= 1
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_get_by_id():
    client = AsyncArxivClient()
    try:
        paper = await client.get_by_id("2101.00001v2")
        assert paper is not None
        assert paper.id == "http://arxiv.org/abs/2101.00001v2"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_invalid_query():
    client = AsyncArxivClient()
    try:
        with pytest.raises(ValueError):
            await client.search("")
    finally:
        await client.close()