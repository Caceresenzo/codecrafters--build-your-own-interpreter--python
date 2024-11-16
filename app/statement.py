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
class ExpressionStatement(Statement):

    expression: Expression

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_expression(self)


@dataclasses.dataclass
class FunctionStatement(Statement):

    name: Token
    parameters: typing.List[Token]
    body: typing.List[Statement]

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_function(self)


@dataclasses.dataclass
class IfStatement(Statement):

    condition: Expression
    then_branch: Statement
    else_branch: typing.Optional[Statement]

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_if(self)


@dataclasses.dataclass
class PrintStatement(Statement):

    expression: Expression

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_print(self)


@dataclasses.dataclass
class WhileStatement(Statement):

    condition: Expression
    body: Statement

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_while(self)


@dataclasses.dataclass
class VariableStatement(Statement):

    name: Token
    initializer: typing.Optional[Expression]

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_variable_statement(self)


@dataclasses.dataclass
class BlockStatement(Statement):

    statements: typing.List[Expression]

    def visit(self, visitor: "StatementVisitor"):
        visitor.visit_block(self)


class StatementVisitor:

    def visit_expression(self, expression: ExpressionStatement):
        pass

    def visit_function(self, function: FunctionStatement):
        pass

    def visit_if(self, if_: IfStatement):
        pass

    def visit_print(self, print: PrintStatement):
        pass

    def visit_while(self, while_: WhileStatement):
        pass

    def visit_variable_statement(self, variable: VariableStatement):
        pass

    def visit_block(self, block: BlockStatement):
        pass
