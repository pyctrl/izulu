import pytest

from tests import errors


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "Unspecified error"),
            (errors.Exc(name="John", age=10), "The John is 10 years old"),
    )
)
def test_str(err, expected):
    assert str(err) == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "izulu.root.Error()"),
            (errors.Exc(name="John", age=10),
             "tests.errors.Exc(name='John', age=10)"),
    )
)
def test_repr(err, expected):
    assert repr(err) == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), "Error: Unspecified error"),
            (errors.Exc(name="John", age=10), "Exc: The John is 10 years old"),
    )
)
def test_as_str(err, expected):
    assert err.as_str() == expected
