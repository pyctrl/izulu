izulu
#####

.. image:: https://repository-images.githubusercontent.com/766241795/85494614-5974-4b26-bfec-03b8e393c7f0?width=128
   :width: 128px

|

    *"The exceptional library"*

|


**Installation**

.. include:: docs/source/user/install.rst
   :start-line: 5


Presenting ``izulu``
********************

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


.. include:: docs/source/specs/pillars.rst
   :start-line: 3

.. include:: docs/source/specs/mechanics.rst

Features
========

.. include:: docs/source/specs/toggles.rst
   :start-line: 3


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


.. include:: docs/source/specs/additional.rst

Tips
****

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
