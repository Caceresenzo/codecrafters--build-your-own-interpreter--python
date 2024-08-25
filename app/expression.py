import abc
import dataclasses
import typing

from .grammar import Token


class Expression(abc.ABC):

    @abc.abstractmethod
    def visit(self, visitor: "ExpressionVisitor"):
        pass


@dataclasses.dataclass
class Literal(Expression):

    value: typing.Any

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_literal(self)


@dataclasses.dataclass
class Grouping(Expression):

    expression: Expression

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_grouping(self)


@dataclasses.dataclass
class Unary(Expression):

    operator: Token
    right: Expression

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_unary(self)


@dataclasses.dataclass
class Binary(Expression):

    left: Expression
    operator: Token
    right: Expression

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_binary(self)


@dataclasses.dataclass
class Variable(Expression):

    name: Token

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_variable_expression(self)


@dataclasses.dataclass
class Assign(Expression):

    name: Token
    value: Expression

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visit_assign_expression(self)


class ExpressionVisitor:

    def visit_literal(self, literal: Literal):
        pass

    def visit_grouping(self, grouping: Grouping):
        pass

    def visit_unary(self, unary: Unary):
        pass

    def visit_binary(self, binary: Binary):
        pass

    def visit_variable_expression(self, variable: Variable):
        pass

    def visit_assign_expression(self, assign: Assign):
        pass


class AstPrinter(ExpressionVisitor):

    def visit_literal(self, literal: Literal):
        value = literal.value

        if value is None:
            return "nil"

        if isinstance(value, bool):
            return str(value).lower()

        return str(literal.value)

    def visit_grouping(self, grouping: Grouping):
        return self.parenthesize("group", grouping.expression)

    def visit_unary(self, unary: Unary):
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def visit_binary(self, binary: Binary):
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def print(self, expression: Expression):
        return expression.visit(self)

    def parenthesize(self, name: str, *expressions: Expression):
        builder = f"({name}"

        for expression in expressions:
            builder += " "
            builder += expression.visit(self)

        return builder + ")"
