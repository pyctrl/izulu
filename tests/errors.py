import datetime
import typing as t

from izulu import root


RootError = root.Error


class TemplateOnlyError(root.Error):

    __template__ = "The {name} is {age} years old"


class AttributesOnlyError(root.Error):

    __template__ = "Static message template"

    name: str
    age: int


class AttributesWithStaticDefaultsError(root.Error):

    __template__ = "Static message template"

    name: str
    age: int = 0


class AttributesWithDynamicDefaultsError(root.Error):

    __template__ = "Static message template"

    name: str
    age: int = root.factory(int)


class ClassVarsError(root.Error):

    __template__ = "Static message template"

    name: t.ClassVar[str] = "Username"
    age: t.ClassVar[int] = 42


class MixedError(root.Error):

    __template__ = "The {name} is {age} years old with {note}"

    entity: t.ClassVar[str] = "The Entity"

    name: str
    age: int = 0
    timestamp: datetime.datetime = root.factory(datetime.datetime.now)
    my_type: str = root.factory(lambda self: self.__class__.__name__,
                                self=True)


class DerivedError(MixedError):

    __template__ = "The {name} {surname} is {age} years old with {note}"

    entity: t.ClassVar[str] = "The Entity"

    surname: str
    location: tuple[float, float] = (50.3, 3.608)
    updated_at: datetime.datetime = root.factory(datetime.datetime.now)
    full_name: str = root.factory(lambda self: f"{self.name} {self.surname}",
                                  self=True)


class Exc(root.Error):

    __template__ = "The {name} is {age} years old"

    MY_CONST: t.ClassVar[int] = 42

    name: str
    age: int
