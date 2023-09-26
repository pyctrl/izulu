import datetime
import unittest

from izulu import _utils


class JoinTestCase(unittest.TestCase):

    def test_no_args(self):
        self.assertRaises(TypeError, _utils.join)

    def test_empty(self):
        data = tuple()
        expected = ""

        result = _utils.join(data)

        self.assertEqual(result, expected)

    def test_single(self):
        data = ("item_1",)
        expected = "item_1"

        result = _utils.join(data)

        self.assertEqual(result, expected)

    def test_multiple(self):
        data = ("item_1", "item_2", "item_3")
        expected = "item_1, item_2, item_3"

        result = _utils.join(data)

        self.assertEqual(result, expected)


class JoinKwargsTestCase(unittest.TestCase):

    def test_no_args(self):
        data = dict()
        expected = ""

        result = _utils.join_kwargs(**data)

        self.assertEqual(result, expected)

    def test_single_simple(self):
        data = dict(a=42)
        expected = "a=42"

        result = _utils.join_kwargs(**data)

        self.assertEqual(result, expected)

    def test_single_complex(self):
        dt = datetime.datetime.utcnow()
        data = dict(timestamp=dt)
        expected = f"timestamp={repr(dt)}"

        result = _utils.join_kwargs(**data)

        self.assertEqual(result, expected)

    def test_many(self):
        count = 42
        owner = "somebody"
        dt = datetime.datetime.utcnow()
        data = dict(owner=owner, count=count, timestamp=dt)
        expected = f"{owner=!r}, {count=!r}, timestamp={dt!r}"

        result = _utils.join_kwargs(**data)

        self.assertEqual(result, expected)


class ExtractFieldsTestCase(unittest.TestCase):

    def test_empty(self):
        tpl = "Having boring message here"
        expected = tuple()

        result = _utils.extract_fields(tpl)

        self.assertEqual(result, expected)

    def test_single(self):
        tpl = "Hello {you}!"
        expected = ("you",)

        result = _utils.extract_fields(tpl)

        self.assertEqual(result, expected)

    def test_duplicate(self):
        tpl = "Hello {you}! How are you, {you}"
        expected = ("you", "you")

        result = _utils.extract_fields(tpl)

        self.assertEqual(result, expected)

    def test_many(self):
        tpl = "{owner}: Having count={count} for owner={owner}"
        expected = ("owner", "count", "owner")

        result = _utils.extract_fields(tpl)

        self.assertEqual(result, expected)
