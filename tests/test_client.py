from arxiv_sdk import ArxivClient


def test_search_empty_query():
    client = ArxivClient()
    try:
        client.search("")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "empty" in str(e)


def test_get_by_id_invalid_format():
    client = ArxivClient()
    try:
        client.get_by_id("invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "format" in str(e)


def test_search_invalid_start():
    client = ArxivClient()
    try:
        client.search("test", start=-1)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "start" in str(e)


def test_search_max_results_too_large():
    client = ArxivClient()
    try:
        client.search("test", max_results=3000)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "2000" in str(e)