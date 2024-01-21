from __future__ import annotations

import dataclasses
import string
import types
import typing as t


_T_HINTS = dict[str, t.Type]

_IZULU_ATTRS = {"__template__", "__features__", "_Error__cls_store"}


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
        raise TypeError(f"Missing arguments: {join(missing)}")


def check_undeclared_fields(store: Store, kws: frozenset[str]) -> None:
    undeclared = kws.difference(store.registered, store.const_hints)
    if undeclared:
        raise TypeError(f"Undeclared arguments: {join(undeclared)}")


def check_kwarg_consts(store: Store, kws: frozenset[str]) -> None:
    consts = kws.intersection(store.const_hints)
    if consts:
        raise TypeError(f"Constants in arguments: {join(consts)}")


def join(items: t.Iterable[str], symbol: str = ",") -> str:
    return f"{symbol} ".join(items)


def join_kwargs(**kwargs: t.Any) -> str:
    return join(f"{k!s}={v!r}" for k, v in kwargs.items())


def format_template(template: str, kwargs: dict[str, t.Any]):
    try:
        return template.format(**kwargs)
    except Exception as e:
        msg_part = "Failed to format template with provided kwargs: "
        raise ValueError(msg_part + join_kwargs(**kwargs)) from e


def extract_fields(template: str) -> t.Generator[str, None, None]:
    # TODO(d.burmistrov):
    #   - unit tests
    #   - README expected exception contract (ValueError here)
    #   - README: note about original exception in `e.__cause__`
    #   - pretty exception with all field not .isidentifier()

    parsed = string.Formatter().parse(template)

    for _, fn, _, _ in parsed:
        if fn is None:
            continue
        elif not fn:
            raise ValueError("Positional arguments forbidden in template")

        fields = fn.split(".")
        if not all(map(str.isidentifier, fields)):
            raise ValueError(f"Fields must be identifiers: {fn}")

        yield fields[0]


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
