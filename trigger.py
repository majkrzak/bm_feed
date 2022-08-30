from typing import Callable, cast

from lark import Lark, Transformer, v_args

from .data import Call

PARSER = Lark(
    r"""
        ?trigger: caller | callee | exp | parens
        
        ?exp: or | and | not
        or: trigger "|" trigger
        and: trigger "&" trigger
        not: "!" trigger
        
        ?parens: "(" trigger ")"
        
        caller: "<" private
        callee: ">" (private | group)
        
        private: callsign | id
        group: "@" id
        
        callsign: /[A-Z0-9]+/
        id: "#" /[0-9]+/
    """,
    start="trigger",
    parser="lalr",
    transformer=v_args(inline=True)(
        type(
            "trigger",
            (Transformer,),
            {
                "or": staticmethod(lambda lhs, rhs: lambda x: lhs(x) or rhs(x)),
                "and": staticmethod(lambda lhs, rhs: lambda x: lhs(x) and rhs(x)),
                "not": staticmethod(lambda rhs: lambda x: not rhs(x)),
                "caller": staticmethod(lambda rhs: lambda x: rhs(x.caller)),
                "callee": staticmethod(lambda rhs: lambda x: rhs(x.callee)),
                "private": staticmethod(lambda rhs: lambda x: rhs(x)),
                "group": staticmethod(lambda rhs: lambda x: x.is_group and rhs(x)),
                "callsign": staticmethod(lambda rhs: lambda x: x.callsign == rhs),
                "id": staticmethod(lambda rhs: lambda x: x.id == int(rhs)),
            },
        )
    )(),
)


class Trigger:
    query: str
    kernel: Callable[[Call], bool]

    def __init__(self, query):
        self.query = query
        self.kernel = cast(Callable[[Call], bool], PARSER.parse(query))

    def __call__(self, event: Call):
        return self.kernel(event)

    def __str__(self):
        return self.query
