from unittest import mock

import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    "kls",
    (errors.TemplateOnlyError, errors.AttributesOnlyError),
)
@pytest.mark.parametrize("kwargs", (dict(), dict(name="John"), dict(age=42)))
def test_forbid_missing_fields_triggered(kls, kwargs):
    with pytest.raises(TypeError):
        type("TestError",
             (kls,),
             {"__features__": root.Features.FORBID_MISSING_FIELDS}
             )(**kwargs)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    (
            (errors.RootError,
             dict(field="value")),
            (errors.TemplateOnlyError,
             dict(name="John", age=42, field="field")),
            (errors.AttributesOnlyError,
             dict(name="John", age=42, field="field")),
    ),
)
def test_forbid_undeclared_fields_triggered(kls, kwargs):
    with pytest.raises(TypeError):
        type("TestError",
             (kls,),
             {"__features__": root.Features.FORBID_UNDECLARED_FIELDS}
             )(**kwargs)


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    (
            (errors.ClassVarsError, dict(name="John")),
            (errors.ClassVarsError, dict(age=0)),
            (errors.ClassVarsError, dict(blah=1.0)),
            (errors.ClassVarsError, dict(name="John", age=0)),
            (errors.ClassVarsError, dict(age=0, blah=1.0)),
            (errors.MixedError, dict(name="John", age=42, entity="thing")),
    ),
)
def test_forbid_kwarg_consts_triggered(kls, kwargs):
    with pytest.raises(TypeError):
        type("TestError",
             (kls,),
             {"__features__": root.Features.FORBID_KWARG_CONSTS}
             )(**kwargs)


@pytest.mark.parametrize("features", tuple(root.Features(i) for i in range(7)))
@mock.patch("izulu._utils.check_kwarg_consts")
@mock.patch("izulu._utils.check_undeclared_fields")
@mock.patch("izulu._utils.check_missing_fields")
def test_process_features(mock_missing, mock_undeclared, mock_const, features):
    with mock.patch.object(errors.RootError,
                           "__features__",
                           new_callable=mock.PropertyMock) as mocked:
        mocked.return_value = features

        e = errors.RootError()
        args = (e._Error__cls_store, frozenset(e._Error__kwargs))

        if root.Features.FORBID_MISSING_FIELDS in features:
            mock_missing.assert_called_once_with(*args)
        else:
            mock_missing.assert_not_called()
        if root.Features.FORBID_UNDECLARED_FIELDS in features:
            mock_undeclared.assert_called_once_with(*args)
        else:
            mock_undeclared.assert_not_called()
        if root.Features.FORBID_KWARG_CONSTS in features:
            mock_const.assert_called_once_with(*args)
        else:
            mock_const.assert_not_called()


def test_feature_presets():
    default = (
            root.Features.FORBID_MISSING_FIELDS
            | root.Features.FORBID_UNDECLARED_FIELDS
            | root.Features.FORBID_KWARG_CONSTS
            | root.Features.FORBID_NON_NAMED_FIELDS
    )

    assert root.Features.NONE is root.Features(0)
    assert root.Features.NONE == root.Features(0)
    assert root.Features.DEFAULT is default
    assert root.Features.DEFAULT == default


def test_default_features():
    assert root.Error.__features__ is root.Features.DEFAULT
