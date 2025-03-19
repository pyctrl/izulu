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
