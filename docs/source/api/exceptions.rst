Exceptions
==========

All package exceptions inherit from ``AbuseFilterError``.

``LoginError``
   Authentication failed.

``FilterError``
   General filter error.

``FilterNotFoundError``
   The requested filter does not exist or cannot be found.

``FilterSaveError``
   A filter change did not complete successfully.

``FilterSyntaxError``
   MediaWiki rejected the filter expression.

``FilterPermissionError``
   The account does not have permission for the requested operation.

``ValidationError``
   MediaWiki rejected the supplied filter data.

``RuleEditError``
   A requested rule transformation could not be applied.
