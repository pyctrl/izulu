import datetime
import typing as t

import pytest

from izulu import _utils
from tests import errors
from tests import helpers as h

count = 42
owner = "somebody"
dt = datetime.datetime.now(datetime.timezone.utc)


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        (h._make_store_kwargs(), frozenset()),
        (
            h._make_store_kwargs(fields=("field_1", "field_2")),
            frozenset(("field_1", "field_2")),
        ),
        (
            h._make_store_kwargs(inst_hints=dict(field_2=2, field_3=3)),
            frozenset(("field_2", "field_3")),
        ),
        (
            h._make_store_kwargs(
                fields=("field_1", "field_2"),
                inst_hints=dict(field_2=2, field_3=3),
            ),
            frozenset(("field_1", "field_2", "field_3")),
        ),
        (
            h._make_store_kwargs(
                fields=("field_1", "field_2"),
                inst_hints=dict(field_1=1, field_2=2),
            ),
            frozenset(("field_1", "field_2")),
        ),
    ],
)
def test_store_post_init(kwargs, expected):
    assert _utils.Store(**kwargs).registered == expected


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ((tuple(),), ""),
        ((("item_1",),), "'item_1'"),
        ((("item_1", "item_2", "item_3"),), "'item_1', 'item_2', 'item_3'"),
    ],
)
def test_join_items(args, expected):
    assert _utils.join_items(*args) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (dict(), ""),
        (dict(a=42), "a=42"),
        (
            dict(owner=owner, count=count, timestamp=dt),
            f"{owner=!r}, {count=!r}, timestamp={dt!r}",
        ),
        (dict(timestamp=dt), f"timestamp={dt!r}"),
    ],
)
def test_join_kwargs(data, expected):
    assert _utils.join_kwargs(**data) == expected


@pytest.mark.parametrize(
    ("template", "kwargs", "expected"),
    [
        ("Static message template", dict(), "Static message template"),
        (
            "Static message template",
            dict(name="John", age=42, ENTITY="The thing"),
            "Static message template",
        ),
        (
            "The {name} and {ENTITY}",
            dict(name="John", age=42, ENTITY="The thing"),
            "The John and The thing",
        ),
        (
            "The {name} of {age} and {ENTITY}",
            dict(name="John", age=42, ENTITY="The thing"),
            "The John of 42 and The thing",
        ),
        (
            "The {name} of {age:f} and {ENTITY}",
            dict(name="John", age=42, ENTITY="The thing"),
            "The John of 42.000000 and The thing",
        ),
    ],
)
def test_format_template_ok(template, kwargs, expected):
    assert _utils.format_template(template, kwargs) == expected


@pytest.mark.parametrize(
    ("template", "kwargs"),
    [
        (
            "The {name} of {age} and {ENTITY}",
            dict(name="John", ENTITY="The thing"),
        ),
        (
            "The {name} of {age:f} and {ENTITY}",
            dict(name="John", age="42", ENTITY="The thing"),
        ),
    ],
)
def test_format_template_fail(template, kwargs):
    with pytest.raises(
        ValueError, match="Failed to format template with provided kwargs:"
    ):
        _utils.format_template(template, kwargs)


@pytest.mark.parametrize(
    ("tpl", "expected"),
    [
        ("", tuple()),
        ("abc def", tuple()),
        ("{}", ("",)),
        ("abc {} def", ("",)),
        ("{-}", ("-",)),
        ("{_}", ("_",)),
        ("{'}", ("'",)),
        ("{01abc}", ("01abc",)),
        ("{]}", ("]",)),
        ("{1}", (1,)),
        ("{field}", ("field",)),
        ("{field.attribute}", ("field",)),
        ("{field[key]}", ("field",)),
        ("{field[key].attr}", ("field",)),
        ("{field.attr[key]}", ("field",)),
        ("{field.attr[key].attr}", ("field",)),
        ("{field[key][another]}", ("field",)),
        ("{field.attribute.attr}", ("field",)),
        ("{fi-eld}", ("fi-eld",)),
        ("{field.-attribute}", ("field",)),
        ("{field[-key]}", ("field",)),
        ("{-field[key].attr}", ("-field",)),
        ("{field-.-attr[-key]}", ("field-",)),
        ("{fi-eld.at-tr[key].attr}", ("fi-eld",)),
        ("{field[0key][another]}", ("field",)),
        ("{fi-eld.0attribute.attr}", ("fi-eld",)),
        ("Having boring message here", tuple()),
        ("Hello {}!", ("",)),
        ("Hello {0}!", (0,)),
        ("Hello {you}!", ("you",)),
        ("Hello {you:f}!", ("you",)),
        ("Hello {you}! How are you, {you!a}", ("you", "you")),
        (
            "{owner:f!a}: Having {!a} count={count!a:f} for owner={0:f}",
            ("owner", "", "count", 0),
        ),
    ],
)
def test_iterate_field_specs(tpl, expected):
    assert tuple(_utils.iter_fields(tpl)) == expected


@pytest.mark.parametrize(
    ("kls", "const_hints", "inst_hints"),
    [
        (errors.RootError, dict(), dict()),
        (errors.TemplateOnlyError, dict(), dict()),
        (errors.ComplexTemplateOnlyError, dict(), dict()),
        (errors.AttributesOnlyError, dict(), dict(age=int, name=str)),
        (
            errors.AttributesWithStaticDefaultsError,
            dict(),
            dict(age=int, name=str),
        ),
        (
            errors.AttributesWithDynamicDefaultsError,
            dict(),
            dict(age=int, name=str),
        ),
        (
            errors.ClassVarsError,
            dict(
                name=t.ClassVar[str],
                age=t.ClassVar[int],
                blah=t.ClassVar[float],
            ),
            dict(),
        ),
        (
            errors.MixedError,
            dict(entity=t.ClassVar[str]),
            dict(name=str, age=int, my_type=str, timestamp=datetime.datetime),
        ),
        (
            errors.DerivedError,
            dict(entity=t.ClassVar[str]),
            dict(
                name=str,
                surname=str,
                full_name=str,
                age=int,
                my_type=str,
                timestamp=datetime.datetime,
                updated_at=datetime.datetime,
                box=dict,
                location=t.Tuple[float, float],
            ),
        ),
    ],
)
def test_split_cls_hints(kls, const_hints, inst_hints):
    assert _utils.split_cls_hints(kls) == (const_hints, inst_hints)


@pytest.mark.parametrize(
    ("kls", "attrs", "expected"),
    [
        (errors.DerivedError, (), dict()),
        (errors.DerivedError, ("entity",), dict(entity="The Entity")),
        (
            errors.DerivedError,
            (
                "name",
                "surname",
                "age",
                "timestamp",
                "my_type",
                "location",
                "updated_at",
                "full_name",
                "box",
            ),
            dict(
                age=0,
                location=(50.3, 3.608),
                timestamp=errors.DerivedError.timestamp,
                updated_at=errors.DerivedError.updated_at,
                full_name=errors.DerivedError.full_name,
                my_type=errors.DerivedError.my_type,
            ),
        ),
        (errors.RootError, ("entity",), dict()),
        (errors.TemplateOnlyError, ("name",), dict()),
    ],
)
def test_get_cls_defaults(kls, attrs, expected):
    assert _utils.get_cls_defaults(kls, attrs) == expected
