from unittest import mock

from tests import errors


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
    expected_calls = [mock.call.fake_proc_ftrs(),
                      mock.call.fake_set_attrs(),
                      mock.call.fake_proc_tpl({}),
                      mock.call.fake_hook(store,
                                          {},
                                          errors.RootError.__template__)]

    e = errors.RootError()

    assert manager.mock_calls == expected_calls
    assert str(e) == overriden_message
