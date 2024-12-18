import dataclasses
import sys
import typing

from .error import RuntimeError
from .grammar import Token


class Lox:

    had_error = False
    had_runtime_error = False

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        Lox.had_error = True

    @staticmethod
    def report_runtime(line: int, message: str):
        print(f"{message}\n[line {line}]", file=sys.stderr)
        Lox.had_runtime_error = True


class Environment:

    enclosing: typing.Optional["Environment"]
    values: typing.Dict[str, typing.Any]

    def __init__(
        self,
        enclosing: typing.Optional["Environment"] = None,
        initial: typing.Optional[typing.Dict[str, typing.Any]] = None
    ):
        self.enclosing = enclosing
        self.values = initial or dict()

    def inner(self):
        return Environment(self)

    def define(self, name: str, value: typing.Any):
        self.values[name] = value

    def assign(self, name: Token, value: typing.Any):
        lexeme = name.lexeme
        if lexeme in self.values:
            self.values[lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise RuntimeError(name, f"Undefined variable '{lexeme}'.")

    def get(self, name: Token):
        lexeme = name.lexeme
        if lexeme in self.values:
            return self.values[lexeme]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{lexeme}'.")
