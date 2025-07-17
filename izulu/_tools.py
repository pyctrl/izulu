import contextlib
import logging
import typing as t

_LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress(*excs: Exception) -> t.Generator[None, None, None]:
    excs = excs or Exception
    try:
        yield
    except excs as e:
        _LOG.error("Error suppressed: %s", e)  # noqa: TRY400
