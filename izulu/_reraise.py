import contextlib
import functools
import typing as t


class FatalMixin:
    pass


class ReraisingMixin:

    __reraising__: bool = False

    @classmethod
    def __get_reraising(cls):
        return cls.__dict__.get("__reraising__", False)

    @classmethod
    def remap(cls, e: Exception):
        return None

    @classmethod
    @contextlib.contextmanager
    def reraise(
            cls,
            kwargs: t.Optional[dict] = None,
    ) -> t.Generator[None, None, None]:
        kwargs = kwargs or {}
        reraising = cls.__get_reraising()

        try:
            yield
        except cls:  # type: ignore[misc]
            raise
        except Exception as e:
            orig = e
        else:
            return

        # TODO(d.burmistrov): how does it work?
        if isinstance(orig, cls.__bases__) and FatalMixin in cls.__bases__:
            raise

        if reraising is True:  # greedy remapping: remap all
            raise t.cast(Exception, cls(**kwargs)) from orig

        raise

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
