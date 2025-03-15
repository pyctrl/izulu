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

