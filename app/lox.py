import sys


class Lox:

    had_error = False
    had_runtime_error = False

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        Lox.had_error = True

    @staticmethod
    def report_runtime(line: int, message: str):
        print(f"{message}\n[line {line}]", file=sys.stderr)
        Lox.had_runtime_error = True
