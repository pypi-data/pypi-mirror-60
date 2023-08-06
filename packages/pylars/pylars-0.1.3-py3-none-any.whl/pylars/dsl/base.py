from pylars.dsl import ExprDSL
from pylars.expr import Column, Litteral


def C(name: str):
    return ExprDSL(Column(name))


def L(name: str):
    return ExprDSL(Litteral(name))
