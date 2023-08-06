from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result


class Alias(Expr):
    parent: Expr
    name: str

    def __init__(self, parent: Expr, name: str):
        self.parent = parent
        self.name = name
        self.varname = parent.varname

    def is_compatible(self, schema: Set[str]) -> Result:
        return self.parent.is_compatible(schema)

    def get_name(self) -> str:
        return self.name

    def compile(self, scope):
        return self.parent.compile(scope)
