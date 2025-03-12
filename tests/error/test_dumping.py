import copy
import datetime
import pickle

import pytest

from izulu import root
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

    assert id(kwargs) != id(err._Error__kwargs)


@pytest.mark.parametrize(
    ("err", "expected", "wide"),
    (
            (errors.RootError(), dict(), False),
            (errors.RootError(), dict(), True),
            (errors.ClassVarsError(), dict(), False),
            (errors.ClassVarsError(), dict(age=42, name="Username"), True),
            (errors.AttributesWithStaticDefaultsError(name="John"),
             dict(name="John", age=0),
             False),
            (errors.AttributesWithStaticDefaultsError(name="John"),
             dict(name="John", age=0),
             True),
            (errors.MixedError(name="John", age=10, note="...", timestamp=TS),
             dict(name="John",
                  age=10,
                  note="...",
                  my_type="MixedError",
                  timestamp=TS),
             False),
            (errors.MixedError(name="John", age=10, note="...", timestamp=TS),
             dict(name="John",
                  age=10,
                  note="...",
                  my_type="MixedError",
                  timestamp=TS,
                  entity="The Entity"),
             True),
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
                  updated_at=TS),
             False),
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
                  updated_at=TS,
                  entity="The Entity"),
             True),
    )
)
def test_as_dict(err, expected, wide):
    data = err.as_dict(wide)
    assert data == expected

    data["item"] = "SURPRISE"
    assert "key" not in err._Error__kwargs

    with pytest.raises(AttributeError):
        getattr(data, "key")

    assert id(data) != id(err._Error__kwargs)


def test_as_dict_wide_override_const():
    kls = type("Err",
               (errors.ClassVarsError,),
               {"__features__": root.Features.NONE})

    err = kls(age=500)

    assert err.as_dict(True) == dict(age=500, name="Username")


def _assert_copy_mutual(orig, cp):
    assert cp is not orig
    assert cp._Error__kwargs is not orig._Error__kwargs
    assert cp.as_dict() == orig.as_dict()
    assert cp.box == orig.box == dict()


def test_copy_shallow(derived_error):
    orig = derived_error
    shallow = copy.copy(orig)

    assert shallow.box is orig.box
    _assert_copy_mutual(orig, shallow)

    orig.box.update(a=11)

    assert shallow.box == dict(a=11)


def test_copy_deep(derived_error):
    orig = derived_error
    deep = copy.deepcopy(orig)

    assert deep is not orig.box
    _assert_copy_mutual(orig, deep)

    orig.box.update(a=11)

    assert deep.box == dict()


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

    assert str(err) == str(resurrected)
    assert repr(err) == repr(resurrected)
    assert err.as_dict() == resurrected.as_dict()
