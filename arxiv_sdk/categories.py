"""arXiv category codes.

This module provides a simple Enum of commonly-used arXiv category codes.
Use like:

    from ArxivSDK.categories import Category
    qb.category(Category.CS_LG.value)

The Enum values are the standard arXiv category codes (e.g. ``cs.LG``).
This file is intentionally a compact, curated list — extend as needed.
"""
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Category(str, Enum):
    # Computer Science
    CS_AI = "cs.AI"
    CS_LG = "cs.LG"
    CS_CV = "cs.CV"
    CS_CL = "cs.CL"
    CS_NE = "cs.NE"
    CS_CR = "cs.CR"
    CS_AR = "cs.AR"
    CS_CC = "cs.CC"
    CS_CE = "cs.CE"
    CS_CG = "cs.CG"
    CS_CY = "cs.CY"
    CS_DB = "cs.DB"
    CS_DC = "cs.DC"
    CS_DL = "cs.DL"
    CS_DM = "cs.DM"
    CS_DS = "cs.DS"
    CS_ET = "cs.ET"
    CS_FL = "cs.FL"
    CS_GL = "cs.GL"
    CS_GT = "cs.GT"
    CS_HC = "cs.HC"
    CS_IR = "cs.IR"
    CS_IT = "cs.IT"
    CS_LO = "cs.LO"
    CS_MA = "cs.MA"
    CS_MM = "cs.MM"
    CS_MS = "cs.MS"
    CS_NA = "cs.NA"
    CS_NI = "cs.NI"
    CS_OH = "cs.OH"
    CS_OS = "cs.OS"
    CS_PF = "cs.PF"
    CS_PL = "cs.PL"
    CS_RO = "cs.RO"
    CS_SC = "cs.SC"
    CS_SD = "cs.SD"
    CS_SE = "cs.SE"
    CS_SI = "cs.SI"
    CS_SY = "cs.SY"

    # Mathematics
    MATH_AG = "math.AG"
    MATH_AP = "math.AP"
    MATH_AT = "math.AT"
    MATH_CA = "math.CA"
    MATH_CO = "math.CO"
    MATH_CT = "math.CT"
    MATH_CV = "math.CV"
    MATH_DG = "math.DG"
    MATH_DS = "math.DS"
    MATH_FA = "math.FA"
    MATH_GM = "math.GM"
    MATH_GN = "math.GN"
    MATH_GR = "math.GR"
    MATH_GT = "math.GT"
    MATH_HO = "math.HO"
    MATH_IT = "math.IT"
    MATH_KT = "math.KT"
    MATH_LO = "math.LO"
    MATH_MG = "math.MG"
    MATH_MP = "math.MP"
    MATH_NA = "math.NA"
    MATH_NT = "math.NT"
    MATH_OA = "math.OA"
    MATH_OC = "math.OC"
    MATH_PR = "math.PR"
    MATH_QA = "math.QA"
    MATH_RA = "math.RA"
    MATH_RT = "math.RT"
    MATH_SG = "math.SG"
    MATH_SP = "math.SP"
    MATH_ST = "math.ST"

    # Statistics
    STAT_AP = "stat.AP"
    STAT_CO = "stat.CO"
    STAT_ME = "stat.ME"
    STAT_ML = "stat.ML"
    STAT_OT = "stat.OT"
    STAT_TH = "stat.TH"

    # Physics
    ASTRO_PH = "astro-ph"  # Alias for astro-ph.*
    COND_MAT = "cond-mat"  # Alias
    GR_QC = "gr-qc"
    HEP_EX = "hep-ex"
    HEP_LAT = "hep-lat"
    HEP_PH = "hep-ph"
    HEP_TH = "hep-th"
    MATH_PH = "math-ph"
    NUCL_EX = "nucl-ex"
    NUCL_TH = "nucl-th"
    PHYSICS = "physics"  # Alias
    QUANT_PH = "quant-ph"

    # Quantitative Biology
    Q_BIO_BM = "q-bio.BM"
    Q_BIO_CB = "q-bio.CB"
    Q_BIO_GN = "q-bio.GN"
    Q_BIO_MN = "q-bio.MN"
    Q_BIO_NC = "q-bio.NC"
    Q_BIO_OT = "q-bio.OT"
    Q_BIO_PE = "q-bio.PE"
    Q_BIO_QM = "q-bio.QM"
    Q_BIO_SC = "q-bio.SC"
    Q_BIO_TO = "q-bio.TO"
    Q_BIO = "q-bio"  # Alias

    # Quantitative Finance
    Q_FIN_CP = "q-fin.CP"
    Q_FIN_EC = "q-fin.EC"
    Q_FIN_GN = "q-fin.GN"
    Q_FIN_MF = "q-fin.MF"
    Q_FIN_PM = "q-fin.PM"
    Q_FIN_PR = "q-fin.PR"
    Q_FIN_RM = "q-fin.RM"
    Q_FIN_ST = "q-fin.ST"
    Q_FIN_TR = "q-fin.TR"
    Q_FIN = "q-fin"  # Alias

    # Electrical Engineering and Systems Science
    EESS_AS = "eess.AS"
    EESS_IV = "eess.IV"
    EESS_SP = "eess.SP"
    EESS_SY = "eess.SY"
    EESS = "eess"  # Alias

    # Economics
    ECON_EM = "econ.EM"
    ECON_GN = "econ.GN"
    ECON_TH = "econ.TH"


__all__ = ["Category", "load_full_taxonomy", "search_categories", "get_category_description"]

# Human-readable descriptions for categories. Keep in sync with `Category`.
CATEGORY_DESCRIPTIONS: dict[Category, str] = {
    # Computer Science
    Category.CS_AI: "Computer Science - Artificial Intelligence",
    Category.CS_AR: "Computer Science - Hardware Architecture",
    Category.CS_CC: "Computer Science - Computational Complexity",
    Category.CS_CE: "Computer Science - Computational Engineering, Finance, and Science",
    Category.CS_CG: "Computer Science - Computational Geometry",
    Category.CS_CL: "Computer Science - Computation and Language",
    Category.CS_CR: "Computer Science - Cryptography and Security",
    Category.CS_CV: "Computer Science - Computer Vision and Pattern Recognition",
    Category.CS_CY: "Computer Science - Computers and Society",
    Category.CS_DB: "Computer Science - Databases",
    Category.CS_DC: "Computer Science - Distributed, Parallel, and Cluster Computing",
    Category.CS_DL: "Computer Science - Digital Libraries",
    Category.CS_DM: "Computer Science - Discrete Mathematics",
    Category.CS_DS: "Computer Science - Data Structures and Algorithms",
    Category.CS_ET: "Computer Science - Emerging Technologies",
    Category.CS_FL: "Computer Science - Formal Languages and Automata Theory",
    Category.CS_GL: "Computer Science - General Literature",
    Category.CS_GT: "Computer Science - Computer Science and Game Theory",
    Category.CS_HC: "Computer Science - Human-Computer Interaction",
    Category.CS_IR: "Computer Science - Information Retrieval",
    Category.CS_IT: "Computer Science - Information Theory",
    Category.CS_LG: "Computer Science - Machine Learning",
    Category.CS_LO: "Computer Science - Logic in Computer Science",
    Category.CS_MA: "Computer Science - Multiagent Systems",
    Category.CS_MM: "Computer Science - Multimedia",
    Category.CS_MS: "Computer Science - Mathematical Software",
    Category.CS_NA: "Computer Science - Numerical Analysis",
    Category.CS_NE: "Computer Science - Neural and Evolutionary Computing",
    Category.CS_NI: "Computer Science - Networking and Internet Architecture",
    Category.CS_OH: "Computer Science - Other Computer Science",
    Category.CS_OS: "Computer Science - Operating Systems",
    Category.CS_PF: "Computer Science - Performance",
    Category.CS_PL: "Computer Science - Programming Languages",
    Category.CS_RO: "Computer Science - Robotics",
    Category.CS_SC: "Computer Science - Symbolic Computation",
    Category.CS_SD: "Computer Science - Sound",
    Category.CS_SE: "Computer Science - Software Engineering",
    Category.CS_SI: "Computer Science - Social and Information Networks",
    Category.CS_SY: "Computer Science - Systems and Control",

    # Mathematics
    Category.MATH_AG: "Mathematics - Algebraic Geometry",
    Category.MATH_AP: "Mathematics - Analysis of PDEs",
    Category.MATH_AT: "Mathematics - Algebraic Topology",
    Category.MATH_CA: "Mathematics - Classical Analysis and ODEs",
    Category.MATH_CO: "Mathematics - Combinatorics",
    Category.MATH_CT: "Mathematics - Category Theory",
    Category.MATH_CV: "Mathematics - Complex Variables",
    Category.MATH_DG: "Mathematics - Differential Geometry",
    Category.MATH_DS: "Mathematics - Dynamical Systems",
    Category.MATH_FA: "Mathematics - Functional Analysis",
    Category.MATH_GM: "Mathematics - General Mathematics",
    Category.MATH_GN: "Mathematics - General Topology",
    Category.MATH_GR: "Mathematics - Group Theory",
    Category.MATH_GT: "Mathematics - Geometric Topology",
    Category.MATH_HO: "Mathematics - History and Overview",
    Category.MATH_IT: "Mathematics - Information Theory",
    Category.MATH_KT: "Mathematics - K-Theory and Homology",
    Category.MATH_LO: "Mathematics - Logic",
    Category.MATH_MG: "Mathematics - Metric Geometry",
    Category.MATH_MP: "Mathematics - Mathematical Physics",
    Category.MATH_NA: "Mathematics - Numerical Analysis",
    Category.MATH_NT: "Mathematics - Number Theory",
    Category.MATH_OA: "Mathematics - Operator Algebras",
    Category.MATH_OC: "Mathematics - Optimization and Control",
    Category.MATH_PR: "Mathematics - Probability",
    Category.MATH_QA: "Mathematics - Quantum Algebra",
    Category.MATH_RA: "Mathematics - Rings and Algebras",
    Category.MATH_RT: "Mathematics - Representation Theory",
    Category.MATH_SG: "Mathematics - Symplectic Geometry",
    Category.MATH_SP: "Mathematics - Spectral Theory",
    Category.MATH_ST: "Mathematics - Statistics Theory",

    # Statistics
    Category.STAT_AP: "Statistics - Applications",
    Category.STAT_CO: "Statistics - Computation",
    Category.STAT_ME: "Statistics - Methodology",
    Category.STAT_ML: "Statistics - Machine Learning",
    Category.STAT_OT: "Statistics - Other Statistics",
    Category.STAT_TH: "Statistics - Statistics Theory",

    # Physics
    Category.ASTRO_PH: "Astrophysics",
    Category.COND_MAT: "Condensed Matter",
    Category.GR_QC: "General Relativity and Quantum Cosmology",
    Category.HEP_EX: "High Energy Physics - Experiment",
    Category.HEP_LAT: "High Energy Physics - Lattice",
    Category.HEP_PH: "High Energy Physics - Phenomenology",
    Category.HEP_TH: "High Energy Physics - Theory",
    Category.MATH_PH: "Mathematical Physics",
    Category.NUCL_EX: "Nuclear Experiment",
    Category.NUCL_TH: "Nuclear Theory",
    Category.PHYSICS: "Physics",
    Category.QUANT_PH: "Quantum Physics",

    # Quantitative Biology
    Category.Q_BIO: "Quantitative Biology",
    Category.Q_BIO_BM: "Quantitative Biology - Biomolecules",
    Category.Q_BIO_CB: "Quantitative Biology - Cell Behavior",
    Category.Q_BIO_GN: "Quantitative Biology - Genomics",
    Category.Q_BIO_MN: "Quantitative Biology - Molecular Networks",
    Category.Q_BIO_NC: "Quantitative Biology - Neurons and Cognition",
    Category.Q_BIO_OT: "Quantitative Biology - Other Quantitative Biology",
    Category.Q_BIO_PE: "Quantitative Biology - Populations and Evolution",
    Category.Q_BIO_QM: "Quantitative Biology - Quantitative Methods",
    Category.Q_BIO_SC: "Quantitative Biology - Subcellular Processes",
    Category.Q_BIO_TO: "Quantitative Biology - Tissues and Organs",

    # Quantitative Finance
    Category.Q_FIN: "Quantitative Finance",
    Category.Q_FIN_CP: "Quantitative Finance - Computational Finance",
    Category.Q_FIN_EC: "Quantitative Finance - Economics",
    Category.Q_FIN_GN: "Quantitative Finance - General Finance",
    Category.Q_FIN_MF: "Quantitative Finance - Mathematical Finance",
    Category.Q_FIN_PM: "Quantitative Finance - Portfolio Management",
    Category.Q_FIN_PR: "Quantitative Finance - Pricing of Securities",
    Category.Q_FIN_RM: "Quantitative Finance - Risk Management",
    Category.Q_FIN_ST: "Quantitative Finance - Statistical Finance",
    Category.Q_FIN_TR: "Quantitative Finance - Trading and Market Microstructure",

    # Electrical Engineering and Systems Science
    Category.EESS: "Electrical Engineering and Systems Science",
    Category.EESS_AS: "Electrical Engineering and Systems Science - Audio and Speech Processing",
    Category.EESS_IV: "Electrical Engineering and Systems Science - Image and Video Processing",
    Category.EESS_SP: "Electrical Engineering and Systems Science - Signal Processing",
    Category.EESS_SY: "Electrical Engineering and Systems Science - Systems and Control",

    # Economics
    Category.ECON_EM: "Economics - Econometrics",
    Category.ECON_GN: "Economics - General Economics",
    Category.ECON_TH: "Economics - Theoretical Economics",
}


def load_full_taxonomy() -> dict[str, str]:
    """Load full arXiv category taxonomy from the official page.

    Returns a dict of category code to description.
    Falls back to built-in descriptions if fetch fails.
    """
    try:
        import requests
        resp = requests.get("https://arxiv.org/category_taxonomy", timeout=10)
        resp.raise_for_status()
        # Parse HTML for categories (simplified; in practice, use BeautifulSoup)
        # For now, return built-in
        logger.warning("Full taxonomy loading not implemented; using built-in")
        return {cat.value: desc for cat, desc in CATEGORY_DESCRIPTIONS.items()}
    except Exception as e:
        logger.warning("Failed to load full taxonomy: %s", e)
        return {cat.value: desc for cat, desc in CATEGORY_DESCRIPTIONS.items()}


def search_categories(query: str) -> list[tuple[str, str]]:
    """Search categories by keyword in code or description.

    Returns list of (code, description) tuples.
    """
    query_lower = query.lower()
    results = []
    for cat, desc in CATEGORY_DESCRIPTIONS.items():
        if query_lower in cat.value.lower() or query_lower in desc.lower():
            results.append((cat.value, desc))
    return results


def get_category_description(cat: Category | str) -> str | None:
    """Return a short description for a category code or Category enum.

    Returns None when no description is available.
    """
    if isinstance(cat, str):
        # try to map string to enum
        try:
            cat = Category(cat)
        except ValueError as e:
            logger.warning("Invalid category: %s", e)
            return None
    return CATEGORY_DESCRIPTIONS.get(cat)
