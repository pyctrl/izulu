import datetime
import pytest

from izulu import _utils
from izulu import root
from tests import errors


count = 42
owner = "somebody"
dt = datetime.datetime.utcnow()


@pytest.mark.parametrize(
    ("args", "expected"),
    (
        ((tuple(),), ""),
        ((("item_1",),), "item_1"),
        ((("item_1", "item_2", "item_3"),), "item_1, item_2, item_3"),
        ((tuple(), ","), ""),
        ((("item_1",), ","), "item_1"),
        ((("item_1", "item_2", "item_3"), ","), "item_1, item_2, item_3"),
        ((tuple(), ";"), ""),
        ((("item_1",), ";"), "item_1"),
        ((("item_1", "item_2", "item_3"), ";"), "item_1; item_2; item_3"),
    )
)
def test_join(args, expected):
    assert _utils.join(*args) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    (
        (dict(), ""),
        (dict(a=42), "a=42"),
        (dict(owner=owner, count=count, timestamp=dt),
         f"{owner=!r}, {count=!r}, timestamp={dt!r}"),
        (dict(timestamp=dt), f"timestamp={dt!r}")
    )
)
def test_join_kwargs(data, expected):
    assert _utils.join_kwargs(**data) == expected


@pytest.mark.parametrize(
    ("tpl", "expected"),
    (
        ("Having boring message here", tuple()),
        ("Hello {you}!", ("you",)),
        ("Hello {you}! How are you, {you}", ("you", "you")),
        ("{owner}: Having count={count} for owner={owner}",
         ("owner", "count", "owner"))
    )
)
def test_extract_fields(tpl, expected):
    assert tuple(_utils.extract_fields(tpl)) == expected


@pytest.mark.parametrize(
    ("kls", "expected"),
    (
        (type("Klass1", tuple(), dict()), tuple()),
        (root.Error, tuple()),
        (errors.MixedError,
         (("name", str),
          ("age", int),
          ("timestamp", datetime.datetime),
          ("my_type", str))),
    )
)
def test_filter_hints(kls, expected):
    assert tuple(_utils.filter_hints(kls)) == expected
