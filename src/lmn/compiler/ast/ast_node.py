# file: lmn/compiler/ast/ast_node.py
import json
import logging
from pydantic import BaseModel
from typing import Any, Dict

logger = logging.getLogger(__name__)

class ASTNode(BaseModel):
    # define the model configuration
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",
        "use_enum_values": True
    }

    def __repr__(self) -> str:
        # output the node as a string
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields_str})"

    def to_dict(self) -> dict:
        # output the node as a dictionary
        return self.model_dump(by_alias=True, exclude_none=True)

    def to_json(self) -> str:
        """
        Output the node as a pretty-printed JSON string.
        Again, we add debug logs to see the final JSON.
        """
        dict_data = self.to_dict()
        json_str = json.dumps(dict_data, indent=2)
        #logger.debug("ASTNode.to_json() => %s", json_str)
        return json_str