import typing

from .error import RuntimeError
from .expression import Expression, ExpressionVisitor
from .grammar import Token, TokenType
from .lox import Lox, Environment
from .statement import Statement, StatementVisitor


class Interpreter(ExpressionVisitor, StatementVisitor):

    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: typing.List[Statement]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            Lox.report_runtime(error.token.line, str(error))

    def interpret_expression(self, expression: Expression):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except RuntimeError as error:
            Lox.report_runtime(error.token.line, str(error))

    def execute(self, statement: Statement):
        statement.visit(self)

    def evaluate(self, expression: Expression):
        return expression.visit(self)

    def visit_expression(self, expression):
        self.evaluate(expression.expression)

    def visit_print(self, print_):
        value = self.evaluate(print_.expression)
        print(self.stringify(value))

    def visit_variable_statement(self, variable):
        value = None
        if variable.initializer is not None:
            value = self.evaluate(variable.initializer)

        self.environment.define(variable.name.lexeme, value)

    def visit_literal(self, literal):
        return literal.value

    def visit_grouping(self, grouping):
        return self.evaluate(grouping.expression)

    def visit_unary(self, unary):
        right = self.evaluate(unary.right)

        match unary.operator.type:
            case TokenType.BANG: return not self.is_truthy(right)

            case TokenType.MINUS:
                self.check_number_operand(unary.operator, right)
                return -right

        raise NotImplementedError("unreachable")

    def visit_binary(self, binary):
        left = self.evaluate(binary.left)
        right = self.evaluate(binary.right)

        match binary.operator.type:
            case TokenType.MINUS:
                self.check_number_operands(binary.operator, left, right)
                return left - right

            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right

                if isinstance(left, str) and isinstance(right, str):
                    return left + right

                raise RuntimeError(binary.operator, "Operands must be two numbers or two strings.")

            case TokenType.SLASH:
                self.check_number_operands(binary.operator, left, right)
                return left / right

            case TokenType.STAR:
                self.check_number_operands(binary.operator, left, right)
                return left * right

            case TokenType.GREATER:
                self.check_number_operands(binary.operator, left, right)
                return left > right

            case TokenType.GREATER_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left >= right

            case TokenType.LESS:
                self.check_number_operands(binary.operator, left, right)
                return left < right

            case TokenType.LESS_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left <= right

            case TokenType.BANG_EQUAL: return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL: return self.is_equal(left, right)

        raise NotImplementedError("unreachable")

    def visit_variable_expression(self, variable):
        return self.environment.get(variable.name)

    def visit_assign_expression(self, assign):
        value = self.evaluate(assign.value)

        self.environment.assign(assign.name, value)

        return value

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

    def check_number_operands(self, operator: Token, left: typing.Any, right: typing.Any):
        if isinstance(left, float) and isinstance(right, float):
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
