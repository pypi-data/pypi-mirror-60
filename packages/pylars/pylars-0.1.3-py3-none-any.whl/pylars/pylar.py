
from pylars.steps import *
from pylars.utils import flatlist
from typing import List


class Pylar:
    ast: Step

    def __init__(self, name, schema):
        self.ast = Source(set(schema), set([name]))

    def __repr__(self):
        return self.ast.repr()

    def _compile(self):

        parameters = ','.join(self.ast.inputs)

        module = flatlist(
            f"def compute({parameters}):",
            "    import pandas",
            "    import operator",
            "    import numpy as np",
            ["    " + line for line in self.ast.compile()],
            f"    return {self.ast.varname}",
            "\n"
        )

        return module

    def compile(self, export_file=None):
        code = "\n".join(self._compile())
        if export_file != None:
            with open(export_file, "w") as ofile:
                ofile.write(code)

        exec(code)

        return locals()['compute']

    def select(self, *args, **kwargs):

        kwargs_exprs = [expr.alias(name)
                        for name, expr in kwargs.items()]

        args_exprs = [arg for arg in args]

        self.ast = Select(self.ast, args_exprs + kwargs_exprs)
        return self

    def assign(self, *args, **kwargs):

        kwargs_exprs = [expr.alias(name)
                        for name, expr in kwargs.items()]

        args_exprs = [arg for arg in args]

        self.ast = Assign(self.ast, args_exprs + kwargs_exprs)
        return self

    def filter(self, predicate: ExprDSL):
        self.ast = Filter(self.ast, predicate)
        return self

    def limit(self, n: int):
        self.ast = Limit(self.ast, n)
        return self

    def groupby(self, grps, *args):
        self.ast = GroupBy(self.ast, grps, *args)
        return self

    def inner_join(self, right, *on: List[ExprDSL]):
        self.ast = Join(self.ast, right.ast, list(on), "inner")
        return self

    def left_join(self, right, *on: List[ExprDSL]):
        self.ast = Join(self.ast, right.ast, list(on), "left")
        return self

    def right_join(self, right, *on: List[ExprDSL]):
        self.ast = Join(self.ast, right.ast, list(on), "right")
        return self

    def outer_join(self, right, *on: List[ExprDSL]):
        self.ast = Join(self.ast, right.ast, list(on), "outer")
        return self

    def order_by(self, *by):
        self.ast = OrderBy(self.ast, by)
        return self

    def drop(self, *columns):
        self.ast = Drop(self.ast, list(columns))
        return self
