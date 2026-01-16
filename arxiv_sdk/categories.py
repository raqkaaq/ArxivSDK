"""arXiv category codes.

This module provides a simple Enum of commonly-used arXiv category codes.
Use like:

    from ArxivSDK.categories import Category
    qb.category(Category.CS_LG.value)

The Enum values are the standard arXiv category codes (e.g. ``cs.LG``).
This file is intentionally a compact, curated list — extend as needed.
"""
from enum import Enum


class Category(str, Enum):
    # Computer Science
    CS_AI = "cs.AI"
    CS_LG = "cs.LG"
    CS_CV = "cs.CV"
    CS_CL = "cs.CL"
    CS_NE = "cs.NE"
    CS_CR = "cs.CR"

    # Mathematics
    MATH_PR = "math.PR"
    MATH_NA = "math.NA"

    # Statistics
    STAT_ML = "stat.ML"

    # Physics / High energy
    HEP_TH = "hep-th"
    HEP_PH = "hep-ph"

    # Astrophysics
    ASTRO_PH = "astro-ph"

    # Nuclear
    NUCL_TH = "nucl-th"

    # Quantitative Biology / Finance
    Q_BIO = "q-bio"
    Q_FIN = "q-fin"

    # Other common
    COND_MAT = "cond-mat"
    EESS = "eess"


__all__ = ["Category"]

# Human-readable descriptions for categories. Keep in sync with `Category`.
CATEGORY_DESCRIPTIONS: dict[Category, str] = {
    Category.CS_AI: "Computer Science - Artificial Intelligence",
    Category.CS_LG: "Computer Science - Machine Learning",
    Category.CS_CV: "Computer Science - Computer Vision and Pattern Recognition",
    Category.CS_CL: "Computer Science - Computation and Language (NLP)",
    Category.CS_NE: "Computer Science - Neural and Evolutionary Computing",
    Category.CS_CR: "Computer Science - Cryptography and Security",

    Category.MATH_PR: "Mathematics - Probability",
    Category.MATH_NA: "Mathematics - Numerical Analysis",

    Category.STAT_ML: "Statistics - Machine Learning",

    Category.HEP_TH: "High Energy Physics - Theory",
    Category.HEP_PH: "High Energy Physics - Phenomenology",

    Category.ASTRO_PH: "Astrophysics",

    Category.NUCL_TH: "Nuclear Theory",

    Category.Q_BIO: "Quantitative Biology",
    Category.Q_FIN: "Quantitative Finance",

    Category.COND_MAT: "Condensed Matter",
    Category.EESS: "Electrical Engineering and Systems Science",
}


def get_category_description(cat: Category | str) -> str | None:
    """Return a short description for a category code or Category enum.

    Returns None when no description is available.
    """
    if isinstance(cat, str):
        # try to map string to enum
        try:
            cat = Category(cat)
        except Exception:
            return None
    return CATEGORY_DESCRIPTIONS.get(cat)
