from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result


class Desc(Expr):
    parent: Expr

    def __init__(self, parent: Expr):
        self.parent = parent
        self.varname = parent.varname

    def is_compatible(self, schema: Set[str]) -> Result:
        return self.parent.is_compatible(schema)

    def get_name(self) -> str:
        return self.parent.name

    def compile(self, scope):  # pragma: no cover
        pass
