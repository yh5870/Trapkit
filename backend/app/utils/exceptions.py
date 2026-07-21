"""커스텀 예외."""


class TrapkitException(Exception):
    """Trapkit 기본 예외."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(TrapkitException):
    """리소스 없음 예외."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class UnauthorizedException(TrapkitException):
    """인증 실패 예외."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)


class ForbiddenException(TrapkitException):
    """권한 없음 예외."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)


class ValidationException(TrapkitException):
    """검증 실패 예외."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=422)


class RateLimitException(TrapkitException):
    """레이트 리밋 초과 예외."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class AIServiceException(TrapkitException):
    """AI 서비스 예외."""

    def __init__(self, message: str = "AI service error") -> None:
        super().__init__(message, status_code=500)