import typing as t


def iterate_causes(
    exc: BaseException,
    *,
    self: bool = False,
) -> t.Generator[BaseException, None, None]:
    if self:
        yield exc
    cause = exc.__cause__
    while cause is not None:
        yield cause
        exc = cause
        cause = exc.__cause__
