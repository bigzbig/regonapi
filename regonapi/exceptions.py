from typing import Optional


class ResponseException(Exception):
    """
    General response exception
    """
    pass


class EmptyResponse(ResponseException):
    """
    Empty response

    May indicate an authorization problem, but because it is not reported literally,
    I have defined an exception that reflects the current problem.
    """
    pass


class UnexpectedResponse(ResponseException):
    """
    Unexpected respnse

    Raised when the response structure is non-standard.
    """
    pass


class RegonAPIError(ResponseException):

    def __init__(self, message: str, code: Optional[int]):
        self.message = str(message)
        try:
            self.code = int(code)
        except (TypeError, ValueError):
            self.code = None

    def __str__(self):
        return self.message
