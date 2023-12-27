import typing as t

from izulu import root


class Exc(root.Error):

    __template__ = "The {name} is {age} years old"

    MY_CONST: t.ClassVar[int] = 42

    name: str
    age: int
