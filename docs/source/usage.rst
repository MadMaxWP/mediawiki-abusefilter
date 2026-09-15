Usage
=====

Installation
------------

Install mediawiki-abusefilter with pip:

.. code-block:: console

   pip install mediawiki-abusefilter

Quick start
-----------

Create a client with the URL of the wiki and the account credentials to use for filter management. New filters are public and enabled by default.

.. code-block:: python

   import mediawiki_abusefilter as mwaf

   filters = mwaf.filters(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD"
   )

   filter = filters.get(123)
   print(filter.description)

Authentication
--------------

The client can authenticate directly, or authentication can be created separately when it needs to be reused.

.. code-block:: python

   auth = mwaf.auth(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD"
   )

   filters = mwaf.filters("https://example.org", auth=auth)

Use ``debug=True`` when diagnostic output is useful.

User-Agent
----------

The client sends a descriptive User-Agent with its requests. The default identifies mediawiki-abusefilter and includes the project contact address. Set ``user_agent`` when you want to identify your own application instead.

.. code-block:: python

   filters = mwaf.filters(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD",
       user_agent="MyBot/1.0 (https://example.org/bot; bot@example.org)"
   )

.. code-block:: python

   filters = mwaf.filters(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD",
       debug=True
   )

Checking the account
--------------------

.. code-block:: python

   print(filters.whoami())

Finding filters
----------------

Retrieve a filter directly:

.. code-block:: python

   filter = filters.get(123)

List filters:

.. code-block:: python

   for filter in filters.list():
       print(filter.id, filter.description)

Restrict results by status or visibility:

.. code-block:: python

   filters.list(enabled=True)
   filters.list(public=True)
   filters.list(private=True)
   filters.list(protected=True)
   filters.list(suppressed=True)

Search available filter information:

.. code-block:: python

   for filter in filters.search("spam"):
       print(filter.id, filter.description)

Creating a filter
-----------------

.. code-block:: python

   filter = filters.create(
       "Edit count restriction",
       "user_editcount < 10",
       notes="Created by the bot",
       enabled=True
   )

Editing a filter
----------------

Update any supported property directly:

.. code-block:: python

   filter.edit(
       description="Updated description",
       rules="user_editcount < 20",
       notes="Updated by the bot",
       enabled=True
   )

Rule changes
------------

Replace or modify part of the existing rule expression:

.. code-block:: python

   filter.edit(replace=("user_editcount < 10", "user_editcount < 20"))
   filter.edit(append=" & page_namespace == 0")
   filter.edit(prepend="page_namespace == 0 & ")
   filter.edit(remove=" & page_namespace == 0")
   filter.edit(regex=(r"user_editcount\s*<\s*\d+", "user_editcount < 100"))

Notes
-----

Supplied notes are appended to existing notes by default. Leave ``notes`` out to keep the current notes unchanged. Use ``notes_mode="replace"`` to replace or clear them, and ``sign_notes=True`` to add the current account and date.

.. code-block:: python

   filter.edit(notes="Changed the rule")
   filter.edit(notes="Replacement", notes_mode="replace")
   filter.edit(notes="Changed the rule", sign_notes=True)

Actions
-------

Configure multiple actions in one edit:

.. code-block:: python

   filter.edit(actions={
       "warn": "abusefilter-warning",
       "disallow": "abusefilter-disallowed",
       "block": {
           "talk": True,
           "anonymous": "1 day",
           "user": "1 day"
       },
       "tag": ["review", "bot"]
   })

Set an action to ``False`` to disable it.

History
-------

.. code-block:: python

   for entry in filter.history(limit=20):
       print(entry["id"], entry["user"], entry["timestamp"])

Refreshing
----------

.. code-block:: python

   filter.refresh()

Verification and dry runs
-------------------------

Verify requested changes after saving:

.. code-block:: python

   filter.edit(
       rules="user_editcount < 20",
       enabled=True,
       verify=True
   )

Create previews with ``dry_run=True`` as well:

.. code-block:: python

   preview = filters.create(
       "Example",
       "false",
       dry_run=True
   )

Preview a change without saving it:

.. code-block:: python

   preview = filter.edit(
       rules="user_editcount < 20",
       dry_run=True
   )
   print(preview)

Deleting a filter
-----------------

.. code-block:: python

   filter.delete()
