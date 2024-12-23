# lmn/compiler/ast/mega_union.py
from __future__ import annotations
from typing import Annotated, Union
from pydantic import Field

MegaUnion = Annotated[
    Union[
        # Expressions
        "LiteralExpression",
        "VariableExpression",
        "BinaryExpression",
        "UnaryExpression",
        "FnExpression",
        # Statements
        "CallStatement",
        "ForStatement",
        "FunctionDefinition",
        "IfStatement",
        "PrintStatement",
        "ReturnStatement",
        "SetStatement",
    ],
    Field(discriminator="type")
]
