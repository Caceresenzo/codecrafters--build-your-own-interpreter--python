import builtins

from .grammar import Token


class RuntimeError(builtins.RuntimeError):

    def __init__(self, token: Token, *args):
        super().__init__(*args)

        self.token = token
