from .auth import Auth
from .client import Filters
from .filter import Filter
from .exceptions import (
    AbuseFilterError,
    FilterError,
    FilterNotFoundError,
    FilterPermissionError,
    FilterSaveError,
    FilterSyntaxError,
    LoginError,
    RuleEditError,
    ValidationError,
)


# keep the package version in one place
__version__ = "0.1.1"

auth = Auth
filters = Filters

__all__ = [
    "auth",
    "filters",
    "Auth",
    "Filters",
    "Filter",
    "AbuseFilterError",
    "LoginError",
    "FilterError",
    "FilterNotFoundError",
    "FilterPermissionError",
    "FilterSaveError",
    "FilterSyntaxError",
    "ValidationError",
    "RuleEditError",
]
