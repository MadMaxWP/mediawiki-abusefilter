Filter
======

A ``Filter`` object represents one MediaWiki AbuseFilter and provides its current settings together with methods for changing and reviewing it.

Filter
------

.. autoclass:: mediawiki_abusefilter.filter.Filter
   :members: description, rules, notes, enabled, public, actions, hits, last_editor, last_edit_time, protected, suppressed, history, refresh, edit, save, delete
   :undoc-members:
   :show-inheritance:

Properties
----------

``id``
   The numeric filter ID.

``description``
   The filter description.

``rules``
   The current AbuseFilter expression.

``notes``
   The filter notes.

``enabled``
   ``True`` when the filter is enabled.

``public``
   ``True`` when the filter is public and ``False`` when it is private.

``actions``
   A dictionary containing the currently configured actions.

``hits``
   The recorded hit count when available.

``last_editor``
   The most recent editor when available.

``last_edit_time``
   The most recent edit time when available.

``protected``
   ``True`` when the filter is protected.

``suppressed``
   ``True`` when the filter is suppressed.

Editing filters
---------------

Use ``edit()`` to change one or more settings at the same time. Values that are not supplied are left unchanged.

.. code-block:: python

   filter.edit(description="Updated description")
   filter.edit(enabled=False)
   filter.edit(public=False)

Several changes can be combined:

.. code-block:: python

   filter.edit(
       description="Updated filter",
       rules="page_namespace == 0 & user_editcount < 20",
       enabled=True,
       public=True,
       actions={"warn": "abusefilter-warning"}
   )

The main ``edit()`` arguments are:

``rules``
   Replace the complete rule expression.

``description``
   Replace the filter description.

``notes``
   Add to or replace the filter notes according to ``notes_mode``.

``enabled``
   Enable or disable the filter.

``public``
   Change the filter between public and private.

``actions``
   Add, change, or remove supported actions.

``replace``
   Replace text in the existing rule expression.

``append``
   Add text to the end of the existing rule expression.

``prepend``
   Add text to the beginning of the existing rule expression.

``remove``
   Remove text from the existing rule expression.

``regex``
   Replace a regular-expression match in the existing rule expression.

``strict``
   Controls whether a rule replacement operation must find its target. The default is ``True``.

``verify``
   Verify the requested values against the saved filter. The default is ``True``.

``dry_run``
   Return the proposed change without saving it.

``sign_notes``
   Add the current account and date to a supplied note.

``notes_mode``
   ``"append"`` or ``"replace"``. The default is ``"append"``.

Rules
-----

Replace the complete expression:

.. code-block:: python

   filter.edit(rules="page_namespace == 0")

Make targeted changes with the rule operations:

.. code-block:: python

   filter.edit(replace=("user_editcount < 10", "user_editcount < 20"))
   filter.edit(append=" & page_namespace == 0")
   filter.edit(prepend="page_namespace == 0 & ")
   filter.edit(remove=" & page_namespace == 1")
   filter.edit(regex=(r"user_editcount\s*<\s*\d+", "user_editcount < 100"))

Replacement operations are strict by default. Set ``strict=False`` when a missing match should be ignored.

.. code-block:: python

   filter.edit(
       replace=("old text", "new text"),
       strict=False
   )

Notes
-----

Notes are appended by default:

.. code-block:: python

   filter.edit(notes="Changed the rule")

Replace the current notes:

.. code-block:: python

   filter.edit(notes="Replacement", notes_mode="replace")

Clear the notes:

.. code-block:: python

   filter.edit(notes="", notes_mode="replace")

Add the current account and date to a supplied note:

.. code-block:: python

   filter.edit(notes="Changed the rule", sign_notes=True)

Actions
-------

The following actions are supported.

warn
~~~~

Enable the warning action with the default warning message:

.. code-block:: python

   filter.edit(actions={"warn": True})

Select a standard warning message:

.. code-block:: python

   filter.edit(actions={"warn": "abusefilter-warning"})

Use a custom warning message by supplying its text:

.. code-block:: python

   filter.edit(actions={"warn": "My warning message"})

Set the action to ``False`` to remove it.

.. code-block:: python

   filter.edit(actions={"warn": False})

disallow
~~~~~~~~

Enable the disallow action with the default message:

.. code-block:: python

   filter.edit(actions={"disallow": True})

Select the standard message or provide custom text in the same way as ``warn``.

.. code-block:: python

   filter.edit(actions={"disallow": "abusefilter-disallowed"})
   filter.edit(actions={"disallow": "My message"})
   filter.edit(actions={"disallow": False})

blockautopromote
~~~~~~~~~~~~~~~~

Enable or remove the action with a boolean:

.. code-block:: python

   filter.edit(actions={"blockautopromote": True})
   filter.edit(actions={"blockautopromote": False})

block
~~~~~

Configure the block action with a dictionary. ``talk`` controls whether the user's talk page is also blocked. ``anonymous`` and ``user`` set the block duration for anonymous and registered users.

.. code-block:: python

   filter.edit(actions={
       "block": {
           "talk": True,
           "anonymous": "1 day",
           "user": "1 day"
       }
   })

The action can be removed with ``False``:

.. code-block:: python

   filter.edit(actions={"block": False})

tag
~~~

Supply a list of tags to add when the filter matches:

.. code-block:: python

   filter.edit(actions={
       "tag": ["review", "bot"]
   })

Remove the action with ``False``:

.. code-block:: python

   filter.edit(actions={"tag": False})

throttle
~~~~~~~~

Configure a rate limit with ``count``, ``period``, and ``groups``:

.. code-block:: python

   filter.edit(actions={
       "throttle": {
           "count": 5,
           "period": 120,
           "groups": "user"
       }
   })

Remove the action with ``False``:

.. code-block:: python

   filter.edit(actions={"throttle": False})

Several actions can be changed together:

.. code-block:: python

   filter.edit(actions={
       "warn": "abusefilter-warning",
       "disallow": "abusefilter-disallowed",
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

Verification and previews
-------------------------

Writes are verified by default. Verification checks the requested changes against the saved filter after the operation completes.

Set ``verify=False`` when you explicitly want to skip that correctness check:

.. code-block:: python

   filter.edit(
       rules="page_namespace == 0",
       verify=False
   )

Use ``dry_run=True`` to preview an edit without saving it:

.. code-block:: python

   preview = filter.edit(
       rules="page_namespace == 0",
       dry_run=True
   )

History
-------

Return the filter's edit history with ``history()``:

.. code-block:: python

   for entry in filter.history(limit=20):
       print(entry["id"], entry["user"], entry["description"])

Each history entry contains the revision ID, timestamp, user, description, flags, actions, and links to the history item and diff when available.

Refreshing
----------

Reload the current filter from the wiki:

.. code-block:: python

   filter.refresh()

``refresh()`` returns the same ``Filter`` object.

Saving
------

``save()`` is an alias for ``edit()`` and accepts the same keyword arguments:

.. code-block:: python

   filter.save(description="Updated description")

Deleting
--------

Delete the filter when the current account has permission to do so:

.. code-block:: python

   filter.delete()
