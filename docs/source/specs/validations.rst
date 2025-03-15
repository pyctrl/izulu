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
