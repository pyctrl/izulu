import string
import typing as t


def join(items: t.Iterable[str]) -> str:
    return ", ".join(items)


def join_kwargs(**kwargs: t.Any) -> str:
    return join(f"{k!s}={v!r}" for k, v in kwargs.items())


def extract_fields(template: str) -> t.Generator[str, None, None]:
    parsed = string.Formatter().parse(template)
    for _, fn, _, _ in parsed:
        if fn is not None:
            yield fn


def extract_hints(klass: type) -> t.Generator[str, None, None]:
    for field in t.get_type_hints(klass):
        if field is not t.ClassVar:
            yield field
