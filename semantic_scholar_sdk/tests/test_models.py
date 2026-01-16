"""Unit tests for semantic_scholar_sdk models."""
from semantic_scholar_sdk.models import SemanticScholarPaper


def test_semantic_scholar_paper_creation():
    """Test creating a SemanticScholarPaper."""
    paper = SemanticScholarPaper(
        id="12345",
        title="Test Paper",
        summary="Abstract here",
        authors=[{"name": "Author One"}],
        year=2023,
        venue="Test Venue"
    )
    assert paper.id == "12345"
    assert paper.title == "Test Paper"
    assert paper.year == 2023
    assert paper.venue == "Test Venue"


def test_semantic_scholar_paper_inheritance():
    """Test that SemanticScholarPaper inherits from Paper."""
    from academic_sdk.models import Paper
    paper = SemanticScholarPaper(id="123", title="Test")
    assert isinstance(paper, Paper)


def test_optional_fields():
    """Test optional fields specific to Semantic Scholar."""
    paper = SemanticScholarPaper(
        id="123",
        title="Test",
        citation_count=10,
        influential_citation_count=5,
        references=[{"title": "Ref1", "paperId": "ref1"}]
    )
    assert paper.citation_count == 10
    assert len(paper.references) == 1