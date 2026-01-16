"""Unit tests for semantic_scholar_sdk client."""
import pytest
from unittest.mock import Mock, patch
from semantic_scholar_sdk.client import SemanticScholarClient
from academic_sdk.errors import AcademicNetworkError


@pytest.fixture
def client():
    return SemanticScholarClient()


def test_client_init_without_key():
    """Test client initialization without API key."""
    client = SemanticScholarClient()
    assert client.api_key is None


def test_client_init_with_key():
    """Test client initialization with API key."""
    client = SemanticScholarClient(api_key="test_key")
    assert client.api_key == "test_key"


@patch.dict('os.environ', {'SEMANTIC_SCHOLAR_API_KEY': 'env_key'})
def test_client_init_with_env_key():
    """Test client initialization using environment variable."""
    client = SemanticScholarClient()
    assert client.api_key == "env_key"


@patch('requests.Session.get')
def test_search_success(mock_get, client):
    """Test successful search."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {"paperId": "123", "title": "Test Paper", "abstract": "Abstract", "authors": [{"name": "Author"}], "year": 2023, "venue": "Venue"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    papers = client.search("test query")
    assert len(papers) == 1
    assert papers[0].id == "123"
    assert papers[0].title == "Test Paper"


@patch('requests.Session.get')
def test_get_by_id_success(mock_get, client):
    """Test successful get_by_id."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "paperId": "123", "title": "Test Paper", "abstract": "Abstract",
        "authors": [{"name": "Author"}], "year": 2023, "venue": "Venue",
        "references": [{"title": "Ref", "paperId": "ref1"}],
        "citations": [{"title": "Cit", "paperId": "cit1"}]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    paper = client.get_by_id("123")
    assert paper.id == "123"
    assert paper.title == "Test Paper"
    assert len(paper.references) == 1
    assert len(paper.citations) == 1


@patch('requests.Session.get')
@patch('time.sleep')
def test_backoff_on_429(mock_sleep, mock_get, client):
    """Test exponential backoff on 429 errors."""
    import requests
    # First call returns 429, second succeeds
    mock_response_429 = Mock()
    mock_response_429.status_code = 429
    mock_response_429.raise_for_status.side_effect = requests.HTTPError("429")
    mock_response_429.raise_for_status.response = mock_response_429  # for hasattr check

    mock_response_success = Mock()
    mock_response_success.json.return_value = {"data": []}
    mock_response_success.raise_for_status = Mock()

    mock_get.side_effect = [
        mock_response_429,
        mock_response_success
    ]

    client.search("test")

    # Should have slept (backoff)
    mock_sleep.assert_called()


@patch('requests.Session.get')
def test_network_error(mock_get, client):
    """Test network error handling."""
    import requests
    mock_get.side_effect = requests.RequestException("Network error")

    with pytest.raises(AcademicNetworkError):
        client.search("test")


@patch('requests.Session.get')
def test_get_paper_citations(mock_get, client):
    """Test get_paper_citations."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"title": "Cit1", "paperId": "cit1"}]}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    citations = client.get_paper_citations("123")
    assert len(citations) == 1
    assert citations[0]["title"] == "Cit1"


@patch('requests.Session.get')
def test_get_paper_references(mock_get, client):
    """Test get_paper_references."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"title": "Ref1", "paperId": "ref1"}]}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    references = client.get_paper_references("123")
    assert len(references) == 1
    assert references[0]["title"] == "Ref1"


@patch('requests.Session.post')
def test_batch_get_papers(mock_post, client):
    """Test batch_get_papers."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {"paperId": "123", "title": "Paper1"},
        {"paperId": "456", "title": "Paper2"}
    ]
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    papers = client.batch_get_papers(["123", "456"])
    assert len(papers) == 2
    assert papers[0].id == "123"


@patch('requests.Session.get')
def test_search_authors(mock_get, client):
    """Test search_authors."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"name": "Author1", "paperCount": 10}]}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    authors = client.search_authors("author name")
    assert len(authors) == 1
    assert authors[0]["name"] == "Author1"


@patch('requests.Session.get')
def test_get_author_by_id(mock_get, client):
    """Test get_author_by_id."""
    mock_response = Mock()
    mock_response.json.return_value = {"name": "Author1", "paperCount": 10}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    author = client.get_author_by_id("auth123")
    assert author["name"] == "Author1"


@patch('requests.Session.get')
def test_autocomplete(mock_get, client):
    """Test autocomplete."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"title": "Suggestion1"}]}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    suggestions = client.autocomplete("query")
    assert len(suggestions) == 1
    assert suggestions[0] == "Suggestion1"