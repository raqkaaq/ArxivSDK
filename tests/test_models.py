from arxiv_sdk.models import ArxivPaper, Link, Author
from datetime import datetime


def make_entry():
    return {
        'id': 'http://arxiv.org/abs/2101.00001v2',
        'title': '  Example Title  ',
        'summary': ' An abstract. ',
        'authors': [{'name': 'Alice'}, {'name': 'Bob'}],
        'published': '2021-01-01T00:00:00Z',
        'updated': '2021-02-01T00:00:00Z',
        'links': [
            {'href': 'http://arxiv.org/abs/2101.00001v2', 'rel': 'alternate', 'type': 'text/html'},
            {'href': 'http://arxiv.org/pdf/2101.00001v2', 'rel': 'related', 'type': 'application/pdf'},
        ],
        'arxiv_primary_category': {'term': 'cs.LG'},
        'arxiv_comment': 'No comment',
        'arxiv_journal_ref': None,
        'arxiv_doi': None,
    }


def test_paper_model():
    entry = make_entry()
    p = ArxivPaper.model_validate(entry)
    assert p.title == 'Example Title'
    assert p.summary == 'An abstract.'
    assert p.pdf_url.endswith('.pdf')
    assert p.version == 2
