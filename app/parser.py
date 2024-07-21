import typing

from .expression import Binary, Grouping, Literal, Unary
from .grammar import Token, TokenType
from .lox import Lox


class ParserError(RuntimeError):
    pass


class Parser:

    def __init__(
        self,
        tokens: typing.List[Token]
    ):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParserError:
            return None

    def expression(self):
        return self.comparison()

    def comparison(self):
        expression = self.factor()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()

            expression = Binary(expression, operator, right)

        return expression

    def term(self):
        expression = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()

            expression = Binary(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()

            expression = Binary(expression, operator, right)

        return expression

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()

            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()

            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")

            return Grouping(expression)

        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types: typing.Iterable[TokenType]):
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType):
        if self.is_at_end:
            return False

        return self.peek().type == type

    def advance(self):
        if not self.is_at_end:
            self.current += 1

        return self.previous()

    @property
    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        if token.type == TokenType.EOF:
            Lox.report(token.line, " at end", message)
        else:
            Lox.report(token.line, f" at '{token.lexeme}'", message)

        return ParserError()
