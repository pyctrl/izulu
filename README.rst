izulu
#####

.. image:: https://repository-images.githubusercontent.com/766241795/85494614-5974-4b26-bfec-03b8e393c7f0
   :width: 128px

|

    *"The exceptional library"*

|


**Installation**

For Python versions prior to 3.11 also install ``izulu[compatibility]``.

::

    # py311 and higher
    pip install izulu

    # py38-py310
    pip install izulu izulu[compatibility]

Presenting "izulu"
******************

Bring OOP into exception/error management
=========================================

You can read docs *from top to bottom* or jump straight into **"Quickstart"** section.
For details note **"Specifications"** sections below.


Neat #1: Stop messing with raw strings and manual message formatting
--------------------------------------------------------------------

.. code-block:: python

    if not data:
        raise ValueError("Data is invalid: no data")

    amount = data["amount"]
    if amount < 0:
        raise ValueError(f"Data is invalid: amount can't be negative ({amount})")
    elif amount > 1000:
        raise ValueError(f"Data is invalid: amount is too large ({amount})")

    if data["status"] not in {"READY", "IN_PROGRESS"}:
        raise ValueError("Data is invalid: unprocessable status")

With ``izulu`` you can forget about manual error message management all over the codebase!

.. code-block:: python

    class ValidationError(Error):
        __template__ = "Data is invalid: {reason}"

    class AmountValidationError(ValidationError):
        __template__ = "Invalid amount: {amount}"


    if not data:
        raise ValidationError(reason="no data")

    amount = data["amount"]
    if amount < 0:
        raise AmountValidationError(reason="amount can't be negative", amount=amount)
    elif amount > 1000:
        raise AmountValidationError(reason="amount is too large", amount=amount)

    if data["status"] not in {"READY", "IN_PROGRESS"}:
        raise ValidationError(reason="unprocessable status")


Provide only variable data for error instantiations. Keep static data within error class.

Under the hood ``kwargs`` are used to format ``__template__`` into final error message.


Neat #2: Attribute errors with useful fields
--------------------------------------------

.. code-block:: python

    from falcon import HTTPBadRequest

    class AmountValidationError(ValidationError):
        __template__ = "Data is invalid: {reason} ({amount})"
        amount: int


    try:
        validate(data)
    except AmountValidationError as e:
        if e.amount < 0:
            raise HTTPBadRequest(f"Bad amount: {e.amount}")
        raise


Annotated instance attributes automatically populated from ``kwargs``.


Neat #3: Static and dynamic defaults
------------------------------------

.. code-block:: python

    class AmountValidationError(ValidationError):
        __template__ = "Data is invalid: {reason} ({amount}; MAX={_MAX}) at {ts}"
        _MAX: ClassVar[int] = 1000
        amount: int
        reason: str = "amount is too large"
        ts: datetime = factory(datetime.now)


    print(AmountValidationError(amount=15000))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 22:59:25.132699

    print(AmountValidationError(amount=-1, reason="amount can't be negative"))
    # Data is invalid: amount can't be negative (-1; MAX=1000) at 2024-01-13 22:59:54.482577

Quickstart
==========

.. note::

    **Prepare playground**

    ::

        pip install ipython izulu

        ipython -i -c 'from izulu.root import *; from typing import *; from datetime import *'


Let's start with defining our initial error class (exception)
-------------------------------------------------------------

#. subclass ``Error``
#. provide special message template for each of your exceptions
#. use **only kwargs** to instantiate exception *(no more message copying across the codebase)*

.. code-block:: python

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"


    print(MyError(count=10, owner="me"))
    # MyError: Having count=10 for owner=me

    MyError(10, owner="me")
    # TypeError: __init__() takes 1 positional argument but 2 were given


Move on and improve our class with attributes
---------------------------------------------

#. define annotations for fields you want to publish as exception instance attributes
#. you have to define desired template fields in annotations too
   (see ``AttributeError`` for ``owner``)
#. you can provide annotation for attributes not included in template (see ``timestamp``)
#. **type hinting from annotations are not enforced or checked** (see ``timestamp``)

.. code-block:: python

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"
        count: int
        timestamp: datetime

    e = MyError(count=10, owner="me", timestamp=datetime.now())

    print(e.count)
    # 10
    print(e.timestamp)
    # 2023-09-27 18:18:22.957925

    e.owner
    # AttributeError: 'MyError' object has no attribute 'owner'


We can provide defaults for our attributes
------------------------------------------

#. define *default static values* after field annotation just as usual
#. for *dynamic defaults* use provided ``factory`` tool with your callable - it would be
   evaluated without arguments during exception instantiation
#. now fields would receive values from ``kwargs`` if present - otherwise from *defaults*

.. code-block:: python

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"
        count: int
        owner: str = "nobody"
        timestamp: datetime = factory(datetime.now)

    e = MyError(count=10)

    print(e.count)
    # 10
    print(e.owner)
    # nobody
    print(e.timestamp)
    # 2023-09-27 18:19:37.252577


Dynamic defaults also supported
-------------------------------

.. code-block:: python

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"

        count: int
        begin: datetime
        owner: str = "nobody"
        timestamp: datetime = factory(datetime.now)
        duration: timedelta = factory(lambda self: self.timestamp - self.begin, self=True)


    begin = datetime.fromordinal(date.today().toordinal())
    e = MyError(count=10, begin=begin)

    print(e.begin)
    # 2023-09-27 00:00:00
    print(e.duration)
    # 18:45:44.502490
    print(e.timestamp)
    # 2023-09-27 18:45:44.502490


* very similar to dynamic defaults, but callable must accept single
  argument - your exception fresh instance
* **don't forget** to provide second ``True`` argument for ``factory`` tool
  (keyword or positional - doesn't matter)

Specifications
**************

``izulu`` bases on class definitions to provide handy instance creation.

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

Mechanics
=========

.. note::

    **Prepare playground**

    ::

        pip install ipython izulu

        ipython -i -c 'from izulu.root import *; from typing import *; from datetime import *'


* inheritance from ``izulu.root.Error`` is required

.. code-block:: python

    class AmountError(Error):
        pass

* **optionally** behaviour can be adjusted with ``__features__`` (not recommended)

.. code-block:: python

    class AmountError(Error):
        __features__ = Features.DEFAULT ^ Features.FORBID_UNDECLARED_FIELDS

* you should provide a template for the target error message with ``__template__``

  .. code-block:: python

    class AmountError(Error):
        __template__ = "Data is invalid: {reason} (amount={amount})"

    print(AmountError(reason="negative amount", amount=-10.52))
    # [2024-01-23 19:16] Data is invalid: negative amount (amount=-10.52)

  * sources of formatting arguments:

    * *"class defaults"*
    * *"instance defaults"*
    * ``kwargs`` (overlap any *"default"*)

  * new style formatting is used:

    .. code-block:: python

      class AmountError(Error):
          __template__ = "[{ts:%Y-%m-%d %H:%M}] Data is invalid: {reason:_^20} (amount={amount:06.2f})"

      print(AmountError(ts=datetime.now(), reason="negative amount", amount=-10.52))
      # [2024-01-23 19:16] Data is invalid: __negative amount___ (amount=-10.52)

    * ``help(str.format)``
    * https://pyformat.info/
    * https://docs.python.org/3/library/string.html#format-string-syntax

      .. warning::
        There is a difference between docs and actual behaviour:
        https://discuss.python.org/t/format-string-syntax-specification-differs-from-actual-behaviour/46716

  * only named fields are allowed

    * positional (digit) and empty field are forbidden

* error instantiation requires data to format ``__template__``

  * all data for ``__template__`` fields must be provided

    .. code-block:: python

      class AmountError(Error):
          __template__ = "Data is invalid: {reason} (amount={amount})"

      print(AmountError(reason="amount can't be negative", amount=-10))
      # Data is invalid: amount can't be negative (amount=-10)

      AmountError()
      # TypeError: Missing arguments: 'reason', 'amount'
      AmountError(amount=-10)
      # TypeError: Missing arguments: 'reason'

  * only named arguments allowed: ``__init__()`` accepts only ``kwargs``

    .. code-block:: python

      class AmountError(Error):
          __template__ = "Data is invalid: {reason} (amount={amount})"

      print(AmountError(reason="amount can't be negative", amount=-10))
      # Data is invalid: amount can't be negative (amount=-10)

      AmountError("amount can't be negative", -10)
      # TypeError: __init__() takes 1 positional argument but 3 were given
      AmountError("amount can't be negative", amount=-10)
      # TypeError: __init__() takes 1 positional argument but 2 were given

* *"class defaults"* can be defined and used

  * *"class defaults"* must be type hinted with ``ClassVar`` annotation and provide static values
  * template *"fields"* may refer *"class defaults"*

.. code-block:: python

    class AmountError(Error):
        LIMIT: ClassVar[int] = 10_000
        __template__ = "Amount is too large: amount={amount} limit={LIMIT}"
        amount: int

    print(AmountError(amount=10_500))
    # Amount is too large: amount=10500 limit=10000

* *"instance attributes"* are populated from relevant ``kwargs``

.. code-block:: python

    class AmountError(Error):
        amount: int

    print(AmountError(amount=-10).amount)
    # -10

* instance and class attribute types from **annotations are not validated or enforced**
  (``izulu`` uses type hints just for attribute discovery and only ``ClassVar`` marker
  is processed for instance/class segregation)

.. code-block:: python

    class AmountError(Error):
        amount: int

    print(AmountError(amount="lots of money").amount)
    # lots of money

* static *"instance defaults"* can be provided regularly with instance type hints and static values

.. code-block:: python

    class AmountError(Error):
        amount: int = 500

    print(AmountError().amount)
    # 500

* dynamic *"instance defaults"* are also supported

  * they must be type hinted and have special value
  * value must be a callable object wrapped with ``factory`` helper
  * ``factory`` provides 2 modes depending on value of the ``self`` flag:

    * ``self=False`` (default): callable accepting no arguments

      .. code-block:: python

        class AmountError(Error):
            ts: datetime = factory(datetime.now)

        print(AmountError().ts)
        # 2024-01-23 23:18:22.019963

    * ``self=True``: provide callable accepting single argument (error instance)

      .. code-block:: python

        class AmountError(Error):
            LIMIT = 10_000
            amount: int
            overflow: int = factory(lambda self: self.amount - self.LIMIT, self=True)

        print(AmountError(amount=10_500).overflow)
        # 500

* *"instance defaults"* and *"instance attributes"* may be referred in ``__template__``

.. code-block:: python

    class AmountError(Error):
        __template__ = "[{ts:%Y-%m-%d %H:%M}] Amount is too large: {amount}"
        amount: int
        ts: datetime = factory(datetime.now)

    print(AmountError(amount=10_500))
    # [2024-01-23 23:21] Amount is too large: 10500

* *Pause and sum up: defaults, attributes and template*

.. code-block:: python

    class AmountError(Error):
        LIMIT: ClassVar[int] = 10_000
        __template__ = "[{ts:%Y-%m-%d %H:%M}] Amount is too large: amount={amount} limit={LIMIT} overflow={overflow}"
        amount: int
        overflow: int = factory(lambda self: self.amount - self.LIMIT, self=True)
        ts: datetime = factory(datetime.now)

    err = AmountError(amount=15_000)

    print(err.amount)
    # 15000
    print(err.LIMIT)
    # 10000
    print(err.overflow)
    # 5000
    print(err.ts)
    # 2024-01-23 23:21:26

    print(err)
    # [2024-01-23 23:21] Amount is too large: amount=15000 limit=10000 overflow=5000

* ``kwargs`` overlap *"instance defaults"*

.. code-block:: python

    class AmountError(Error):
        LIMIT: ClassVar[int] = 10_000
        __template__ = "[{ts:%Y-%m-%d %H:%M}] Amount is too large: amount={amount} limit={LIMIT} overflow={overflow}"
        amount: int = 15_000
        overflow: int = factory(lambda self: self.amount - self.LIMIT, self=True)
        ts: datetime = factory(datetime.now)

    print(AmountError())
    # [2024-01-23 23:21] Amount is too large: amount=15000 limit=10000 overflow=5000

    print(AmountError(amount=10_333, overflow=42, ts=datetime(1900, 1, 1)))
    # [2024-01-23 23:21] Amount is too large: amount=10333 limit=10000 overflow=42

* ``izulu`` provides flexibility for templates, fields, attributes and defaults

  * *"defaults"* are not required to be ``__template__`` *"fields"*

    .. code-block:: python

      class AmountError(Error):
          LIMIT: ClassVar[int] = 10_000
          __template__ = "Amount is too large"

      print(AmountError().LIMIT)
      # 10000
      print(AmountError())
      # Amount is too large

  * there can be hints for attributes not present in error message template

    .. code-block:: python

      class AmountError(Error):
          __template__ = "Amount is too large"
          amount: int

      print(AmountError(amount=500).amount)
      # 500
      print(AmountError(amount=500))
      # Amount is too large

  * *"fields"* don't have to be hinted as instance attributes

    .. code-block:: python

      class AmountError(Error):
          __template__ = "Amount is too large: {amount}"

      print(AmountError(amount=500))
      # Amount is too large: 500
      print(AmountError(amount=500).amount)
      # AttributeError: 'AmountError' object has no attribute 'amount'

Features
========

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

Validation and behavior in case of problems
===========================================

``izulu`` may trigger native Python exceptions on invalid data during validation process.
By default you should expect following ones

* ``TypeError``: argument constraints issues
* ``ValueError``: template and formatting issues

Some exceptions are *raised from* original exception (e.g. template formatting issues),
so you can check ``e.__cause__`` and traceback output for details.


The validation behavior depends on the set of enabled features.
Changing feature set may cause different and raw exceptions being raised.
Read and understand **"Features"** section to predict and experiment with different situations and behaviours.


``izulu`` has **2 validation stages:**

* class definition stage

  * validation is made during error class definition

    .. code-block:: python

      # when you import error module
      from izulu import root

      # when you import error from module
      from izulu.root import Error

      # when you interactively define new error classes
      class MyError(Error):
          pass

  * class attributes ``__template__`` and ``__features__`` are validated

    .. code-block:: python

      class MyError(Error):
          __template__ = "Hello {}"

      # ValueError: Field names can't be empty

* runtime stage

  * validation is made during error instantiation

    .. code-block:: python

      root.Error()

  * ``kwargs`` are validated according to enabled features

    .. code-block:: python

      class MyError(Error):
          __template__ = "Hello {name}"

      MyError()
      # TypeError: Missing arguments: 'name'

Additional APIs
===============


Representations
---------------

.. code-block:: python

    class AmountValidationError(Error):
        __template__ = "Data is invalid: {reason} ({amount}; MAX={_MAX}) at {ts}"
        _MAX: ClassVar[int] = 1000
        amount: int
        reason: str = "amount is too large"
        ts: datetime = factory(datetime.now)


    err = AmountValidationError(amount=15000)

    print(str(err))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586

    print(repr(err))
    # __main__.AmountValidationError(amount=15000, ts=datetime.datetime(2024, 1, 13, 23, 33, 13, 847586), reason='amount is too large')


* ``str`` and ``repr`` output differs
* ``str`` is for humans and Python (Python dictates the result to be exactly and only the message)
* ``repr`` allows to reconstruct the same error instance from its output
  (if data provided into ``kwargs`` supports ``repr`` the same way)

  **note:** class name is fully qualified name of class (dot-separated module full path with class name)

  .. code-block:: python

    reconstructed = eval(repr(err).replace("__main__.", "", 1))

    print(str(reconstructed))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586

    print(repr(reconstructed))
    # AmountValidationError(amount=15000, ts=datetime.datetime(2024, 1, 13, 23, 33, 13, 847586), reason='amount is too large')

* in addition to ``str`` there is another human-readable representations provided by ``.as_str()`` method;
  it prepends message with class name:

  .. code-block:: python

    print(err.as_str())
    # AmountValidationError: Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586


Pickling
--------

``izulu``-based errors **support pickling** by default.


Dumping and loading
-------------------

**Dumping**

* ``.as_kwargs()`` dumps shallow copy of original ``kwargs``

.. code-block:: python

    err.as_kwargs()
    # {'amount': 15000}

* ``.as_dict()`` by default, combines original ``kwargs`` and all *"instance attribute"* values into *"full state"*

  .. code-block:: python

    err.as_dict()
    # {'amount': 15000, 'ts': datetime(2024, 1, 13, 23, 33, 13, 847586), 'reason': 'amount is too large'}

  Additionally, there is the ``wide`` flag for enriching the result with *"class defaults"*
  (note additional ``_MAX`` data)

  .. code-block:: python

    err.as_dict(True)
    # {'amount': 15000, 'ts': datetime(2024, 1, 13, 23, 33, 13, 847586), 'reason': 'amount is too large', '_MAX': 1000}

  Data combination process follows prioritization — if there are multiple values for same name then high priority data
  will overlap data with lower priority. Here is the prioritized list of data sources:

  #. ``kwargs`` (max priority)
  #. *"instance attributes"*
  #. *"class defaults"*


**Loading**

* ``.as_kwargs()`` result can be used to create **inaccurate** copy of original error,
  but pay attention to dynamic factories — ``datetime.now()``, ``uuid()`` and many others would produce new values
  for data missing in ``kwargs`` (note ``ts`` field in the example below)

.. code-block:: python

    inaccurate_copy = AmountValidationError(**err.as_kwargs())

    print(inaccurate_copy)
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-02-01 21:11:21.681080
    print(repr(inaccurate_copy))
    # __main__.AmountValidationError(amount=15000, reason='amount is too large', ts=datetime.datetime(2024, 2, 1, 21, 11, 21, 681080))

* ``.as_dict()`` result can be used to create **accurate** copy of original error;
  flag ``wide`` should be ``False`` by default according to ``FORBID_KWARG_CONSTS`` restriction
  (if you disable ``FORBID_KWARG_CONSTS`` then you may need to use ``wide=True`` depending on your situation)

.. code-block:: python

    accurate_copy = AmountValidationError(**err.as_dict())

    print(accurate_copy)
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-02-01 21:11:21.681080
    print(repr(accurate_copy))
    # __main__.AmountValidationError(amount=15000, reason='amount is too large', ts=datetime.datetime(2024, 2, 1, 21, 11, 21, 681080))


(advanced) Wedge
----------------

There is a special method you can override and additionally manage the machinery.

But it should not be need in 99,9% cases. Avoid it, please.

.. code-block:: python

    def _hook(self,
              store: _utils.Store,
              kwargs: dict[str, t.Any],
              msg: str) -> str:
        """Adapter method to wedge user logic into izulu machinery

        This is the place to override message/formatting if regular mechanics
        don't work for you. It has to return original or your flavored message.
        The method is invoked between izulu preparations and original
        `Exception` constructor receiving the result of this hook.

        You can also do any other logic here. You will be provided with
        complete set of prepared data from izulu. But it's recommended
        to use classic OOP inheritance for ordinary behaviour extension.

        Params:
          * store: dataclass containing inner error class specifications
          * kwargs: original kwargs from user
          * msg: formatted message from the error template
        """

        return msg

Recipes & Tips
**************

1. inheritance / root exception
===============================

.. code-block:: python

    # intermediate class to centrally control the default behaviour
    class BaseError(Error):  # <-- inherit from this in your code (not directly from ``izulu``)
        __features__ = Features.None


    class MyRealError(BaseError):
        __template__ = "Having count={count} for owner={owner}"


2. factories
============

TODO: self=True / self.as_kwargs()  (as_dict forbidden? - recursion)


* stdlib factories

.. code-block:: python

    from uuid import uuid4

    class MyError(Error):
        id: datetime = factory(uuid4)
        timestamp: datetime = factory(datetime.now)

* lambdas

.. code-block:: python

    class MyError(Error):
        timestamp: datetime = factory(lambda: datetime.now().isoformat())

* function

.. code-block:: python

    from random import randint

    def flip_coin():
        return "TAILS" if randint(0, 100) % 2 else "HEADS

    class MyError(Error):
        coin: str = factory(flip_coin)


* method

.. code-block:: python

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"

        def __make_duration(self) -> timedelta:
            kwargs = self.as_kwargs()
            return self.timestamp - kwargs["begin"]

        timestamp: datetime = factory(datetime.now)
        duration: timedelta = factory(__make_duration, self=True)


    begin = datetime.fromordinal(date.today().toordinal())
    e = MyError(count=10, begin=begin)

    print(e.begin)
    # 2023-09-27 00:00:00
    print(e.duration)
    # 18:45:44.502490
    print(e.timestamp)
    # 2023-09-27 18:45:44.502490


3. handling errors in presentation layers / APIs
================================================

.. code-block:: python

    err = Error()
    view = RespModel(error=err.as_dict(wide=True)


    class MyRealError(BaseError):
        __template__ = "Having count={count} for owner={owner}"


Additional examples
-------------------

TBD

For developers
**************

* Use regular virtualenv or any other (no pre-defined preparations provided)

* Running tests::

    tox

* Building package::

    tox -e build

* Contributing: contact me through `Issues <https://github.com/pyctrl/izulu/issues>`__


Versioning
**********

`SemVer <http://semver.org/>`__ used for versioning.
For available versions see the repository
`tags <https://github.com/pyctrl/izulu/tags>`__
and `releases <https://github.com/pyctrl/izulu/releases>`__.

Authors
*******

-  **Dima Burmistrov** - *Initial work* -
   `pyctrl <https://github.com/pyctrl>`__

*Special thanks to* `Eugene Frolov <https://github.com/phantomii/>`__ *for inspiration.*


License
*******

This project is licensed under the X11 License (extended MIT) - see the
`LICENSE <https://github.com/pyctrl/izulu/blob/main/LICENSE>`__ file for details

