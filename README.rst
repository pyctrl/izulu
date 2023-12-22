izulu
=====

*"An exceptional library"*


Features
--------

First one is to bring more OOP into exception management (see *walkthrough* below).


Installing
----------

::

   pip install izulu


Walkthrough: step by step guide
-------------------------------

1. imports :)
^^^^^^^^^^^^^

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


* subclass ``Error`` or ``LaxError``
* provide special message template for each of your exceptions
* use only **kwargs** to instantiate exception
  *(no more message copying around the codebase)*


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


* define annotations for fields you want to publish as exception instance attributes
* you have to define desired template fields in annotations too
  (see ``AttributeError`` for ``owner``)
* you can provide annotation for attributes not included in template (see ``timestamp``)
* **type hinting from annotations are not enforced or checked** (see ``timestamp``)


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


Difference between ``Error`` and ``LaxError``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Error`` is a strict - it forbids you to provide undefined *kwargs*.

And ``LaxError`` is tolerant to undefined *kwargs* - it mainly ignores them
(only stores as kwargs).


::

   class MyQuietError(root.LaxError):
       __template__ = "Having count={count} for owner={owner}"


   class MyLoudError(root.Error):
       __template__ = "Having count={count} for owner={owner}"


   print(MyQuietError(count=10, owner="me", undefined_field="you don't know me"))
   # MyQuietError: Having count=10 for owner=me

   print(MyLoudError(count=10, owner="me", undefined_field="you don't know me"))
   # TypeError: Undeclared arguments: undefined_field


**Attribute "undefined_field" won't apper**


String representations
^^^^^^^^^^^^^^^^^^^^^^

::

   class MyError(root.Error):
       __template__ = "Having count={count} for owner={owner}"
       count: int
       owner: str = "nobody"
       timestamp: datetime.datetime = root.factory(datetime.datetime.utcnow)

   e = MyError(count=10, owner="me")

   print(str(e))
   # MyError: Having count=10 for owner=me
   print(repr(e))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))


* there are different results for ``str`` and ``repr``
* ``str`` is for humans and nice clear look
* and ``repr`` could allow you to reconstruct the same exception instance
  (if data provided into *kwargs* supports ``repr`` the same way)


Reconstruct exception from ``repr``:

::

   e2 = eval(repr(e))
   print(repr(e))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))
   print(repr(e2))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))


Other ``Error`` API
^^^^^^^^^^^^^^^^^^^

::

   ### flag (differs for Error/LaxError)
   e.is_strict()
   # True

   ### getters
   e.get_message()
   # 'Having count=42 for owner=somebody'
   e.get_kwargs()
   # {'count': 42, 'owner': 'somebody', 'timestamp': datetime.datetime(2023, 9, 17, 19, 50, 31, 7578)}


For developers
--------------

Running tests
^^^^^^^^^^^^^

::

   tox


Contributing
------------

Contact me through `Issues <https://gitlab.com/pyctrl/izulu/-/issues>`__.


Versioning
----------

We use `SemVer <http://semver.org/>`__ for versioning. For the versions
available, see the `tags on this
repository <https://gitlab.com/pyctrl/izulu/-/tags>`__.


Authors
-------

-  **Dima Burmistrov** - *Initial work* -
   `pyctrl <https://gitlab.com/pyctrl/>`__

*Special thanks to* `Eugene Frolov <https://github.com/phantomii/>`__ *for inspiration.*


License
-------

This project is licensed under the MIT/X11 License - see the
`LICENSE <https://gitlab.com/pyctrl/izulu/-/blob/main/LICENSE>`__ file for details