import copy
import datetime
import pickle

import pytest

from tests import errors


TS = datetime.datetime.now()


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), dict()),
            (errors.MixedError(name="John", age=10, note="..."),
             dict(name="John", age=10, note="...")),
            (errors.DerivedError(name="John",
                                 surname="Brown",
                                 note="...",
                                 box={}),
             dict(name="John", surname="Brown", note="...", box={})),
    )
)
def test_as_kwargs(err, expected):
    kwargs = err.as_kwargs()
    assert kwargs == expected

    kwargs["item"] = "SURPRISE"
    assert kwargs != err._Error__kwargs


@pytest.mark.parametrize(
    ("err", "expected"),
    (
            (errors.RootError(), dict()),
            (errors.ClassVarsError(), dict()),
            (errors.AttributesWithStaticDefaultsError(name="John"),
             dict(name="John", age=0)),
            (errors.MixedError(name="John", age=10, note="...", timestamp=TS),
             dict(name="John",
                  age=10,
                  note="...",
                  my_type="MixedError",
                  timestamp=TS)),
            (errors.DerivedError(name="John",
                                 surname="Brown",
                                 note="...",
                                 box={},
                                 timestamp=TS,
                                 updated_at=TS),
             dict(name="John",
                  surname="Brown",
                  full_name="John Brown",
                  note="...",
                  age=0,
                  box={},
                  location=(50.3, 3.608),
                  my_type="DerivedError",
                  timestamp=TS,
                  updated_at=TS)),
    )
)
def test_as_dict(err, expected):
    data = err.as_dict()
    assert data == expected

    data["item"] = "SURPRISE"
    assert "SURPRISE" not in err._Error__kwargs


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
