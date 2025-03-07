import contextlib
import functools
import typing as t


class ReraiseForbiddenError(Exception):
    pass


class FatalMixin:
    pass


class ReraisingMixin:

    __reraising__: t.Optional[bool] = None
    # NOTE(d.burmistrov):
    #   - None - proxy-pass any exception (do not reraise/rewrap)
    #   - True - greedy (rewrap any with self)
    #   - False - forbidden (forbid rewrap operations for current class)
    #   (always local for current class - inheritance is ignored)

    @classmethod
    def __get_conf(cls):
        conf = cls.__dict__.get("__reraising__")
        if conf or conf is None:
            return conf
        raise ReraiseForbiddenError

    @classmethod
    @contextlib.contextmanager
    def reraise(
            cls,
            kwargs: t.Optional[dict] = None,
    ) -> t.Generator[None, None, None]:
        conf = cls.__get_conf()

        if not conf:
            yield
            return

        kwargs = kwargs or {}
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

        raise cls(**kwargs) from orig  # type: ignore[misc]

    @classmethod
    def rewrap(cls, kwargs: t.Optional[dict] = None) -> t.Callable:
        cls.__get_conf()
        _kwargs = kwargs

        def decorator(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                with cls.reraise(kwargs=_kwargs):
                    return func(*args, **kwargs)
            return wrapped

        return decorator
