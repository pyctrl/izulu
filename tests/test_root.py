import copy
import datetime
import pickle
import types
from unittest import mock
import uuid

import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    "err",
    (
            errors.RootError(),
            errors.TemplateOnlyError(name="John", age=42),
            errors.AttributesOnlyError(name="John", age=42),
            errors.MixedError(name="John", note="..."),
            errors.DerivedError(name="John",
                                surname="Brown",
                                note="...",
                                box={}),
    ),
)
def test_pickling(err):
    dumped = pickle.dumps(err)
    resurrected = pickle.loads(dumped)

    assert err.as_dict() == resurrected.as_dict()


def test_copy():  # shallow
    ts = datetime.datetime.now()
    orig = errors.DerivedError(name="John",
                               surname="Brown",
                               note="...",
                               age=42,
                               updated_at=ts,
                               full_name="secret",
                               box=dict())

    copied = copy.copy(orig)

    assert id(copied) != id(orig)
    assert copied.as_dict() == orig.as_dict()
    assert copied.box is orig.box
    assert copied.box == orig.box == dict()

    orig.box.update(a=11)

    assert copied.box == dict(a=11)


def test_deepcopy():
    ts = datetime.datetime.now()
    orig = errors.DerivedError(name="John",
                               surname="Brown",
                               note="...",
                               age=42,
                               updated_at=ts,
                               full_name="secret",
                               box=dict())

    copied = copy.deepcopy(orig)

    assert id(copied) != id(orig)
    assert copied.as_dict() == orig.as_dict()
    assert id(copied.box) != id(orig.box)
    assert copied.box == orig.box == dict()

    orig.box.update(a=11)

    assert copied.box == dict()


@pytest.mark.parametrize(
    "kwargs",
    (
            dict(),
            dict(name="John"),
            dict(age=42),
            dict(name="John", age=42),
            dict(name="John", age=42, ts=53452345.3465),
            dict(name="John", age="Karl", ts=datetime.datetime.now()),
    ),
)
def test_templating(kwargs):
    with pytest.raises(ValueError):
        errors.ComplexTemplateOnlyError(**kwargs)


@pytest.mark.parametrize(
    ("kls", "features", "kwargs"),
    (
            (
                    errors.TemplateOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(),
            ),
            (
                    errors.TemplateOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(name="John"),
            ),
            (
                    errors.TemplateOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(age=42),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(name="John"),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_MISSING_FIELDS,
                    dict(age=42),
            ),
            (
                    errors.RootError,
                    root.Features.FORBID_UNDECLARED_FIELDS,
                    dict(field="value"),
            ),
            (
                    errors.TemplateOnlyError,
                    root.Features.FORBID_UNDECLARED_FIELDS,
                    dict(name="John", age=42, field="field"),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_UNDECLARED_FIELDS,
                    dict(name="John", age=42, field="field"),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_WRONG_TYPES,
                    dict(name=42),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_WRONG_TYPES,
                    dict(age=42.503),
            ),
            (
                    errors.AttributesOnlyError,
                    root.Features.FORBID_WRONG_TYPES,
                    dict(name="John", age="42"),
            ),
            (
                    errors.AttributesWithStaticDefaultsError,
                    root.Features.FORBID_WRONG_TYPES,
                    dict(name="John", age="42"),
            ),
    ),
)
def test_features_triggered(kls, features, kwargs):
    with pytest.raises(TypeError):
        type("TestError", (kls,), {"__features__": features})(**kwargs)


def test_feature_presets():
    default = (root.Features.FORBID_MISSING_FIELDS
               | root.Features.FORBID_UNDECLARED_FIELDS)
    alls = (root.Features.FORBID_MISSING_FIELDS
            | root.Features.FORBID_UNDECLARED_FIELDS
            | root.Features.FORBID_WRONG_TYPES)

    assert root.Features.NONE is root.Features(0)
    assert root.Features.NONE == root.Features(0)
    assert root.Features.DEFAULT is default
    assert root.Features.DEFAULT == default
    assert root.Features.ALL is alls
    assert root.Features.ALL == alls


def test_default_features():
    assert root.Error.__features__ is root.Features.DEFAULT


@mock.patch("izulu.root.Error._hook")
@mock.patch("izulu.root.Error._Error__process_template")
@mock.patch("izulu.root.Error._Error__populate_attrs")
@mock.patch("izulu.root.Error._Error__process_features")
def test_init(fake_proc_ftrs, fake_set_attrs, fake_proc_tpl, fake_hook):
    fake_proc_tpl.return_value = root.Error.__template__
    overriden_message = "overriden message"
    fake_hook.return_value = overriden_message
    store = getattr(root.Error, "_Error__cls_store")
    manager = mock.Mock()
    manager.attach_mock(fake_proc_ftrs, "fake_proc_ftrs")
    manager.attach_mock(fake_set_attrs, "fake_set_attrs")
    manager.attach_mock(fake_proc_tpl, "fake_proc_tpl")
    manager.attach_mock(fake_hook, "fake_hook")
    expected_calls = [mock.call.fake_proc_ftrs(),
                      mock.call.fake_set_attrs(),
                      mock.call.fake_proc_tpl({}),
                      mock.call.fake_hook(store, {}, root.Error.__template__)]

    e = root.Error()

    assert manager.mock_calls == expected_calls
    assert str(e) == overriden_message


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
                                                full_name=str,
                                                box=dict)),
                    frozenset(("name",
                               "age",
                               "note",
                               "timestamp",
                               "my_type",
                               "surname",
                               "location",
                               "updated_at",
                               "full_name",
                               "box")),
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
    """validates root.Error.__init_subclass__"""

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
