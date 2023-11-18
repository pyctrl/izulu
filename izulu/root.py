import copy
import enum
import functools
import types
import typing as t

from izulu import _utils


class Features(enum.Flag):
    FORBID_MISSING_FIELDS = enum.auto()
    FORBID_UNDECLARED_FIELDS = enum.auto()
    FORBID_WRONG_TYPES = enum.auto()

    DEFAULT = FORBID_MISSING_FIELDS | FORBID_UNDECLARED_FIELDS
    ALL = DEFAULT | FORBID_WRONG_TYPES
    NONE = 0


class Error(Exception):
    __template__: t.ClassVar[str] = "Unspecified error"
    __features__: t.ClassVar[Features] = Features.DEFAULT

    __cls_store: t.ClassVar[_utils.Store]

    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        fields = frozenset(_utils.extract_fields(cls.__template__))
        hints = types.MappingProxyType(dict(_utils.filter_hints(cls)))
        defaults = frozenset(attr for attr in hints if hasattr(cls, attr))
        cls.__cls_store = _utils.Store(fields=fields,
                                       hints=hints,
                                       registered=fields.union(hints),
                                       defaults=defaults)

    def __init__(self, **kwargs: t.Any) -> None:
        self.__kwargs = kwargs.copy()
        self.__process_features()
        self.__populate_attrs()
        data = self.as_dict()
        message = self._process_user(store=self.__cls_store,
                                     kwargs=kwargs,
                                     message=self.__process_template(data))
        super().__init__(message)

    def __process_features(self):
        store = self.__cls_store
        kws = frozenset(self.__kwargs)

        if Features.FORBID_MISSING_FIELDS in self.__features__:
            if missing := (store.registered - store.defaults - kws):
                msg = f"Missing arguments: {_utils.join(missing)}"
                raise TypeError(msg)  # ? exc type

        if Features.FORBID_UNDECLARED_FIELDS in self.__features__:
            if undeclared := (kws - store.registered):
                msg = f"Undeclared arguments: {_utils.join(undeclared)}"
                raise TypeError(msg)  # ? exc type

        if Features.FORBID_WRONG_TYPES in self.__features__:
            errors = []
            for k, v in self.__kwargs.items():
                type_ = store.hints[k]
                if not isinstance(v, type_):
                    errors.append((k, type_, type(v)))
            if errors:
                tpl = "field '{}' must be '{}' but is '{}'"
                chunks = (tpl.format(*err) for err in errors)
                msg = "Unexpected types: " + _utils.join(chunks, ";")
                raise TypeError(msg)  # ? exc type

    def __populate_attrs(self):
        for k, v in self.__kwargs.items():
            if k in self.__cls_store.hints:
                setattr(self, k, v)

    def __process_template(self, data) -> str:
        try:
            return self.__template__.format(**data)
        except Exception as e:  # ?
            msg = ("Failed to format template with provided kwargs: "
                   + _utils.join_kwargs(**self.__kwargs))
            raise ValueError(msg) from e

    def _process_user(self,
                      store: _utils.Store,
                      kwargs: dict[str, t.Any],
                      message: str) -> str:
        return message

    def __repr__(self) -> str:
        kwargs = _utils.join_kwargs(**self.as_dict())
        return f"{self.__class__.__name__}({kwargs})"

    def __copy__(self):
        return type(self)(**self.as_dict())

    def __deepcopy__(self, memo):
        if self not in memo:
            kwargs = {k: copy.deepcopy(v) for k, v in self.as_dict()}
            memo[self] = type(self)(**kwargs)
        return memo[self]

    def __reduce__(self):
        parent = list(super().__reduce__())
        parent[1] = tuple()
        return tuple(parent)

    def as_str(self) -> str:
        return f"{self.__class__.__name__}: {self}"

    def as_kwargs(self) -> dict[str, t.Any]:
        return self.__kwargs.copy()

    def as_dict(self) -> dict[str, t.Any]:
        d = self.__kwargs.copy()
        for field in self.__cls_store.defaults:
            d.setdefault(field, getattr(self, field))
        return d


def factory(func, self: bool = False) -> functools.cached_property:
    target = func if self else (lambda obj: func())
    return functools.cached_property(target)
