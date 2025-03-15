Toggles
=======

The ``izulu`` error class behaviour is controlled by ``__features__`` class attribute.

(For details about "runtime" and "class definition" stages
see **Validation and behavior in case of problems** below)


Supported features
------------------

* ``FORBID_MISSING_FIELDS``: checks provided ``kwargs`` contain data for all template *"fields"*
  and *"instance attributes"* that have no *"defaults"*

  * always should be enabled (provides consistent and detailed ``TypeError`` exceptions
    for appropriate arguments)
  * if disabled raw exceptions from ``izulu`` machinery internals could appear

  =======  =============
   Stage      Raises
  =======  =============
  runtime  ``TypeError``
  =======  =============

.. code-block:: python

    class AmountError(Error):
        __template__ = "Some {amount} of money for {client_id} client"
        client_id: int

    # I. enabled
    AmountError()
    # TypeError: Missing arguments: client_id, amount

    # II. disabled
    AmountError.__features__ ^= Features.FORBID_MISSING_FIELDS

    AmountError()
    # ValueError: Failed to format template with provided kwargs:

* ``FORBID_UNDECLARED_FIELDS``: forbids undefined arguments in provided ``kwargs``
  (names not present in template *"fields"* and *"instance/class hints"*)

  * if disabled allows and **completely ignores** unknown data in ``kwargs``

  =======  =============
   Stage      Raises
  =======  =============
  runtime  ``TypeError``
  =======  =============

.. code-block:: python

    class MyError(Error):
        __template__ = "My error occurred"

    # I. enabled
    MyError(unknown_data="data")
    # Undeclared arguments: unknown_data

    # II. disabled
    MyError.__features__ ^= Features.FORBID_UNDECLARED_FIELDS
    err = MyError(unknown_data="data")

    print(err)
    # Unspecified error
    print(repr(err))
    # __main__.MyError(unknown_data='data')
    err.unknown_data
    # AttributeError: 'MyError' object has no attribute 'unknown_data'

* ``FORBID_KWARG_CONSTS``: checks provided ``kwargs`` not to contain attributes defined as ``ClassVar``

  * if disabled allows data in ``kwargs`` to overlap class attributes during template formatting
  * overlapping data won't modify class attribute values

  =======  =============
   Stage      Raises
  =======  =============
  runtime  ``TypeError``
  =======  =============

.. code-block:: python

    class MyError(Error):
        __template__ = "My error occurred {_TYPE}"
        _TYPE: ClassVar[str]

    # I. enabled
    MyError(_TYPE="SOME_ERROR_TYPE")
    # TypeError: Constants in arguments: _TYPE

    # II. disabled
    MyError.__features__ ^= Features.FORBID_KWARG_CONSTS
    err = MyError(_TYPE="SOME_ERROR_TYPE")

    print(err)
    # My error occurred SOME_ERROR_TYPE
    print(repr(err))
    # __main__.MyError(_TYPE='SOME_ERROR_TYPE')
    err._TYPE
    # AttributeError: 'MyError' object has no attribute '_TYPE'

* ``FORBID_NON_NAMED_FIELDS``: forbids empty and digit field names in ``__template__``

  * if disabled validation (runtime issues)
  * ``izulu`` relies on ``kwargs`` and named fields
  * by default it's forbidden to provide empty (``{}``) and digit (``{0}``) fields in ``__template__``

  ================  ==============
   Stage               Raises
  ================  ==============
  class definition  ``ValueError``
  ================  ==============

.. code-block:: python

    class MyError(Error):
        __template__ = "My error occurred {_TYPE}"
        _TYPE: ClassVar[str]

    # I. enabled
    MyError(_TYPE="SOME_ERROR_TYPE")
    # TypeError: Constants in arguments: _TYPE

    # II. disabled
    MyError.__features__ ^= Features.FORBID_KWARG_CONSTS
    err = MyError(_TYPE="SOME_ERROR_TYPE")

    print(err)
    # My error occurred SOME_ERROR_TYPE
    print(repr(err))
    # __main__.MyError(_TYPE='SOME_ERROR_TYPE')
    err._TYPE
    # AttributeError: 'MyError' object has no attribute '_TYPE'


Tuning ``__features__``
-----------------------

Features are represented as *"Flag Enum"*, so you can use regular operations
to configure desired behaviour.
Examples:

* Use single option

.. code-block:: python

    class AmountError(Error):
        __features__ = Features.FORBID_MISSING_FIELDS

* Use presets

.. code-block:: python

    class AmountError(Error):
        __features__ = Features.NONE

* Combining wanted features:

.. code-block:: python

    class AmountError(Error):
        __features__ = Features.FORBID_MISSING_FIELDS | Features.FORBID_KWARG_CONSTS

* Discarding unwanted feature from default feature set:

.. code-block:: python

    class AmountError(Error):
        __features__ = Features.DEFAULT ^ Features.FORBID_UNDECLARED_FIELDS

