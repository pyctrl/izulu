from __future__ import annotations

import contextlib
import functools
import typing as t

_T_KWARGS = dict[str, t.Any]
_T_FACTORY = t.Callable[
    [t.Type[Exception], Exception, _T_KWARGS],
    t.Optional[Exception],
]
_T_ACTION = t.Union[None, str, t.Type[Exception], _T_FACTORY]
_T_COMPILED_ACTION = t.Callable[[Exception, _T_KWARGS], t.Optional[Exception]]

_MISSING = object()


# TODO(d.burmistrov): chains

# TODO(d.burmistrov): support WTF case
class FatalMixin:
    pass


class ReraisingMixin:

    __reraising__: t.Union[
        bool,
        t.Tuple[t.Tuple[t.Type[Exception], _T_ACTION], ...],
    ] = False

    __reraising: t.Union[
        bool,
        t.Tuple[t.Tuple[t.Type[Exception], _T_COMPILED_ACTION], ...],
    ]

    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        rules = cls.__dict__.get("__reraising__", False)
        cls.__reraising = rules
        if isinstance(rules, tuple):
            cls.__reraising = tuple(
                (exc_type, cls._compile_action(action))
                for exc_type, action in rules
            )

    @classmethod
    def _compile_action(cls, action: _T_ACTION) -> _T_COMPILED_ACTION:
        if action is None:

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                return None

        elif (
            action is getattr(t, "Self", _MISSING)
            or action == cls.__qualname__
        ):

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                kls = t.cast(t.Type[Exception], cls)
                return kls(**kwargs)

        elif isinstance(action, str):

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                action_ = getattr(cls, t.cast(str, action))
                return action_(orig, kwargs)

        elif isinstance(action, type) and issubclass(action, Exception):

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                return t.cast(t.Type[Exception], action)(**kwargs)

        elif callable(action):

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
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
        kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Union[Exception, None]:
        # TODO(d.burmistrov): support Fatal
        if isinstance(exc, cls):
            return None
        # TODO(d.burmistrov): duplicated code
        if not cls.__reraising:
            return None
        kwargs = kwargs or {}
        if cls.__reraising is True:
            kls = t.cast(t.Type[Exception], cls)
            return kls(**kwargs)

        reraising = t.cast(
            t.Tuple[t.Tuple[t.Type[Exception], _T_COMPILED_ACTION], ...],
            cls.__reraising
        )
        for match, rule in reraising:
            if not isinstance(exc, match):
                continue

            e = rule(exc, kwargs)
            if e is None:
                return None

            return e

        return None

    @classmethod
    @contextlib.contextmanager
    def reraise(
            cls,
            kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Generator[None, None, None]:
        if not cls.__reraising:
            yield
            return

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

        kwargs = kwargs or {}

        # greedy remapping (any occurred exception)
        if cls.__reraising is True:
            raise t.cast(Exception, cls(**kwargs)) from orig

        exc = cls.remap(orig, kwargs)
        if exc is None:
            raise

        raise exc from orig

    @classmethod
    def rewrap(cls, kwargs: t.Optional[_T_KWARGS] = None) -> t.Callable:
        _kwargs = kwargs

        def decorator(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                with cls.reraise(kwargs=_kwargs):
                    return func(*args, **kwargs)
            return wrapped

        return decorator
