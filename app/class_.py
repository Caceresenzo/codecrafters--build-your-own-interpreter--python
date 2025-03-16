import typing

from .error import RuntimeError
from .function import Callable
from .grammar import Token


class LoxClass(Callable):

    def __init__(self, name: str):
        self.name = name

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return LoxInstance(self)

    def __str__(self):
        return self.name


class LoxInstance:

    fields: typing.Dict[str, typing.Any]

    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: typing.Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
