# file: lmn/compiler/ast/expressions/expression_base.py
from typing import Any, Dict, Optional, Union

# import ast's
from lmn.compiler.ast.ast_node import ASTNode

class ExpressionBase(ASTNode):
    """
    A base for all expressions. Inherits from ASTNode (which is a Pydantic BaseModel).
    We can store 'inferred_type' or other common expression fields here.
    """
    inferred_type: Optional[Union[str, Dict[str, Any]]] = None
