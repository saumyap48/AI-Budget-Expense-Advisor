class DomainException(Exception):
    """Base exception for application domain errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(DomainException):

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND")


class ValidationException(DomainException):

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, code="VALIDATION_ERROR")


class AuthenticationException(DomainException):

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="UNAUTHORIZED")


class AIException(DomainException):

    def __init__(self, message: str = "AI service unavailable"):
        super().__init__(message, code="AI_SERVICE_ERROR")


class VectorStoreException(DomainException):

    def __init__(self, message: str = "Vector database error"):
        super().__init__(message, code="VECTOR_STORE_ERROR")
