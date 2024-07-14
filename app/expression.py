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


@dataclasses.dataclass
class Grouping(Expression):

    expression: Expression

    def visit(self, visitor: "Visitor"):
        return visitor.visit_grouping(self)


class Visitor:

    def visit_literal(self, literal: Literal):
        pass

    def visit_grouping(self, grouping: Grouping):
        pass


class AstPrinter(Visitor):

    def visit_literal(self, literal: Literal):
        value = literal.value

        if value is None:
            return "nil"

        if isinstance(value, bool):
            return str(value).lower()

        return str(literal.value)

    def visit_grouping(self, grouping: Grouping):
        return self.parenthesize("group", grouping.expression)

    def print(self, expression: Expression):
        return expression.visit(self)

    def parenthesize(self, name: str, *expressions: Expression):
        builder = f"({name}"

        for expression in expressions:
            builder += " "
            builder += expression.visit(self)

        return builder + ")"
