import contextlib
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
    undeclared = kws.difference(store.registered, store.consts)
    if undeclared:
        raise TypeError(f"Undeclared arguments: {join(undeclared)}")


def check_constants_in_kwargs(store: Store, kws: frozenset[str]) -> None:
    consts = kws.intersection(store.consts)
    if consts:
        raise TypeError(f"Constants in arguments: {join(consts)}")


def join(items: t.Iterable[str], symbol: str = ",") -> str:
    return f"{symbol} ".join(items)


def join_kwargs(**kwargs: t.Any) -> str:
    return join(f"{k!s}={v!r}" for k, v in kwargs.items())


def extract_fields(template: str) -> t.Generator[str, None, None]:
    parsed = string.Formatter().parse(template)
    for _, fn, _, _ in parsed:
        if fn is not None:
            yield fn


def split_hints(cls: t.Type) -> tuple[_T_HINTS, _T_HINTS]:
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


def get_defaults(cls: t.Type, attrs: t.Iterable[str]) -> dict[str, t.Any]:
    result = {}
    for attr in attrs:
        with contextlib.suppress(AttributeError):
            result[attr] = getattr(cls, attr)
    return result
