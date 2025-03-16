import abc
import builtins
import typing

from .lox import Environment
from .statement import FunctionStatement

if typing.TYPE_CHECKING:
    from .class_ import LoxInstance
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
        closure: Environment,
        is_initializer: bool,
    ):
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def arity(self) -> int:
        return len(self._declaration.parameters)

    def call(self, interpreter, arguments):
        environment = self._closure.inner()

        for parameter, argument in zip(self._declaration.parameters, arguments):
            environment.define(parameter.lexeme, argument)

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except Return as returned:
            return returned.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")

        return None

    def bind(self, instance: "LoxInstance"):
        environment = Environment(self._closure)
        environment.define("this", instance)

        return LoxFunction(self._declaration, environment, self._is_initializer)

    def __str__(self):
        return f"<fn {self._declaration.name.lexeme}>"
