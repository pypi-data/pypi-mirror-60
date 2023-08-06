
from pylars.dsl import ExprDSL
import pylars.expr.agg_expr as agg


def Count():
    return ExprDSL(agg.Count())


def Sum(name):
    return ExprDSL(agg.Sum(name))


def Mean(name):
    return ExprDSL(agg.Mean(name))
