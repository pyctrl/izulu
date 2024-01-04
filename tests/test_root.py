import datetime
import types
from unittest import mock
import uuid

import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    ("kls", "fields", "hints", "registered", "defaults"),
    (
            (
                    root.Error,
                    frozenset(),
                    types.MappingProxyType({}),
                    frozenset(),
                    frozenset(),
            ),
            (
                    errors.TemplateOnlyError,
                    frozenset(("name", "age")),
                    types.MappingProxyType({}),
                    frozenset(("name", "age")),
                    frozenset(),
            ),
            (
                    errors.AttributesOnlyError,
                    frozenset(),
                    types.MappingProxyType(dict(name=str, age=int)),
                    frozenset(("name", "age")),
                    frozenset(),
            ),
            (
                    errors.AttributesWithStaticDefaultsError,
                    frozenset(),
                    types.MappingProxyType(dict(name=str, age=int)),
                    frozenset(("name", "age")),
                    frozenset(("age",)),
            ),
            (
                    errors.AttributesWithDynamicDefaultsError,
                    frozenset(),
                    types.MappingProxyType(dict(name=str, age=int)),
                    frozenset(("name", "age")),
                    frozenset(("age",)),
            ),
            (
                    errors.ClassVarsError,
                    frozenset(),
                    types.MappingProxyType({}),
                    frozenset(),
                    frozenset(),
            ),
            (
                    errors.MixedError,
                    frozenset(("name", "age", "note")),
                    types.MappingProxyType(dict(name=str,
                                                age=int,
                                                timestamp=datetime.datetime,
                                                my_type=str)),
                    frozenset(("name", "age", "note", "timestamp", "my_type")),
                    frozenset(("age", "timestamp", "my_type")),
            ),
            (
                    errors.DerivedError,
                    frozenset(("name", "surname", "age", "note")),
                    types.MappingProxyType(dict(name=str,
                                                age=int,
                                                timestamp=datetime.datetime,
                                                my_type=str,
                                                surname=str,
                                                location=tuple[float, float],
                                                updated_at=datetime.datetime,
                                                full_name=str)),
                    frozenset(("name",
                               "age",
                               "note",
                               "timestamp",
                               "my_type",
                               "surname",
                               "location",
                               "updated_at",
                               "full_name")),
                    frozenset(("age",
                               "timestamp",
                               "my_type",
                               "location",
                               "updated_at",
                               "full_name")),
            ),
    )
)
def test_class_stores(kls, fields, hints, registered, defaults):
    store = getattr(kls, "_Error__cls_store")

    assert type(store.fields) is type(fields)
    assert store.fields == fields
    assert type(store.hints) is type(hints)
    assert store.hints == hints
    assert type(store.registered) is type(registered)
    assert store.registered == registered
    assert type(store.defaults) is type(defaults)
    assert store.defaults == defaults


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (root.Error(), "izulu.root.Error()"),
            (errors.Exc(name="John", age=10),
             "tests.errors.Exc(name='John', age=10)"),
    )
)
def test_repr(err, expected):
    assert repr(err) == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (root.Error(), "Error: Unspecified error"),
            (errors.Exc(name="John", age=10), "Exc: The John is 10 years old"),
    )
)
def test_as_str(err, expected):
    assert err.as_str() == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (root.Error(), dict()),
            (errors.Exc(name="John", age=10), dict(name="John", age=10)),
    )
)
def test_as_kwargs(err, expected):
    assert err.as_kwargs() == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (root.Error(), dict()),
            (errors.Exc(name="John", age=10), dict(name="John", age=10)),
    )
)
def test_as_dict(err, expected):
    assert err.as_dict() == expected


@pytest.mark.parametrize("flag", (True, False))
def test_factory(flag):
    expected = uuid.uuid4()
    m = mock.Mock(return_value=expected)
    attr = root.factory(m, self=flag)
    k = type("Klass", tuple(), {"attr_with_self": attr})()
    call_args = (k,)

    result = k.attr_with_self

    assert result is expected
    m.assert_called_once_with(*call_args[:flag])
