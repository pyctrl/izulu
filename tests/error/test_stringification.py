import datetime
from unittest import mock

import pytest

from tests import errors


TS = datetime.datetime.now()


@pytest.mark.parametrize(
    "kwargs",
    (
            dict(),
            dict(name="John"),
            dict(age=42),
            dict(name="John", age=42),
            dict(name="John", age=42, ts=53452345.3465),
            dict(name="John", age="Karl", ts=TS),
    ),
)
def test_templating(kwargs):
    with pytest.raises(ValueError):
        errors.ComplexTemplateOnlyError(**kwargs)


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "Unspecified error"),
            (errors.MixedError(name="John", age=10, note="..."),
             "The John is 10 years old with ..."),
    )
)
def test_str(err, expected):
    assert str(err) == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "izulu.root.Error()"),
            (errors.MixedError(name="John", age=10, note="...", timestamp=TS),
             ("tests.errors.MixedError(name='John', age=10,"
              f" note='...', timestamp={TS!r}, my_type='MixedError')")),
    )
)
def test_repr(err, expected):
    assert repr(err) == expected


def test_repl_repr():
    e = errors.TemplateOnlyError(name="John", age=42)

    with mock.patch.object(errors.TemplateOnlyError,
                           "__module__",
                           new_callable=mock.PropertyMock) as mocked:
        mocked.return_value = "__main__"

        assert repr(e) == "__main__.TemplateOnlyError(name='John', age=42)"


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "Error: Unspecified error"),
            (errors.MixedError(name="John", age=10, note="..."),
             "MixedError: The John is 10 years old with ..."),
    )
)
def test_as_str(err, expected):
    assert err.as_str() == expected
