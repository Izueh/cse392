from construct.core import *
from json import loads, dumps

JSON = ExprAdapter(GreedyBytes,
        lambda x,y : loads(x),
        lambda x,y : dumps(x)
    )
difuse_request = Struct(
        operation=Int16ub,
        size=Int16ub,
    )
difuse_response = Struct(
        status=Int16ub,
        size=Int16ub)



