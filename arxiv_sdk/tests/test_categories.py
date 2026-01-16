from arxiv_sdk.categories import Category, CATEGORY_DESCRIPTIONS, get_category_description, search_categories, load_full_taxonomy


def test_all_categories_have_descriptions():
    missing = [c for c in Category if c not in CATEGORY_DESCRIPTIONS]
    assert not missing, f"Missing descriptions for: {missing}"


def test_get_description_by_string():
    # pick one known mapping
    desc = get_category_description("cs.LG")
    assert desc is not None and "Machine Learning" in desc


def test_search_categories():
    results = search_categories("machine learning")
    assert len(results) > 0
    assert any("cs.LG" in r[0] for r in results)


def test_load_full_taxonomy():
    tax = load_full_taxonomy()
    assert isinstance(tax, dict)
    assert "cs.LG" in tax
