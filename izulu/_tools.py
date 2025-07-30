import contextlib
import logging
import typing as t

_LOG = logging.getLogger(__name__)


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
