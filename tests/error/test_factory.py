from unittest import mock
import uuid

import pytest

from izulu import root


@pytest.mark.parametrize("flag", (True, False))
def test_factory(flag):
    expected = uuid.uuid4()
    m = mock.Mock(return_value=expected)
    attr = root.factory(m, self=flag)
    k = type("Klass", tuple(), {"attr_with_self": attr})()
    call_args = (k,)

    result = k.attr_with_self

    assert result is expected
    m.assert_called_once_with(*call_args[:flag])
