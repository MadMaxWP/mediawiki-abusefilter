Filter
======

Represents a MediaWiki AbuseFilter.

.. autoclass:: mediawiki_abusefilter.filter.Filter
   :members:
   :undoc-members:
   :show-inheritance:

Edit
----

The ``edit()`` method can update one or more filter properties at once.

Rules
~~~~~

``rules``
    Replace the complete filter expression.

``replace``
    Replace text in the existing expression.

``append``
    Add text to the end of the existing expression.

``prepend``
    Add text to the beginning of the existing expression.

``remove``
    Remove text from the existing expression.

``regex``
    Replace text using a regular expression.

Actions
~~~~~~~

``warn``
    ...

``disallow``
    ...

``blockautopromote``
    ...

``block``
    ...

``tag``
    ...

``throttle``
    ...
