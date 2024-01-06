import copy
import datetime
import pickle

import pytest

from tests import errors


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), dict()),
            (errors.Exc(name="John", age=10), dict(name="John", age=10)),
    )
)
def test_as_kwargs(err, expected):
    assert err.as_kwargs() == expected


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), dict()),
            (errors.Exc(name="John", age=10), dict(name="John", age=10)),
    )
)
def test_as_dict(err, expected):
    assert err.as_dict() == expected


def test_copy():  # shallow
    ts = datetime.datetime.now()
    orig = errors.DerivedError(name="John",
                               surname="Brown",
                               note="...",
                               age=42,
                               updated_at=ts,
                               full_name="secret",
                               box=dict())

    copied = copy.copy(orig)

    assert id(copied) != id(orig)
    assert copied.as_dict() == orig.as_dict()
    assert copied.box is orig.box
    assert copied.box == orig.box == dict()

    orig.box.update(a=11)

    assert copied.box == dict(a=11)


def test_deepcopy():

    ts = datetime.datetime.now()
    orig = errors.DerivedError(name="John",
                               surname="Brown",
                               note="...",
                               age=42,
                               updated_at=ts,
                               full_name="secret",
                               box=dict())

    copied = copy.deepcopy(orig)

    assert id(copied) != id(orig)
    assert copied.as_dict() == orig.as_dict()
    assert id(copied.box) != id(orig.box)
    assert copied.box == orig.box == dict()

    orig.box.update(a=11)

    assert copied.box == dict()


@pytest.mark.parametrize(
    "err",
    (
            errors.RootError(),
            errors.TemplateOnlyError(name="John", age=42),
            errors.AttributesOnlyError(name="John", age=42),
            errors.MixedError(name="John", note="..."),
            errors.DerivedError(name="John",
                                surname="Brown",
                                note="...",
                                box={}),
    ),
)
def test_pickling(err):
    dumped = pickle.dumps(err)
    resurrected = pickle.loads(dumped)

    assert err.as_dict() == resurrected.as_dict()
