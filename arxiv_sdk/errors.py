class ArxivSDKError(Exception):
    """Base class for SDK errors."""
    pass


class ArxivAPIError(ArxivSDKError):
    def __init__(self, status_code: int, body: str = None):
        super().__init__(f"API error: {status_code}")
        self.status_code = status_code
        self.body = body


class ArxivNetworkError(ArxivSDKError):
    def __init__(self, original_exception: Exception):
        super().__init__(f"Network error: {original_exception}")
        self.original_exception = original_exception


class ArxivParseError(ArxivSDKError):
    pass


class ArxivDownloadError(ArxivSDKError):
    pass
