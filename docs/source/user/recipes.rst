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
