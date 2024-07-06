import sys
import typing

from .grammar import Token, TokenType


class Scanner:

    def __init__(
        self,
        source: str
    ):
        self.source = source
        self.tokens: typing.List[Token] = []

        self.start = 0
        self.current = 0
        self.line = 1

        self.had_error = False

    @property
    def is_at_end(self):
        return self.current >= len(self.source)

    @property
    def text(self):
        return self.source[self.start:self.current]

    def scan_tokens(self):
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        character = self.advance()

        match character:
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case ',': self.add_token(TokenType.COMMA)
            case '.': self.add_token(TokenType.DOT)
            case '-': self.add_token(TokenType.MINUS)
            case '+': self.add_token(TokenType.PLUS)
            case ';': self.add_token(TokenType.SEMICOLON)
            case '*': self.add_token(TokenType.STAR)
            case '!': self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case _: self.error(self.line, f"Unexpected character: {character}")

    def advance(self):
        index = self.current
        self.current += 1
        return self.source[index]

    def match(self, expected: str):
        if self.is_at_end:
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def add_token(self, type: TokenType, literal: typing.Any = None):
        self.tokens.append(Token(type, self.text, literal, self.line))

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    for token in tokens:
        literal = token.literal
        if literal is None:
            literal = "null"

        print(f"{token.type.name} {token.lexeme} {literal}")

    if scanner.had_error:
        exit(65)


if __name__ == "__main__":
    main()
