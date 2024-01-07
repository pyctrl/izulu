izulu
=====

*"An exceptional library"*


Installing
----------

::

   pip install izulu


Features
--------

**The main and global one is to bring more OOP into error and exception
management (for details see "walkthrough" below).**

::

    class MyError(root.Error):
        __template__ = "{smth} has happened at {ts}"
        ts: root.factory(datetime.now)


#. instead of manual error message formatting (and copying it all over
   the codebase) provide only ``kwargs``:

   - before: ``raise MyError(f"{smth} has happened at {datetime.now()}")``
   - **after:** ``raise MyError(smth=smth)``

   Just provide ``__template__`` class attribute with your error message
   template string. New style formatting is used:

   - ``str.format()``
   - https://pyformat.info/
   - https://docs.python.org/3/library/string.html#formatspec

#. you can attach default values to error types (even dynamic defaults):
   this is why ``datetime.now()`` was omitted above

#. out-of-box validation for provided ``kwargs``
   (individually enable/disable checks with ``__features__`` attribute)

#. Automatic ``kwargs`` conversion into error instance attributes
   if such kwarg is present in type hints
   (for example above ``ts`` would be an attribute and ``smth`` won't)


Walkthrough: step by step guide
-------------------------------

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


Additional options
------------------

Controlling behaviour with ``__features__``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default ``Error`` does some validations controlled by flag enum ``Features``.

* FORBID_MISSING_FIELDS: checks provided ``kwargs`` to contain all fields from template
  and all type hinted attributes (excluding fields with default values)
* FORBID_UNDECLARED_FIELDS: forbids undefined arguments in provided ``kwargs``
  (names not present in template of type hints)


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
   # Having count=10 for owner=me
   print(repr(e))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))
   print(e.as_str())  # just another pretty human-readable representation
   # 'Having count=42 for owner=somebody'


* there are different results for ``str`` and ``repr``
* ``str`` is for humans and nice clear look
* and ``repr`` could allow you to reconstruct the same exception instance
  (if data provided into *kwargs* supports ``repr`` the same way)


**Reconstruct exception from** ``repr``:

::

   e2 = eval(repr(e))
   print(repr(e))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))
   print(repr(e2))
   # MyError(count=10, owner='me', timestamp=datetime.datetime(2023, 9, 27, 18, 58, 0, 340218))


Other ``Error`` API
^^^^^^^^^^^^^^^^^^^

::

   e.as_kwargs()  # original kwargs
   # {'count': 42, 'owner': 'somebody', 'timestamp': datetime.datetime(2023, 9, 17, 19, 50, 31, 7578)}
   e.as_dict()  # shallow
   # {'count': 42, 'owner': 'somebody', 'timestamp': datetime.datetime(2023, 9, 17, 19, 50, 31, 7578)}


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

Running tests
^^^^^^^^^^^^^

::

   tox


Building package
^^^^^^^^^^^^^^^^

::

   tox -e build


Contributing
------------

Contact me through `Issues <https://gitlab.com/pyctrl/izulu/-/issues>`__.


Versioning
----------

We use `SemVer <http://semver.org/>`__ for versioning. For the versions
available, see the `tags on this repository <https://gitlab.com/pyctrl/izulu/-/tags>`__.


Authors
-------

-  **Dima Burmistrov** - *Initial work* -
   `pyctrl <https://gitlab.com/pyctrl/>`__

*Special thanks to* `Eugene Frolov <https://github.com/phantomii/>`__ *for inspiration.*


License
-------

This project is licensed under the MIT/X11 License - see the
`LICENSE <https://gitlab.com/pyctrl/izulu/-/blob/main/LICENSE>`__ file for details
