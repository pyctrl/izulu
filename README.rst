izulu
=====

    *"An exceptional library"*


**Installation**

::

    pip install izulu


**Prepare playground**

::

    pip install ipython

    ipython -i -c 'from izulu.root import *; from typing import *; from datetime import *'


Presenting ``izulu``: bring OOP into exception/error management
---------------------------------------------------------------

You can read docs *from top to bottom* or jump strait into **"Quickstart"** section.
For details note **"Specifications"** sections below.


Neat #1: Stop messing with raw strings and manual message formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    if not data:
        raise ValueError("Data is invalid: no data")

    amount = data["amount"]
    if amount < 0:
        raise ValueError(f"Data is invalid: amount can't be negative ({amount})")
    elif amount > 1000:
        raise ValueError(f"Data is invalid: amount is too large ({amount})")

    if data["status"] not in {"READY", "IN_PROGRESS}:
        raise ValueError("Data is invalid: unprocessable status")

With ``izulu`` you can forget about manual error message management all over the codebase!

::

    class ValidationError(Error):
        __template__ = "Data is invalid: {reason}"

    class AmountValidationError(ValidationError):
        __template__ = f"{ValidationError.__template__} ({{amount}})"


    if not data:
        raise ValidationError(reason="no data")

    amount = data["amount"]
    if amount < 0:
        raise AmountValidationError(reason="amount can't be negative", amount=amount)
    elif amount > 1000:
        raise AmountValidationError(reason="amount is too large", amount=amount)

    if data["status"] not in {"READY", "IN_PROGRESS}:
        raise ValidationError(reason="unprocessable status")


Provide only variable data for error instantiations. Keep static data within error class.

Under the hood ``kwargs`` are used to format ``__template__`` into final error message.


Neat #2: Attribute errors with useful fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

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
----------

**Prepare playground**

::

    pip install ipython

    ipython -i -c 'from izulu.root import *; from typing import *; from datetime import *'


**Let's start with defining our initial error class (exception).**

#. subclass ``Error``
#. provide special message template for each of your exceptions
#. use **only kwargs** to instantiate exception
  *(no more message copying across the codebase)*

::

    class MyError(Error):
        __template__ = "Having count={count} for owner={owner}"


    print(MyError(count=10, owner="me"))
    # MyError: Having count=10 for owner=me

    MyError(10, owner="me")
    # TypeError: __init__() takes 1 positional argument but 2 were given


**Move on and improve our class with attributes**

#. define annotations for fields you want to publish as exception instance attributes
#. you have to define desired template fields in annotations too
   (see ``AttributeError`` for ``owner``)
#. you can provide annotation for attributes not included in template (see ``timestamp``)
#. **type hinting from annotations are not enforced or checked** (see ``timestamp``)

::

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


**We can provide defaults for our attributes**

#. define *default static values* after field annotation just as usual
#. for *dynamic defaults* use provided ``factory`` tool with your callable - it would be
   evaluated without arguments during exception instantiation
#. now fields would receive values from *kwargs* if present - otherwise from *defaults*

::

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


**Dynamic defaults also supported**

::

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
--------------

``izulu`` bases on class definitions to provide handy instance creation.


The 6 pillars of ``izulu``
^^^^^^^^^^^^^^^^^^^^^^^^^^

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

**WARNING**: types from type hints are not validated or enforced


Features
^^^^^^^^

The ``izulu`` error class behaviour is controlled by ``__features__`` class attribute.

Features are represented as flag enum ``Features`` with following options:

* ``FORBID_MISSING_FIELDS``: checks provided ``kwargs`` contain data for all template *"fields"*
  and *"instance attributes"* that have no *"defaults"*

  * always should be enabled (provides consistent and detailed ``TypeError`` exceptions for appropriate arguments)
  * if disabled raw exceptions from ``izulu`` machinery internals could appear

* ``FORBID_UNDECLARED_FIELDS``: forbids undefined arguments in provided ``kwargs``
  (names not present in template *"fields"* and *"instance/class hints"*)

  * if disabled allows and **completely ignores** unknown data in ``kwargs``

* ``FORBID_KWARG_CONSTS``: checks provided ``kwargs`` not to contain attributes defined as ``ClassVar``

  * if disabled allows data in ``kwargs`` to overlap class attributes during template formatting
  * overlapping data won't modify class attribute values


Mechanics
^^^^^^^^^

::

    pip install ipython

    ipython -i -c 'from izulu.root import *; from typing import *; from datetime import *'

* inheritance from ``izulu.root.Error`` is required

::

    class AmountError(Error):
        pass

* **optionally** behaviour can be adjusted with ``__features__``

::

    class AmountError(Error):
        __features__ = Features.FORBID_MISSING_FIELDS | Features.FORBID_KWARG_CONSTS

* you should provide a template for the target error message with ``__template__`` ::

    class AmountError(Error):
        __template__ = "Data is invalid: {reason} (amount={amount})"

    print(AmountError(reason="negative amount", amount=-10.52))
    # [2024-01-23 19:16] Data is invalid: negative amount (amount=-10.52)

  * sources of formatting arguments:

    * *"class defaults"*
    * *"instance defaults"*
    * ``kwargs`` (overlap any *"default"*)

  * new style formatting is used::

        class AmountError(Error):
            __template__ = "[{ts:%Y-%m-%d %H:%M}] Data is invalid: {reason:_^20} (amount={amount:06.2f})"

        print(AmountError(ts=datetime.now(), reason="negative amount", amount=-10.52))
        # [2024-01-23 19:16] Data is invalid: __negative amount___ (amount=-10.52)

    * ``help(str.format)``
    * https://pyformat.info/
    * https://docs.python.org/3/library/string.html#formatspec

* ``__init__()`` accepts only ``kwargs``

::

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

::

    class AmountError(Error):
        LIMIT: ClassVar[int] = 10_000
        __template__ = "Amount is too large: amount={amount} limit={LIMIT}"
        amount: int

    print(AmountError(amount=10_500))
    # Amount is too large: amount=10500 limit=10000

* *"instance attributes"* are populated from relevant ``kwargs``

::

    class AmountError(Error):
        amount: int

    print(AmountError(amount=-10).amount)
    # -10

* static *"instance defaults"* can be provided regularly with instance type hints and static values

::

    class AmountError(Error):
        amount: int = 500

    print(AmountError().amount)
    # 500

* dynamic *"instance defaults"* are also supported

  * they must be type hinted and have special value
  * value must be a callable object wrapped with ``factory`` helper
  * ``factory`` provides 2 modes depending on value of the ``self`` flag:

    * ``self=False`` (default): callable accepting no arguments ::

        class AmountError(Error):
            ts: datetime = factory(datetime.now)

        print(AmountError().ts)
        # 2024-01-23 23:18:22.019963

    * ``self=True``: provide callable accepting single argument (error instance) ::

        class AmountError(Error):
            LIMIT = 10_000
            amount: int
            overflow: int = factory(lambda self: self.amount - self.LIMIT, self=True)

        print(AmountError(amount=10_500).overflow)
        # 500

* *"instance defaults"* and *"instance attributes"* may be referred in ``__template__``

::

    class AmountError(Error):
        __template__ = "[{ts:%Y-%m-%d %H:%M}] Amount is too large: {amount}"
        amount: int
        ts: datetime = factory(datetime.now)

    print(AmountError(amount=10_500))
    # [2024-01-23 23:21] Amount is too large: 10500

* *Pause and sum up: defaults, attributes and template*

::

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

::

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

**Special notes**

* XXX *"fields"* defined in ``__template__`` rules

  * *"fields"* may refer class and instance *"defaults"*
  * you can omit them in ``kwargs`` or not (override defaults)
  * *"fields"* defined in ``__template__`` require these data in ``kwargs``

* exceptions you should expect with default feature set enabled:

  * ``TypeError``: constraint and argument issues
  * ``ValueError``: template formatting issue

* types from type hints are not validated or enforced

* *"defaults"* don't have to be ``__template__`` *"fields"*

  * there can be hints for attributes not present in error message template
  * and vice versa — there can be *"fields"* not present as instance attributes

* //pillars// annotated class attributes without values (just annotations) affects ``FORBID_KWARG_CONSTS`` feature (see below)


**Recommended**


Additional APIs
^^^^^^^^^^^^^^^

Representations
"""""""""""""""

::

    class AmountValidationError(Error):
        __template__ = "Data is invalid: {reason} ({amount}; MAX={_MAX}) at {ts}"
        _MAX: ClassVar[int] = 1000
        amount: int
        reason: str = "amount is too large"
        ts: datetime = factory(datetime.datetime.now)


    err = AmountValidationError(amount=15000)

    print(str(err))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586

    print(repr(err))
    # __main__.AmountValidationError(amount=15000, ts=datetime.datetime(2024, 1, 13, 23, 33, 13, 847586), reason='amount is too large')


* ``str`` and ``repr`` output differs
* ``str`` is for humans and Python (Python dictates the result to be exactly and only the message)
* ``repr`` allows to reconstruct the same error instance from its output
  (if data provided into *kwargs* supports ``repr`` the same way)

  **note:** class name is fully qualified name of class (dot-separated module full path with class name) ::

    reconstructed = eval(repr(err).replace("__main__.", "", 1))

    print(str(reconstructed))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586

    print(repr(reconstructed))
    # AmountValidationError(amount=15000, ts=datetime.datetime(2024, 1, 13, 23, 33, 13, 847586), reason='amount is too large')

* in addition to ``str`` there is another human-readable representations provided by ``.as_str()`` method;
  it prepends message with class name::

    print(err.as_str())
    # AmountValidationError: Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 23:33:13.847586



Dump
""""

# TODO: wide

* ``.as_kwargs()`` dumps shallow copy of original kwargs::

    err.as_kwargs()
    # {'amount': 15000}

* ``.as_dict()`` combines original kwargs and all *"instance attribute"* values into
  *"full state"* (note: this dumped state is a shallow copy of errors data)::

    err.as_dict()
    # {'amount': 15000, 'ts': datetime(2024, 1, 13, 23, 33, 13, 847586), 'reason': 'amount is too large'}

    err.as_dict(True)
    # {'amount': 15000, 'ts': datetime(2024, 1, 13, 23, 33, 13, 847586), 'reason': 'amount is too large'}

    err_copy = Error(**err.as_dict())  # exact copy


(advanced) Wedge
""""""""""""""""

There is a special method you can override and additionally manage the machinery.

But it should not be need in 99,9% cases. Avoid it, please.

::

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


Tips
----

1. inheritance / root exception
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # intermediate class to centrally control the default behaviour
    class BaseError(Error):  # <-- inherit from this in your code (not directly from ``izulu``)
        __features__ = Features.None


    class MyRealError(BaseError):
        __template__ = "Having count={count} for owner={owner}"


2. factories
^^^^^^^^^^^^

TODO: self=True / self.as_kwargs()  (as_dict forbidden? - recursion)


* stdlib factories

::

    from uuid import uuid4

    class MyError(Error):
        id: datetime = factory(uuid4)
        timestamp: datetime = factory(datetime.now)

* lambdas

::

    class MyError(Error):
        timestamp: datetime = factory(lambda: datetime.now().isoformat())

* function

::

    from random import randint

    def flip_coin():
        return "TAILS" if randint(0, 100) % 2 else "HEADS

    class MyError(Error):
        coin: str = factory(flip_coin)


* method

::

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    err = Error()
    view = RespModel(error=err.as_dict(wide=True)


    class MyRealError(BaseError):
        __template__ = "Having count={count} for owner={owner}"


Additional examples
-------------------

TBD


For developers
--------------

* Running tests::

    tox

* Building package::

    tox -e build

* Contributing: contact me through `Issues <https://gitlab.com/pyctrl/izulu/-/issues>`__


Versioning
----------

`SemVer <http://semver.org/>`__ used for versioning.
For available versions see the repository
`tags <https://gitlab.com/pyctrl/izulu/-/tags>`__
and `releases <https://gitlab.com/pyctrl/izulu/-/releases>`__.


Authors
-------

-  **Dima Burmistrov** - *Initial work* -
   `pyctrl <https://gitlab.com/pyctrl/>`__

*Special thanks to* `Eugene Frolov <https://github.com/phantomii/>`__ *for inspiration.*


License
-------

This project is licensed under the X11 License (extended MIT) - see the
`LICENSE <https://gitlab.com/pyctrl/izulu/-/blob/main/LICENSE>`__ file for details
