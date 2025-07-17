import contextlib
import logging
import typing as t

_LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress(*excs: t.Type[Exception]) -> t.Generator[None, None, None]:
    exc_targets = excs or Exception
    try:
        yield
    except exc_targets as e:
        _LOG.error("Error suppressed: %s", e)
