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

    def _override_message(
        self,
        store: _utils.Store,  # noqa: ARG002
        kwargs: t.Dict[str, t.Any],  # noqa: ARG002
        msg: str,
    ) -> str:
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

