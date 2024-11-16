import abc
import typing

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
