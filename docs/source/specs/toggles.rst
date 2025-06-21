Toggles
=======

The ``izulu`` error class behaviour is controlled by ``__toggles__`` class attribute.

(For details about "runtime" and "class definition" stages
see **Validation and behavior in case of problems** below)


Supported toggles
-----------------

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
    MyError.__toggles__ ^= Toggles.FORBID_UNDECLARED_FIELDS
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
    MyError.__toggles__ ^= Toggles.FORBID_KWARG_CONSTS
    err = MyError(_TYPE="SOME_ERROR_TYPE")

    print(err)
    # My error occurred SOME_ERROR_TYPE
    print(repr(err))
    # __main__.MyError(_TYPE='SOME_ERROR_TYPE')
    err._TYPE
    # AttributeError: 'MyError' object has no attribute '_TYPE'


Tuning ``__toggles__``
-----------------------

Toggles are represented as *"Flag Enum"*, so you can use regular operations
to configure desired behaviour.
Examples:

* Use single option

.. code-block:: python

    class AmountError(Error):
        __toggles__ = Toggles.FORBID_MISSING_FIELDS

* Use presets

.. code-block:: python

    class AmountError(Error):
        __toggles__ = Toggles.NONE

* Combining wanted toggles:

.. code-block:: python

    class AmountError(Error):
        __toggles__ = Toggles.FORBID_MISSING_FIELDS | Toggles.FORBID_KWARG_CONSTS

* Discarding unwanted toggle from default toggle set:

.. code-block:: python

    class AmountError(Error):
        __toggles__ = Toggles.DEFAULT ^ Toggles.FORBID_UNDECLARED_FIELDS

