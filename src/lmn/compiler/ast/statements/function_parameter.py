# lmn/compiler/ast/statements/function_parameter.py
from typing import Literal, Optional
from pydantic import BaseModel

class FunctionParameter(BaseModel):
    # The kind of the node
    type: Literal["FunctionParameter"] = "FunctionParameter"

    # The name and optional type annotation
    name: str
    type_annotation: Optional[str] = None
