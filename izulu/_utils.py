import string
import typing as t


def join(items: t.Iterable[str]) -> str:
    return ", ".join(items)


def join_kwargs(**kwargs: t.Any) -> str:
    return join(f"{k!s}={v!r}" for k, v in kwargs.items())


def extract_fields(template: str) -> tuple[str, ...]:
    parsed = string.Formatter().parse(template)
    return tuple(fn for _, fn, _, _ in parsed if fn is not None)
