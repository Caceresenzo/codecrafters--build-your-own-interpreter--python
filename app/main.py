import sys

from .evaluation import Interpreter
from .expression import AstPrinter
from .lox import Lox
from .parser import Parser
from .resolver import Resolver
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
    root = parser.parse_expression()

    if not Lox.had_error:
        print(AstPrinter().print(root))


def evaluate(content: str):
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()

    if Lox.had_error:
        return

    parser = Parser(tokens)
    expression = parser.parse_expression()

    if Lox.had_error:
        return

    interpreter = Interpreter()
    interpreter.interpret_expression(expression)


def run(content: str):
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()

    if Lox.had_error:
        return

    parser = Parser(tokens)
    statements = parser.parse()

    if Lox.had_error:
        return
    
    interpreter = Interpreter()

    resolver = Resolver(interpreter);
    resolver.resolve_statements(statements);

    interpreter.interpret(statements)


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

    elif command == "evaluate":
        evaluate(file_contents)

    elif command == "run":
        run(file_contents)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if Lox.had_error:
        exit(65)

    if Lox.had_runtime_error:
        exit(70)


if __name__ == "__main__":
    main()
