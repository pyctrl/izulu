import dataclasses
import string
import types
import typing as t


def join(items: t.Iterable[str], symbol: str = ",") -> str:
    return f"{symbol} ".join(items)


def join_kwargs(**kwargs: t.Any) -> str:
    return join(f"{k!s}={v!r}" for k, v in kwargs.items())


def extract_fields(template: str) -> t.Generator[str, None, None]:
    parsed = string.Formatter().parse(template)
    for _, fn, _, _ in parsed:
        if fn is not None:
            yield fn


def filter_hints(cls: t.Type) -> t.Generator[tuple[str, t.Type], None, None]:
    for k, v in t.get_type_hints(cls).items():
        if t.get_origin(v) is not t.ClassVar:
            yield k, v


# TODO(d.burmistrov): dataclass options
@dataclasses.dataclass
class Store:
    fields: frozenset[str]
    hints: types.MappingProxyType[str, t.Type]
    registered: frozenset[str]
    defaults: frozenset[str]
