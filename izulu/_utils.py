from __future__ import annotations

import _string  # type: ignore
import dataclasses
import string
import types
import typing as t

if t.TYPE_CHECKING:
    _T_HINTS = dict[str, t.Type]

_IZULU_ATTRS = {"__template__", "__features__", "_Error__cls_store"}
_FORMATTER = string.Formatter()


# TODO(d.burmistrov): dataclass options
@dataclasses.dataclass
class Store:

    fields: frozenset[str]
    const_hints: types.MappingProxyType[str, t.Type]
    inst_hints: types.MappingProxyType[str, t.Type]
    consts: types.MappingProxyType[str, t.Any]
    defaults: frozenset[str]

    registered: frozenset[str] = dataclasses.field(init=False)

    def __post_init__(self):
        self.registered = self.fields.union(self.inst_hints)


def check_missing_fields(store: Store, kws: frozenset[str]) -> None:
    missing = store.registered.difference(store.defaults, store.consts, kws)
    if missing:
        raise TypeError(f"Missing arguments: {join_items(missing)}")


def check_undeclared_fields(store: Store, kws: frozenset[str]) -> None:
    undeclared = kws.difference(store.registered, store.const_hints)
    if undeclared:
        raise TypeError(f"Undeclared arguments: {join_items(undeclared)}")


def check_kwarg_consts(store: Store, kws: frozenset[str]) -> None:
    consts = kws.intersection(store.const_hints)
    if consts:
        raise TypeError(f"Constants in arguments: {join_items(consts)}")


def check_non_named_fields(store: Store) -> None:
    for field in store.fields:
        if isinstance(field, int):
            raise ValueError(f"Field names can't be digits: {field}")
        elif not field:
            raise ValueError("Field names can't be empty")


def join_items(items: t.Iterable[str]) -> str:
    return ", ".join(map("'{}'".format, items))


def join_kwargs(**kwargs: t.Any) -> str:
    return ", ".join(f"{k!s}={v!r}" for k, v in kwargs.items())


def format_template(template: str, kwargs: dict[str, t.Any]):
    try:
        return template.format_map(kwargs)
    except Exception as e:
        msg_part = "Failed to format template with provided kwargs: "
        raise ValueError(msg_part + join_kwargs(**kwargs)) from e


def iter_fields(template: str) -> t.Generator[str, None, None]:
    # https://docs.python.org/3/library/string.html#format-string-syntax
    for _, fn, _, _ in _FORMATTER.parse(template):
        if fn is not None:
            yield _string.formatter_field_name_split(fn)[0]


def split_cls_hints(cls: t.Type) -> tuple[_T_HINTS, _T_HINTS]:
    const_hints: _T_HINTS = {}
    inst_hints: _T_HINTS = {}

    for k, v in t.get_type_hints(cls).items():
        if k in _IZULU_ATTRS:
            continue
        elif t.get_origin(v) is t.ClassVar:
            const_hints[k] = v
        else:
            inst_hints[k] = v

    return const_hints, inst_hints


def get_cls_defaults(cls: t.Type, attrs: t.Iterable[str]) -> dict[str, t.Any]:
    return {attr: getattr(cls, attr)
            for attr in attrs
            if hasattr(cls, attr)}
