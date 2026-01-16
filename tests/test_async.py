"""Tests for async client."""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from arxiv_sdk.async_client import AsyncArxivClient
from arxiv_sdk.query import QueryBuilder
from arxiv_sdk.errors import ArxivDownloadError


class AsyncIter:
    """Helper for mocking async iterators."""
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)


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


@pytest.mark.asyncio
async def test_async_download_success():
    """Test successful PDF download."""
    with tempfile.TemporaryDirectory() as tmpdir:
        client = AsyncArxivClient()
        try:
            # Mock paper
            paper = Mock()
            paper.id = 'http://arxiv.org/abs/2101.00001v2'
            paper.title = 'Test Paper'
            paper.pdf_url = 'http://example.com/test.pdf'
            paper.primary_category = 'cs.AI'

            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.url = 'http://example.com/test.pdf'
            mock_response.headers = {'content-length': '13'}
            mock_response.content.iter_chunked = Mock(side_effect=lambda size: AsyncIter([b'fake pdf data']))
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.raise_for_status = Mock()

            with patch.object(client.session, 'get', return_value=mock_response):
                path = await client.download_pdf(paper, tmpdir)
                assert os.path.exists(path)
                assert os.path.getsize(path) > 0
                with open(path, 'rb') as f:
                    assert f.read() == b'fake pdf data'
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_async_download_empty_response():
    """Test download with empty response body."""
    with tempfile.TemporaryDirectory() as tmpdir:
        client = AsyncArxivClient()
        try:
            paper = Mock()
            paper.id = 'http://arxiv.org/abs/2101.00001v2'
            paper.title = 'Test Paper'
            paper.pdf_url = 'http://example.com/test.pdf'
            paper.primary_category = 'cs.AI'

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.url = 'http://example.com/test.pdf'
            mock_response.headers = {'content-length': '10'}
            mock_response.content.iter_chunked = Mock(side_effect=lambda size: AsyncIter([]))
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.raise_for_status = Mock()

            with patch.object(client.session, 'get', return_value=mock_response):
                with pytest.raises(ArxivDownloadError, match="Downloaded file is empty"):
                    await client.download_pdf(paper, tmpdir)
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_async_download_content_length_zero():
    """Test download with content-length 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        client = AsyncArxivClient()
        try:
            paper = Mock()
            paper.id = 'http://arxiv.org/abs/2101.00001v2'
            paper.title = 'Test Paper'
            paper.pdf_url = 'http://example.com/test.pdf'
            paper.primary_category = 'cs.AI'

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.url = 'http://example.com/test.pdf'
            mock_response.headers = {'content-length': '0'}
            mock_response.content.iter_chunked = Mock(side_effect=lambda size: AsyncIter([]))
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.raise_for_status = Mock()

            with patch.object(client.session, 'get', return_value=mock_response):
                with pytest.raises(ArxivDownloadError, match="Empty response"):
                    await client.download_pdf(paper, tmpdir)
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_async_download_http_error():
    """Test download with HTTP error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        client = AsyncArxivClient()
        try:
            paper = Mock()
            paper.id = 'http://arxiv.org/abs/2101.00001v2'
            paper.title = 'Test Paper'
            paper.pdf_url = 'http://example.com/test.pdf'
            paper.primary_category = 'cs.AI'

            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.url = 'http://example.com/test.pdf'
            mock_response.text = AsyncMock(return_value="Not Found")
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.raise_for_status = Mock(side_effect=Exception("404"))

            with patch.object(client.session, 'get', return_value=mock_response):
                with pytest.raises(Exception):  # ArxivAPIError or similar
                    await client.download_pdf(paper, tmpdir)
        finally:
            await client.close()