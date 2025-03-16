import dataclasses
import typing

from .error import RuntimeError
from .function import Callable, LoxFunction
from .grammar import Token


@dataclasses.dataclass
class LoxClass(Callable):

    name: str
    methods: typing.Dict[str, LoxFunction]

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return LoxInstance(self)

    def find_method(self, name: str):
        return self.methods.get(name)

    def __str__(self):
        return self.name


@dataclasses.dataclass
class LoxInstance:

    klass: LoxClass
    fields: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=lambda: {})

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: typing.Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
