from __future__ import annotations

import _string  # type: ignore[import-not-found]
import dataclasses
import logging
import string
import types
import typing as t

from izulu import _types as _t

_IMPORT_ERROR_TEXT = (
    "",
    "You have early version of Python.",
    "  Extra compatibility dependency required.",
    "  Please add 'izulu[compatibility]' to your project dependencies.",
    "",
    "Pip: `pip install izulu[compatibility]`",
)


def log_import_error() -> None:
    for message in _IMPORT_ERROR_TEXT:
        logging.error(message)  # noqa: LOG015,TRY400


if hasattr(t, "dataclass_transform"):
    t_ext = t
else:
    try:
        import typing_extensions as t_ext  # type: ignore[no-redef]
    except ImportError:
        log_import_error()
        raise

_IZULU_ATTRS = {
    "__template__",
    "__toggles__",
    "_Error__cls_store",
    "__reraising__",
    "_ReraisingMixin__reraising",
}
_FORMATTER = string.Formatter()


# TODO(d.burmistrov): dataclass options
@dataclasses.dataclass
class Store:
    fields: t.FrozenSet[str]
    """Template fields."""

    const_hints: types.MappingProxyType[str, type]
    """Mapping attribute names to their hints with ``ClassVar`` mark."""

    inst_hints: types.MappingProxyType[str, type]
    """Mapping attribute names to their hints without ``ClassVar`` mark."""

    props: t.FrozenSet[str]
    """Property attribute names."""

    consts: types.MappingProxyType[str, t.Any]
    """Mapping ``ClassVar``/``Final`` attribute names to their values."""

    defaults: t.FrozenSet[str]
    """Mapping attribute names to their values without ``ClassVar`` mark."""

    registered: t.FrozenSet[str] = dataclasses.field(init=False)
    """Attribute names that already have values."""

    valued: t.FrozenSet[str] = dataclasses.field(init=False)
    """Attribute names that already have values."""

    def __post_init__(self) -> None:
        self.registered = self.fields.union(self.inst_hints)
        self.valued = self.props.union(self.consts, self.defaults)


def check_missing_fields(store: Store, kws: t.FrozenSet[str]) -> None:
    """Raise on ..."""
    missing = store.registered.difference(kws)
    if missing:
        raise TypeError(f"Missing arguments: {join_items(missing)}")


def check_undeclared_fields(store: Store, kws: t.FrozenSet[str]) -> None:
    """Raise on ..."""
    undeclared = kws.difference(store.registered, store.const_hints)
    if undeclared:
        raise TypeError(f"Undeclared arguments: {join_items(undeclared)}")


def check_kwarg_consts(store: Store, kws: t.FrozenSet[str]) -> None:
    consts = kws.intersection(store.const_hints)
    if consts:
        raise TypeError(f"Constants in arguments: {join_items(consts)}")


def check_non_named_fields(store: Store) -> None:
    for field in store.fields:
        if isinstance(field, int):
            msg = f"Field names can't be digits: {field}"
            raise ValueError(msg)  # noqa: TRY004
        if not field:
            raise ValueError("Field names can't be empty")


def check_unannotated_fields(store: Store) -> None:
    unannotated = (
        store.fields
        - set(store.const_hints)
        - set(store.props)
        - set(store.inst_hints)
    )
    if unannotated:
        msg = f"Fields must be annotated: {join_items(unannotated)}"
        raise ValueError(msg)


def join_items(items: t.Iterable[str]) -> str:
    return ", ".join(map("'{}'".format, items))


def join_kwargs(**kwargs: t.Any) -> str:  # noqa: ANN401
    return ", ".join(f"{k!s}={v!r}" for k, v in kwargs.items())


def format_template(template: str, kwargs: t.Dict[str, t.Any]) -> str:
    try:
        return template.format_map(kwargs)
    except Exception as e:
        msg_part = "Failed to format template with provided kwargs: "
        raise ValueError(msg_part + join_kwargs(**kwargs)) from e


def iter_fields(template: str) -> t.Generator[str, None, None]:
    """Extract fields from the template."""

    # https://docs.python.org/3/library/string.html#format-string-syntax
    for _, fn, _, _ in _FORMATTER.parse(template):
        if fn is not None:
            yield _string.formatter_field_name_split(fn)[0]


# TODO(d.burmistrov): t.Final? t.Literal?
def split_cls_hints(
    cls: type,
) -> t.Tuple[t.Dict[str, type], t.Dict[str, type]]:
    """Split class annotations into class and non-class hints.

    The criterion is based on presence or absence
    of ``ClassVar``/``Final`` marks.
    """
    const_hints: t.Dict[str, type] = {}
    inst_hints: t.Dict[str, type] = {}

    for k, v in t.get_type_hints(cls).items():
        if k in _IZULU_ATTRS:
            continue

        hint = t.get_origin(v)
        if hint is t.ClassVar:
            const_hints[k] = v
        elif hint is t.Final:
            const_hints[k] = v
        else:
            inst_hints[k] = v

    return const_hints, inst_hints


def get_cls_prop_names(cls: type) -> frozenset[str]:
    return frozenset(
        field
        for field, value in vars(cls).items()
        if isinstance(value, property)
    )


def get_cls_defaults(
    cls: type,
    attrs: t.Iterable[str],
) -> t.Dict[str, t.Any]:
    """Create a mapping for attributes that have values."""
    return {attr: getattr(cls, attr) for attr in attrs if hasattr(cls, attr)}


def traverse_tree(cls: type) -> t.Generator[type, None, None]:
    workload = cls.__subclasses__()
    discovered = []
    while workload:
        item = workload.pop()
        discovered.append(item)
        workload.extend(item.__subclasses__())
    yield from discovered


class ReraiseHandler:
    def __init__(self, match: _t.EXC_MATCH, action: _t.ACTION) -> None:
        self.match = match
        self._orig = action

        if action is None:
            self._handler = self.__action_is_none
        elif action is t_ext.Self:
            self._handler = self.__action_is_self
        elif isinstance(action, type) and issubclass(action, Exception):
            self._handler = self.__action_is_exc_cls
        elif callable(action):
            self._handler = self.__action_is_user_fn
        else:
            raise ValueError(f"Unsupported action: {action}")

    def __call__(
        self,
        handler_cls: _t.EXC_CLS,
        exc: Exception,
        map_kwargs: _t.KWARGS,
    ) -> _t.MAYBE_EXC:
        return self._handler(handler_cls, exc, map_kwargs)

    def __action_is_none(
        self,
        handler_cls: _t.EXC_CLS,
        exc: Exception,
        map_kwargs: _t.KWARGS,
    ) -> _t.MAYBE_EXC:
        return None

    def __action_is_self(
        self,
        handler_cls: _t.EXC_CLS,
        exc: Exception,
        map_kwargs: _t.KWARGS,
    ) -> _t.MAYBE_EXC:
        return handler_cls(**map_kwargs)

    def __action_is_exc_cls(
        self,
        handler_cls: _t.EXC_CLS,
        exc: Exception,
        map_kwargs: _t.KWARGS,
    ) -> _t.MAYBE_EXC:
        exc_cls = t.cast(_t.EXC_CLS, self._orig)
        return exc_cls(**map_kwargs)

    def __action_is_user_fn(
        self,
        handler_cls: _t.EXC_CLS,
        exc: Exception,
        map_kwargs: _t.KWARGS,
    ) -> _t.MAYBE_EXC:
        fn = t.cast(_t.USER_FN, self._orig)
        return fn(handler_cls, exc, map_kwargs)

    @classmethod
    def factory(
        cls,
        reraising: _t.RERAISING,
    ) -> t.Union[bool, tuple[t_ext.Self, ...]]:
        if isinstance(reraising, bool):
            return reraising

        return tuple(cls(*r) for r in reraising)
