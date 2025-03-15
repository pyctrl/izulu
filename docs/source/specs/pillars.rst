The 6 pillars
=============

**The 6 pillars of** ``izulu``

* all behavior is defined on the class-level

* ``__template__`` class attribute defines the template for target error message

  * template may contain *"fields"* for substitution from ``kwargs`` and *"defaults"* to produce final error message

* ``__features__`` class attribute defines constraints and behaviour (see "Features" section below)

  * by default all constraints are enabled

* *"class hints"* annotated with ``ClassVar`` are noted by ``izulu``

  * annotated class attributes normally should have values (treated as *"class defaults"*)
  * *"class defaults"* can only be static
  * *"class defaults"* may be referred within ``__template__``

* *"instance hints"* regularly annotated (not with ``ClassVar``) are noted by ``izulu``

  * all annotated attributes are treated as *"instance attributes"*
  * each *"instance attribute"* will automatically obtain value from the ``kwarg`` of the same name
  * *"instance attributes"* with default are also treated as *"instance defaults"*
  * *"instance defaults"* may be **static and dynamic**
  * *"instance defaults"* may be referred within ``__template__``

* ``kwargs`` — the new and main way to form exceptions/error instance

  * forget about creating exception instances from message strings
  * ``kwargs`` are the datasource for template *"fields"* and *"instance attributes"*
    (shared input for templating attribution)

.. warning:: **Types from type hints are not validated or enforced!**
