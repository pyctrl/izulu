import datetime
import types

import pytest

from izulu import _utils
from tests import errors

count = 42
owner = "somebody"
dt = datetime.datetime.utcnow()


def _make_store_kwargs(fields=None, inst_hints=None,
                       consts=None, defaults=None):
    return dict(
        fields=frozenset(fields or tuple()),
        inst_hints=types.MappingProxyType(inst_hints or dict()),
        consts=types.MappingProxyType(consts or dict()),
        defaults=frozenset(defaults or tuple()),
    )


def _make_store(fields=None, inst_hints=None, consts=None, defaults=None):
    return _utils.Store(
        **_make_store_kwargs(fields=fields,
                             inst_hints=inst_hints,
                             consts=consts,
                             defaults=defaults)
    )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    (
        (_make_store_kwargs(),
         frozenset()),
        (_make_store_kwargs(fields=("field_1", "field_2")),
         frozenset(("field_1", "field_2"))),
        (_make_store_kwargs(inst_hints=dict(field_2=2, field_3=3)),
         frozenset(("field_2", "field_3"))),
        (_make_store_kwargs(fields=("field_1", "field_2"),
                            inst_hints=dict(field_2=2, field_3=3)),
         frozenset(("field_1", "field_2", "field_3"))),
        (_make_store_kwargs(fields=("field_1", "field_2"),
                            inst_hints=dict(field_1=1, field_2=2)),
         frozenset(("field_1", "field_2"))),
    )
)
def test_store_post_init(kwargs, expected):
    assert _utils.Store(**kwargs).registered == expected


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(), tuple()),
        (_make_store(fields=("name", "age")), ("name", "age")),
        (_make_store(fields=("name", "age"),
                     inst_hints=dict(name=str, age=int)),
         ("name", "age")),
        (_make_store(fields=("name", "age"),
                     inst_hints=dict(name=str, age=int),
                     defaults=("age",)),
         ("name",)),
        (_make_store(fields=("name", "age", "ENTITY"),
                     inst_hints=dict(name=str, age=int),
                     defaults=("age",),
                     consts=dict(ENTITY="THING")),
         ("name",)),
        (_make_store(fields=("name", "age"),
                     inst_hints=dict(name=str, age=int),
                     defaults=("name", "age"),
                     consts=dict(ENTITY="THING")),
         tuple()),
        (_make_store(fields=("name", "age"),
                     inst_hints=dict(name=str, age=int),
                     defaults=("age",),
                     consts=dict(ENTITY="THING")),
         ("name",)),
        (_make_store(fields=("name", "ENTITY"),
                     inst_hints=dict(name=str),
                     consts=dict(ENTITY="THING")),
         ("name",)),
        (_make_store(fields=("name", "ENTITY"), consts=dict(ENTITY="THING")),
         ("name",)),
        (_make_store(inst_hints=dict(name=str, age=int),
                     defaults=dict(age=42)),
         ("name",)),
        (_make_store(defaults=("age",), consts=dict(ENTITY="THING")),
         ("name",)),
    )
)
def test_check_missing_fields_ok(store, kws):
    _utils.check_missing_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(fields=("a", "b")), tuple()),
        (_make_store(fields=("name", "age")), ("age",)),
        (_make_store(fields=("name",), inst_hints=dict(name=str, age=int)),
         ("name",)),
        (_make_store(fields=("name", "age", "ENTITY"), defaults=("age",)),
         ("name",)),
        (_make_store(inst_hints=dict(name=str, age=int)), ("name",)),
        (_make_store(fields=("name", "ENTITY"),
                     inst_hints=dict(name=str),
                     consts=dict(ENTITY="THING")),
         ("ENTITY",)),
        (_make_store(fields=("name", "ENTITY"), consts=dict(ENTITY="THING")),
         ("age",)),
    )
)
def test_check_missing_fields_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_missing_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(), tuple()),
        (_make_store(fields=("name", "age")), ("name", "age")),
        (_make_store(inst_hints=dict(name=str, age=int)), ("name", "age")),
        (_make_store(consts=dict(name="John", age=42)), ("name", "age")),
        (_make_store(fields=("name", "age", "ENTITY"),
                     inst_hints=dict(name=str, age=int),
                     defaults=("age",),
                     consts=dict(ENTITY="THING")),
         ("name",)),
        (_make_store(fields=("name",),
                     inst_hints=dict(name=str, age=int),
                     defaults=("name", "age"),
                     consts=dict(ENTITY="THING")),
         tuple()),
    )
)
def test_check_undeclared_fields_ok(store, kws):
    _utils.check_undeclared_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(), ("entity",)),
        (_make_store(fields=("name", "age")), ("entity",)),
        (_make_store(inst_hints=dict(name=str, age=int)), ("entity",)),
        (_make_store(consts=dict(name="John", age=42)), ("entity",)),
    )
)
def test_check_undeclared_fields_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_undeclared_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(), tuple()),
        (_make_store(consts=dict(ENTITY="Thing")), tuple()),
        (_make_store(consts=dict(ENTITY="Thing")), ("name",)),
    )
)
def test_check_kwarg_consts_ok(store, kws):
    _utils.check_kwarg_consts(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (_make_store(consts=dict(ENTITY="Thing")), ("ENTITY",)),
        (_make_store(consts=dict(ENTITY="Thing")), ("ENTITY", "name")),
    )
)
def test_check_kwarg_consts_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_kwarg_consts(store, frozenset(kws))


@pytest.mark.parametrize(
    ("args", "expected"),
    (
        ((tuple(),), ""),
        ((("item_1",),), "item_1"),
        ((("item_1", "item_2", "item_3"),), "item_1, item_2, item_3"),
        ((tuple(), ","), ""),
        ((("item_1",), ","), "item_1"),
        ((("item_1", "item_2", "item_3"), ","), "item_1, item_2, item_3"),
        ((tuple(), ";"), ""),
        ((("item_1",), ";"), "item_1"),
        ((("item_1", "item_2", "item_3"), ";"), "item_1; item_2; item_3"),
    )
)
def test_join(args, expected):
    assert _utils.join(*args) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    (
        (dict(), ""),
        (dict(a=42), "a=42"),
        (dict(owner=owner, count=count, timestamp=dt),
         f"{owner=!r}, {count=!r}, timestamp={dt!r}"),
        (dict(timestamp=dt), f"timestamp={dt!r}")
    )
)
def test_join_kwargs(data, expected):
    assert _utils.join_kwargs(**data) == expected


@pytest.mark.parametrize(
    ("tpl", "expected"),
    (
        ("Having boring message here", tuple()),
        ("Hello {you}!", ("you",)),
        ("Hello {you}! How are you, {you}", ("you", "you")),
        ("{owner}: Having count={count} for owner={owner}",
         ("owner", "count", "owner"))
    )
)
def test_extract_fields(tpl, expected):
    assert tuple(_utils.extract_fields(tpl)) == expected


@pytest.mark.parametrize(
    ("kls", "attrs", "expected"),
    (
        (errors.DerivedError, (), dict()),
        (errors.DerivedError, ("entity",), dict(entity="The Entity")),
        (errors.DerivedError,
         ("name", "surname", "age", "timestamp", "my_type", "location",
          "updated_at", "full_name", "box"),
         dict(age=0, location=(50.3, 3.608),
              timestamp=errors.DerivedError.timestamp,
              updated_at=errors.DerivedError.updated_at,
              full_name=errors.DerivedError.full_name,
              my_type=errors.DerivedError.my_type)),
        (errors.RootError, ("entity",), dict()),
        (errors.TemplateOnlyError, ("name",), dict()),
    )
)
def test_get_defaults(kls, attrs, expected):
    assert _utils.get_cls_defaults(kls, attrs) == expected
