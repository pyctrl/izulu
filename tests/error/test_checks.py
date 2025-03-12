import pytest

from izulu import _utils
from tests import helpers as h


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(), tuple()),
        (h._make_store(fields=("name", "age")), ("name", "age")),
        (h._make_store(fields=("name", "age"),
                       inst_hints=dict(name=str, age=int)),
         ("name", "age")),
        (h._make_store(fields=("name", "age"),
                       inst_hints=dict(name=str, age=int),
                       defaults=("age",)),
         ("name",)),
        (h._make_store(fields=("name", "age", "ENTITY"),
                       inst_hints=dict(name=str, age=int),
                       defaults=("age",),
                       consts=dict(ENTITY="THING")),
         ("name",)),
        (h._make_store(fields=("name", "age"),
                       inst_hints=dict(name=str, age=int),
                       defaults=("name", "age"),
                       consts=dict(ENTITY="THING")),
         tuple()),
        (h._make_store(fields=("name", "age"),
                       inst_hints=dict(name=str, age=int),
                       defaults=("age",),
                       consts=dict(ENTITY="THING")),
         ("name",)),
        (h._make_store(fields=("name", "ENTITY"),
                       inst_hints=dict(name=str),
                       consts=dict(ENTITY="THING")),
         ("name",)),
        (h._make_store(fields=("name", "ENTITY"), consts=dict(ENTITY="THING")),
         ("name",)),
        (h._make_store(inst_hints=dict(name=str, age=int),
                       defaults=dict(age=42)),
         ("name",)),
        (h._make_store(defaults=("age",), consts=dict(ENTITY="THING")),
         ("name",)),
    )
)
def test_check_missing_fields_ok(store, kws):
    _utils.check_missing_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(fields=("name", "age")), tuple()),
        (h._make_store(fields=("name", "age")), ("age",)),
        (h._make_store(fields=("name",), inst_hints=dict(name=str, age=int)),
         ("name",)),
        (h._make_store(fields=("name", "age", "ENTITY"), defaults=("age",)),
         ("name",)),
        (h._make_store(inst_hints=dict(name=str, age=int)), ("name",)),
        (h._make_store(fields=("name", "ENTITY"),
                       inst_hints=dict(name=str),
                       consts=dict(ENTITY="THING")),
         ("ENTITY",)),
        (h._make_store(fields=("name", "ENTITY"), consts=dict(ENTITY="THING")),
         ("age",)),
    )
)
def test_check_missing_fields_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_missing_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(), tuple()),
        (h._make_store(fields=("name", "age")), ("name", "age")),
        (h._make_store(inst_hints=dict(name=str, age=int)), ("name", "age")),
        (h._make_store(const_hints=dict(name=str, age=int)), ("name", "age")),
        (h._make_store(fields=("name", "age", "ENTITY"),
                       inst_hints=dict(name=str, age=int),
                       defaults=("age",),
                       const_hints=dict(ENTITY=str)),
         ("name",)),
        (h._make_store(fields=("name",),
                       inst_hints=dict(name=str, age=int),
                       defaults=("name", "age"),
                       const_hints=dict(ENTITY=str)),
         tuple()),
    )
)
def test_check_undeclared_fields_ok(store, kws):
    _utils.check_undeclared_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(), ("entity",)),
        (h._make_store(fields=("name", "age")), ("entity",)),
        (h._make_store(inst_hints=dict(name=str, age=int)), ("entity",)),
        (h._make_store(consts=dict(name="John", age=42)), ("entity",)),
    )
)
def test_check_undeclared_fields_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_undeclared_fields(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(), tuple()),
        (h._make_store(const_hints=dict(ENTITY=str)), tuple()),
        (h._make_store(const_hints=dict(ENTITY=str)), ("name",)),
    )
)
def test_check_kwarg_consts_ok(store, kws):
    _utils.check_kwarg_consts(store, frozenset(kws))


@pytest.mark.parametrize(
    ("store", "kws"),
    (
        (h._make_store(const_hints=dict(ENTITY=str)), ("ENTITY",)),
        (h._make_store(const_hints=dict(ENTITY=str)), ("ENTITY", "name")),
    )
)
def test_check_kwarg_consts_fail(store, kws):
    with pytest.raises(TypeError):
        _utils.check_kwarg_consts(store, frozenset(kws))


@pytest.mark.parametrize(
    "store",
    (
        h._make_store(),
        h._make_store(fields=frozenset(("abc", "-", "01abc"))),
    )
)
def test_check_non_named_fields_ok(store):
    _utils.check_non_named_fields(store)


@pytest.mark.parametrize(
    "store",
    (
        h._make_store(fields=frozenset(("",))),
        h._make_store(fields=frozenset((1,))),
        h._make_store(fields=frozenset((0,))),
    )
)
def test_check_non_named_fields_fail(store):
    with pytest.raises(ValueError):
        _utils.check_non_named_fields(store)
