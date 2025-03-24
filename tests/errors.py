import datetime as dtm
import typing as t

from izulu import root


class RootError(root.Error):
    __toggles__ = root.Toggles.DEFAULT ^ root.Toggles.FORBID_UNANNOTATED_FIELDS


class TemplateOnlyError(RootError):
    __template__ = "The {name} is {age} years old"


class ComplexTemplateOnlyError(RootError):
    __template__ = "{name:*^20} {age: f} {age:#b} {ts:%Y-%m-%d %H:%M:%S}"
    __toggles__ = root.Toggles.NONE


class AttributesOnlyError(RootError):
    __template__ = "Static message template"

    name: str
    age: int


class AttributesWithStaticDefaultsError(RootError):
    __template__ = "Static message template"

    name: str
    age: int = 0


class AttributesWithDynamicDefaultsError(RootError):
    __template__ = "Static message template"

    name: str
    age: int = root.factory(default_factory=int)


class ClassVarsError(RootError):
    __template__ = "Static message template"

    name: t.ClassVar[str] = "Username"
    age: t.ClassVar[int] = 42
    blah: t.ClassVar[float]


class MixedError(RootError):
    __template__ = "The {name} is {age} years old with {note}"

    entity: t.ClassVar[str] = "The Entity"

    name: str
    age: int = 0
    timestamp: dtm.datetime = root.factory(default_factory=dtm.datetime.now)
    my_type: str = root.factory(
        default_factory=lambda self: self.__class__.__name__,
        self=True,
    )


class DerivedError(MixedError):
    __template__ = "The {name} {surname} is {age} years old with {note}"

    entity: t.ClassVar[str] = "The Entity"

    surname: str
    location: t.Tuple[float, float] = (50.3, 3.608)
    updated_at: dtm.datetime = root.factory(default_factory=dtm.datetime.now)
    full_name: str = root.factory(
        default_factory=lambda self: f"{self.name} {self.surname}",
        self=True,
    )
    box: dict


class MyError(RootError):
    __template__ = "The {name} is {age} years old with {ENTITY} {note}"

    DEFAULT = "default"
    HINT: t.ClassVar[int]
    ENTITY: t.ClassVar[str] = "The Entity"

    name: str
    age: int = 0
    timestamp: dtm.datetime = root.factory(default_factory=dtm.datetime.now)
    my_type: str = root.factory(
        default_factory=lambda self: self.__class__.__name__,
        self=True,
    )
