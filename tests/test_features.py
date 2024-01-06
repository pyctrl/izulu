import pytest

from izulu import root
from tests import errors


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
