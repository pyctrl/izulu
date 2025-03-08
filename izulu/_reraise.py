from __future__ import annotations

import contextlib
import functools
import typing as t

_T_FACTORY = t.Callable[
    [t.Type[Exception], Exception, dict],
    t.Optional[Exception],
]
_T_ACTION = t.Union[None, str, t.Type[Exception], _T_FACTORY]

_MISSING = object()


class FatalMixin:
    pass


class ReraisingMixin:

    __reraising: t.Tuple[t.Tuple[t.Type[Exception], t.Callable], ...]

    __reraising__: t.Union[
        bool,
        t.Tuple[t.Tuple[t.Type[Exception], _T_ACTION], ...],
    ] = False

    @classmethod
    def __get_reraising(cls):
        return cls.__dict__.get("__reraising__", False)

    @classmethod
    def _compile_action(
            cls,
            action: _T_ACTION,
    ) -> t.Callable[[Exception, dict], t.Optional[Exception]]:
        if action is None:

            def compiled_action(
                orig: Exception,
                kwargs: dict[str, t.Any],
            ) -> t.Optional[Exception]:
                return None

        elif (
            action is getattr(t, "Self", _MISSING)
            or action == cls.__qualname__
        ):

            def compiled_action(
                orig: Exception,
                kwargs: dict[str, t.Any],
            ) -> t.Optional[Exception]:
                kls = t.cast(t.Type[Exception], cls)
                return kls(**kwargs)

        elif isinstance(action, str):

            def compiled_action(
                orig: Exception,
                kwargs: dict[str, t.Any],
            ) -> t.Optional[Exception]:
                action_ = getattr(cls, t.cast(str, action))
                return action_(orig, kwargs)

        elif isinstance(action, type) and issubclass(action, Exception):

            def compiled_action(
                orig: Exception,
                kwargs: dict[str, t.Any],
            ) -> t.Optional[Exception]:
                return t.cast(t.Type[Exception], action)(**kwargs)

        elif callable(action):

            def compiled_action(
                orig: Exception,
                kwargs: dict[str, t.Any],
            ) -> t.Optional[Exception]:
                kls = t.cast(t.Type[Exception], cls)
                return t.cast(_T_FACTORY, action)(kls, orig, kwargs)

        else:
            raise ValueError(f"Unsupported action: {action}")

        return compiled_action

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
