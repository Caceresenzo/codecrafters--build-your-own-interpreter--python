import abc
import dataclasses
import typing

from .expression import Expression
from .grammar import Token


class Statement(abc.ABC):

    @abc.abstractmethod
    def visit(self, visitor: "StatementVisitor"):
        pass


@dataclasses.dataclass
class ExpressionStatement(abc.ABC):

    expression: Expression

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_expression(self)


@dataclasses.dataclass
class PrintStatement(abc.ABC):

    expression: Expression

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_print(self)


@dataclasses.dataclass
class VariableStatement(abc.ABC):

    name: Token
    initializer: typing.Optional[Expression]

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_variable_statement(self)


class StatementVisitor:

    def visit_expression(self, expression: ExpressionStatement):
        pass

    def visit_print(self, print: PrintStatement):
        pass

    def visit_variable_statement(self, variable: VariableStatement):
        pass
