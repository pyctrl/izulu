izulu
=====

*"An exceptional library"*

**Installation**

::

    pip install izulu

    python -m izulu.root -i


Bring OOP into exception/error management
-----------------------------------------

*For details see* **"Tutorial"** *and* **"Specification"** *sections below.*


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

Stop manually manage error messages all over the codebase!

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

    class AmountValidationError(ValidationError):
        __template__ = "Data is invalid: {reason} ({amount})"
        amount: int


    try:
        validate(data)
    except ValidationError as e:
        if e.amount < 0:
            raise BadRequestError(fields="amount")
        raise


Annotated instance attributes automatically populated from ``kwargs``.


Neat #3: Static and dynamic defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


::

    class AmountValidationError(ValidationError):
        __template__ = "Data is invalid: {reason} ({amount}; MAX={_MAX}) at {ts}"
        _MAX: ClassVar[int] = 1000
        amount: int
        reason: int = "amount is too large"
        ts: datetime = factory(datetime.datetime.now)


    print(AmountValidationError(amount=15000))
    # Data is invalid: amount is too large (15000; MAX=1000) at 2024-01-13 22:59:25.132699

    print(AmountValidationError(amount=-1, reason="amount can't be negative"))
    # Data is invalid: amount can't be negative (-1; MAX=1000) at 2024-01-13 22:59:54.482577


Tutorial: step by step guide
----------------------------

1. imports
^^^^^^^^^^

::

    import datetime

    from izulu import root


2. define your first basic exception class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    class MyError(root.Error):
        __template__ = "Having count={count} for owner={owner}"


    print(MyError(count=10, owner="me"))
    # MyError: Having count=10 for owner=me

    MyError(10, owner="me")
    # TypeError: __init__() takes 1 positional argument but 2 were given


* subclass ``Error``
* provide special message template for each of your exceptions
* use **only kwargs** to instantiate exception
  *(no more message copying across the codebase)*


3. attribute your exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    class MyError(root.Error):
        __template__ = "Having count={count} for owner={owner}"
        count: int
        timestamp: datetime.datetime

    e = MyError(count=10, owner="me", timestamp=datetime.datetime.utcnow())

    print(e.count)
    # 10
    print(e.timestamp)
    # 2023-09-27 18:18:22.957925

    e.owner
    # AttributeError: 'MyError' object has no attribute 'owner'


#. define annotations for fields you want to publish as exception instance attributes
#. you have to define desired template fields in annotations too
   (see ``AttributeError`` for ``owner``)
#. you can provide annotation for attributes not included in template (see ``timestamp``)
#. **type hinting from annotations are not enforced or checked** (see ``timestamp``)


4. provide desired defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    class MyError(root.Error):
        __template__ = "Having count={count} for owner={owner}"
        count: int
        owner: str = "nobody"
        timestamp: datetime.datetime = root.factory(datetime.datetime.utcnow)

    e = MyError(count=10)

    print(e.count)
    # 10
    print(e.owner)
    # nobody
    print(e.timestamp)
    # 2023-09-27 18:19:37.252577


* define *default static values* after field annotation just as usual
* for *dynamic defaults* use provided ``factory`` tool with your callable - it would be
  evaluated without arguments during exception instantiation
* now fields would receive values from *kwargs* if present - otherwise from *defaults*


5. *(we need to go deeper)* define "composite" defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    class MyError(root.Error):
        __template__ = "Having count={count} for owner={owner}"

        def __make_duration(self) -> datetime.timedelta:
            return self.timestamp - self.begin

        count: int
        begin: datetime.datetime
        owner: str = "nobody"
        timestamp: datetime.datetime = root.factory(datetime.datetime.utcnow)
        duration: datetime.timedelta = root.factory(__make_duration, self=True)


    begin = datetime.datetime.fromordinal(datetime.date.today().toordinal())
    e = MyError(count=10, begin=begin)

    print(e.begin)
    # 2023-09-27 00:00:00
    print(e.duration)
    # 18:45:44.502490
    print(e.timestamp)
    # 2023-09-27 18:45:44.502490


alternate syntax without method
"""""""""""""""""""""""""""""""

::

    def _make_duration(self) -> datetime.timedelta:
        return self.timestamp - self.begin

    class MyError(root.Error):
        __template__ = "Having count={count} for owner={owner}"

        count: int
        begin: datetime.datetime
        owner: str = "nobody"
        timestamp: datetime.datetime = root.factory(datetime.datetime.utcnow)
        duration: datetime.timedelta = root.factory(_make_duration, self=True)


    begin = datetime.datetime.fromordinal(datetime.date.today().toordinal())
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


Specification
-------------

``izulu`` bases on class definitions to provide handy instance creation.


The 5 pillars
^^^^^^^^^^^^^

* ``__template__`` class attribute defines the template for target error message

  * template may contain *"fields"* for substitution from ``kwargs`` and *"defaults"*

* ``__features__`` class attribute defines constraints and behaviour (see "Features" section below)

  * by default all constraints are enabled

* *"class hints"* annotated with ``ClassVar`` are noted by ``izulu``

  * annotated class attributes with values may be used within ``__template__``
    (we name these attributes as *"class defaults"*)
  * default values can only be static
  * annotated class attributes without values (just annotations) affects ``FORBID_KWARG_CONSTS`` feature (see below)

* *"instance hints"* regularly annotated (not with ``ClassVar``) are noted by ``izulu``

  * all annotated attributes (*"instance attributes"*) will become instance attributes from ``kwargs`` data (like ``ts`` in example above)
  * annotated attributes with default values may be used as *"fields"* within ``__template__``
    (we name these attributes as *"instance defaults"*)
  * annotated attributes may have **static and dynamic** defaults values
  * dynamic defaults are callables wrapped with ``factory`` helper;
    there are 2 modes depending on the value of the ``self`` flag:

    * ``self=False`` (default): provide callable not accepting arguments
    * ``self=True``: provide callable accepting single argument (error instance)

* ``kwargs`` — the new and main way to form exceptions/error instance

  * forget about creating exception instances from message strings
  * now ``__init__()`` accepts only ``kwargs``
  * *"fields"* and *"instance attributes"* are populated through ``kwargs`` (shared input for templating attribution)


**WARNING**: types from type hints are not validated or enforced


Features
^^^^^^^^

The ``izulu`` error class behaviour is controlled by ``__features__`` class attribute.

Features are represented as flag enum ``Features`` with following options:

* ``FORBID_MISSING_FIELDS``: checks provided ``kwargs`` contain data for all template *"fields"*
  and *"instance attributes"* that have no *"defaults"*

  * always should be enabled (provides consistent and detailed ``TypeError`` exceptions for appropriate arguments)
  * if disabled raw exceptions from izulu machinery internals could appear

* ``FORBID_UNDECLARED_FIELDS``: forbids undefined arguments in provided ``kwargs``
  (names not present in template *"fields"* and *"instance/class hints"*)

  * if disabled allows and **completely ignores** unknown data in ``kwargs``

* ``FORBID_KWARG_CONSTS``: checks provided ``kwargs`` not to contain attributes defined as ``ClassVar``

  * if enabled allows data in ``kwargs`` to overlap class attributes during template formatting
  * overlapping data won't modify class attribute values


Rules
^^^^^

* inherit from ``izulu.root.Error``
* behavior is defined on class-level
* **optionally** change the behaviour with ``__features__``
* ``__init__()`` accepts only ``kwargs``
* provide template with ``__template__``

  * *"fields"* defined in ``__template__`` require these data in ``kwargs``
  * *"fields"* may refer class and instance *"defaults"* — you can omit them in ``kwargs`` or not (override defaults)

* final message is formatted from ``__template__`` with

  * ``kwargs`` (overlap any *"default"*)
  * *"instance defaults"*
  * *"class defaults"*

* *"class defaults"* can be provided regularly with ``ClassVar`` type hints and static values
* (annotated with instance type hints) *"instance attributes"* will be populated from relevant ``kwargs``
* static *"instance defaults"* can be provided regularly with instance type hints and static values
* dynamic *"instance defaults"* can be provided with type hints and callable value wrapped in ``factory`` helper

  * ``self=False`` (default): callable accepting no arguments
  * ``self=True``: provide callable accepting single argument (error instance)

* exceptions you should expect with default feature set enabled:

  * ``TypeError``: constraint and argument issues
  * ``ValueError``: template formatting issue

* types from type hints are not validated or enforced
* *"defaults"* don't have to be ``__template__`` *"fields"*

  * there can be hints for attributes not present in error message template
  * and vice versa — there can be *"fields"* not present as instance attributes

* formatting for ``__template__`` works with new style formatting:

  * ``help(str.format)``
  * https://pyformat.info/
  * https://docs.python.org/3/library/string.html#formatspec


Additional API
--------------


String API (representations)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    class AmountValidationError(Error):
        __template__ = "Data is invalid: {reason} ({amount}; MAX={_MAX}) at {ts}"
        _MAX: ClassVar[int] = 1000
        amount: int
        reason: int = "amount is too large"
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



Dump API
^^^^^^^^

* ``.as_kwargs()`` dumps shallow copy of original kwargs::

    err.as_kwargs()
    # {'amount': 15000}

* ``.as_dict()`` combines original kwargs and all *"instance attribute"* values into
  *"full state"* (note: this dumped state is a shallow copy of errors data)::

    err.as_dict()
    # {'amount': 15000, 'ts': datetime.datetime(2024, 1, 13, 23, 33, 13, 847586), 'reason': 'amount is too large'}


Advanced
^^^^^^^^

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
