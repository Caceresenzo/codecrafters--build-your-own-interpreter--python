import time
import typing

from .class_ import LoxClass
from .error import RuntimeError
from .expression import Expression, ExpressionVisitor
from .function import Callable, LoxFunction, NativeFunction, Return
from .grammar import Token, TokenType
from .lox import Environment, Lox
from .statement import Statement, StatementVisitor


class Interpreter(ExpressionVisitor, StatementVisitor):

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        self.locals: typing.Dict[int, int] = {}

        self.globals.define("clock", NativeFunction("clock", 0, lambda: float(int(time.time()))))

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

    def execute_block(self, statements: typing.List[Statement], environment: Environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def execute(self, statement: Statement):
        statement.visit(self)

    def resolve(self, expression: Expression, depth: int):
        self.locals[id(expression)] = depth

    def evaluate(self, expression: Expression):
        return expression.visit(self)

    def visit_expression(self, expression):
        self.evaluate(expression.expression)

    def visit_function(self, function):
        lox_function = LoxFunction(function, self.environment)

        self.environment.define(function.name.lexeme, lox_function)

    def visit_if(self, if_):
        if self.is_truthy(self.evaluate(if_.condition)):
            self.execute(if_.then_branch)
        elif if_.else_branch is not None:
            self.execute(if_.else_branch)

    def visit_print(self, print_):
        value = self.evaluate(print_.expression)
        print(self.stringify(value))

    def visit_return(self, return_):
        value = None
        if return_.value is not None:
            value = self.evaluate(return_.value)

        raise Return(value)

    def visit_while(self, while_):
        while self.is_truthy(self.evaluate(while_.condition)):
            self.execute(while_.body)

    def visit_variable_statement(self, variable):
        value = None
        if variable.initializer is not None:
            value = self.evaluate(variable.initializer)

        self.environment.define(variable.name.lexeme, value)

    def visit_block(self, block):
        self.execute_block(block.statements, self.environment.inner())

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
        return self.look_up_variable(variable.name, variable)

    def look_up_variable(self, name: Token, expression: Expression):
        distance = self.locals.get(id(expression))

        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)

        return self.globals.get(name)

    def visit_assign_expression(self, assign):
        value = self.evaluate(assign.value)

        distance = self.locals.get(id(assign))
        if distance is not None:
            self.environment.assign_at(distance, assign.name, value)
        else:
            self.globals.assign(assign.name, value)

        return value

    def visit_logical(self, logical):
        left = self.evaluate(logical.left)

        if logical.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(logical.right)

    def visit_call(self, call):
        callee = self.evaluate(call.callee)

        arguments = [
            self.evaluate(argument)
            for argument in call.arguments
        ]

        if not isinstance(callee, Callable):
            raise RuntimeError(call.parenthesis, "Can only call functions and classes.")

        function = typing.cast(Callable, callee)
        if len(arguments) != function.arity():
            raise RuntimeError(call.parenthesis, f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_class(self, class_):
        self.environment.define(class_.name.lexeme, None)

        klass = LoxClass(class_.name.lexeme)

        self.environment.assign(class_.name, klass)

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
