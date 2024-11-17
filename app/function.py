import abc
import builtins
import typing

from .lox import Environment
from .statement import FunctionStatement

if typing.TYPE_CHECKING:
    from .evaluation import Interpreter


class Callable(abc.ABC):

    @abc.abstractmethod
    def arity(self) -> int:
        pass

    @abc.abstractmethod
    def call(
        self,
        interpreter: "Interpreter",
        arguments: typing.List[typing.Any]
    ) -> typing.Any:
        pass


class NativeFunction(Callable):

    def __init__(
        self,
        name: str,
        arity: int,
        callable: typing.Callable
    ):
        self._name = name
        self._arity = arity
        self._callable = callable

    def arity(self) -> int:
        return self._arity

    def call(self, interpreter, arguments):
        return self._callable(*arguments)

    def __str__(self):
        return f"<native fn {self._name}>"


class Return(builtins.RuntimeError):

    def __init__(self, value: typing.Any):
        self.value = value


class LoxFunction(Callable):

    def __init__(
        self,
        declaration: FunctionStatement,
    ):
        self._declaration = declaration

    def arity(self) -> int:
        return len(self._declaration.parameters)

    def call(self, interpreter, arguments):
        environment = interpreter.globals.inner()

        for parameter, argument in zip(self._declaration.parameters, arguments):
            environment.define(parameter.lexeme, argument)

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except Return as returned:
            return returned.value

        return None

    def __str__(self):
        return f"<fn {self._declaration.name.lexeme}>"
