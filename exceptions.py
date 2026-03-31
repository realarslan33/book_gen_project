class ProjectError(Exception):
    """Base project exception."""


class ValidationError(ProjectError):
    """Raised when required input is missing or invalid."""


class DatabaseError(ProjectError):
    """Raised when DB action fails."""


class AIServiceError(ProjectError):
    """Raised when AI call fails."""
