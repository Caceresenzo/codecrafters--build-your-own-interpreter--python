import sys

from .scanner import Scanner
from .parser import Parser
from .expression import AstPrinter

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    
    parser = Parser(tokens)

    if command == "tokenize":
        for token in tokens:
            literal = token.literal
            if literal is None:
                literal = "null"

            print(f"{token.type.name} {token.lexeme} {literal}")

    elif command == "parse":
        root = parser.expression()
        print(AstPrinter().print(root))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if scanner.had_error:
        exit(65)


if __name__ == "__main__":
    main()
