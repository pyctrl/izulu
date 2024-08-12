import typing as t


def iterate_causes(
        e: BaseException,
        *,
        self: bool = False
) -> t.Generator[BaseException, None, None]:
    if self:
        yield e
    cause = e.__cause__
    while cause is not None:
        yield cause
        e = cause
        cause = e.__cause__
