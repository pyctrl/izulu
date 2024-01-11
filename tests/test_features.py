import pytest

from izulu import root
from tests import errors


@pytest.mark.parametrize(
    ("kls", "kwargs"),
    (
            (errors.TemplateOnlyError, dict()),
            (errors.TemplateOnlyError, dict(name="John")),
            (errors.TemplateOnlyError, dict(age=42)),
            (errors.AttributesOnlyError, dict()),
            (errors.AttributesOnlyError, dict(name="John")),
            (errors.AttributesOnlyError, dict(age=42)),
    ),
)
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


# @pytest.mark.parametrize(
#     ("kls", "kwargs"),
#     (
#             (errors.AttributesOnlyError, dict(name=42)),
#             (errors.AttributesOnlyError, dict(age=42.503)),
#             (errors.AttributesOnlyError, dict(name="John", age="42")),
#             (errors.AttributesWithStaticDefaultsError,
#              dict(name="John", age="42")),
#     ),
# )
# def test_forbid_wrong_types_triggered(kls, kwargs):
#     with pytest.raises(TypeError):
#         type("TestError",
#              (kls,),
#              {"__features__": root.Features.FORBID_WRONG_TYPES}
#              )(**kwargs)


def test_feature_presets():
    default = (
            root.Features.FORBID_MISSING_FIELDS
            | root.Features.FORBID_UNDECLARED_FIELDS
            | root.Features.FORBID_KWARG_CONSTS
    )

    assert root.Features.NONE is root.Features(0)
    assert root.Features.NONE == root.Features(0)
    assert root.Features.DEFAULT is default
    assert root.Features.DEFAULT == default


def test_default_features():
    assert root.Error.__features__ is root.Features.DEFAULT
