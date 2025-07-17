import contextlib


@contextlib.contextmanager
def suppress(*excs: Exception):
    excs = excs or Exception
    try:
        yield
    except excs as e:
        LOG.error("Error suppressed: %s", e)
