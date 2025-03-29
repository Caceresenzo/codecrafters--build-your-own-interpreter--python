import abc
import dataclasses
import typing

class Expression(abc.ABC):

    def __hash__(self):
        return id(self)

@dataclasses.dataclass
class Literal(Expression):

    value: typing.Any

x = Literal("x")
x.__hash__ = id
print(x.__hash__)

print(hash(x))