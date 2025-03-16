import typing

from .expression import *
from .grammar import Token, TokenType
from .lox import Lox
from .statement import *


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
            statements: typing.List[Statement] = []

            while not self.is_at_end:
                statements.append(self.declaration())

            return statements
        except ParserError:
            return None

    def parse_expression(self):
        try:
            return self.expression()
        except ParserError:
            return None

    def declaration(self):
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()

            if self.match(TokenType.FUN):
                return self.function("function")

            if self.match(TokenType.VAR):
                return self.variable_declaration()

            return self.statement()
        except ParserError:
            self.synchronize()
            return None

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end:
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStatement(name, methods)

    def function(self, kind: str):
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters: typing.List[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    raise self.error(self.peek(), "Can't have more than 255 parameters.")

                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")

        body = self.block()

        return FunctionStatement(name, parameters, body)

    def variable_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")

        return VariableStatement(name, initializer)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.LEFT_BRACE):
            return BlockStatement(self.block())

        return self.expression_statement()

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = BlockStatement([
                body,
                ExpressionStatement(increment)
            ])

        if condition is None:
            condition = Literal(True)

        body = WhileStatement(condition, body)

        if initializer is not None:
            body = BlockStatement([
                initializer,
                body
            ])

        return body

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()

        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStatement(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")

        return PrintStatement(value)

    def return_statement(self):
        keyword = self.previous()

        value: Expression = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        return ReturnStatement(keyword, value)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        body = self.statement()

        return WhileStatement(condition, body)

    def block(self):
        statements: typing.List[Statement] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end:
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self):
        expression = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")

        return ExpressionStatement(expression)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expression = self.or_()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expression, Variable):
                name = expression.name
                return Assign(name, value)
            elif isinstance(expression, Get):
                return Set(expression.object, expression.name, value)

            raise self.error(equals, "Invalid assignment target.")

        return expression

    def or_(self):
        expression = self.and_()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()
            expression = Logical(expression, operator, right)

        return expression

    def and_(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = Logical(expression, operator, right)

        return expression

    def equality(self):
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()

            expression = Binary(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

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

        return self.call()

    def call(self):
        expression = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expression = Get(expression, name)
            else:
                break

        return expression

    def finish_call(self, callee: Expression):
        arguments: typing.List[Expression] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    raise self.error(self.peek(), "Can't have more than 255 arguments.")

                arguments.append(self.expression())

                if not self.match(TokenType.COMMA):
                    break

        parenthesis = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, parenthesis, arguments)

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.THIS):
            return This(self.previous())

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

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
        Lox.error_token(token, message)

        return ParserError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end:
            if self.previous().type == TokenType.SEMICOLON:
                return

            match self.peek().type:
                case TokenType.CLASS: return
                case TokenType.FUN: return
                case TokenType.VAR: return
                case TokenType.FOR: return
                case TokenType.IF: return
                case TokenType.WHILE: return
                case TokenType.PRINT: return
                case TokenType.RETURN: return

            self.advance()
