import abc
import dataclasses
import typing


class Expression(abc.ABC):

    @abc.abstractmethod
    def visit(self, visitor: "Visitor"):
        pass


@dataclasses.dataclass
class Literal(Expression):

    value: typing.Any

    def visit(self, visitor: "Visitor"):
        return visitor.visit_literal(self)


class Visitor:

    def visit_literal(self, literal: Literal):
        pass


class AstPrinter(Visitor):

    def visit_literal(self, literal: Literal):
        value = literal.value

        if value is None:
            return "nil"

        if isinstance(value, bool):
            return str(value).lower()

        return str(literal.value)

    def print(self, expression: Expression):
        return expression.visit(self)
