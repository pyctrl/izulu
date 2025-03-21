from __future__ import annotations

import contextlib
import functools
import logging
import typing as t

from izulu import _utils

_IMPORT_ERROR_TEXTS = (
    "",
    "You have early version of Python.",
    "  Extra compatibility dependency required.",
    "  Please add 'izulu[compatibility]' to your project dependencies.",
    "",
    "Pip: `pip install izulu[compatibility]",
)


if hasattr(t, "dataclass_transform"):
    t_ext = t
else:
    try:
        import typing_extensions as t_ext  # type: ignore [no-redef]
    except ImportError:
        for message in _IMPORT_ERROR_TEXTS:
            logging.error(message)  # noqa: LOG015,TRY400
        raise

_T_KWARGS = t.Dict[str, t.Any]
_T_EXC_CLASS_OR_TUPLE = t.Union[
    t.Type[Exception],
    t.Tuple[t.Type[Exception], ...],
]
_T_FACTORY = t.Callable[
    [t.Type[Exception], Exception, _T_KWARGS],
    t.Optional[Exception],
]
_T_ACTION = t.Union[str, t.Type[Exception], _T_FACTORY, None]
_T_RULES = t.Union[
    bool,
    t.Tuple[t.Tuple[_T_EXC_CLASS_OR_TUPLE, _T_ACTION], ...],  # tup, chain?
]
_T_RERAISING = t.Union[
    None,
    bool,
    t.Tuple[t.Tuple[_T_EXC_CLASS_OR_TUPLE, _T_ACTION], ...],  # tup, chain?
]
_T_COMPILED_ACTION = t.Callable[[Exception, _T_KWARGS], t.Optional[Exception]]
_T_COMPILED_RULES = t.Union[
    bool,
    t.Tuple[t.Tuple[_T_EXC_CLASS_OR_TUPLE, _T_COMPILED_ACTION], ...],
]

_MISSING = object()

DecParam = t_ext.ParamSpec("DecParam")
DecReturnType = t.TypeVar("DecReturnType")


class FatalMixin:
    def __init_subclass__(cls, **kwargs: t.Any) -> None:  # noqa: ANN401
        if FatalMixin not in cls.__bases__:
            raise TypeError("Fatal can't be indirectly inherited")
        super().__init_subclass__(**kwargs)


class ReraisingMixin:
    __reraising__: _T_RULES = False

    __reraising: _T_COMPILED_RULES

    def __init_subclass__(cls, **kwargs: t.Any) -> None:  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        rules = cls.__dict__.get("__reraising__", False)
        cls.__reraising = cls.__compile_rules(rules)

    @classmethod
    def __compile_rules(cls, rules: _T_RULES) -> _T_COMPILED_RULES:
        if isinstance(rules, bool):
            return rules

        return tuple(
            (exc_type, cls.__compile_action(action))
            for exc_type, action in rules
        )

    @classmethod
    def __compile_action(  # noqa: C901
        cls,
        action: _T_ACTION,
    ) -> _T_COMPILED_ACTION:
        if action is None:

            def compiled_action(
                orig: Exception,  # noqa: ARG001
                kwargs: _T_KWARGS,  # noqa: ARG001
            ) -> t.Optional[Exception]:
                return None

        elif (
            action is getattr(t, "Self", _MISSING)
            or action == cls.__qualname__
        ):

            def compiled_action(
                orig: Exception,  # noqa: ARG001
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                kls = t.cast(t.Type[Exception], cls)
                return kls(**kwargs)

        elif isinstance(action, str):

            def compiled_action(
                orig: Exception,
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                action_ = t.cast(
                    t.Callable[[Exception, _T_KWARGS], t.Optional[Exception]],
                    getattr(cls, action),
                )
                return action_(orig, kwargs)

        elif isinstance(action, type) and issubclass(action, Exception):

            def compiled_action(
                orig: Exception,  # noqa: ARG001
                kwargs: _T_KWARGS,
            ) -> t.Optional[Exception]:
                return action(**kwargs)

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
        reraising: _T_RERAISING = None,
        remap_kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Union[Exception, None]:
        if reraising is None:
            reraising_ = cls.__reraising
        else:
            reraising_ = cls.__compile_rules(reraising)

        if (
            isinstance(exc, cls)
            or not reraising_
            or FatalMixin in exc.__class__.__bases__
        ):
            return None

        remap_kwargs = remap_kwargs or {}

        # greedy remapping (any occurred exception)
        if reraising_ is True:
            kls = t.cast(t.Type[Exception], cls)
            return kls(**remap_kwargs)

        reraising__ = t.cast(
            t.Tuple[t.Tuple[_T_EXC_CLASS_OR_TUPLE, _T_COMPILED_ACTION], ...],
            reraising_,
        )

        for match, rule in reraising__:
            if not isinstance(exc, match):
                continue

            e = rule(exc, remap_kwargs)
            if e is None:
                return None

            return e

        return None

    @classmethod
    @contextlib.contextmanager
    def reraise(
        cls,
        reraising: _T_RERAISING = None,
        remap_kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Generator[None, None, None]:
        try:
            yield
        except Exception as e:
            orig = e
        else:
            return

        exc = cls.remap(
            exc=orig,
            reraising=reraising,
            remap_kwargs=remap_kwargs,
        )
        if exc is None:
            raise

        raise exc from orig

    @classmethod
    def rewrap(
        cls,
        reraising: _T_RERAISING = None,
        remap_kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Callable[
        [t.Callable[DecParam, DecReturnType]],
        t.Callable[DecParam, DecReturnType],
    ]:
        def decorator(
            func: t.Callable[DecParam, DecReturnType],
        ) -> t.Callable[DecParam, DecReturnType]:
            @functools.wraps(func)
            def wrapped(
                *args: DecParam.args,
                **kwargs: DecParam.kwargs,
            ) -> DecReturnType:
                with cls.reraise(
                    reraising=reraising,
                    remap_kwargs=remap_kwargs,
                ):
                    return func(*args, **kwargs)

            return wrapped

        return decorator


class chain:  # noqa: N801
    def __init__(self, kls: ReraisingMixin, *klasses: ReraisingMixin) -> None:
        self._klasses = (kls, *klasses)

    def __call__(
        self,
        actor: t.Type[Exception],  # noqa: ARG002
        exc: Exception,
        reraising: _T_RERAISING = None,
        remap_kwargs: t.Optional[_T_KWARGS] = None,
    ) -> t.Optional[Exception]:
        for kls in self._klasses:
            remapped = kls.remap(exc=exc, remap_kwargs=remap_kwargs)
            if remapped is not None:
                return remapped
        return None

    @classmethod
    def from_subtree(cls, klass: t.Type[ReraisingMixin]) -> "chain":
        it = (
            t.cast(ReraisingMixin, kls) for kls in _utils.traverse_tree(klass)
        )
        return cls(*it)

    @classmethod
    def from_names(cls, name: str, *names: str) -> "chain":
        objects = globals()
        err_klasses = []
        for name in (name, *names):  # noqa: B020,PLR1704
            kls = objects.get(name, _MISSING)
            if kls is _MISSING:
                msg = f"module '{__name__}' has no attribute '{name}'"
                raise AttributeError(msg)

            err_klasses.append(kls)

        return cls(*err_klasses)
