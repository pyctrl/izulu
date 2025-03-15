Quickstart
==========

If you haven't done so already, please take a moment to
:ref:`install <install>` the ``izulu`` before continuing.


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
