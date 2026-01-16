"""Shared error classes for academic SDKs."""


class AcademicSDKError(Exception):
    """Base exception for academic SDK errors."""
    pass


class AcademicAPIError(AcademicSDKError):
    """Raised when the API returns an error."""
    def __init__(self, status: int, body: str = ""):
        self.status = status
        self.body = body
        super().__init__(f"API error {status}: {body}")


class AcademicNetworkError(AcademicSDKError):
    """Raised for network-related errors."""
    pass


class AcademicParseError(AcademicSDKError):
    """Raised when parsing API responses fails."""
    pass


class AcademicDownloadError(AcademicSDKError):
    """Raised for download-related errors."""
    pass