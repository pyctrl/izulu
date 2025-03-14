import pytest

from izulu import _reraise


def test_fatal_direct_inheritance():
    type("Klass", (_reraise.FatalMixin,), {})


def test_fatal_indirect_inheritance():
    kls = type("Klass", (_reraise.FatalMixin,), {})

    with pytest.raises(TypeError):
        type("Klass2", (kls,), {})
