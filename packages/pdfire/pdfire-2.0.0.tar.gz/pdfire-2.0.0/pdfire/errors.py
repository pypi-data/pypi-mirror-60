from typing import List

class ApiError:
    def __init__(self, message: str):
        self.message = message

class RequestError(Exception):
    def __init__(self, errors: List[ApiError], default: str = 'Request error.'):
        super().__init__(errors[0].message if errors else default)
        self.errors = errors

class InvalidRequestError(RequestError):
    def __init__(self, errors: List[ApiError]):
        super().__init__(errors, 'Invalid request.')

class AuthenticationError(RequestError):
    def __init__(self, errors: List[ApiError]):
        super().__init__(errors, 'Unauthenticated.')

class QuotaExceededError(RequestError):
    def __init__(self, errors: List[ApiError]):
        super().__init__(errors, 'Quota exceeded.')

class ForbiddenActionError(RequestError):
    def __init__(self, errors: List[ApiError]):
        super().__init__(errors, 'Forbidden action.')

class ConversionError(RequestError):
    def __init__(self, errors: List[ApiError]):
        super().__init__(errors, 'Conversion failed.')
