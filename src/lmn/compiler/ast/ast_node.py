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
        data = self.model_dump(
            exclude_none=False,      # do not exclude fields that are None
            exclude_unset=False,     # do not exclude fields that haven't been explicitly set
            exclude_defaults=False   # do not exclude fields that match their default value
        )
        return data

    def to_json(self) -> str:
        """
        Output the node as a pretty-printed JSON string.
        Again, we add debug logs to see the final JSON.
        """
        dict_data = self.to_dict()
        json_str = json.dumps(dict_data, indent=2)
        #logger.debug("ASTNode.to_json() => %s", json_str)
        return json_str

# # lmn/compiler/ast/ast_node.py
# import json
# from pydantic import BaseModel
# from typing import Any, Dict

# class ASTNode(BaseModel):
#     # define the model configuration
#     model_config = {
#         "arbitrary_types_allowed": True,
#         "extra": "allow"
#     }

#     def __repr__(self) -> str:
#         # output the node as a string
#         fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())

#         # return the string representation of the object
#         return f"{self.__class__.__name__}({fields_str})"


#     def to_dict(self) -> dict:
#         # output the node as a dictionary
#         return self.model_dump(by_alias=True, exclude_none=True)
 
#     def to_json(self):
#         # output the node as json
#         return json.dumps(self.to_dict(), indent=2)