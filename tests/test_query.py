from arxiv_sdk.query import QueryBuilder


def test_build_simple():
    qb = QueryBuilder().title("deep learning").and_().author("Goodfellow")
    s = qb.build()
    assert 'ti:"deep learning"' in s
    assert 'au:"Goodfellow"' in s


def test_date_range():
    qb = QueryBuilder().date_range('2023-01-01', '2023-12-31')
    s = qb.build()
    assert 'submittedDate:[' in s
    assert '20230101' in s


def test_invalid_date_format():
    qb = QueryBuilder()
    try:
        qb.date_range('invalid', '2023-01-01')
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_today_and_date_range_conflict():
    qb = QueryBuilder().today().date_range('2023-01-01', '2023-12-31')
    try:
        qb.build()
        assert False, "Should raise ValueError"
    except ValueError:
        pass
