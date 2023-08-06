from typing import Set, List, Dict, Callable
from pandas import DataFrame
from pylars.dsl import ExprDSL, C
from pylars.expr.agg_expr import Count
from pylars.expr.desc import Desc
from pylars.utils import varname, flatlist


class Step:
    schema: Set[str]
    inputs: Set[str]

    def __init__(self, schema: Set[str], inputs: Set[str]):
        self.schema = schema
        self.inputs = inputs
        self.varname = varname("DF", self)

    def __repr__(self):
        self.repr()

    def compile(self) -> List[str]:
        raise NotImplementedError

    def repr(self, indent=0):
        raise NotImplementedError


class Source(Step):

    def __init__(self, schema, name):
        super().__init__(set(schema), set(name))

    def compile(self) -> List[str]:
        inputs_key = list(self.inputs)[0]
        return flatlist(
            f"{self.varname} = {inputs_key}.copy()"
        )

    def repr(self, indent=0):
        return " " * indent + f"Source({self.inputs})"


def check_schema(schema: Set[str], columns: List[ExprDSL]):
    checks = [c.is_compatible(schema) for c in columns]
    reasons = [check.errors for check in checks if not check.compatible]
    if len(reasons) > 0:
        raise Exception(reasons, schema)


class LinearStep(Step):
    def __init__(self, parent, schema):
        self.parent = parent
        super().__init__(schema, self.parent.inputs)

    def compile(self) -> List[str]:
        return self.parent.compile() + self.compile_impl()

    def compile_impl(self) -> List[str]:
        raise NotImplementedError

    def repr(self, indent=0):
        return (" " * indent + f"{self.__class__.__name__}({self.inputs})" + "\n" +
                self.parent.repr(indent + 2))


class Select(LinearStep):
    columns: List[ExprDSL]

    def __init__(self, parent: Step, columns: List[ExprDSL]):
        check_schema(parent.schema, columns)
        super().__init__(parent, set([c.get_name() for c in columns]))
        self.columns = columns

    def compile_impl(self) -> List[str]:
        cols_c = [item
                  for expr in self.columns
                  for item in expr.compile(self.parent)]
        return flatlist(
            cols_c,
            f"{self.varname} = pandas.DataFrame" + "({",
            [f"    '{expr.get_name()}': {self.parent.varname}_{expr.expr.varname},"
             for expr in self.columns],
            "})"
        )


class Assign(LinearStep):
    columns: List[ExprDSL]

    def __init__(self, parent: Step, columns: List[ExprDSL]):
        check_schema(parent.schema, columns)
        super().__init__(parent, parent.schema |
                         set([c.get_name() for c in columns]))
        self.columns = columns

    def compile_impl(self) -> List[str]:
        cols_c = [item
                  for expr in self.columns
                  for item in expr.compile(self.parent)]
        return flatlist(
            cols_c,
            f"{self.varname} = {self.parent.varname}",
            [f"{self.varname}['{col.get_name()}'] = {self.parent.varname}_{col.expr.varname}"
             for col in self.columns])


class Filter(LinearStep):
    predicate: ExprDSL

    def __init__(self, parent: Step, predicate: ExprDSL):
        check_schema(parent.schema, [predicate])
        super().__init__(parent, parent.schema)
        self.parent = parent
        self.predicate = predicate

    def compile_impl(self) -> List[str]:
        cols_c = [item
                  for item in self.predicate.compile(self.parent)]

        return flatlist(
            cols_c,
            f"{self.varname} = {self.parent.varname}.loc[{self.parent.varname}_{self.predicate.expr.varname}]"
        )


class Limit(LinearStep):
    n: int

    def __init__(self, parent: Step, n: int):
        super().__init__(parent, parent.schema)
        self.n = n

    def compile_impl(self) -> List[str]:
        return flatlist(f"{self.varname} = {self.parent.varname}.head({self.n})")


class GroupBy(LinearStep):
    grps: Set[str]
    aggs: List[ExprDSL]

    def __init__(self, parent, grps, *aggs):
        check_schema(parent.schema, map(C, grps))
        check_schema(parent.schema - set(grps), aggs)
        super().__init__(parent,
                         set(grps) | set(map(lambda x: x.get_name(), aggs)))

        self.parent = parent
        self.grps = set(grps)
        self.aggs = list(aggs)

    def compile_impl(self) -> List[str]:
        if any(map(lambda x: isinstance(x.expr, Count), self.aggs)):
            add_c = [f"{self.parent.varname}['COUNTS'] = 1"]
        else:
            add_c = []

        return flatlist(
            add_c,
            f"{self.varname} = {self.parent.varname}.groupby({list(self.grps)})" +
            ".agg(**{",
            ["    " + f"'{agg.get_name()}': {agg.compile(self.parent)},"
             for agg in self.aggs],
            "}).reset_index()"
        )


class Join(Step):
    lhs: Step
    rhs: Step
    on: List[ExprDSL]
    how: str

    def __init__(self, lhs: Step, rhs: Step, on: List[ExprDSL], how: str):
        check_schema(lhs.schema, on)
        check_schema(rhs.schema, on)
        self.lhs = lhs
        self.rhs = rhs
        self.on = on
        self.how = how
        super().__init__(lhs.schema | rhs.schema, lhs.inputs | rhs.inputs)

    def compile(self) -> List[str]:
        return flatlist(
            self.lhs.compile(),
            self.rhs.compile(),
            f"{self.varname} = {self.lhs.varname}.merge(",
            f"    {self.rhs.varname},",
            f"    how='{self.how}',",
            f"    on={list(map(lambda x: x.get_name(), self.on))}",
            f")"
        )

    def repr(self, indent=0):
        return (" " * indent + f"{self.__class__.__name__}({self.inputs})" + "\n" +
                self.lhs.repr(indent + 2) + "\n" +
                self.rhs.repr(indent + 2))


class OrderBy(LinearStep):
    def __init__(self, parent: Step, by: List[ExprDSL]):
        check_schema(parent.schema, by)
        self.by = by
        super().__init__(parent, parent.schema)

    def compile_impl(self) -> List[str]:
        names = [x.get_name()
                 for x in self.by]
        orders = [not isinstance(x.expr, Desc)
                  for x in self.by]

        return flatlist(f"{self.varname} = {self.parent.varname}.sort_values(",
                        f"by={names},ascending={orders}",
                        f").reset_index(drop=True)")


class Drop(LinearStep):
    def __init__(self, parent: Step, columns: List[str]):
        check_schema(parent.schema, map(C, columns))
        self.columns = columns
        super().__init__(parent, parent.schema)

    def compile_impl(self) -> List[str]:
        return flatlist(f"{self.varname} = {self.parent.varname}.drop(",
                        f"columns={self.columns}",
                        f").reset_index(drop=True)")
