# compiler/ast/ast_node.py

from pydantic import BaseModel
from typing import Any, Dict

class ASTNode(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow"
    }

    def __repr__(self) -> str:
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields_str})"


    def to_dict(self) -> dict:
        # Force usage of the alias-based keys
        return self.model_dump(by_alias=True)
