from academic_sdk.errors import AcademicSDKError, AcademicAPIError, AcademicNetworkError, AcademicParseError, AcademicDownloadError


class ArxivSDKError(AcademicSDKError):
    """Base class for SDK errors."""
    pass


class ArxivAPIError(AcademicAPIError):
    pass


class ArxivNetworkError(AcademicNetworkError):
    pass


class ArxivParseError(AcademicParseError):
    pass


class ArxivDownloadError(AcademicDownloadError):
    pass
