from pylars.dsl import ExprDSL
from pylars.expr.stringops import *


class StringDSL:
    def __init__(self, expr):  # pragma: no cover
        self.expr = expr

    def capitalize(self):
        return ExprDSL(Capitalize(self.expr))

    def casefold(self):
        return ExprDSL(Casefold(self.expr))

    def contains(self, pat):
        return ExprDSL(Contains(self.expr, pat))

    def match(self, pat):
        return ExprDSL(Match(self.expr, pat))

    def replace(self, pat, repl):
        return ExprDSL(Replace(self.expr, pat, repl))

    def len(self):
        return ExprDSL(Len(self.expr))

    def lower(self):
        return ExprDSL(Lower(self.expr))

    def upper(self):
        return ExprDSL(Upper(self.expr))

    def title(self):
        return ExprDSL(Title(self.expr))

    def isalnum(self):
        return ExprDSL(Isalnum(self.expr))

    def isalpha(self):
        return ExprDSL(Isalpha(self.expr))

    def isdigit(self):
        return ExprDSL(Isdigit(self.expr))

    def isspace(self):
        return ExprDSL(Isspace(self.expr))

    def islower(self):
        return ExprDSL(Islower(self.expr))

    def isupper(self):
        return ExprDSL(Isupper(self.expr))

    def istitle(self):
        return ExprDSL(Istitle(self.expr))

    def isnumeric(self):
        return ExprDSL(Isnumeric(self.expr))

    def isdecimal(self):
        return ExprDSL(Isdecimal(self.expr))
