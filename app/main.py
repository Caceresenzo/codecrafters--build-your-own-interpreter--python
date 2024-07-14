import sys

from .expression import AstPrinter
from .lox import Lox
from .parser import Parser
from .scanner import Scanner


def tokenize(content: str):
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()

    for token in tokens:
        literal = token.literal
        if literal is None:
            literal = "null"

        print(f"{token.type.name} {token.lexeme} {literal}")


def parse(content: str):
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()

    if Lox.had_error:
        return

    parser = Parser(tokens)
    root = parser.parse()

    if not Lox.had_error:
        print(AstPrinter().print(root))


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()

    if command == "tokenize":
        tokenize(file_contents)

    elif command == "parse":
        parse(file_contents)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if Lox.had_error:
        exit(65)


if __name__ == "__main__":
    main()
