from typing import Set
from pylars.expr import Expr
from pylars.expr.result import Result, combine
from pylars.utils import varname
import operator


class BinaryExpr(Expr):
    lhs: Expr
    rhs: Expr

    def __init__(self, lhs: Expr, rhs: Expr, ops):
        self.lhs = lhs
        self.rhs = rhs
        self.ops = ops
        self.varname = varname("COL", self)

    def is_compatible(self, schema: Set[str]) -> Result:
        return combine(self.lhs.is_compatible(schema),
                       self.lhs.is_compatible(schema))

    def compile(self, scope):
        lhs_c = self.lhs.compile(scope)
        rhs_c = self.rhs.compile(scope)
        return lhs_c + rhs_c + [
            f"{scope.varname}_{self.varname} = {self.ops}(",
            f"    {scope.varname}_{self.lhs.varname},",
            f"    {scope.varname}_{self.rhs.varname}",
            ")"
        ]

    def get_name(self):
        return f"{type(self).__name__}({self.lhs.get_name()},{self.rhs.get_name()})"


class Equals(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__eq__")


class NotEquals(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__ne__")


class GreaterThan(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__gt__")


class LesserThan(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__lt__")


class GreaterThanOrEquals(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__ge__")


class LesserThanOrEquals(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__le__")


class Plus(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__add__")


class Minus(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__sub__")


class Multiply(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__mul__")


class TrueDiv(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__truediv__")


class FloorDiv(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__floordiv__")


class Modulo(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__mod__")


class And(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__and__")


class Or(BinaryExpr):
    def __init__(self, lhs: Expr, rhs: Expr):
        super().__init__(lhs, rhs, "operator.__or__")
