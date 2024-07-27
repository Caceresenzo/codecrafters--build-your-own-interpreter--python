import typing
import builtins

from .expression import Binary, Expression, Grouping, Literal, Unary, Visitor
from .grammar import TokenType, Token
from .lox import Lox


class RuntimeError(builtins.RuntimeError):

    def __init__(self, token: Token, *args):
        super().__init__(*args)

        self.token = token


class Interpreter(Visitor):

    def interpret(self, expression: Exception):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except RuntimeError as error:
            Lox.report_runtime(error.token.line, str(error))

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

            case TokenType.MINUS:
                self.check_number_operand(unary.operator, right)
                return -right

        raise NotImplementedError("unreachable")

    def visit_binary(self, binary: Binary):
        left = self.evaluate(binary.left)
        right = self.evaluate(binary.right)

        match binary.operator.type:
            case TokenType.MINUS: return left - right
            case TokenType.PLUS: return left + right
            case TokenType.SLASH: return left / right
            case TokenType.STAR: return left * right
            case TokenType.GREATER: return left > right
            case TokenType.GREATER_EQUAL: return left >= right
            case TokenType.LESS: return left < right
            case TokenType.LESS_EQUAL: return left <= right
            case TokenType.BANG_EQUAL: return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL: return self.is_equal(left, right)

        raise NotImplementedError("unreachable")

    def is_truthy(self, value: typing.Any):
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def is_equal(self, a: typing.Any, b: typing.Any):
        if a is None and b is None:
            return True

        if a is None:
            return False

        return a == b

    def check_number_operand(self, operator: Token, operand: typing.Any):
        if isinstance(operand, float):
            return

        raise RuntimeError(operator, "Operand must be a number.")

    def stringify(self, value: typing.Any):
        if value is None:
            return "nil"

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, float):
            value = str(value)

            if value.endswith(".0"):
                value = value[:-2]

            return value

        return str(value)
