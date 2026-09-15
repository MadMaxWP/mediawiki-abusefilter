import re

from .exceptions import RuleEditError


def _operations(value):
    if value is None:
        return []
    if isinstance(value, (tuple, list)) and value and isinstance(value[0], (tuple, list)):
        return value
    return [value]


def apply_rules(rules, replace=None, append=None, prepend=None, remove=None, regex=None, strict=True):
    # apply requested changes in a predictable order
    result = rules
    for operation in _operations(replace):
        if not isinstance(operation, (tuple, list)) or len(operation) not in (2, 3):
            raise RuleEditError("replace must be (old, new), (old, new, count), or a list of those")
        old, new = operation[:2]
        count = operation[2] if len(operation) == 3 else -1
        if old == "":
            raise RuleEditError("replace text cannot be empty")
        if old not in result and strict:
            raise RuleEditError(f"text not found: {old!r}")
        result = result.replace(old, new, count)
    for operation in _operations(regex):
        if not isinstance(operation, (tuple, list)) or len(operation) not in (2, 3):
            raise RuleEditError("regex must be (pattern, replacement), (pattern, replacement, count), or a list of those")
        pattern, replacement = operation[:2]
        count = operation[2] if len(operation) == 3 else 0
        try:
            result, matches = re.subn(pattern, replacement, result, count=count)
        except re.error as exc:
            raise RuleEditError(f"invalid regular expression: {exc}") from exc
        if matches == 0 and strict:
            raise RuleEditError(f"pattern not found: {pattern!r}")
    for value in (remove if isinstance(remove, (list, tuple, set)) else [remove]):
        if value is None:
            continue
        if value not in result and strict:
            raise RuleEditError(f"text not found: {value!r}")
        result = result.replace(value, "")
    if prepend is not None:
        result = prepend + result
    if append is not None:
        result += append
    return result
