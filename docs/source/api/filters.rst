Filters
=======

``mediawiki_abusefilter.filters()`` creates a client for one MediaWiki site.

Constructor
-----------

.. code-block:: python

   filters = mediawiki_abusefilter.filters(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD",
       debug=True
   )

The main arguments are:

``url``
   MediaWiki site URL.

``username`` / ``password``
   Credentials for the account used by the client.

``auth``
   An existing ``Auth`` object to reuse.

``user_agent``
   HTTP User-Agent. A project-specific default is supplied.

``tls_verify``
   Whether TLS certificates should be verified. Defaults to ``True``.

``timeout``
   Request timeout in seconds. Defaults to ``30``.

``debug``
   Print request and authentication diagnostics. Defaults to ``False``.

Methods
-------

``list(limit=50, enabled=None, public=None, private=None, protected=None, suppressed=None, start=None, end=None, direction=None)``
   Return matching filters. Large result sets are continued automatically.

``search(query, limit=50)``
   Search filter descriptions, rules, notes, actions, and last editors.

``get(filter_id)``
   Return one filter with its current metadata and editable state.

``create(description, rules, notes=None, enabled=True, public=True, actions=None, verify=True, sign_notes=False, dry_run=False, notes_mode="append")``
   Create a filter, or return a preview when ``dry_run=True``.

``login()``
   Authenticate the configured account and return the client.

``whoami()``
   Return information about the current account.

Examples
--------

.. code-block:: python

   filters.list()
   filters.list(enabled=True)
   filters.list(public=False)
   filters.search("spam")
   filter = filters.get(123)

   filter = filters.create(
       "Edit count restriction",
       "user_editcount < 10",
       notes="Created by the bot",
       verify=True
   )
