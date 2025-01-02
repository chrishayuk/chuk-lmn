# lmn/compiler/ast/ast_node.py
import json
from pydantic import BaseModel
from typing import Any, Dict

class ASTNode(BaseModel):
    # define the model configuration
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow"
    }

    def __repr__(self) -> str:
        # output the node as a string
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())

        # return the string representation of the object
        return f"{self.__class__.__name__}({fields_str})"


    def to_dict(self) -> dict:
        # output the node as a dictionary
        return self.model_dump(by_alias=True, exclude_none=True)
 
    def to_json(self):
        # output the node as json
        return json.dumps(self.to_dict(), indent=2)
