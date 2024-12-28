# lmn/compiler/ast/statements/function_parameter.py
from typing import Literal, Optional
from pydantic import BaseModel

class FunctionParameter(BaseModel):
    type: Literal["FunctionParameter"] = "FunctionParameter"
    name: str
    type_annotation: Optional[str] = None
