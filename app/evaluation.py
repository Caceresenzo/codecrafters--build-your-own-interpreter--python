from .expression import Binary, Grouping, Literal, Unary, Visitor, Expression


class Interpreter(Visitor):

    def evaluate(self, expression: Expression):
        return expression.visit(self)

    def visit_literal(self, literal: Literal):
        return literal.value

    def visit_grouping(self, grouping: Grouping):
        return self.evaluate(grouping.expression)

    def visit_unary(self, unary: Unary):
        raise NotImplementedError()

    def visit_binary(self, binary: Binary):
        raise NotImplementedError()
