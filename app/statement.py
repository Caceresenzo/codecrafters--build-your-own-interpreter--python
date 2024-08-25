import abc
import dataclasses

from .expression import Expression


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


class StatementVisitor:

    def visit_expression(self, expression: ExpressionStatement):
        pass

    def visit_print(self, print: PrintStatement):
        pass
