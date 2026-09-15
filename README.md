# mediawiki-abusefilter

[![CI](https://github.com/MadMaxWP/mediawiki-abusefilter/actions/workflows/ci.yml/badge.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/actions/workflows/ci.yml)
[![Documentation status](https://readthedocs.org/projects/mediawiki-abusefilter/badge/?version=latest)](https://mediawiki-abusefilter.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/mediawiki-abusefilter.svg)](https://pypi.org/project/mediawiki-abusefilter/)
[![Python](https://img.shields.io/pypi/pyversions/mediawiki-abusefilter.svg)](https://pypi.org/project/mediawiki-abusefilter/)
[![License](https://img.shields.io/github/license/MadMaxWP/mediawiki-abusefilter.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/blob/main/LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/MadMaxWP/mediawiki-abusefilter.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/releases/latest)

Python client for working with MediaWiki AbuseFilters.

It provides a simple interface for listing, searching, creating, editing, and reviewing filters from Python.

## Installation

```bash
pip install mediawiki-abusefilter
```

## Quick start

```python
import mediawiki_abusefilter as mwaf

filters = mwaf.filters(
    "https://example.org",
    username="Username",
    password="PASSWORD"
)

filter = filters.get(123)

print(filter.description)
print(filter.rules)
```

The authentication object can also be created separately and reused:

```python
auth = mwaf.auth(
    "https://example.org",
    username="Username",
    password="PASSWORD"
)

filters = mwaf.filters("https://example.org", auth=auth)
```

## Listing filters

```python
filters.list()
```

Filters can be narrowed by status and visibility:

```python
filters.list(enabled=True)
filters.list(public=True)
filters.list(private=True)
```

To search by text:

```python
matches = filters.search("spam")
```

Large result sets can be limited with `limit`:

```python
filters.list(limit=100)
filters.search("spam", limit=20)
```

## Creating a filter

```python
filter = filters.create(
    "Low edit count edits",
    "page_namespace == 0 & user_editcount < 10"
)
```

Filters can also be created with notes, actions, and other options:

```python
filter = filters.create(
    "Example filter",
    "page_namespace == 0",
    notes="Created for testing",
    enabled=False,
    public=False,
    actions={
        "warn": "abusefilter-warning",
        "tag": ["review", "test"]
    }
)
```

Use `dry_run=True` to preview a new filter without saving it:

```python
change = filters.create(
    "Example filter",
    "page_namespace == 0",
    dry_run=True
)

print(change)
```

## Editing a filter

Get the filter and change only the values you need:

```python
filter = filters.get(123)

filter.edit(description="Updated description")
filter.edit(enabled=False)
filter.edit(public=False)
```

Values that are not supplied are left unchanged.

Several changes can be made together:

```python
filter.edit(
    description="Updated filter",
    rules="page_namespace == 0 & user_editcount < 20",
    enabled=True,
    public=True,
    actions={"warn": "abusefilter-warning"}
)
```

## Notes

Notes are appended by default:

```python
filter.edit(notes="Changed the edit-count limit")
```

To replace the existing notes:

```python
filter.edit(
    notes="Updated notes",
    notes_mode="replace"
)
```

To clear the notes:

```python
filter.edit(
    notes="",
    notes_mode="replace"
)
```

Notes can also include the current account and date:

```python
filter.edit(
    notes="Changed the rule",
    sign_notes=True
)
```

## Rule changes

Replace the complete rule:

```python
filter.edit(
    rules="page_namespace == 0"
)
```

Or modify part of the existing rule:

```python
filter.edit(replace=("old text", "new text"))
filter.edit(append=" & user_editcount < 20")
filter.edit(prepend="page_namespace == 0 & ")
filter.edit(remove=" & page_namespace == 1")
filter.edit(regex=(r"user_editcount\s*<\s*10", "user_editcount < 20"))
```

Replacement operations are strict by default. Use `strict=False` when a missing match should not raise an error:

```python
filter.edit(
    replace=("old text", "new text"),
    strict=False
)
```

## Actions

Actions can be configured when creating or editing a filter:

```python
filter.edit(
    actions={
        "warn": "abusefilter-warning",
        "disallow": "abusefilter-disallowed",
        "blockautopromote": True,
        "block": {
            "talk": True,
            "anonymous": "1 day",
            "user": "1 day"
        },
        "tag": ["review", "bot"],
        "throttle": {
            "count": 5,
            "period": 120,
            "groups": "user"
        }
    }
)
```

Set an action to `False` to remove it:

```python
filter.edit(
    actions={
        "warn": False,
        "tag": False
    }
)
```

## History

Filter history is available through `history()`:

```python
for entry in filter.history(limit=20):
    print(
        entry["id"],
        entry["user"],
        entry["description"]
    )
```

## Previewing changes

Use `dry_run=True` to inspect a change before applying it:

```python
change = filter.edit(
    description="Preview only",
    rules="page_namespace == 0",
    dry_run=True
)

print(change)
```

Changes made through `edit()` and `create()` are verified by default.

Set `verify=False` when you specifically need to skip that verification:

```python
filter.edit(
    rules="page_namespace == 0",
    verify=False
)
```

## Account information

The current account can be inspected with `whoami()`:

```python
info = filters.whoami()

print(info["name"])
print(info["groups"])
```

## Delete

```python
filter.delete()
```

## Requirements

Python 3.9 or newer.

## Limitations

BotPassword login does not work with this package.

The package uses the MediaWiki web interface for filter creation and editing, which requires a normal user login.

## Documentation

Full API documentation and usage examples are available on [Read the Docs](https://mediawiki-abusefilter.readthedocs.io/en/latest/).

## License

MIT
