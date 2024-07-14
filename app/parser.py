import typing

from .expression import Literal
from .grammar import Token, TokenType
from .lox import Lox


class Parser:

    def __init__(
        self,
        tokens: typing.List[Token]
    ):
        self.tokens = tokens
        self.current = 0

    def expression(self):
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

    def error(self, token: Token, message: str):
        if token.type == TokenType.EOF:
            Lox.report(token.line, " at end", message)
        else:
            Lox.report(token.line, f" at '{token.lexeme}'", message)
