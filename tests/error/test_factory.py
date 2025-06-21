import uuid
from unittest import mock  # noqa: RUF100,H306

import pytest

from izulu import root


@pytest.mark.parametrize("flag", [True, False])
def test_factory(flag):
    expected = uuid.uuid4()
    m = mock.Mock(__name__="__mock_func__", return_value=expected)
    attr = root.factory(default_factory=m, self=flag)
    kls = type("Klass", tuple(), {"attr_with_self": attr})
    inst = kls()
    call_args = (inst,)

    result = inst.attr_with_self

    assert result is expected
    m.assert_called_once_with(*call_args[:flag])
