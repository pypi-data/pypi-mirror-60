from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result, success, failure
from pylars.utils import varname


class Column(Expr):
    name: str

    def __init__(self, name: str):
        self.name = name
        self.varname = varname("COL", self)

    def is_compatible(self, schema: Set[str]) -> Result:
        if self.name in schema:
            return success()
        else:
            return failure(f"Column `{self.name}` is not present in schema.")

    def get_name(self) -> str:
        return self.name

    def compile(self, scope) -> str:
        return [f"{scope.varname}_{self.varname} = {scope.varname}['{self.name}']"]
