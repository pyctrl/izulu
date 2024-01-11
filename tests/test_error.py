import datetime
from unittest import mock

import pytest

from tests import errors


TS = datetime.datetime.now()


@mock.patch("izulu.root.Error._hook")
@mock.patch("izulu.root.Error._Error__process_template")
@mock.patch("izulu.root.Error._Error__populate_attrs")
@mock.patch("izulu.root.Error._Error__process_features")
def test_init(fake_proc_ftrs, fake_set_attrs, fake_proc_tpl, fake_hook):
    fake_proc_tpl.return_value = errors.RootError.__template__
    overriden_message = "overriden message"
    fake_hook.return_value = overriden_message
    store = getattr(errors.RootError, "_Error__cls_store")
    manager = mock.Mock()
    manager.attach_mock(fake_proc_ftrs, "fake_proc_ftrs")
    manager.attach_mock(fake_set_attrs, "fake_set_attrs")
    manager.attach_mock(fake_proc_tpl, "fake_proc_tpl")
    manager.attach_mock(fake_hook, "fake_hook")
    fake_hook_call = mock.call.fake_hook(store,
                                         {},
                                         errors.RootError.__template__)
    expected_calls = [mock.call.fake_proc_ftrs(),
                      mock.call.fake_set_attrs(),
                      mock.call.fake_proc_tpl({}),
                      fake_hook_call]

    e = errors.RootError()

    assert manager.mock_calls == expected_calls
    assert str(e) == overriden_message


@pytest.mark.parametrize(
    ("kls", "kwargs", "msg", "attrs", "not_attrs"),
    (
            (errors.RootError, dict(), "Unspecified error", dict(), tuple()),
            (errors.TemplateOnlyError,
             dict(name="John", age=42),
             "The John is 42 years old",
             dict(),
             ("name", "age")),
            (errors.ComplexTemplateOnlyError,
             dict(name="John", age=42, ts=TS),
             ("********John********  42.000000"
              f" 0b101010 {TS:%Y-%m-%d %H:%M:%S}"),
             dict(),
             ("name", "age", "ts")),
            (errors.AttributesOnlyError,
             dict(name="John", age=42),
             "Static message template",
             dict(name="John", age=42),
             tuple()),
            (errors.AttributesWithStaticDefaultsError,
             dict(name="John"),
             "Static message template",
             dict(name="John", age=0),
             tuple()),
            (errors.AttributesWithDynamicDefaultsError,
             dict(name="John"),
             "Static message template",
             dict(name="John", age=0),
             tuple()),
            (errors.ClassVarsError,
             dict(),
             "Static message template",
             dict(name="Username", age=42),
             tuple()),
            (errors.MixedError,
             dict(name="John", age=10, note="...", timestamp=TS),
             "The John is 10 years old with ...",
             dict(entity="The Entity", name="John", age=10, timestamp=TS,
                  my_type="MixedError"),
             ("note",)),
            (errors.DerivedError,
             dict(name="John", age=10, note="...", timestamp=TS,
                  surname="Brown", box=dict(a=11)),
             "The John Brown is 10 years old with ...",
             dict(entity="The Entity", name="John", age=10, timestamp=TS,
                  my_type="DerivedError", surname="Brown", box=dict(a=11)),
             ("note",)),
    )
)
def test_errors(kls, kwargs, msg, attrs, not_attrs):
    e = kls(**kwargs)

    assert str(e) == msg
    for attr, value in attrs.items():
        assert getattr(e, attr) == value
    for attr in not_attrs:
        assert not hasattr(e, attr)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    (
            (errors.RootError, dict(name="John")),
            (errors.TemplateOnlyError, dict(name="John")),
            (errors.AttributesOnlyError, dict(age=42)),
            (errors.AttributesWithStaticDefaultsError, dict()),
            (errors.AttributesWithDynamicDefaultsError, dict(age=0)),
            (errors.ClassVarsError, dict(name="John")),
    )
)
def test_failures(kls, kwargs):
    with pytest.raises(TypeError):
        kls(**kwargs)


def test_hook():
    e = errors.RootError()
    orig_msg = "my message"

    final_msg = e._hook(e._Error__cls_store, dict(), orig_msg)

    assert final_msg == orig_msg
    assert id(final_msg) == id(orig_msg)
