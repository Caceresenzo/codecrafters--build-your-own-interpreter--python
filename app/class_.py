from .function import Callable


class LoxClass(Callable):

    def __init__(self, name: str):
        self.name = name

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return LoxInstance(self)

    def __str__(self):
        return self.name


class LoxInstance:

    def __init__(self, klass: LoxClass):
        self.klass = klass

    def __str__(self):
        return f"{self.klass.name} instance"
