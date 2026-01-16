from arxiv_sdk.categories import Category, CATEGORY_DESCRIPTIONS, get_category_description


def test_all_categories_have_descriptions():
    missing = [c for c in Category if c not in CATEGORY_DESCRIPTIONS]
    assert not missing, f"Missing descriptions for: {missing}"


def test_get_description_by_string():
    # pick one known mapping
    desc = get_category_description("cs.LG")
    assert desc is not None and "Machine Learning" in desc
