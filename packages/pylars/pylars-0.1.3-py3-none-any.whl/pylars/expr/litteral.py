from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result, success
from pylars.utils import varname


class Litteral(Expr):
    def __init__(self, value):
        self.value = value
        self.varname = varname("COL", self)

    def is_compatible(self, schema: Set[str]) -> Result:
        return success()

    def get_name(self) -> str:
        return str(self.value)

    def compile(self, scope):
        if isinstance(self.value, str):
            value_str = f"\"{self.value}\""
        else:
            value_str = f"{self.value}"

        return [f"{scope.varname}_{self.varname} = {value_str}"]
