import typing

from .expression import Binary, Expression, Grouping, Literal, Unary, Visitor
from .grammar import TokenType


class Interpreter(Visitor):

    def evaluate(self, expression: Expression):
        return expression.visit(self)

    def visit_literal(self, literal: Literal):
        return literal.value

    def visit_grouping(self, grouping: Grouping):
        return self.evaluate(grouping.expression)

    def visit_unary(self, unary: Unary):
        right = self.evaluate(unary.right)

        match unary.operator.type:
            case TokenType.BANG: return not self.is_truthy(right)
            case TokenType.MINUS: return -right

        raise NotImplementedError("unreachable")

    def visit_binary(self, binary: Binary):
        raise NotImplementedError()

    def is_truthy(self, value: typing.Any):
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True
