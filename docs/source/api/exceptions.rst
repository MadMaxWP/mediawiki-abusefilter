Exceptions
==========

The package provides specific exceptions for authentication, filter access, validation, rule editing, and save failures.

Exception reference
-------------------

.. automodule:: mediawiki_abusefilter.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Common exceptions
-----------------

``LoginError``
   Authentication failed.

``FilterNotFoundError``
   The requested filter could not be found.

``FilterPermissionError``
   The account is not allowed to perform the requested operation.

``FilterSyntaxError``
   MediaWiki rejected the supplied AbuseFilter expression.

``ValidationError``
   The supplied filter data was rejected as invalid.

``FilterSaveError``
   A filter save could not be completed or verified.

``RuleEditError``
   A rule transformation could not be applied.

``FilterError``
   A general filter-related error.

All package-specific exceptions inherit from ``AbuseFilterError``.

Handling errors
---------------

Catch a specific exception when the caller needs to handle a particular failure:

.. code-block:: python

   import mediawiki_abusefilter as mwaf

   try:
       filter.edit(rules="invalid expression")
   except mwaf.FilterSyntaxError:
       print("The filter expression is invalid.")
   except mwaf.FilterPermissionError:
       print("The account cannot edit this filter.")
