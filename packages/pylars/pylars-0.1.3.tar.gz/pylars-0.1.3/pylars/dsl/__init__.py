from pylars.utils import extendDSL
from pylars.dsl.exprdsl import *
from pylars.dsl.base import *
from pylars.dsl.aggs import *
from pylars.dsl.stringdsl import StringDSL

extendDSL(ExprDSL, StringDSL)


class Catalog:
    def __getattribute__(self, attr):
        return C(attr)


_ = Catalog()
