from __future__ import annotations

import _string  # type: ignore[import-not-found]
import dataclasses
import string
import types
import typing as t

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
    const_hints: types.MappingProxyType[str, type]
    inst_hints: types.MappingProxyType[str, type]
    consts: types.MappingProxyType[str, t.Any]
    defaults: t.FrozenSet[str]

    registered: t.FrozenSet[str] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.registered = self.fields.union(self.inst_hints)


def check_missing_fields(store: Store, kws: t.FrozenSet[str]) -> None:
    missing = store.registered.difference(store.defaults, store.consts, kws)
    if missing:
        raise TypeError(f"Missing arguments: {join_items(missing)}")


def check_undeclared_fields(store: Store, kws: t.FrozenSet[str]) -> None:
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
    unannotated = store.fields - set(store.const_hints) - set(store.inst_hints)
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
    # https://docs.python.org/3/library/string.html#format-string-syntax
    for _, fn, _, _ in _FORMATTER.parse(template):
        if fn is not None:
            yield _string.formatter_field_name_split(fn)[0]


def split_cls_hints(
    cls: type,
) -> t.Tuple[t.Dict[str, type], t.Dict[str, type]]:
    const_hints: t.Dict[str, type] = {}
    inst_hints: t.Dict[str, type] = {}

    for k, v in t.get_type_hints(cls).items():
        if k in _IZULU_ATTRS:
            continue
        if t.get_origin(v) is t.ClassVar:
            const_hints[k] = v
        else:
            inst_hints[k] = v

    return const_hints, inst_hints


def get_cls_defaults(
    cls: type,
    attrs: t.Iterable[str],
) -> t.Dict[str, t.Any]:
    return {attr: getattr(cls, attr) for attr in attrs if hasattr(cls, attr)}


def traverse_tree(cls: type) -> t.Generator[type, None, None]:
    workload = cls.__subclasses__()
    discovered = []
    while workload:
        item = workload.pop()
        discovered.append(item)
        workload.extend(item.__subclasses__())
    yield from discovered
