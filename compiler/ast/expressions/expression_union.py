# compiler/ast/expressions/expression_union.py
from __future__ import annotations
from typing import Annotated, Union
from pydantic import Field

# We list each expression class as a *string* instead of importing it,
# avoiding circular imports.
ExpressionUnion = Annotated[
    Union[
        "LiteralExpression",
        "VariableExpression",
        "BinaryExpression",
        "UnaryExpression",
        "FnExpression",
    ],
    Field(discriminator="type")
]
