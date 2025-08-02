from __future__ import annotations

import contextlib
import logging
import typing as t

_LOG = logging.getLogger(__name__)


class ErrorDumpDict(t.TypedDict):
    type: str
    reason: str
    fields: t.Dict[str, t.Any] | None
    details: t.Dict[t.Any, t.Any]


@contextlib.contextmanager
def suppress(
    *excs: t.Type[Exception],
    exclude: t.Optional[t.Type[Exception]] = None,
) -> t.Generator[None, None, None]:
    exc_targets = excs or Exception
    try:
        yield
    except exc_targets as e:
        if exclude and isinstance(e, exclude):
            raise
        _LOG.error("Error suppressed: %s", e)


def error_chain(exc: BaseException) -> t.Generator[BaseException, None, None]:
    """Return generator over the whole exception chain."""
    yield exc
    while exc.__cause__ is not None:
        exc = exc.__cause__
        yield exc


@t.overload
def dump(exc: BaseException, /) -> ErrorDumpDict: ...


@t.overload
def dump(
    exc: BaseException,
    /,
    *excs: BaseException,
) -> t.Tuple[ErrorDumpDict, ...]: ...


def dump(
    exc: BaseException,
    /,
    *excs: BaseException,
) -> t.Union[ErrorDumpDict, t.Tuple[ErrorDumpDict, ...]]:
    """Return single or tuple of dict representations."""
    fields = None
    if hasattr(exc, "_Error__cls_store"):
        fields = exc.as_dict(wide=True)  # type: ignore[attr-defined]

    dumped: ErrorDumpDict = dict(
        type=exc.__class__.__name__,
        reason=str(exc),
        fields=fields,
        details={},
    )

    if excs:
        return dumped, *(dump(e) for e in excs)

    return dumped
