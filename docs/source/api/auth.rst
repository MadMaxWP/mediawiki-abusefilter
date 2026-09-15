Authentication
==============

The :func:`mediawiki_abusefilter.auth` entry point creates an authentication session that can be reused by one or more ``Filters`` clients.

Creating an authentication session
-----------------------------------

.. code-block:: python

   import mediawiki_abusefilter as mwaf

   auth = mwaf.auth(
       "https://example.org",
       username="MyBot@mybotpassword",
       password="BOT_PASSWORD"
   )

   print(auth.whoami()["name"])

The same authentication object can be passed to :func:`mediawiki_abusefilter.filters`:

.. code-block:: python

   filters = mwaf.filters("https://example.org", auth=auth)

Auth
----

.. autoclass:: mediawiki_abusefilter.auth.Auth
   :members: api_url, login, whoami
   :undoc-members:
   :show-inheritance:

login()
~~~~~~~~

Call ``login()`` explicitly when credentials were not supplied when the authentication object was created. Calling it again reuses the existing login unless ``force=True`` is used.

.. code-block:: python

   auth.login()
   auth.login(force=True)

whoami()
~~~~~~~~

Return information about the current account, including its name, groups, and rights.

.. code-block:: python

   info = auth.whoami()
   print(info["name"])
   print(info["groups"])
   print(info["rights"])
