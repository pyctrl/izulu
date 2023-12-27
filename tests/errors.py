import typing as t

from izulu import root


class Exc(root.Error):
    MY_CONST: t.ClassVar[int] = 42

    name: str
    age: int
