from unittest import mock

import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    "kls",
    [errors.TemplateOnlyError, errors.AttributesOnlyError],
)
@pytest.mark.parametrize("kwargs", [dict(), dict(name="John"), dict(age=42)])
def test_forbid_missing_fields_triggered(kls, kwargs):
    toggles = {"__toggles__": root.Toggles.FORBID_MISSING_FIELDS}

    with pytest.raises(TypeError):
        type("TestError", (kls,), toggles)(**kwargs)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    [
        (errors.RootError, dict(field="value")),
        (errors.TemplateOnlyError, dict(name="John", age=42, field="field")),
        (errors.AttributesOnlyError, dict(name="John", age=42, field="field")),
    ],
)
def test_forbid_undeclared_fields_triggered(kls, kwargs):
    toggles = {"__toggles__": root.Toggles.FORBID_UNDECLARED_FIELDS}

    with pytest.raises(TypeError):
        type("TestError", (kls,), toggles)(**kwargs)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    [
        (errors.ClassVarsError, dict(name="John")),
        (errors.ClassVarsError, dict(age=0)),
        (errors.ClassVarsError, dict(blah=1.0)),
        (errors.ClassVarsError, dict(name="John", age=0)),
        (errors.ClassVarsError, dict(age=0, blah=1.0)),
        (errors.MixedError, dict(name="John", age=42, entity="thing")),
    ],
)
def test_forbid_kwarg_consts_triggered(kls, kwargs):
    toggles = {"__toggles__": root.Toggles.FORBID_KWARG_CONSTS}

    with pytest.raises(TypeError):
        type("TestError", (kls,), toggles)(**kwargs)


@pytest.mark.parametrize("toggles", [root.Toggles(i) for i in range(7)])
@mock.patch("izulu._utils.check_kwarg_consts")
@mock.patch("izulu._utils.check_undeclared_fields")
@mock.patch("izulu._utils.check_missing_fields")
def test_process_toggles(mock_missing, mock_undeclared, mock_const, toggles):
    with mock.patch.object(
        errors.RootError,
        "__toggles__",
        new_callable=mock.PropertyMock,
    ) as mocked:
        mocked.return_value = toggles

        e = errors.RootError()
        args = (e._Error__cls_store, frozenset(e._Error__kwargs))

        if root.Toggles.FORBID_MISSING_FIELDS in toggles:
            mock_missing.assert_called_once_with(*args)
        else:
            mock_missing.assert_not_called()
        if root.Toggles.FORBID_UNDECLARED_FIELDS in toggles:
            mock_undeclared.assert_called_once_with(*args)
        else:
            mock_undeclared.assert_not_called()
        if root.Toggles.FORBID_KWARG_CONSTS in toggles:
            mock_const.assert_called_once_with(*args)
        else:
            mock_const.assert_not_called()


def test_feature_presets():
    default = (
        root.Toggles.FORBID_MISSING_FIELDS
        | root.Toggles.FORBID_UNDECLARED_FIELDS
        | root.Toggles.FORBID_KWARG_CONSTS
        | root.Toggles.FORBID_NON_NAMED_FIELDS
        | root.Toggles.FORBID_UNANNOTATED_FIELDS
    )

    assert root.Toggles.NONE is root.Toggles(0)
    assert root.Toggles(0) == root.Toggles.NONE
    assert root.Toggles.DEFAULT is default
    assert default == root.Toggles.DEFAULT


def test_default_toggles():
    assert root.Error.__toggles__ is root.Toggles.DEFAULT
