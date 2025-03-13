from __future__ import annotations

import copy
import enum
import functools
import logging
import types
import typing as t

from izulu import _utils
from izulu import causes

_IMPORT_ERROR_TEXTS = (
    "",
    "You have early version of Python.",
    "  Extra compatibility dependency required.",
    "  Please add 'izulu[compatibility]' to your project dependencies.",
    "",
    "Pip: `pip install izulu[compatibility]",
)


if hasattr(t, "dataclass_transform"):
    t_ext = t
else:
    try:
        import typing_extensions as t_ext  # type: ignore [no-redef]
    except ImportError:
        for message in _IMPORT_ERROR_TEXTS:
            logging.error(message)
        raise

FactoryReturnType = t.TypeVar("FactoryReturnType")

_HOOK_RENAMED_MSG = (
    "<_hook> method name is deprecated - use <_override_message>"
)


@t.overload
def factory(
    func: t.Callable[[], FactoryReturnType],
    *,
    self: t.Literal[False] = False,
) -> FactoryReturnType: ...


@t.overload
def factory(
    func: t.Callable[[Error], FactoryReturnType],
    *,
    self: t.Literal[True],
) -> FactoryReturnType: ...


def factory(func: t.Callable, *, self: bool = False):
    """Attaches factory for dynamic default values

    :param func: callable factory receiving 0 or 1 argument (see `self` param)
    :param bool self: controls callable factory argument
        if `True` func will receive single argument of error instance
        otherwise func will be invoced without argument
    """

    target = func if self else (lambda obj: func())
    target = t.cast(
        t.Callable[[t.Any], t.Any],
        target,
    )  # type: ignore [assignment]
    return functools.cached_property(target)


class Features(enum.Flag):
    FORBID_MISSING_FIELDS = enum.auto()
    FORBID_UNDECLARED_FIELDS = enum.auto()
    FORBID_KWARG_CONSTS = enum.auto()
    FORBID_NON_NAMED_FIELDS = enum.auto()

    NONE = 0
    DEFAULT = (
            FORBID_MISSING_FIELDS
            | FORBID_UNDECLARED_FIELDS
            | FORBID_KWARG_CONSTS
            | FORBID_NON_NAMED_FIELDS
    )


class Error(Exception):
    """Base class for your exception trees

    Example:

        class MyError(root.Error):
            __template__ = "{smth} has happened at {ts}"
            ts: root.factory(datetime.now)

    Provides 4 main features:

      * instead of manual error message formatting (and copying it all over
        the codebase) provide just `kwargs`:
        - before: `raise MyError(f"{smth} has happened at {datetime.now()}")`
        - after: `raise MyError(smth=smth)`

        Just provide `__template__` class attribute with your error message
        template string. New style formatting is used:
        - `str.format()`
        - https://pyformat.info/
        - https://docs.python.org/3/library/string.html#formatspec

      * Automatic `kwargs` conversion into error instance attributes
        if such kwarg is present in type hints
        (for example above `ts` would be an attribute and `smth` won't)

      * you can attach static and dynamic default values:
        this is why `datetime.now()` was omitted above

      * out-of-box validation for provided `kwargs`
        (individually enable/disable checks with `__features__` attribute)
    """

    __template__: t.ClassVar[str] = "Unspecified error"
    __features__: t.ClassVar[Features] = Features.DEFAULT

    __cls_store: t.ClassVar[_utils.Store] = _utils.Store(
        fields=frozenset(),
        const_hints=types.MappingProxyType(dict()),
        inst_hints=types.MappingProxyType(dict()),
        consts=types.MappingProxyType(dict()),
        defaults=frozenset(),
    )

    iter_causes = causes.iterate_causes

    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        fields = frozenset(_utils.iter_fields(cls.__template__))
        const_hints, inst_hints = _utils.split_cls_hints(cls)
        consts = _utils.get_cls_defaults(cls, const_hints)
        defaults = _utils.get_cls_defaults(cls, inst_hints)
        cls.__cls_store = _utils.Store(
            fields=fields,
            const_hints=types.MappingProxyType(const_hints),
            inst_hints=types.MappingProxyType(inst_hints),
            consts=types.MappingProxyType(consts),
            defaults=frozenset(defaults),
        )
        if Features.FORBID_NON_NAMED_FIELDS in cls.__features__:
            _utils.check_non_named_fields(cls.__cls_store)

    def __init__(self, **kwargs: t.Any) -> None:
        self.__kwargs = kwargs.copy()
        self.__process_features()
        self.__populate_attrs()
        msg = self.__process_template(self.as_dict())
        msg = self._override_message(self.__cls_store, kwargs, msg)
        super().__init__(msg)

    def __process_features(self) -> None:
        """Trigger features"""

        store = self.__cls_store
        kws = frozenset(self.__kwargs)

        if Features.FORBID_MISSING_FIELDS in self.__features__:
            _utils.check_missing_fields(store, kws)

        if Features.FORBID_UNDECLARED_FIELDS in self.__features__:
            _utils.check_undeclared_fields(store, kws)

        if Features.FORBID_KWARG_CONSTS in self.__features__:
            _utils.check_kwarg_consts(store, kws)

    def __populate_attrs(self) -> None:
        """Set hinted kwargs as exception attributes"""

        for k, v in self.__kwargs.items():
            if k in self.__cls_store.inst_hints:
                setattr(self, k, v)

    def __process_template(self, data: dict[str, t.Any]) -> str:
        """Format the error template from provided data (kwargs & defaults)"""

        kwargs = self.__cls_store.consts.copy()
        kwargs.update(data)
        return _utils.format_template(self.__template__, kwargs)

    def _override_message(
        self,
        store: _utils.Store,
        kwargs: dict[str, t.Any],
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

    def _hook(self, *args, **kwargs):
        logging.warning(_HOOK_RENAMED_MSG)
        return self._override_message(*args, **kwargs)

    def __repr__(self) -> str:
        kwargs = _utils.join_kwargs(**self.as_dict())
        return f"{self.__module__}.{self.__class__.__qualname__}({kwargs})"

    def __copy__(self):
        return type(self)(**self.as_dict())

    def __deepcopy__(self, memo: dict[int, t.Any]):
        _id = id(self)
        if _id not in memo:
            kwargs = {k: copy.deepcopy(v, memo)
                      for k, v in self.as_dict().items()}
            memo[_id] = type(self)(**kwargs)
        return memo[_id]

    def __reduce__(self) -> tuple[t.Any, ...]:
        return functools.partial(self.__class__, **self.as_dict()), tuple()

    def as_str(self) -> str:
        """Represent error as exception type with message"""

        return f"{self.__class__.__qualname__}: {self}"

    def as_kwargs(self) -> dict[str, t.Any]:
        """Return the copy of original kwargs used to initialize the error"""

        return self.__kwargs.copy()

    def as_dict(self, wide: bool = False) -> dict[str, t.Any]:
        """Represent error as dict of fields including default values

        By default, only *instance* data and defaults are provided.

        :param bool wide: if `True` *class* defaults will be included in result
        """

        d = self.__kwargs.copy()
        for field in self.__cls_store.defaults:
            d.setdefault(field, getattr(self, field))
        if wide:
            for field, const in self.__cls_store.consts.items():
                d.setdefault(field, const)
        return d


@t_ext.dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=True,
    frozen_default=False,
    field_specifiers=(factory,),
)
class DataclassHintedError(Error):
    pass
