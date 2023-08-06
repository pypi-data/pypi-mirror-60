from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result, success, failure
import numpy as np


class Count(Expr):
    def __init__(self):
        pass

    def is_compatible(self, schema: Set[str]) -> Result:
        return success()

    def get_name(self):
        return f"Count"

    def compile(self, scope):
        return "('COUNTS', np.size)"


class AggExpr(Expr):
    name: str

    def __init__(self, name, aggfunc):
        self.name = name
        self.aggfunc = aggfunc

    def is_compatible(self, schema: Set[str]) -> Result:
        if self.name in schema:
            return success()
        else:
            return failure(f"Column `{self.name}` not in schema.")

    def get_name(self):
        return f"{type(self).__name__}({self.name})"

    def compile(self, scope):
        return f"('{self.name}', {self.aggfunc})"


class Sum(AggExpr):
    def __init__(self, name):
        super().__init__(name, "np.sum")


class Mean(AggExpr):
    def __init__(self, name):
        super().__init__(name, "np.mean")
