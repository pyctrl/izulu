from __future__ import annotations

import contextlib
import types
import typing as t
try:
    import typing_extensions as t_ext
except ImportError:
    t_ext: types.ModuleType = t  # type: ignore[no-redef]

from izulu import _types as _t
from izulu import _utils

_MISSING = object()


class FatalMixin:
    """Mark exception as non-recoverable.

    Should be directly inherited. You can't inherit from fatal exception.
    Fatal exceptions are by-passed by ``ReraisingMixin`` tools.
    """

    def __init_subclass__(cls, **kwargs: t.Any) -> None:  # noqa: ANN401
        if FatalMixin not in cls.__bases__:
            raise TypeError("Fatal can't be indirectly inherited")
        super().__init_subclass__(**kwargs)


class ReraisingMixin:
    """

    Rules...

    ``__reraising__`` values and meaning:
      - ``False``: bypass original exception; no remapping
      - ``True``: force and always
    __reraising__ = tuple()
    __reraising__ = tuple((Exception, t.Self))
    """
    __reraising__: _t.RERAISING = False

    __handlers: t.Union[bool, tuple[_utils.ReraiseHandler, ...]]

    def __init_subclass__(cls, **kwargs: t.Any) -> None:  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        rules = cls.__dict__.get("__reraising__", False)
        cls.__handlers = rules
        if not isinstance(cls.__handlers, bool):
            rules = t.cast(_t.RULES, rules)
            cls.__handlers = tuple(_utils.ReraiseHandler(*r) for r in rules)

    @classmethod
    def remap(
        cls,
        exc: Exception,
        reraising: t.Optional[_t.RERAISING] = None,
        remap_kwargs: t.Optional[_t.KWARGS] = None,
        or_original: bool = False,
    ) -> t.Union[Exception, None]:
        """Return remapped exception instance.

        Remapping rules:

        1. if the result of remapping is to leave the original exception
           method will return

           a. ``None`` for ``or_original=False``,
           b. original exception for ``or_original=True``.

        2. early-return rule works first to abort remapping process for:

           a. exception with ``FatalMixin``,
           b. descendant exceptions for used class.

        3. Default behaviour is not to remap exception.

        4. Rules: ...

        Args:
            exc:
                original exception to be remapped
            reraising:
                manual overriding reraising rules
            remap_kwargs:
                provide kwargs for reraise exception
            or_original:
                if ``True`` return original exception instead of ``None``

        Returns:
            ...
        """

        kls = t.cast(_t.EXC_CLS, cls)

        reraising_ = cls.__handlers
        if reraising is not None:
            reraising_ = _utils.ReraiseHandler.factory(reraising)

        if (
            isinstance(exc, cls)
            # or not reraising_
            or reraising_ is None
            or reraising_ is False
            or FatalMixin in exc.__class__.__bases__
        ):
            return exc if or_original else None

        remap_kwargs = remap_kwargs or {}

        # greedy remapping (any occurred exception)
        if reraising_ is True:
            return kls(**(remap_kwargs))

        for handler in reraising_:
            # match, handler
            if not isinstance(exc, handler.match):
                continue

            e = handler(kls, exc, remap_kwargs)
            if e is None:
                break

            return e

        return exc if or_original else None

    @classmethod
    @contextlib.contextmanager
    def reraise(
        cls,
        reraising: t.Optional[_t.RERAISING] = None,
        remap_kwargs: t.Optional[_t.KWARGS] = None,
    ) -> t.Generator[None, None, None]:
        """Context Manager & Decorator to raise class exception over original.

        Args:
            reraising: manual overriding reraising rules
            remap_kwargs: provide kwargs for reraise exception

        Returns:
            reraising context manager
        """

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


def skip(match: _t.EXC_CLS) -> _t.RULES:
    """Make rule to bypass matched exceptions."""
    return ((match, None),)


def catch(
    match: _t.EXC_CLS = Exception,
    *,
    exclude: t.Optional[_t.EXC_CLS] = None,
    new: _t.ACTION = t_ext.Self,
) -> _t.RULES:
    """Make rules to bypass excluded exceptions and remap matched."""
    rule = (match, new)
    if exclude is None:
        return (rule,)
    return (exclude, None), rule


class _chain:  # noqa: N801
    def __init__(self, kls: ReraisingMixin, *klasses: ReraisingMixin) -> None:
        self._klasses = (kls, *klasses)

    def __call__(
        self,
        actor: _t.EXC_CLS,  # noqa: ARG002
        exc: Exception,
        reraising: t.Optional[_t.RERAISING] = None,
        remap_kwargs: t.Optional[_t.KWARGS] = None,
    ) -> t.Optional[Exception]:
        for kls in self._klasses:
            remapped = kls.remap(exc=exc, remap_kwargs=remap_kwargs)
            if remapped is not None:
                return remapped
        return None

    @classmethod
    def from_subtree(cls, klass: t.Type[ReraisingMixin]) -> t_ext.Self:
        it = (
            t.cast(ReraisingMixin, kls) for kls in _utils.traverse_tree(klass)
        )
        return cls(*it)

    @classmethod
    def from_names(cls, name: str, *names: str) -> t_ext.Self:
        objects = globals()
        err_klasses = []
        for name in (name, *names):  # noqa: B020,PLR1704
            kls = objects.get(name, _MISSING)
            if kls is _MISSING:
                msg = f"module '{__name__}' has no attribute '{name}'"
                raise AttributeError(msg)

            err_klasses.append(kls)

        return cls(*err_klasses)
