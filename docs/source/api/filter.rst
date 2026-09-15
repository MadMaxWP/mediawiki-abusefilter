Filter
======

A ``Filter`` represents one AbuseFilter.

Properties
----------

``id``
   Numeric filter ID.

``description``
   Filter description.

``rules``
   Current AbuseFilter expression.

``notes``
   Current filter notes.

``enabled``
   Whether the filter is enabled.

``public``
   Whether the filter is public.

``actions``
   Configured actions.

``hits``
   Recorded hit count when available.

``last_editor``
   Most recent editor when available.

``last_edit_time``
   Most recent edit time when available.

``protected``
   Whether the filter is protected.

``suppressed``
   Whether the filter is suppressed.

Editing
-------

``edit(...)`` updates one or more settings and returns the same ``Filter`` object.

```python
filter.edit(description="Updated description")
filter.edit(enabled=False)
filter.edit(public=False)
```

Omitted settings are left unchanged. ``notes`` is appended by default; use ``notes_mode="replace"`` to replace or clear it.

Rule changes can be made with ``rules``, ``replace``, ``append``, ``prepend``, ``remove``, or ``regex``.

.. code-block:: python

   filter.edit(rules="page_namespace == 0")
   filter.edit(replace=("old", "new"))
   filter.edit(append=" & page_namespace == 0")
   filter.edit(prepend="page_namespace == 0 & ")
   filter.edit(remove=" & page_namespace == 1")
   filter.edit(regex=(r"foo\s+bar", "foo"))

``strict`` controls whether missing matches raise a ``RuleEditError``.

``verify=True`` reloads the filter and checks requested changes after saving, including actions when ``actions`` is supplied. Write verification is enabled by default; set ``verify=False`` to skip the correctness check.

``dry_run=True`` returns the proposed change without saving it.

Actions
-------

Action configuration is supplied through ``actions``. The available actions depend on the target wiki's AbuseFilter configuration.

.. code-block:: python

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

Set an action to ``False`` to disable it.

History
-------

``history(limit=50)`` returns the filter's edit history.

Each entry contains ``id``, ``timestamp``, ``user``, ``description``, ``flags``, ``actions``, ``item_url``, and ``diff_url``.

.. code-block:: python

   for entry in filter.history(limit=20):
       print(entry["id"], entry["user"], entry["description"])

Other methods
-------------

``refresh()``
   Reload the filter and return the same object.

``save(**changes)``
   Alias for ``edit(**changes)``.

``delete()``
   Delete the filter when the account has the required permission.

API
---

.. autoclass:: mediawiki_abusefilter.Filter
   :members: edit, save, refresh, history, delete
   :no-index:
