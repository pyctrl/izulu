import types

from izulu import _utils


def _make_store_kwargs(
    fields=None,
    const_hints=None,
    inst_hints=None,
    consts=None,
    defaults=None,
) -> dict:
    return dict(
        fields=frozenset(fields or tuple()),
        const_hints=types.MappingProxyType(const_hints or dict()),
        inst_hints=types.MappingProxyType(inst_hints or dict()),
        consts=types.MappingProxyType(consts or dict()),
        defaults=frozenset(defaults or tuple()),
    )


def _make_store(
    fields=None,
    const_hints=None,
    inst_hints=None,
    consts=None,
    defaults=None,
) -> _utils.Store:
    return _utils.Store(
        **_make_store_kwargs(
            fields=fields,
            inst_hints=inst_hints,
            const_hints=const_hints,
            consts=consts,
            defaults=defaults,
        )
    )
