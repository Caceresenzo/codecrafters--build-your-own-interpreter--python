import enum
import typing

from .evaluation import Interpreter
from .expression import Expression, ExpressionVisitor
from .grammar import Token
from .lox import Lox
from .statement import FunctionStatement, Statement, StatementVisitor


class FunctionType(enum.Enum):
    NONE = enum.auto()
    FUNCTION = enum.auto()
    METHOD = enum.auto()


class Resolver(ExpressionVisitor, StatementVisitor):

    scopes: typing.List[typing.Dict[str, bool]]

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter

        self.scopes = []
        self.current_function = FunctionType.NONE

    def _resolve(self, statement_or_expression: Statement | Expression):
        statement_or_expression.visit(self)

    def resolve_statements(self, statements: typing.List[Statement]):
        for statement in statements:
            self._resolve(statement)

    def _resolve_local(self, expression: Expression, name: Token):
        for index in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[index]:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - index)
                return

    def _resolve_function(self, function: FunctionStatement, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type

        self._begin_scope()

        for parameter in function.parameters:
            self._declare(parameter)
            self._define(parameter)

        self.resolve_statements(function.body)

        self._end_scope()

        self.current_function = enclosing_function

    def _begin_scope(self):
        self.scopes.append({})

    def _end_scope(self):
        self.scopes.pop()

    def _peek_scope(self):
        return self.scopes[-1]

    def _declare(self, name: Token):
        if not len(self.scopes):
            return

        scope = self._peek_scope()
        if name.lexeme in scope:
            Lox.error_token(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def _define(self, name: Token):
        if not len(self.scopes):
            return

        scope = self._peek_scope()
        scope[name.lexeme] = True

    def visit_block(self, block):
        self._begin_scope()
        self.resolve_statements(block.statements)
        self._end_scope()

    def visit_variable_statement(self, variable):
        self._declare(variable.name)

        initializer = variable.initializer
        if initializer:
            self._resolve(initializer)

        self._define(variable.name)

    def visit_variable_expression(self, variable):
        if len(self.scopes) and self._peek_scope().get(variable.name.lexeme) == False:
            Lox.error_token(variable.name, "Can't read local variable in its own initializer.")

        self._resolve_local(variable, variable.name)

    def visit_assign_expression(self, assign):
        self._resolve(assign.value)
        self._resolve_local(assign, assign.name)

    def visit_function(self, function):
        self._declare(function.name)
        self._define(function.name)

        self._resolve_function(function, FunctionType.FUNCTION)

    def visit_expression(self, expression):
        self._resolve(expression.expression)

    def visit_if(self, if_):
        self._resolve(if_.condition)
        self._resolve(if_.then_branch)

        if if_.else_branch is not None:
            self._resolve(if_.else_branch)

    def visit_print(self, print):
        self._resolve(print.expression)

    def visit_return(self, return_):
        if self.current_function == FunctionType.NONE:
            Lox.error_token(return_.keyword, "Can't return from top-level code.")

        if return_.value is not None:
            self._resolve(return_.value)

    def visit_while(self, while_):
        self._resolve(while_.condition)
        self._resolve(while_.body)

    def visit_binary(self, binary):
        self._resolve(binary.left)
        self._resolve(binary.right)

    def visit_call(self, call):
        self._resolve(call.callee)

        for argument in call.arguments:
            self._resolve(argument)

    def visit_grouping(self, grouping):
        self._resolve(grouping.expression)

    def visit_literal(self, literal):
        pass

    def visit_logical(self, logical):
        self._resolve(logical.left)
        self._resolve(logical.right)

    def visit_unary(self, unary):
        self._resolve(unary.right)

    def visit_class(self, class_):
        self._declare(class_.name)
        self._define(class_.name)

        self._begin_scope()
        self._peek_scope()["this"] = True

        for method in class_.methods:
            declaration = FunctionType.METHOD
            self._resolve_function(method, declaration)

        self._end_scope()

    def visit_get(self, get):
        self._resolve(get.object)

    def visit_set(self, set):
        self._resolve(set.value)
        self._resolve(set.object)

    def visit_this(self, this):
        self._resolve_local(this, this.keyword)
