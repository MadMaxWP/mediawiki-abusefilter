Filters
=======

The :func:`mediawiki_abusefilter.filters` entry point creates a client for finding and managing filters on one MediaWiki site.

Creating a client
-----------------

.. code-block:: python

   import mediawiki_abusefilter as mwaf

   filters = mwaf.filters(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD"
   )

Filters
-------

.. autoclass:: mediawiki_abusefilter.client.Filters
   :members: api_url, login, whoami, list, search, get, create
   :undoc-members:
   :show-inheritance:

login()
~~~~~~~

Log in to the configured account. A client that was created with credentials already logs in automatically.

.. code-block:: python

   filters.login()

whoami()
~~~~~~~~~

Return information about the current account.

.. code-block:: python

   info = filters.whoami()
   print(info["name"])

list()
~~~~~~

Return filters matching the supplied status and visibility options.

.. code-block:: python

   filters.list()
   filters.list(enabled=True)
   filters.list(public=True)
   filters.list(private=True)
   filters.list(protected=True)
   filters.list(suppressed=True)

The ``limit`` argument controls the maximum number of results returned. ``start``, ``end``, and ``direction`` can be used when working with a particular filter ID range.

.. code-block:: python

   filters.list(limit=100)
   filters.list(start=100, end=200, direction="newer")

search()
~~~~~~~~

Search available filter information for a query string.

.. code-block:: python

   matches = filters.search("spam")
   for filter in matches:
       print(filter.id, filter.description)

Use ``limit`` to restrict the number of returned filters.

.. code-block:: python

   filters.search("spam", limit=20)

get()
~~~~~

Return a :class:`~mediawiki_abusefilter.filter.Filter` for a filter ID.

.. code-block:: python

   filter = filters.get(123)
   print(filter.description)

create()
~~~~~~~~

Create a new filter and return it as a :class:`~mediawiki_abusefilter.filter.Filter` object.

A new filter is enabled and public by default.

.. code-block:: python

   filter = filters.create(
       "Low edit count edits",
       "page_namespace == 0 & user_editcount < 10"
   )

The main creation options are:

``description``
   The filter description.

``rules``
   The AbuseFilter expression.

``notes``
   Notes to store with the filter.

``enabled``
   Whether the filter should be enabled.

``public``
   Whether the filter should be public.

``actions``
   Actions to apply when the filter matches. See :doc:`filter` for the supported action formats.

``verify``
   Verify the requested values after saving. The default is ``True``.

``sign_notes``
   Add the current account and date to a supplied note.

``dry_run``
   Return the proposed change without creating the filter.

``notes_mode``
   Either ``"append"`` or ``"replace"`` for supplied notes.

.. code-block:: python

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

Preview creation without saving:

.. code-block:: python

   preview = filters.create(
       "Example filter",
       "page_namespace == 0",
       dry_run=True
   )
