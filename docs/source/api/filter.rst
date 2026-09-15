Filter
======

.. autoclass:: mediawiki_abusefilter.filter.Filter
   :members:
   :undoc-members:
   :show-inheritance:

Actions
-------

The following actions are supported by ``edit()`` and ``create()``.

warn
~~~~

Enable or configure a warning:

.. code-block:: python

   filter.edit(actions={"warn": True})
   filter.edit(actions={"warn": "abusefilter-warning"})

Set ``False`` to remove the action:

.. code-block:: python

   filter.edit(actions={"warn": False})

disallow
~~~~~~~~

Enable or configure the disallow action:

.. code-block:: python

   filter.edit(actions={"disallow": True})
   filter.edit(actions={"disallow": "abusefilter-disallowed"})

Set ``False`` to remove it.

blockautopromote
~~~~~~~~~~~~~~~~

Enable or disable the action:

.. code-block:: python

   filter.edit(actions={"blockautopromote": True})
   filter.edit(actions={"blockautopromote": False})

block
~~~~~

Configure blocking:

.. code-block:: python

   filter.edit(
       actions={
           "block": {
               "talk": True,
               "anonymous": "1 day",
               "user": "1 day"
           }
       }
   )

tag
~~~

Add tags:

.. code-block:: python

   filter.edit(
       actions={
           "tag": ["review", "bot"]
       }
   )

throttle
~~~~~~~~

Configure rate limiting:

.. code-block:: python

   filter.edit(
       actions={
           "throttle": {
               "count": 5,
               "period": 120,
               "groups": "user"
           }
       }
   )

Set an action to ``False`` to remove it.

Rule editing
------------

``edit()`` supports complete rule replacement as well as targeted changes using ``replace``, ``append``, ``prepend``, ``remove``, and ``regex``.

.. code-block:: python

   filter.edit(rules="page_namespace == 0")
   filter.edit(append=" & user_editcount < 20")
   filter.edit(prepend="page_namespace == 0 & ")
   filter.edit(remove=" & page_namespace == 1")
   filter.edit(
       regex=(r"user_editcount\s*<\s*\d+", "user_editcount < 100")
   )

Notes
-----

Notes are appended by default. Use ``notes_mode="replace"`` to replace them or clear them.

.. code-block:: python

   filter.edit(notes="Changed the rule")
   filter.edit(notes="Updated notes", notes_mode="replace")
   filter.edit(notes="", notes_mode="replace")

Use ``sign_notes=True`` to add the current account and date to a supplied note.

Verification
------------

Changes made through ``edit()`` and ``create()`` are verified by default.

Set ``verify=False`` to skip the correctness check.

.. code-block:: python

   filter.edit(
       rules="page_namespace == 0",
       verify=False
   )

Dry runs
--------

Use ``dry_run=True`` to preview a change without saving it.

.. code-block:: python

   change = filter.edit(
       description="Preview only",
       dry_run=True
   )
