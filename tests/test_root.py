import unittest
from unittest import mock
import uuid

from izulu import root


class FactoryTestCase(unittest.TestCase):

    def test_with_self(self):
        expected = uuid.uuid4()
        m = mock.Mock(return_value=expected)
        attr = root.factory(m, self=True)
        k = type("Klass", tuple(), {"attr_with_self": attr})()

        result = k.attr_with_self

        self.assertIs(result, expected)
        m.assert_called_once_with(k)

    def test_without_self(self):
        expected = uuid.uuid4()
        m = mock.Mock(return_value=expected)
        attr = root.factory(m)
        k = type("Klass", tuple(), {"attr_with_self": attr})()

        result = k.attr_with_self

        self.assertIs(result, expected)
        m.assert_called_once_with()
