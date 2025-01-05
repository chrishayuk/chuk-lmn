# lmn/compiler/ast/statements/function_parameter.py
from __future__ import annotations
from typing import Literal, Optional

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class FunctionParameter(StatementBase):
    # The kind of the node
    type: Literal["FunctionParameter"] = "FunctionParameter"

    # The name and optional type annotation
    name: str
    type_annotation: Optional[str] = None
