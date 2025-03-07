import contextlib
import functools
import typing as t


class FatalMixin:
    pass


class ReraisingMixin(Exception):

    @classmethod
    @contextlib.contextmanager
    def reraise(
            cls,
            kwargs: t.Optional[dict] = None,
    ) -> t.Generator[None, None, None]:
        kwargs = kwargs or {}

        try:
            yield
        except cls:  # type: ignore[misc]
            raise
        except Exception as e:
            orig = e
        else:
            return

        if isinstance(orig.__class__, cls):
            raise

        # TODO(d.burmistrov): how does it work?
        if isinstance(orig, cls.__bases__) and FatalMixin in cls.__bases__:
            raise

        raise cls(**kwargs) from orig

    @classmethod
    def rewrap(cls, kwargs: t.Optional[dict] = None) -> t.Callable:
        _kwargs = kwargs

        def decorator(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                with cls.reraise(kwargs=_kwargs):
                    return func(*args, **kwargs)
            return wrapped

        return decorator
