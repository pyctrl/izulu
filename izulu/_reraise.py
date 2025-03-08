import contextlib
import functools
import typing as t


class FatalMixin:
    pass


class ReraisingMixin:

    __reraising__: bool = False
    __reraising = []  # type: ignore[var-annotated] # TODO(d.burmistrov): rules

    @classmethod
    def __get_reraising(cls):
        return cls.__dict__.get("__reraising__", False)

    @classmethod
    def remap(
        cls,
        exc: Exception,
        kwargs: t.Optional[dict] = None,
    ) -> t.Union[Exception, None]:
        # TODO(d.burmistrov): support Fatal
        if isinstance(exc, cls):
            return None

        for match, rule in cls.__reraising:
            if not isinstance(exc, match):
                continue

            exc = rule(exc, kwargs or None)
            if exc is None:
                return None

            return exc

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

        if reraising is True:  # greedy remapping (any occurred exception)
            raise t.cast(Exception, cls(**kwargs)) from orig

        exc = cls.remap(orig, kwargs)
        if exc is None:
            raise

        raise exc from orig

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
