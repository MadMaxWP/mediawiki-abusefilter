class AbuseFilterError(Exception):
    """Base exception for mediawiki-abusefilter."""


class LoginError(AbuseFilterError):
    """Raised when MediaWiki authentication fails."""


class FilterError(AbuseFilterError):
    """Raised for general filter errors."""


class FilterNotFoundError(FilterError):
    """Raised when a filter cannot be found."""


class FilterSaveError(FilterError):
    """Raised when a filter cannot be saved."""


class FilterSyntaxError(FilterSaveError):
    """Raised when MediaWiki rejects filter syntax."""


class FilterPermissionError(FilterSaveError):
    """Raised when an operation is rejected for permission reasons."""


class ValidationError(FilterSaveError):
    """Raised when MediaWiki rejects filter data."""


class RuleEditError(FilterError):
    """Raised when a rule transformation cannot be applied."""
