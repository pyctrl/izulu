import datetime
import types
from unittest import mock

import pytest

from izulu import _utils
from izulu import root
from tests import errors

TS = datetime.datetime.now(datetime.timezone.utc)


@mock.patch("izulu.root.Error._override_message")
@mock.patch("izulu.root.Error._Error__process_template")
@mock.patch("izulu.root.Error._Error__populate_attrs")
@mock.patch("izulu.root.Error._Error__process_features")
def test_init(
    fake_proc_ftrs,
    fake_set_attrs,
    fake_proc_tpl,
    fake_override_message,
):
    fake_proc_tpl.return_value = errors.RootError.__template__
    overriden_message = "overriden message"
    fake_override_message.return_value = overriden_message
    store = errors.RootError._Error__cls_store
    manager = mock.Mock()
    manager.attach_mock(fake_proc_ftrs, "fake_proc_ftrs")
    manager.attach_mock(fake_set_attrs, "fake_set_attrs")
    manager.attach_mock(fake_proc_tpl, "fake_proc_tpl")
    manager.attach_mock(fake_override_message, "fake_override_message")
    fake_override_message_call = mock.call.fake_override_message(
        store,
        {},
        errors.RootError.__template__,
    )
    expected_calls = [
        mock.call.fake_proc_ftrs(),
        mock.call.fake_set_attrs(),
        mock.call.fake_proc_tpl({}),
        fake_override_message_call,
    ]

    e = errors.RootError()

    assert manager.mock_calls == expected_calls
    assert str(e) == overriden_message


@pytest.mark.parametrize(
    ("kls", "kwargs", "msg", "attrs", "not_attrs"),
    [
        (errors.RootError, dict(), "Unspecified error", dict(), tuple()),
        (
            errors.TemplateOnlyError,
            dict(name="John", age=42),
            "The John is 42 years old",
            dict(),
            ("name", "age"),
        ),
        (
            errors.ComplexTemplateOnlyError,
            dict(name="John", age=42, ts=TS),
            (
                "********John********  42.000000"
                f" 0b101010 {TS:%Y-%m-%d %H:%M:%S}"
            ),
            dict(),
            ("name", "age", "ts"),
        ),
        (
            errors.AttributesOnlyError,
            dict(name="John", age=42),
            "Static message template",
            dict(name="John", age=42),
            tuple(),
        ),
        (
            errors.AttributesWithStaticDefaultsError,
            dict(name="John"),
            "Static message template",
            dict(name="John", age=0),
            tuple(),
        ),
        (
            errors.AttributesWithDynamicDefaultsError,
            dict(name="John"),
            "Static message template",
            dict(name="John", age=0),
            tuple(),
        ),
        (
            errors.ClassVarsError,
            dict(),
            "Static message template",
            dict(name="Username", age=42),
            tuple(),
        ),
        (
            errors.MixedError,
            dict(name="John", age=10, note="...", timestamp=TS),
            "The John is 10 years old with ...",
            dict(
                entity="The Entity",
                name="John",
                age=10,
                timestamp=TS,
                my_type="MixedError",
            ),
            ("note",),
        ),
        (
            errors.DerivedError,
            dict(
                name="John",
                age=10,
                note="...",
                timestamp=TS,
                surname="Brown",
                box=dict(a=11),
            ),
            "The John Brown is 10 years old with ...",
            dict(
                entity="The Entity",
                name="John",
                age=10,
                timestamp=TS,
                my_type="DerivedError",
                surname="Brown",
                box=dict(a=11),
            ),
            ("note",),
        ),
    ],
)
def test_instantiate_ok(kls, kwargs, msg, attrs, not_attrs):
    e = kls(**kwargs)

    assert str(e) == msg
    for attr, value in attrs.items():
        assert getattr(e, attr) == value
    for attr in not_attrs:
        assert not hasattr(e, attr)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    [
        (errors.RootError, dict(name="John")),
        (errors.TemplateOnlyError, dict(name="John")),
        (errors.AttributesOnlyError, dict(age=42)),
        (errors.AttributesWithStaticDefaultsError, dict()),
        (errors.AttributesWithDynamicDefaultsError, dict(age=0)),
        (errors.ClassVarsError, dict(name="John")),
    ],
)
def test_instantiate_fail(kls, kwargs):
    with pytest.raises(TypeError):
        kls(**kwargs)


@pytest.mark.parametrize(
    ("kls", "kwargs", "expected_kwargs"),
    [
        (errors.RootError, dict(), dict()),
        (errors.RootError, dict(name="John"), dict(name="John")),
        (errors.ClassVarsError, dict(), dict(name="Username", age=42)),
        (errors.ClassVarsError, dict(name="John"), dict(name="John", age=42)),
        (
            errors.MixedError,
            dict(name="John", surname="Brown", updated_at=TS, timestamp=TS),
            dict(
                name="John",
                surname="Brown",
                age=0,
                my_type="MixedError",
                entity="The Entity",
                updated_at=TS,
                timestamp=TS,
            ),
        ),
        (
            errors.MixedError,
            dict(updated_at=TS, timestamp=TS),
            dict(
                age=0,
                my_type="MixedError",
                entity="The Entity",
                updated_at=TS,
                timestamp=TS,
            ),
        ),
        (
            errors.DerivedError,
            dict(name="John", surname="Brown", updated_at=TS, timestamp=TS),
            dict(
                name="John",
                surname="Brown",
                full_name="John Brown",
                age=0,
                my_type="DerivedError",
                entity="The Entity",
                location=(50.3, 3.608),
                updated_at=TS,
                timestamp=TS,
            ),
        ),
    ],
)
@mock.patch("izulu._utils.format_template")
def test_process_template(mock_format, kls, kwargs, expected_kwargs):
    with mock.patch.object(
        kls,
        "__features__",
        new_callable=mock.PropertyMock,
    ) as mocked:
        mocked.return_value = root.Features.NONE
        kls(**kwargs)

    mock_format.assert_called_once_with(kls.__template__, expected_kwargs)


def test_override_message():
    e = errors.RootError()
    orig_msg = "my message"

    final_msg = e._override_message(e._Error__cls_store, dict(), orig_msg)

    assert final_msg == orig_msg
    assert id(final_msg) == id(orig_msg)


def test_constants():
    e = errors.RootError()

    assert e.__template__ == "Unspecified error"
    assert e.__features__ == root.Features.DEFAULT
    assert e._Error__cls_store == _utils.Store(
        fields=frozenset(),
        const_hints=types.MappingProxyType(dict()),
        inst_hints=types.MappingProxyType(dict()),
        consts=types.MappingProxyType(dict()),
        defaults=frozenset(),
    )
