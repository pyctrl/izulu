import datetime
import types
import typing as t
from unittest import mock

import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    ("kls", "fields", "hints", "registered", "defaults", "consts"),
    [
        (
            errors.RootError,
            frozenset(),
            types.MappingProxyType({}),
            frozenset(),
            frozenset(),
            types.MappingProxyType({}),
        ),
        (
            errors.TemplateOnlyError,
            frozenset(("name", "age")),
            types.MappingProxyType({}),
            frozenset(("name", "age")),
            frozenset(),
            types.MappingProxyType({}),
        ),
        (
            errors.AttributesOnlyError,
            frozenset(),
            types.MappingProxyType(dict(name=str, age=int)),
            frozenset(("name", "age")),
            frozenset(),
            types.MappingProxyType({}),
        ),
        (
            errors.AttributesWithStaticDefaultsError,
            frozenset(),
            types.MappingProxyType(dict(name=str, age=int)),
            frozenset(("name", "age")),
            frozenset(("age",)),
            types.MappingProxyType({}),
        ),
        (
            errors.AttributesWithDynamicDefaultsError,
            frozenset(),
            types.MappingProxyType(dict(name=str, age=int)),
            frozenset(("name", "age")),
            frozenset(("age",)),
            types.MappingProxyType({}),
        ),
        (
            errors.ClassVarsError,
            frozenset(),
            types.MappingProxyType({}),
            frozenset(),
            frozenset(),
            types.MappingProxyType(dict(name="Username", age=42)),
        ),
        (
            errors.MixedError,
            frozenset(("name", "age", "note")),
            types.MappingProxyType(
                dict(
                    name=str, age=int, timestamp=datetime.datetime, my_type=str
                )
            ),
            frozenset(("name", "age", "note", "timestamp", "my_type")),
            frozenset(("age", "timestamp", "my_type")),
            types.MappingProxyType(dict(entity="The Entity")),
        ),
        (
            errors.DerivedError,
            frozenset(("name", "surname", "age", "note")),
            types.MappingProxyType(
                dict(
                    name=str,
                    age=int,
                    timestamp=datetime.datetime,
                    my_type=str,
                    surname=str,
                    location=t.Tuple[float, float],
                    updated_at=datetime.datetime,
                    full_name=str,
                    box=dict,
                )
            ),
            frozenset(
                (
                    "name",
                    "age",
                    "note",
                    "timestamp",
                    "my_type",
                    "surname",
                    "location",
                    "updated_at",
                    "full_name",
                    "box",
                )
            ),
            frozenset(
                (
                    "age",
                    "timestamp",
                    "my_type",
                    "location",
                    "updated_at",
                    "full_name",
                )
            ),
            types.MappingProxyType(dict(entity="The Entity")),
        ),
    ],
)
def test_cls_store(kls, fields, hints, registered, defaults, consts):
    """Validates store management from root.Error.__init_subclass__."""
    store = kls._Error__cls_store

    assert type(store.fields) is type(fields)
    assert store.fields == fields
    assert type(store.inst_hints) is type(hints)
    assert store.inst_hints == hints
    assert type(store.registered) is type(registered)
    assert store.registered == registered
    assert type(store.defaults) is type(defaults)
    assert store.defaults == defaults
    assert type(store.consts) is type(consts)
    assert store.consts == consts


@pytest.mark.parametrize(
    "features",
    [root.Features.FORBID_NON_NAMED_FIELDS, root.Features.NONE],
)
@mock.patch("izulu._utils.check_non_named_fields", return_value=0)
def test_cls_validation(mocked_check, features):
    """Validates feature checks from root.Error.__init_subclass__."""
    type("Err", (errors.ClassVarsError,), {"__features__": features})

    if features is root.Features.NONE:
        mocked_check.assert_not_called()
    else:
        mocked_check.assert_called_once()
