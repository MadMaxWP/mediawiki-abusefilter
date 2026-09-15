# mediawiki-abusefilter

[![CI](https://github.com/MadMaxWP/mediawiki-abusefilter/actions/workflows/ci.yml/badge.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/actions/workflows/ci.yml)
[![Documentation status](https://readthedocs.org/projects/mediawiki-abusefilter/badge/?version=latest)](https://mediawiki-abusefilter.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/mediawiki-abusefilter.svg)](https://pypi.org/project/mediawiki-abusefilter/)
[![Python](https://img.shields.io/pypi/pyversions/mediawiki-abusefilter.svg)](https://pypi.org/project/mediawiki-abusefilter/)
[![License](https://img.shields.io/github/license/MadMaxWP/mediawiki-abusefilter.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/blob/main/LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/MadMaxWP/mediawiki-abusefilter.svg)](https://github.com/MadMaxWP/mediawiki-abusefilter/releases/latest)

mediawiki-abusefilter is a small Python client for creating and modifying MediaWiki AbuseFilters on MediaWiki sites. MediaWiki does not provide an API for creating or modifying AbuseFilters, so this package provides an unofficial interface for managing them from Python.

## Install

```bash
pip install mediawiki-abusefilter
```

## Quick start

```python
import mediawiki_abusefilter as mwaf

filters = mwaf.filters(
    "https://example.org",
    username="MyBot@mybotpassword",
    password="BOT_PASSWORD"
)

filter = filters.get(123)
print(filter.description)
```

A separate authentication object can be reused when needed:

```python
auth = mwaf.auth(
    "https://example.org",
    username="MyBot@mybotpassword",
    password="BOT_PASSWORD"
)

filters = mwaf.filters("https://example.org", auth=auth)
```

## Finding filters

```python
filters.list()
filters.list(enabled=True)
filters.list(public=True)
filters.list(private=True)

matches = filters.search("spam")
```

`list()` can page through large collections automatically. It also accepts `start`, `end`, and `direction` when you need to work around a particular range of filter IDs.

```python
filters.list(limit=1000)
filters.list(start=100, end=200, direction="newer")
```

## Creating a filter

New filters are public and enabled by default.

```python
filter = filters.create(
    "Low edit count edits",
    "page_namespace == 0 & user_editcount < 10"
)
```

You can set the main options when creating it:

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
    },
    verify=True
)
```

Use `dry_run=True` to prepare the change without creating the filter:

```python
change = filters.create(
    "Example filter",
    "page_namespace == 0",
    dry_run=True
)
print(change)
```

## Editing a filter

Get the filter and change only what you need:

```python
filter = filters.get(123)
filter.edit(description="Updated description")
filter.edit(enabled=False)
filter.edit(public=False)
```

Leaving an option out keeps its current value. For example, an edit that only changes the description does not change the filter's visibility, status, rules, notes, or actions.

You can update several things together:

```python
filter.edit(
    description="Updated filter",
    rules="page_namespace == 0 & user_editcount < 20",
    enabled=True,
    public=True,
    actions={"warn": "abusefilter-warning"},
    verify=True
)
```

## Notes

Supplied notes are appended to the existing notes by default. Leaving `notes` out does nothing to the current notes.

```python
filter.edit(notes="Changed the edit-count limit")
```

To replace the notes completely, use `notes_mode="replace"`:

```python
filter.edit(notes="Clean replacement", notes_mode="replace")
```

The same form can clear the notes:

```python
filter.edit(notes="", notes_mode="replace")
```

With `sign_notes=True`, a supplied note gets the current account and date added to it:

```python
filter.edit(
    notes="Changed the rule",
    sign_notes=True
)
```

This produces a note in the form `Changed the rule - Max 14 September 2026`.

## Rule changes

You can replace the complete expression:

```python
filter.edit(rules="page_namespace == 0")
```

Or change part of the current expression:

```python
filter.edit(replace=("old text", "new text"))
filter.edit(append=" & user_editcount < 20")
filter.edit(prepend="page_namespace == 0 & ")
filter.edit(remove=" & page_namespace == 1")
filter.edit(regex=(r"user_editcount\s*<\s*10", "user_editcount < 20"))
```

Replacement operations are strict by default. Set `strict=False` when a missing match should be ignored.

The resulting expression is still checked by MediaWiki when it is saved, so a rule edit that leaves invalid syntax will be rejected.

## Actions

Multiple actions can be configured at once:

```python
filter.edit(actions={
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
})
```

Set an action to `False` to turn it off.

## History

```python
for entry in filter.history(limit=20):
    print(entry["id"], entry["user"], entry["description"])
```

History entries include the revision ID, time, user, description, flags, actions, and links to the history item and diff.

## Verification and dry runs

Writes are verified by default. After saving, the client reloads the filter and checks the requested changes against the actual saved state. Set `verify=False` when you explicitly want to skip that correctness check.

```python
filter.edit(
    rules="page_namespace == 0",
    verify=True
)
```

`dry_run=True` returns the proposed edit without saving it:

```python
change = filter.edit(
    description="Preview only",
    dry_run=True
)
print(change)
```

## Account information and debugging

```python
print(filters.whoami()["name"])
```

For request and authentication diagnostics, enable debug output:

```python
filters = mwaf.filters(
    "https://example.org",
    username="MyBot@mybotpassword",
    password="BOT_PASSWORD",
    debug=True
)
```

A descriptive User-Agent is sent automatically. You can provide your own with `user_agent=`.

## Delete

```python
filter.delete()
```

## License

MIT
