from pylars.expr.unary_expr import MethodExpr
from pylars.utils import regex, string, assign, arglist


class Capitalize(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.capitalize")


class Casefold(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.casefold")

# cat
# split
# rsplit
# partition
# rpartition
# get
# join


class Contains(MethodExpr):
    def __init__(self, parent, pat):
        super().__init__(parent, "str.contains", regex(pat))


class Match(MethodExpr):
    def __init__(self, parent, pat):
        super().__init__(parent, "str.match", regex(pat))


class Replace(MethodExpr):
    def __init__(self, parent, pat, repl):
        super().__init__(parent, "str.replace", arglist(
            assign("pat", regex(pat)),
            assign("repl", string(repl)))
        )

# repeat
# pad
# center
# ljust
# rjust
# zfill
# slice
# slice_replace
# decode
# encode
# strip
# lstrip
# rstrip
# wrap
# get_dummies
# translate
# count
# startswith
# endswith
# findall
# extract
# extractall
# find
# rfind
# normalize
# index
# rindex


class Len(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.len")


class Lower(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.lower")


class Upper(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.upper")


class Title(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.title")


class Swapcase(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.swapcase")


class Isalnum(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isalnum")


class Isalpha(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isalpha")


class Isdigit(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isdigit")


class Isspace(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isspace")


class Islower(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.islower")


class Isupper(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isupper")


class Istitle(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.istitle")


class Isnumeric(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isnumeric")


class Isdecimal(MethodExpr):
    def __init__(self, parent):
        super().__init__(parent, "str.isdecimal")
